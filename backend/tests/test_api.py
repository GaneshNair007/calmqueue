"""End-to-end API tests for CalmQueue."""

import json
from pathlib import Path
import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["app"] == "CalmQueue"
    assert "active_runtime" in data


def test_list_and_get_presets():
    resp = client.get("/api/presets")
    assert resp.status_code == 200
    presets = resp.json()
    assert len(presets) == 3
    preset_ids = [p["id"] for p in presets]
    assert "chaotic_monday" in preset_ids
    assert "devops_alert_storm" in preset_ids
    assert "maintainer_backlog" in preset_ids

    # Fetch chaotic_monday preset
    resp2 = client.get("/api/presets/chaotic_monday")
    assert resp2.status_code == 200
    items = resp2.json()
    assert len(items) == 28


def test_process_chaotic_monday():
    resp = client.get("/api/presets/chaotic_monday")
    items = resp.json()

    process_resp = client.post("/api/inbox/process", json={
        "dataset_name": "Chaotic Monday Morning",
        "items": items
    })
    assert process_resp.status_code == 200
    data = process_resp.json()

    assert data["total_raw"] == 28
    assert data["noise_reduction_pct"] >= 85.0
    assert len(data["top_actions"]) == 3

    # Check ranks 1, 2, 3
    ranks = [a["rank"] for a in data["top_actions"]]
    assert ranks == [1, 2, 3]

    # Verify action attributes
    first_action = data["top_actions"][0]
    assert first_action["urgency_tier"] in ["P0", "P1"]
    assert len(first_action["supporting_evidence"]) > 0
    assert first_action["action_draft"] != ""
    assert first_action["approved"] is False


def test_approve_action_safeguard():
    # Process first to ensure an action is created
    resp = client.get("/api/presets/chaotic_monday")
    items = resp.json()
    p_resp = client.post("/api/inbox/process", json={
        "dataset_name": "Chaotic Monday",
        "items": items
    })
    top_actions = p_resp.json()["top_actions"]
    target_action = top_actions[0]

    # Approve with edited draft
    appr_resp = client.post(f"/api/actions/{target_action['id']}/approve", json={
        "action_id": target_action["id"],
        "modified_draft": "Reviewed and signed off. Deploy whenever ready."
    })
    assert appr_resp.status_code == 200
    appr_data = appr_resp.json()
    assert appr_data["success"] is True
    assert appr_data["status"] == "APPROVED"
    assert appr_data["final_draft"] == "Reviewed and signed off. Deploy whenever ready."


def test_benchmarks_endpoint():
    resp = client.get("/api/benchmarks")
    assert resp.status_code == 200
    benchmarks = resp.json()
    assert len(benchmarks) == 3
    for b in benchmarks:
        assert b["raw_message_count"] > 0
        assert b["cognitive_load_reduction_pct"] >= 80.0
        assert b["priority_action_count"] == 3
        assert b["execution_latency_ms"] < 2000.0  # Fast execution
