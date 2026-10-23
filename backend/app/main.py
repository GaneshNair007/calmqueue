"""FastAPI main server for CalmQueue."""

from __future__ import annotations

import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .models import (
    NotificationItem,
    ClusterGroup,
    PriorityAction,
    QueueResponse,
    ApprovalRequest,
    ApprovalResponse,
    BenchmarkMetrics,
)
from .clustering import SemanticClusterEngine
from .gemma_engine import GemmaEngine
from .database import init_db, save_actions, approve_action_in_db

PRESETS_DIR = Path(__file__).resolve().parent.parent.parent / "benchmarks" / "sample_inboxes"

cluster_engine = SemanticClusterEngine(similarity_threshold=0.58)
gemma_engine = GemmaEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="CalmQueue API",
    description="Local-first open-weight AI notification priority engine for Hacktoberfest Week 3 (Slow and Steady).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProcessInboxRequest(BaseModel):
    dataset_name: str
    items: List[NotificationItem]


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "CalmQueue",
        "version": "1.0.0",
        "active_runtime": gemma_engine.active_runtime,
        "theme": "Slow and Steady (DEV Challenge Week 3)"
    }


@app.get("/api/presets")
async def list_presets():
    """List available benchmark inboxes."""
    presets = [
        {
            "id": "chaotic_monday",
            "name": "Chaotic Monday Morning",
            "item_count": 28,
            "description": "28 unread messages from Slack, GitHub, Jira, and Email with duplicate incident reports and ambiguous deadlines.",
            "sources": ["Slack", "GitHub", "PagerDuty", "Jira", "Email", "Linear"]
        },
        {
            "id": "devops_alert_storm",
            "name": "DevOps Alert Storm",
            "item_count": 22,
            "description": "22 automated alerts: OOMKills, Redis failover events, health checks, and scheduled secret rotation.",
            "sources": ["Datadog", "Kubernetes", "Sentry", "AWS GuardDuty", "UptimeRobot", "PagerDuty"]
        },
        {
            "id": "maintainer_backlog",
            "name": "Open-Source Maintainer Backlog",
            "item_count": 35,
            "description": "35 GitHub PRs and issues: bot spam, good-first-issue claims, discussion threads, and a critical YAML RCE advisory.",
            "sources": ["GitHub", "Email", "Discord"]
        }
    ]
    return presets


@app.get("/api/presets/{preset_id}")
async def get_preset(preset_id: str):
    """Retrieve items for a specific benchmark inbox."""
    file_path = PRESETS_DIR / f"{preset_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@app.post("/api/inbox/process", response_model=QueueResponse)
async def process_inbox(req: ProcessInboxRequest):
    """Ingest notifications, perform semantic deduplication, and extract top-3 priority actions."""
    start_time = time.perf_counter()
    raw_count = len(req.items)
    if raw_count == 0:
        return QueueResponse(
            total_raw=0,
            unique_clusters=0,
            duplicates_filtered=0,
            noise_reduction_pct=0.0,
            top_actions=[],
            all_clusters=[],
            execution_latency_ms=0.0,
            model_used=gemma_engine.active_runtime,
            dataset_name=req.dataset_name,
        )

    items_map = {it.id: it for it in req.items}

    # 1. Semantic Deduplication & Clustering
    clusters = cluster_engine.cluster_notifications(req.items)
    unique_clusters_count = len(clusters)
    duplicates_filtered = sum(c.count - 1 for c in clusters)

    # 2. Gemma Priority Extraction & Grounding
    top_actions, model_name = gemma_engine.extract_priorities(clusters, items_map)

    # 3. Save Active Queue in SQLite
    save_actions(top_actions)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    volume_reduction_pct = round(((raw_count - len(top_actions)) / raw_count) * 100, 1)

    return QueueResponse(
        total_raw=raw_count,
        unique_clusters=unique_clusters_count,
        duplicates_filtered=duplicates_filtered,
        volume_reduction_pct=volume_reduction_pct,
        noise_reduction_pct=volume_reduction_pct,
        top_actions=top_actions,
        all_clusters=clusters,
        execution_latency_ms=latency_ms,
        model_used=model_name,
        dataset_name=req.dataset_name,
    )


@app.post("/api/actions/{action_id}/approve", response_model=ApprovalResponse)
async def approve_action(action_id: str, payload: Optional[ApprovalRequest] = None):
    """Human-in-the-loop approval safeguard: records operator confirmation and final draft."""
    modified_draft = payload.modified_draft if payload else None
    action = approve_action_in_db(action_id, modified_draft)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found in active queue.")

    return ApprovalResponse(
        success=True,
        action_id=action.id,
        status="APPROVED",
        approved_at=action.approved_at or "",
        final_draft=action.action_draft,
        message="Action approved and committed to audit ledger. Ready for dispatch or copy."
    )


@app.get("/api/benchmarks")
async def run_all_benchmarks():
    """Runs automated benchmarks across all preset inboxes."""
    results: List[BenchmarkMetrics] = []
    preset_files = [
        ("chaotic_monday", "Chaotic Monday Morning"),
        ("devops_alert_storm", "DevOps Alert Storm"),
        ("maintainer_backlog", "Maintainer Backlog"),
    ]

    for p_id, p_name in preset_files:
        file_path = PRESETS_DIR / f"{p_id}.json"
        if not file_path.exists():
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            raw_items = [NotificationItem(**x) for x in json.load(f)]

        start = time.perf_counter()
        items_map = {it.id: it for it in raw_items}
        clusters = cluster_engine.cluster_notifications(raw_items)
        top_actions, model = gemma_engine.extract_priorities(clusters, items_map)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        duplicate_clusters = sum(1 for c in clusters if c.count > 1)
        noise_filtered = sum(1 for c in clusters if c.is_noise)
        reduction_pct = round(((len(raw_items) - len(top_actions)) / len(raw_items)) * 100, 1)

        confirmed_deadlines = sum(1 for a in top_actions if a.deadline_confidence == "confirmed")
        inferred_deadlines = sum(1 for a in top_actions if a.deadline_confidence == "inferred")

        results.append(
            BenchmarkMetrics(
                dataset_name=p_name,
                raw_message_count=len(raw_items),
                duplicate_clusters_found=duplicate_clusters,
                noise_items_filtered=noise_filtered,
                volume_reduction_pct=reduction_pct,
                cognitive_load_reduction_pct=reduction_pct,
                priority_action_count=len(top_actions),
                confirmed_deadlines_count=confirmed_deadlines,
                inferred_deadlines_count=inferred_deadlines,
                execution_latency_ms=latency_ms,
                model_runtime=model,
            )
        )

    return results


# Mount frontend dist static files if built
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")

