export interface NotificationItem {
  id: string;
  source: string;
  sender: string;
  timestamp: string;
  title: string;
  body: string;
}

export interface ClusterGroup {
  cluster_id: string;
  canonical_title: string;
  canonical_id: string;
  item_ids: string[];
  count: number;
  platform_breakdown: Record<string, number>;
  duplicate_score: number;
  is_noise: boolean;
  sample_text: string;
}


export interface PriorityAction {
  id: string;
  rank: number;
  title: string;
  summary: string;
  urgency_tier: string;
  deadline?: string | null;
  deadline_confidence: string;
  supporting_evidence: string[];
  source_platforms: string[];
  cluster_id: string;
  suggested_action_type: string;
  action_draft: string;
  approved: boolean;
  approved_at?: string | null;
}

export interface QueueResponse {
  total_raw: number;
  unique_clusters: number;
  duplicates_filtered: number;
  volume_reduction_pct?: number;
  noise_reduction_pct: number;
  top_actions: PriorityAction[];
  all_clusters: ClusterGroup[];
  execution_latency_ms: number;
  model_used: string;
  dataset_name: string;
}

export interface PresetInfo {
  id: string;
  name: string;
  item_count: number;
  description: string;
  sources: string[];
}

export interface BenchmarkMetrics {
  dataset_name: string;
  raw_message_count: number;
  duplicate_clusters_found: number;
  noise_items_filtered: number;
  volume_reduction_pct?: number;
  cognitive_load_reduction_pct: number;
  priority_action_count: number;
  confirmed_deadlines_count: number;
  inferred_deadlines_count: number;
  execution_latency_ms: number;
  model_runtime: string;
}
