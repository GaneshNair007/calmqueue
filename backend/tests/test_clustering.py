"""Unit tests for semantic clustering in CalmQueue."""

import pytest
from app.models import NotificationItem
from app.clustering import SemanticClusterEngine, is_noise_item, tokenize


def test_tokenize():
    tokens = tokenize("URGENT: Database latency spiked to 1400ms!")
    assert "urgent" in tokens
    assert "database" in tokens
    assert "latency" in tokens
    assert "1400ms" in tokens
    assert "the" not in tokens  # Stop word removed


def test_empty_clustering():
    engine = SemanticClusterEngine()
    clusters = engine.cluster_notifications([])
    assert clusters == []


def test_duplicate_grouping():
    engine = SemanticClusterEngine()
    items = [
        NotificationItem(
            id="1", source="Slack", sender="Alice", timestamp="2026-10-23T08:00:00Z",
            title="Production Auth Incident", body="Auth gateway latency is climbing."
        ),
        NotificationItem(
            id="2", source="Email", sender="Alice", timestamp="2026-10-23T08:05:00Z",
            title="Production Auth Incident", body="Auth gateway latency is still climbing."
        ),
        NotificationItem(
            id="3", source="Slack", sender="Bob", timestamp="2026-10-23T08:10:00Z",
            title="Cafeteria Menu", body="Special lunch today in cafeteria."
        ),
    ]

    clusters = engine.cluster_notifications(items)
    assert len(clusters) == 2  # 1 cluster for auth incident (2 items), 1 for cafeteria (1 item)

    auth_cluster = [c for c in clusters if "Auth" in c.canonical_title][0]
    assert auth_cluster.count == 2
    assert "Slack" in auth_cluster.platform_breakdown
    assert "Email" in auth_cluster.platform_breakdown
    assert auth_cluster.duplicate_score > 0.0


def test_noise_detection():
    noise_item = NotificationItem(
        id="n1", source="Slack", sender="Facilities", timestamp="2026-10-23T08:00:00Z",
        title="Cafeteria Lunch Menu", body="Enjoy your lunch today."
    )
    assert is_noise_item(noise_item) is True

    action_item = NotificationItem(
        id="a1", source="Linear", sender="Jordan", timestamp="2026-10-23T08:00:00Z",
        title="Sign off on schema migration", body="Need your sign off before 2 PM."
    )
    assert is_noise_item(action_item) is False
