import { useState, useEffect } from 'react';
import {
  CheckCircle2,
  Clock,
  Layers,
  BarChart3,
  Check,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  FileText,
} from 'lucide-react';
import type {
  NotificationItem,
  PriorityAction,
  QueueResponse,
  PresetInfo,
  BenchmarkMetrics,
} from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<'queue' | 'clusters' | 'benchmarks'>('queue');
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('chaotic_monday');
  const [queueData, setQueueData] = useState<QueueResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Benchmarks state
  const [benchmarks, setBenchmarks] = useState<BenchmarkMetrics[]>([]);
  const [benchmarksLoading, setBenchmarksLoading] = useState<boolean>(false);

  // Editable drafts
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);


  // Custom upload modal
  const [showUploadModal, setShowUploadModal] = useState<boolean>(false);
  const [customJson, setCustomJson] = useState<string>('');

  // Fetch presets on initial mount
  useEffect(() => {
    fetchPresets();
  }, []);

  // Fetch queue data whenever selectedPreset changes
  useEffect(() => {
    if (selectedPreset) {
      loadAndProcessPreset(selectedPreset);
    }
  }, [selectedPreset]);

  // Load benchmarks when benchmarks tab is selected
  useEffect(() => {
    if (activeTab === 'benchmarks' && benchmarks.length === 0) {
      loadBenchmarks();
    }
  }, [activeTab]);

  const fetchPresets = async () => {
    try {
      const res = await fetch('/api/presets');
      if (res.ok) {
        const data = await res.json();
        setPresets(data);
      }
    } catch (err) {
      console.error('Failed to load presets:', err);
    }
  };

  const loadAndProcessPreset = async (presetId: string) => {
    setLoading(true);
    setError(null);
    try {
      const pRes = await fetch(`/api/presets/${presetId}`);
      if (!pRes.ok) throw new Error('Failed to load preset dataset');
      const items: NotificationItem[] = await pRes.json();

      const processRes = await fetch('/api/inbox/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_name: presetId,
          items,
        }),
      });
      if (!processRes.ok) throw new Error('Processing failed');
      const qRes: QueueResponse = await processRes.json();
      setQueueData(qRes);

      // Initialize drafts
      const initialDrafts: Record<string, string> = {};
      qRes.top_actions.forEach((act) => {
        initialDrafts[act.id] = act.action_draft;
      });
      setDrafts(initialDrafts);
    } catch (err: any) {
      setError(err.message || 'Error processing notifications');
    } finally {
      setLoading(false);
    }
  };

  const loadBenchmarks = async () => {
    setBenchmarksLoading(true);
    try {
      const res = await fetch('/api/benchmarks');
      if (res.ok) {
        const data = await res.json();
        setBenchmarks(data);
      }
    } catch (err) {
      console.error('Failed to load benchmarks:', err);
    } finally {
      setBenchmarksLoading(false);
    }
  };

  const handleApprove = async (action: PriorityAction) => {
    setApprovingId(action.id);
    const modifiedDraft = drafts[action.id] || action.action_draft;
    try {
      const res = await fetch(`/api/actions/${action.id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_id: action.id,
          modified_draft: modifiedDraft,
        }),
      });

      if (res.ok) {
        // Copy to clipboard as user convenience
        navigator.clipboard.writeText(modifiedDraft);
        setCopiedId(action.id);
        setTimeout(() => setCopiedId(null), 3000);

        // Update local state
        if (queueData) {
          const updatedActions = queueData.top_actions.map((a) =>
            a.id === action.id
              ? { ...a, approved: true, approved_at: new Date().toISOString(), action_draft: modifiedDraft }
              : a
          );
          setQueueData({ ...queueData, top_actions: updatedActions });
        }
      }
    } catch (err) {
      console.error('Approval failed:', err);
    } finally {
      setApprovingId(null);
    }
  };

  const handleCustomUpload = async () => {
    try {
      const parsed = JSON.parse(customJson);
      if (!Array.isArray(parsed)) throw new Error('Expected JSON array of notifications');

      setLoading(true);
      setShowUploadModal(false);
      const processRes = await fetch('/api/inbox/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_name: 'Custom User Upload',
          items: parsed,
        }),
      });
      if (!processRes.ok) throw new Error('Failed to process custom inbox');
      const qRes: QueueResponse = await processRes.json();
      setQueueData(qRes);

      const initialDrafts: Record<string, string> = {};
      qRes.top_actions.forEach((act) => {
        initialDrafts[act.id] = act.action_draft;
      });
      setDrafts(initialDrafts);
      setSelectedPreset('custom');
    } catch (e: any) {
      alert(`Invalid JSON format: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calm-container">
      {/* Header */}
      <header style={{ marginBottom: 24 }}>
        <div className="header-badge-row">
          <span className="badge-sloth">
            <span>🦥</span> Hacktoberfest 2026: Slow & Steady
          </span>
          <span className="badge-gemma">
            <Sparkles size={13} /> Powered by Gemma 2 (Local Open-Weight AI)
          </span>
        </div>
        <h1 className="main-title">CalmQueue</h1>
        <p className="tagline">
          Your notifications have a lot to say. You shouldn't have to read all of them.
        </p>

        {/* Navigation Tabs */}
        <div className="tabs-bar">
          <button
            className={`tab-btn ${activeTab === 'queue' ? 'active' : ''}`}
            onClick={() => setActiveTab('queue')}
          >
            <ShieldCheck size={16} /> Top-3 Priority Queue
          </button>
          <button
            className={`tab-btn ${activeTab === 'clusters' ? 'active' : ''}`}
            onClick={() => setActiveTab('clusters')}
          >
            <Layers size={16} /> Silenced Noise & Clusters ({queueData?.all_clusters.length || 0})
          </button>
          <button
            className={`tab-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
            onClick={() => setActiveTab('benchmarks')}
          >
            <BarChart3 size={16} /> Empirical Benchmarks
          </button>
        </div>
      </header>

      {/* Preset Selector Toolbar */}
      <section className="preset-bar">
        <div className="preset-header-row">
          <span className="preset-title">Select Influx Dataset</span>
          <button
            className="preset-chip"
            style={{ borderStyle: 'dashed' }}
            onClick={() => setShowUploadModal(true)}
          >
            <UploadCloud size={14} /> Custom CSV/JSON
          </button>
        </div>
        <div className="preset-chips">
          {presets.map((p) => (
            <button
              key={p.id}
              className={`preset-chip ${selectedPreset === p.id ? 'active' : ''}`}
              onClick={() => setSelectedPreset(p.id)}
            >
              <span>{p.name}</span>
              <span style={{ opacity: 0.65, fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                ({p.item_count} items)
              </span>
            </button>
          ))}
        </div>
      </section>

      {/* Cognitive Load Reduction Metric Ribbon */}
      {queueData && (
        <section className="metrics-ribbon">
          <div className="metric-card">
            <div className="metric-label">Raw Influx Clutter</div>
            <div className="metric-value">{queueData.total_raw} msgs</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Duplicates & Noise Filtered</div>
            <div className="metric-value">
              {queueData.duplicates_filtered} duplicates
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Review Clutter Reduction</div>
            <div className="metric-value metric-highlight">
              {queueData.noise_reduction_pct}%
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Local Gemma Latency</div>
            <div className="metric-value">
              {queueData.execution_latency_ms} ms
            </div>
          </div>
        </section>
      )}

      {/* Main Content Area */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14 }}>
            🦥 Clustering semantics and extracting priorities with Gemma...
          </div>
        </div>
      ) : error ? (
        <div style={{ padding: 24, background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 10, color: '#991b1b' }}>
          {error}
        </div>
      ) : activeTab === 'queue' ? (
        /* View 1: Hero Top-3 Priority Queue */
        <section className="priority-queue">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Action Queue (Strictly 3 Decisions)
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-subtle)' }}>
              Human approval required before any action is executed
            </span>
          </div>

          {queueData?.top_actions.map((act) => (
            <article
              key={act.id}
              className={`action-card ${act.approved ? 'approved-card' : ''}`}
            >
              <div className="card-top-row">
                <div className="rank-title-group">
                  <span className="rank-num">0{act.rank}</span>
                  <div>
                    <h2 className="action-heading">{act.title}</h2>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 2 }}>
                      {act.summary}
                    </p>
                  </div>
                </div>

                <div className="pill-group">
                  <span className={`pill-urgency tier-${act.urgency_tier.toLowerCase()}`}>
                    {act.urgency_tier}
                  </span>

                  {act.deadline && (
                    <span
                      className={`pill-deadline ${
                        act.deadline_confidence === 'confirmed'
                          ? 'deadline-confirmed'
                          : 'deadline-inferred'
                      }`}
                    >
                      <Clock size={11} /> {act.deadline} ({act.deadline_confidence})
                    </span>
                  )}
                </div>
              </div>

              {/* Source Platforms */}
              <div className="source-badges">
                <span>Sources:</span>
                {act.source_platforms.map((src) => (
                  <span key={src} className="source-pill">
                    {src}
                  </span>
                ))}
              </div>

              {/* Grounded Evidence Box */}
              <div className="evidence-box">
                <span className="evidence-label">Grounded Source Evidence</span>
                {act.supporting_evidence.map((ev, i) => (
                  <p key={i} className="evidence-quote">
                    "{ev}"
                  </p>
                ))}
              </div>

              {/* Human-in-the-Loop Action Draft */}
              <div className="draft-container">
                <div className="draft-header">
                  <span className="draft-label">
                    <FileText size={13} /> Suggested Action / Response Draft
                  </span>
                  <span style={{ fontSize: 11, color: 'var(--text-subtle)' }}>
                    Editable before approval
                  </span>
                </div>
                <textarea
                  className="draft-textarea"
                  value={drafts[act.id] !== undefined ? drafts[act.id] : act.action_draft}
                  disabled={act.approved}
                  onChange={(e) =>
                    setDrafts({ ...drafts, [act.id]: e.target.value })
                  }
                />

                <div className="action-footer">
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <ShieldCheck size={14} color="#059669" />
                    <span>No automated sending. Requires explicit operator confirmation.</span>
                  </div>

                  {act.approved ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span className="btn-approved-done">
                        <CheckCircle2 size={15} /> Approved & Copied
                      </span>
                      {copiedId === act.id && (
                        <span style={{ fontSize: 11, color: '#059669', fontWeight: 600 }}>
                          Copied to clipboard!
                        </span>
                      )}
                      <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: '#059669' }}>
                        Audit Logged: {new Date(act.approved_at || '').toLocaleTimeString()}
                      </span>
                    </div>
                  ) : (
                    <button
                      className="btn-approve"
                      disabled={approvingId === act.id}
                      onClick={() => handleApprove(act)}
                    >
                      {approvingId === act.id ? (
                        'Recording...'
                      ) : (
                        <>
                          <Check size={14} /> Approve Action & Copy Draft
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            </article>
          ))}
        </section>
      ) : activeTab === 'clusters' ? (
        /* View 2: Grouped Semantic Clusters */
        <section className="cluster-list">
          <div style={{ marginBottom: 12 }}>
            <h3 style={{ fontSize: 16, fontWeight: 600 }}>Semantic Notification Clusters</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              CalmQueue identified {queueData?.all_clusters.length} distinct threads across platforms, silencing duplicate pings.
            </p>
          </div>

          {queueData?.all_clusters.map((c) => (
            <div key={c.cluster_id} className="cluster-card">
              <div className="cluster-main">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="cluster-title">{c.canonical_title}</span>
                  {c.is_noise && (
                    <span style={{ fontSize: 10, background: '#f4f4f5', padding: '2px 6px', borderRadius: 4, color: '#71717a' }}>
                      Routine Noise Filtered
                    </span>
                  )}
                </div>
                <div className="cluster-snippet">{c.sample_text}</div>
                <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                  {Object.entries(c.platform_breakdown).map(([plat, count]) => (
                    <span key={plat} style={{ fontSize: 11, color: 'var(--text-subtle)' }}>
                      {plat}: {count}
                    </span>
                  ))}
                </div>
              </div>

              <div className="cluster-stats">
                <span className="cluster-count-badge">{c.count} items</span>
              </div>
            </div>
          ))}
        </section>
      ) : (
        /* View 3: Empirical Benchmarks Table */
        <section>
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, fontWeight: 600 }}>Empirical Clutter Reduction Benchmarks</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Tested on authentic datasets with duplicate incident reports, contradictory deadlines, and background noise.
            </p>
          </div>

          {benchmarksLoading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Running local evaluation benchmarks across all test inboxes...
            </div>
          ) : (
            <div className="benchmark-table-wrapper">

            <table className="benchmark-table">
              <thead>
                <tr>
                  <th>Dataset</th>
                  <th>Raw Influx</th>
                  <th>Actions Surfaced</th>
                  <th>Review Load Reduction</th>
                  <th>Confirmed Deadlines</th>
                  <th>Local Latency</th>
                  <th>Runtime Engine</th>
                </tr>
              </thead>
              <tbody>
                {benchmarks.map((b) => (
                  <tr key={b.dataset_name}>
                    <td style={{ fontWeight: 600 }}>{b.dataset_name}</td>
                    <td className="mono">{b.raw_message_count}</td>
                    <td className="mono" style={{ color: '#059669', fontWeight: 600 }}>
                      {b.priority_action_count}
                    </td>
                    <td className="mono" style={{ color: '#059669', fontWeight: 700 }}>
                      {b.cognitive_load_reduction_pct}%
                    </td>
                    <td className="mono">{b.confirmed_deadlines_count}</td>
                    <td className="mono">{b.execution_latency_ms} ms</td>
                    <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>{b.model_runtime}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    )}


      {/* Custom Upload Modal */}
      {showUploadModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 20,
          }}
        >
          <div
            style={{
              background: 'white',
              borderRadius: 14,
              padding: 24,
              maxWidth: 580,
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: 16,
            }}
          >
            <h3 style={{ fontSize: 18, fontWeight: 600 }}>Import Custom Notification Inbox</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Paste a JSON array of notification objects with <code>title</code> and <code>body</code> fields.
            </p>
            <textarea
              style={{
                width: '100%',
                height: 180,
                fontFamily: 'var(--font-mono)',
                fontSize: 12,
                padding: 10,
                border: '1px solid #d4d4d8',
                borderRadius: 8,
              }}
              placeholder={`[\n  {\n    "id": "1",\n    "source": "Slack",\n    "sender": "Alice",\n    "timestamp": "2026-10-23T08:00:00Z",\n    "title": "Need review on PR",\n    "body": "Can you check PR #42 before 3 PM?"\n  }\n]`}
              value={customJson}
              onChange={(e) => setCustomJson(e.target.value)}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button
                className="preset-chip"
                onClick={() => setShowUploadModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn-approve"
                onClick={handleCustomUpload}
              >
                Process Custom Inbox
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
