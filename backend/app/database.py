"""SQLite database and audit ledger for CalmQueue."""

from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from .models import NotificationItem, PriorityAction, ClusterGroup, QueueResponse

DB_PATH = Path(__file__).resolve().parent.parent / "calmqueue.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes tables for inbox items, clusters, actions, and audit logs."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inboxes (
                id TEXT PRIMARY KEY,
                source TEXT,
                sender TEXT,
                timestamp TEXT,
                title TEXT,
                body TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id TEXT PRIMARY KEY,
                rank INTEGER,
                title TEXT,
                summary TEXT,
                urgency_tier TEXT,
                deadline TEXT,
                deadline_confidence TEXT,
                supporting_evidence TEXT,
                source_platforms TEXT,
                cluster_id TEXT,
                suggested_action_type TEXT,
                action_draft TEXT,
                approved INTEGER DEFAULT 0,
                approved_at TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approvals_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT,
                previous_draft TEXT,
                final_draft TEXT,
                approved_at TEXT,
                actor TEXT
            )
        """)
        conn.commit()


# Run init_db on import to ensure tables exist
init_db()



def save_actions(actions: List[PriorityAction]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM actions")  # Clear active queue
        for act in actions:
            cursor.execute("""
                INSERT OR REPLACE INTO actions (
                    id, rank, title, summary, urgency_tier, deadline, deadline_confidence,
                    supporting_evidence, source_platforms, cluster_id, suggested_action_type,
                    action_draft, approved, approved_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                act.id, act.rank, act.title, act.summary, act.urgency_tier, act.deadline,
                act.deadline_confidence, json.dumps(act.supporting_evidence),
                json.dumps(act.source_platforms), act.cluster_id, act.suggested_action_type,
                act.action_draft, 1 if act.approved else 0, act.approved_at, now
            ))
        conn.commit()


def approve_action_in_db(action_id: str, modified_draft: Optional[str] = None) -> Optional[PriorityAction]:
    now = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actions WHERE id = ?", (action_id,))
        row = cursor.fetchone()
        if not row:
            return None

        current_draft = row["action_draft"]
        final_draft = modified_draft if modified_draft is not None else current_draft

        cursor.execute("""
            UPDATE actions
            SET approved = 1, approved_at = ?, action_draft = ?
            WHERE id = ?
        """, (now, final_draft, action_id))

        cursor.execute("""
            INSERT INTO approvals_audit (action_id, previous_draft, final_draft, approved_at, actor)
            VALUES (?, ?, ?, ?, ?)
        """, (action_id, current_draft, final_draft, now, "HumanOperator"))

        conn.commit()

        cursor.execute("SELECT * FROM actions WHERE id = ?", (action_id,))
        updated_row = cursor.fetchone()
        return PriorityAction(
            id=updated_row["id"],
            rank=updated_row["rank"],
            title=updated_row["title"],
            summary=updated_row["summary"],
            urgency_tier=updated_row["urgency_tier"],
            deadline=updated_row["deadline"],
            deadline_confidence=updated_row["deadline_confidence"],
            supporting_evidence=json.loads(updated_row["supporting_evidence"]),
            source_platforms=json.loads(updated_row["source_platforms"]),
            cluster_id=updated_row["cluster_id"],
            suggested_action_type=updated_row["suggested_action_type"],
            action_draft=updated_row["action_draft"],
            approved=bool(updated_row["approved"]),
            approved_at=updated_row["approved_at"],
        )
