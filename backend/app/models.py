"""Pydantic data models for CalmQueue."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NotificationItem(BaseModel):
    id: str
    source: str
    sender: str
    timestamp: str
    title: str
    body: str


class ClusterGroup(BaseModel):
    cluster_id: str
    canonical_title: str
    canonical_id: str
    item_ids: List[str]
    count: int
    platform_breakdown: Dict[str, int]
    duplicate_score: float
    is_noise: bool
    sample_text: str


class PriorityAction(BaseModel):
    id: str
    rank: int  # 1, 2, or 3
    title: str
    summary: str
    urgency_tier: str  # P0 (Critical), P1 (High), P2 (Normal)
    deadline: Optional[str] = None
    deadline_confidence: str  # confirmed, inferred, none
    supporting_evidence: List[str] = Field(default_factory=list)
    source_platforms: List[str] = Field(default_factory=list)
    cluster_id: str
    suggested_action_type: str  # reply, approve, review, schedule
    action_draft: str
    approved: bool = False
    approved_at: Optional[str] = None


class QueueResponse(BaseModel):
    total_raw: int
    unique_clusters: int
    duplicates_filtered: int
    volume_reduction_pct: float
    noise_reduction_pct: float = 0.0  # backward compatibility alias
    top_actions: List[PriorityAction]
    all_clusters: List[ClusterGroup]
    execution_latency_ms: float
    model_used: str
    dataset_name: str


class ApprovalRequest(BaseModel):
    action_id: str
    modified_draft: Optional[str] = None


class ApprovalResponse(BaseModel):
    success: bool
    action_id: str
    status: str
    approved_at: str
    final_draft: str
    message: str


class BenchmarkMetrics(BaseModel):
    dataset_name: str
    raw_message_count: int
    duplicate_clusters_found: int
    noise_items_filtered: int
    volume_reduction_pct: float
    cognitive_load_reduction_pct: float = 0.0  # legacy alias
    priority_action_count: int
    confirmed_deadlines_count: int
    inferred_deadlines_count: int
    execution_latency_ms: float
    model_runtime: str
