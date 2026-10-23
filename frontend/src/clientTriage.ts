import type { NotificationItem, ClusterGroup, PriorityAction, QueueResponse } from './types';

const NOISE_WORDS = [
  '+1', 'lunch menu', 'cafeteria', 'coffee', 'closed inactive', 'marked as stale',
  'scheduled security scan: 0', 'daily spend within expected', 'monitor up:', 'all checks green'
];

export function runClientSideTriage(datasetName: string, items: NotificationItem[]): QueueResponse {
  const start = performance.now();

  // Simple tokenization and grouping
  const clusters: ClusterGroup[] = [];
  const assigned = new Set<string>();

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (assigned.has(item.id)) continue;

    const group = [item];
    assigned.add(item.id);

    const cleanTitle = item.title.toLowerCase().replace(/\[.*?\]/g, '').trim();

    for (let j = i + 1; j < items.length; j++) {
      const candidate = items[j];
      if (assigned.has(candidate.id)) continue;

      const candTitle = candidate.title.toLowerCase().replace(/\[.*?\]/g, '').trim();
      if (cleanTitle && candTitle && (cleanTitle.includes(candTitle) || candTitle.includes(cleanTitle))) {
        group.push(candidate);
        assigned.add(candidate.id);
      }
    }

    const canonical = group[0];
    const isNoise = group.every(it => NOISE_WORDS.some(w => (it.title + ' ' + it.body).toLowerCase().includes(w)));
    const platforms: Record<string, number> = {};
    group.forEach(it => { platforms[it.source] = (platforms[it.source] || 0) + 1; });

    clusters.push({
      cluster_id: `cluster-${clusters.length + 1}`,
      canonical_title: canonical.title,
      canonical_id: canonical.id,
      item_ids: group.map(it => it.id),
      count: group.length,
      platform_breakdown: platforms,
      duplicate_score: group.length > 1 ? Number((1 - 1 / group.length).toFixed(2)) : 0,
      is_noise: isNoise,
      sample_text: canonical.body.slice(0, 140) + (canonical.body.length > 140 ? '...' : '')
    });
  }

  // Extract priorities
  const nonNoise = clusters.filter(c => !c.is_noise);
  const candidates: { score: number; action: PriorityAction }[] = [];

  nonNoise.forEach((c) => {
    const canonical = items.find(it => it.id === c.canonical_id) || items[0];
    const text = (canonical.title + ' ' + canonical.body).toLowerCase();

    let urgency = 'P2';
    let urgencyScore = 10;
    if (/critical|rce|cve|vulnerability|oomkilled|latency spiked|failover|down in prod/.test(text)) {
      urgency = 'P0';
      urgencyScore = 50;
    } else if (/hard cutoff|sign[- ]off|approval needed|due today|before \d|deadline/.test(text)) {
      urgency = 'P1';
      urgencyScore = 30;
    }

    let deadline: string | null = null;
    let confidence = 'none';
    const deadMatch = canonical.body.match(/(?:before|by|cutoff is|due today at)\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)/i);
    if (deadMatch) {
      deadline = deadMatch[0];
      confidence = 'confirmed';
    }

    let actionType = 'reply';
    let verb = 'Follow up on';
    if (/sign-off|approve|review/.test(text)) {
      actionType = 'approve';
      verb = 'Review and Sign Off on';
    } else if (/cve|security|patch|vulnerability|oomkilled|down/.test(text)) {
      actionType = 'schedule';
      verb = 'Deploy Security Patch / Investigate:';
    }

    const clean = canonical.title.replace(/^(\[.*?\]|Re:\s*|Fwd:\s*)+/, '').trim();
    const actionTitle = `${verb} ${clean.slice(0, 50)}`;

    const draft = actionType === 'approve'
      ? `Hi ${canonical.sender.split(' ')[0]}, I have reviewed ${clean}. The changes look solid. You have my approval to proceed.`
      : actionType === 'schedule'
      ? `Acknowledging priority alert on '${clean}'. Investigating root cause and deploying verified remediation.`
      : `Hi ${canonical.sender.split(' ')[0]}, regarding '${clean}': Tracking this and will follow up shortly.`;

    const score = urgencyScore + c.count * 4 + (confidence === 'confirmed' ? 15 : 0);

    candidates.push({
      score,
      action: {
        id: `action-${c.cluster_id}`,
        rank: 0,
        title: actionTitle,
        summary: canonical.title.slice(0, 65),
        urgency_tier: urgency,
        deadline,
        deadline_confidence: confidence,
        supporting_evidence: [canonical.body.slice(0, 140) + '...'],
        source_platforms: Object.keys(c.platform_breakdown),
        cluster_id: c.cluster_id,
        suggested_action_type: actionType,
        action_draft: draft,
        approved: false,
        approved_at: null,
        generation_method: 'client-offline-fallback',
        model_inference_latency_ms: undefined,
      }
    });
  });

  candidates.sort((a, b) => b.score - a.score);
  const topActions = candidates.slice(0, 3).map((c, idx) => ({ ...c.action, rank: idx + 1 }));

  const elapsed = performance.now() - start;
  const reduction = Number((((items.length - topActions.length) / items.length) * 100).toFixed(1));

  return {
    total_raw: items.length,
    unique_clusters: clusters.length,
    duplicates_filtered: items.length - clusters.length,
    volume_reduction_pct: reduction,
    noise_reduction_pct: reduction,
    top_actions: topActions,
    all_clusters: clusters,
    execution_latency_ms: Number(elapsed.toFixed(2)),
    model_used: 'client-offline-fallback (FastAPI/Ollama backend standby)',
    dataset_name: datasetName
  };
}
