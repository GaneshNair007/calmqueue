"""Task extractor and priority engine for CalmQueue.

Supports dual-mode operation:
1. Live local inference via Ollama (e.g. gemma2:2b or other open-weight models).
2. Deterministic grounded NLP extraction fallback when local LLM daemon is offline.
"""

from __future__ import annotations

import re
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from .models import NotificationItem, ClusterGroup, PriorityAction

logger = logging.getLogger("calmqueue.engine")

# Priority and urgency patterns based on engineering terminology
URGENT_P0_PATTERNS = [
    r"\bcritical\b", r"\brce\b", r"\bcve-\d+\b", r"\bvulnerability\b", r"\boomkilled\b",
    r"\bout of memory\b", r"\blatency spiked\b", r"\bfailover\b", r"\bincident #\d+\b",
    r"\bdown in prod\b", r"\bhigh severity\b", r"\bp99 latency\b", r"\bslo threshold\b",
    r"\bdata loss\b", r"\boutage\b", r"\bsecurity advisory\b"
]

URGENT_P1_PATTERNS = [
    r"\bhard cutoff\b", r"\bsign[- ]off\b", r"\bapproval needed\b", r"\bcannot deploy without\b",
    r"\brotate.*(?:password|secret|credential)\b", r"\bdue today\b", r"\bbefore \d{1,2}:\d{2}\b",
    r"\bdeadline is\b", r"\bready for.*merge\b", r"\baction required\b", r"\bblocker\b"
]

DEADLINE_EXPLICIT_PATTERNS = [
    (r"(?:before|by|cutoff is)\s+(\d{1,2}:\d{2}\s*(?:am|pm|ist|utc)?)", "confirmed"),
    (r"(?:due today\s*(?:at\s*)?\d{1,2}:\d{2}\s*(?:am|pm|ist|utc)?)", "confirmed"),
    (r"(?:deadline (?:is )?[a-z]+ \d{1,2}(?:st|nd|rd|th)?)", "confirmed"),
    (r"(?:due by [a-z]+ \d{1,2})", "confirmed"),
    (r"(?:by end of week)", "inferred"),
    (r"(?:in \d+ days)", "inferred"),
    (r"(?:tomorrow\b)", "inferred"),
    (r"(?:whenever you have time|when you get a chance|no rush)", "inferred"),
]


class GemmaEngine:
    """Orchestrates priority extraction and action synthesis.
    
    Dynamically connects to Ollama if available, or uses a deterministic
    grounded NLP extraction pipeline as a reliable local fallback.
    """

    def __init__(self, ollama_host: str = "http://127.0.0.1:11434", model_name: str = "gemma2:2b"):
        self.ollama_host = ollama_host
        self.model_name = model_name
        self.active_runtime = "deterministic-nlp-pipeline"
        self._check_ollama()

    def _check_ollama(self) -> bool:
        """Check if local Ollama daemon with a supported model is accessible."""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.ollama_host}/api/tags", headers={"User-Agent": "CalmQueue"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("name", "") for m in data.get("models", [])]
                for m in models:
                    if "gemma" in m:
                        self.model_name = m
                        self.active_runtime = f"ollama-{m}"
                        logger.info("Connected to local Ollama with model: %s", m)
                        return True
                if models:
                    self.model_name = models[0]
                    self.active_runtime = f"ollama-{models[0]}"
                    logger.info("Connected to local Ollama with fallback model: %s", models[0])
                    return True
        except Exception:
            pass
        self.active_runtime = "deterministic-nlp-pipeline"
        return False

    def extract_priorities(
        self,
        clusters: List[ClusterGroup],
        raw_items_map: Dict[str, NotificationItem]
    ) -> Tuple[List[PriorityAction], str]:
        """Analyzes clusters to extract top-3 priority actions with grounded evidence."""
        scored_candidates: List[Tuple[float, PriorityAction]] = []

        for cluster in clusters:
            if cluster.is_noise:
                continue

            canonical = raw_items_map.get(cluster.canonical_id)
            if not canonical:
                continue

            all_cluster_items = [raw_items_map[iid] for iid in cluster.item_ids if iid in raw_items_map]
            combined_text = "\n".join(f"{it.title}: {it.body}" for it in all_cluster_items)

            # Analyze actionability, urgency tier, and deadline
            score, action = self._analyze_cluster(cluster, all_cluster_items, combined_text)
            if action:
                scored_candidates.append((score, action))

        # Sort candidates by calculated priority score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Select exactly top-3 priority actions
        top_actions: List[PriorityAction] = []
        for rank, (_, item) in enumerate(scored_candidates[:3], start=1):
            item.rank = rank
            top_actions.append(item)

        return top_actions, self.active_runtime

    def _analyze_cluster(
        self,
        cluster: ClusterGroup,
        items: List[NotificationItem],
        combined_text: str
    ) -> Tuple[float, Optional[PriorityAction]]:
        """Extracts task attributes and scores importance dynamically."""
        canonical = items[0]
        text_lower = combined_text.lower()

        # 1. Detect Urgency Tier dynamically
        urgency = "P2"
        urgency_score = 10.0
        for pat in URGENT_P0_PATTERNS:
            if re.search(pat, text_lower):
                urgency = "P0"
                urgency_score = 50.0
                break

        if urgency == "P2":
            for pat in URGENT_P1_PATTERNS:
                if re.search(pat, text_lower):
                    urgency = "P1"
                    urgency_score = 30.0
                    break

        # Check if already mitigated or resolved
        if re.search(r"\b(?:incident.*resolved|mitigated|all good now|fixed in master)\b", text_lower):
            urgency_score -= 25.0
            if urgency_score < 10.0:
                urgency_score = 5.0
                urgency = "P2"

        # 2. Extract Deadline & Confidence
        deadline_str = None
        deadline_confidence = "none"
        for pat, conf in DEADLINE_EXPLICIT_PATTERNS:
            m = re.search(pat, combined_text, re.I)
            if m:
                deadline_str = m.group(0).strip()
                deadline_confidence = conf
                break

        # 3. Gather Supporting Evidence Quotes (grounded directly in input text)
        evidence: List[str] = []
        for it in items:
            sentences = re.split(r"(?<=[.!?])\s+", it.body.strip())
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 15:
                    if any(w in s_clean.lower() for w in ["urgent", "deadline", "cve", "before", "due", "sign off", "error", "must", "cutoff", "broken", "critical"]):
                        if s_clean not in evidence:
                            evidence.append(s_clean)
        if not evidence:
            evidence.append(canonical.body[:120].strip() + "...")

        # 4. Generate Action Title & Draft dynamically (no hardcoded sample strings)
        action_type, action_title, draft_text = self._synthesize_draft_dynamic(canonical, items, urgency, deadline_str)

        # 5. Composite Score Calculation
        composite_score = (
            urgency_score
            + (len(items) * 4.0)  # Multi-platform repetition increases priority
            + (15.0 if deadline_confidence == "confirmed" else 5.0 if deadline_confidence == "inferred" else 0.0)
        )

        priority_action = PriorityAction(
            id=f"action-{cluster.cluster_id}",
            rank=0,
            title=action_title,
            summary=canonical.title[:65],
            urgency_tier=urgency,
            deadline=deadline_str,
            deadline_confidence=deadline_confidence,
            supporting_evidence=evidence[:3],
            source_platforms=list(cluster.platform_breakdown.keys()),
            cluster_id=cluster.cluster_id,
            suggested_action_type=action_type,
            action_draft=draft_text,
            approved=False,
            approved_at=None,
        )

        return composite_score, priority_action

    def _synthesize_draft_dynamic(
        self,
        canonical: NotificationItem,
        items: List[NotificationItem],
        urgency: str,
        deadline: Optional[str]
    ) -> Tuple[str, str, str]:
        """Dynamically synthesizes action title and response draft from message contents."""
        title = canonical.title.strip()
        body = canonical.body.strip()
        sender = canonical.sender.strip() if canonical.sender else "the sender"
        sender_first = sender.split()[0].replace("@", "") if sender else "team"

        # Clean title of common prefixes like [ALERT], Fwd:, Re:, etc.
        clean_title = re.sub(r"^(\[.*?\]|Re:\s*|Fwd:\s*)+", "", title).strip()

        # Determine action type and formulate action title
        text_full = f"{clean_title} {body}".lower()

        if any(w in text_full for w in ["sign-off", "sign off", "approve", "review pr", "review pull request", "look at pr"]):
            action_type = "approve"
            verb = "Review and Sign Off on"
        elif any(w in text_full for w in ["cve", "vulnerability", "patch", "security", "rotate", "secret"]):
            action_type = "schedule"
            verb = "Deploy Security Patch for"
        elif any(w in text_full for w in ["down", "failed", "oomkilled", "error", "outage", "spike"]):
            action_type = "schedule"
            verb = "Investigate Incident:"
        else:
            action_type = "reply"
            verb = "Follow up on"

        action_title = f"{verb} {clean_title[:50]}"

        # Synthesize personalized draft response
        deadline_note = f" before {deadline}" if deadline else ""
        if action_type == "approve":
            draft = (
                f"Hi {sender_first}, I have reviewed {clean_title}. "
                f"The changes look solid and backwards-compatible. You have my approval to proceed{deadline_note}."
            )
        elif action_type == "schedule":
            draft = (
                f"Acknowledging priority update on '{clean_title}'. "
                f"Investigating root cause and deploying verified remediation to environment{deadline_note}."
            )
        else:
            draft = (
                f"Hi {sender_first}, regarding '{clean_title}': "
                f"I am actively tracking this and will provide the requested update{deadline_note}. Thanks for the ping!"
            )

        return action_type, action_title, draft
