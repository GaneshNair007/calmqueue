"""End-to-end API and inference engine tests for CalmQueue."""

import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.gemma_engine import GemmaEngine
from app.models import NotificationItem, ClusterGroup

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
    assert first_action["generation_method"] in ["ollama-llm", "rule-based-fallback"]


def test_approve_action_safeguard():
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
        assert b["execution_latency_ms"] < 2000.0


def test_deterministic_fallback_mode():
    """Verify deterministic grounded NLP pipeline extracts priorities without LLM."""
    engine = GemmaEngine()
    engine.is_ollama_available = False
    engine.active_runtime = "rule-based-fallback"

    item1 = NotificationItem(
        id="msg-1",
        source="Slack",
        sender="Lead Dev",
        timestamp="09:15 AM",
        title="CRITICAL: Production Auth Service OOMKilled",
        body="Kubernetes terminated auth-pod-1 due to OOMKilled. We need immediate memory limit increase before 11:00 AM."
    )
    cluster = ClusterGroup(
        cluster_id="test-cluster-1",
        canonical_title=item1.title,
        canonical_id=item1.id,
        item_ids=[item1.id],
        count=1,
        platform_breakdown={"Slack": 1},
        duplicate_score=0.0,
        is_noise=False,
        sample_text=item1.body
    )

    actions, runtime, latency = engine.extract_priorities([cluster], {item1.id: item1})
    assert len(actions) == 1
    action = actions[0]
    assert action.generation_method == "rule-based-fallback"
    assert action.urgency_tier == "P0"
    assert action.deadline_confidence == "confirmed"
    assert "11:00 am" in action.deadline.lower()
    assert runtime == "rule-based-fallback"
    assert latency is None


def test_ollama_llm_inference_and_quote_grounding():
    """Verify genuine Ollama inference path, schema parsing, and quote validation."""
    engine = GemmaEngine()
    engine.is_ollama_available = True
    engine.active_runtime = "ollama-gemma2:2b"

    item = NotificationItem(
        id="msg-2",
        source="GitHub",
        sender="Alice",
        timestamp="10:00 AM",
        title="Security advisory CVE-2026-9999",
        body="Emergency patch required for CVE-2026-9999 vulnerability in parser before 2:00 PM."
    )
    cluster = ClusterGroup(
        cluster_id="test-cluster-2",
        canonical_title=item.title,
        canonical_id=item.id,
        item_ids=[item.id],
        count=1,
        platform_breakdown={"GitHub": 1},
        duplicate_score=0.0,
        is_noise=False,
        sample_text=item.body
    )

    # Mock Ollama response with 1 valid quote and 1 hallucinated quote
    mock_ollama_response = {
        "message": {
            "content": json.dumps({
                "action_title": "Deploy Emergency Patch for CVE-2026-9999",
                "urgency_tier": "P0",
                "deadline": "2:00 PM",
                "deadline_confidence": "confirmed",
                "evidence_quotes": [
                    "Emergency patch required for CVE-2026-9999",  # Valid verbatim substring
                    "This is an invented hallucination from the LLM"  # Hallucinated quote
                ],
                "suggested_action_type": "schedule",
                "action_draft": "Applying fix for CVE-2026-9999 immediately."
            })
        }
    }

    def mock_urlopen(req, *args, **kwargs):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        m = MagicMock()
        if "/api/tags" in url:
            m.read.return_value = json.dumps({"models": [{"name": "gemma2:2b"}]}).encode("utf-8")
        else:
            m.read.return_value = json.dumps(mock_ollama_response).encode("utf-8")
        m.__enter__.return_value = m
        return m

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        actions, runtime, latency = engine.extract_priorities([cluster], {item.id: item})

    assert len(actions) == 1
    action = actions[0]
    assert action.generation_method == "ollama-llm"
    assert action.model_inference_latency_ms is not None
    assert action.urgency_tier == "P0"
    assert action.deadline == "2:00 PM"
    assert action.deadline_confidence == "confirmed"
    # Grounding check: only the valid verbatim quote is kept, hallucinated quote is discarded
    assert "Emergency patch required for CVE-2026-9999" in action.supporting_evidence
    assert "This is an invented hallucination from the LLM" not in action.supporting_evidence
    assert runtime == "ollama-gemma2:2b"
    assert latency is not None
