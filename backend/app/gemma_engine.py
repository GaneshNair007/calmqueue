"""Task extractor and priority engine for CalmQueue.

Provides genuine dual-mode operation:
1. Live local LLM inference via Ollama (/api/chat) with structured JSON enforcement,
   grounded quote validation, and true model latency recording.
2. Deterministic grounded rule-based extraction fallback when Ollama is offline or uninstalled.
"""

from __future__ import annotations

import re
import json
import time
import urllib.request
import urllib.error
import logging
from typing import List, Dict, Optional, Tuple, Any
from .models import NotificationItem, ClusterGroup, PriorityAction

logger = logging.getLogger("calmqueue.engine")

# Urgency and priority patterns based on standard DevOps / SRE terminology
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
    """Orchestrates priority action extraction.
    
    If local Ollama is reachable, dispatches actual generative inference requests
    with strict JSON formatting and evidence quote verification.
    If Ollama is unreachable, transparently falls back to the deterministic
    grounded NLP extraction pipeline, clearly marking generation_method='rule-based-fallback'.
    """

    def __init__(self, ollama_host: str = "http://127.0.0.1:11434", model_name: str = "gemma2:2b"):
        self.ollama_host = ollama_host
        self.model_name = model_name
        self.is_ollama_available = False
        self.active_runtime = "rule-based-fallback"
        self._last_check_time = 0.0
        self._check_cache_ttl = 5.0
        self._check_ollama(force=True)

    def _check_ollama(self, force: bool = False) -> bool:
        """Check if local Ollama daemon is reachable and inspect loaded models."""
        now = time.time()
        if not force and (now - self._last_check_time < self._check_cache_ttl):
            return self.is_ollama_available
        self._last_check_time = now

        try:
            req = urllib.request.Request(f"{self.ollama_host}/api/tags", headers={"User-Agent": "CalmQueue"})
            with urllib.request.urlopen(req, timeout=0.2) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("name", "") for m in data.get("models", [])]
                for m in models:
                    if "gemma" in m:
                        self.model_name = m
                        self.is_ollama_available = True
                        self.active_runtime = f"ollama-{m}"
                        logger.info("Connected to local Ollama with Gemma model: %s", m)
                        return True
                if models:
                    self.model_name = models[0]
                    self.is_ollama_available = True
                    self.active_runtime = f"ollama-{models[0]}"
                    logger.info("Connected to local Ollama with model: %s", models[0])
                    return True
        except Exception:
            pass

        self.is_ollama_available = False
        self.active_runtime = "rule-based-fallback"
        return False

    def extract_priorities(
        self,
        clusters: List[ClusterGroup],
        raw_items_map: Dict[str, NotificationItem]
    ) -> Tuple[List[PriorityAction], str, Optional[float]]:
        """Analyzes clusters to extract exactly top-3 priority actions with grounded evidence.
        
        Returns:
            (top_actions, active_runtime, total_llm_inference_latency_ms)
        """
        # Re-check Ollama status in case daemon was started or stopped
        self._check_ollama()

        scored_candidates: List[Tuple[float, PriorityAction]] = []
        total_llm_time_ms = 0.0
        used_llm = False

        for cluster in clusters:
            if cluster.is_noise:
                continue

            canonical = raw_items_map.get(cluster.canonical_id)
            if not canonical:
                continue

            all_cluster_items = [raw_items_map[iid] for iid in cluster.item_ids if iid in raw_items_map]
            combined_text = "\n".join(f"[{it.source}] {it.sender} ({it.timestamp}): {it.title} - {it.body}" for it in all_cluster_items)

            # Try real LLM inference if Ollama is available
            action: Optional[PriorityAction] = None
            score: float = 0.0

            if self.is_ollama_available:
                score, action, llm_latency = self._call_ollama_inference(cluster, canonical, all_cluster_items, combined_text)
                if action:
                    used_llm = True
                    if llm_latency:
                        total_llm_time_ms += llm_latency

            # Fallback to deterministic NLP if LLM was unavailable or call failed
            if not action:
                score, action = self._analyze_cluster_deterministic(cluster, all_cluster_items, combined_text)

            if action:
                scored_candidates.append((score, action))

        # Sort candidates by priority score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Select exactly top-3 priority actions
        top_actions: List[PriorityAction] = []
        for rank, (_, item) in enumerate(scored_candidates[:3], start=1):
            item.rank = rank
            top_actions.append(item)

        runtime_label = self.active_runtime if used_llm else "rule-based-fallback"
        recorded_llm_time = round(total_llm_time_ms, 2) if used_llm else None

        return top_actions, runtime_label, recorded_llm_time

    def _call_ollama_inference(
        self,
        cluster: ClusterGroup,
        canonical: NotificationItem,
        items: List[NotificationItem],
        combined_text: str
    ) -> Tuple[float, Optional[PriorityAction], Optional[float]]:
        """Executes actual generative inference against Ollama /api/chat.
        
        Enforces strict JSON schema, validates verbatim quote evidence grounding,
        and accurately records true model inference duration.
        """
        system_prompt = (
            "You are CalmQueue, a precise on-device notification priority engine. "
            "Analyze the given notification cluster and extract a single actionable priority item. "
            "Respond strictly with valid JSON using exactly this schema:\n"
            "{\n"
            "  \"action_title\": \"concise imperative title (max 60 chars)\",\n"
            "  \"urgency_tier\": \"P0\" or \"P1\" or \"P2\",\n"
            "  \"deadline\": \"explicit deadline string or null\",\n"
            "  \"deadline_confidence\": \"confirmed\" or \"inferred\" or \"none\",\n"
            "  \"evidence_quotes\": [\"exact verbatim substring quote from the messages\"],\n"
            "  \"suggested_action_type\": \"approve\" or \"schedule\" or \"reply\",\n"
            "  \"action_draft\": \"professional drafted response to sender\"\n"
            "}\n"
            "CRITICAL: All evidence_quotes must be exact verbatim quotes from the input. Do not fabricate."
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CLUSTER MESSAGES:\n{combined_text}"}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 300
            }
        }

        start_time = time.perf_counter()
        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.ollama_host}/api/chat",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "CalmQueue"}
            )
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                raw_response = json.loads(resp.read().decode("utf-8"))
                latency_ms = (time.perf_counter() - start_time) * 1000

                content_str = raw_response.get("message", {}).get("content", "")
                parsed = json.loads(content_str)

                # Validate fields
                action_title = str(parsed.get("action_title", canonical.title[:50]))
                urgency = str(parsed.get("urgency_tier", "P2")).upper()
                if urgency not in ("P0", "P1", "P2"):
                    urgency = "P2"

                deadline = parsed.get("deadline")
                deadline_str = str(deadline) if deadline else None

                confidence = str(parsed.get("deadline_confidence", "none")).lower()
                if confidence not in ("confirmed", "inferred", "none"):
                    confidence = "none"

                action_type = str(parsed.get("suggested_action_type", "reply")).lower()
                if action_type not in ("approve", "schedule", "reply", "review"):
                    action_type = "reply"

                action_draft = str(parsed.get("action_draft", f"Acknowledging receipt of {canonical.title}."))

                # Grounding Validation: verify quotes appear in combined_text
                raw_quotes = parsed.get("evidence_quotes", [])
                valid_evidence: List[str] = []
                for q in raw_quotes:
                    q_str = str(q).strip()
                    if q_str and q_str.lower() in combined_text.lower():
                        valid_evidence.append(q_str)

                # If model hallucinated quotes not in input text, fall back to authentic source snippet
                if not valid_evidence:
                    valid_evidence.append(canonical.body[:120].strip() + "...")

                # Calculate priority score
                urgency_score = 50.0 if urgency == "P0" else 30.0 if urgency == "P1" else 10.0
                composite_score = (
                    urgency_score
                    + (len(items) * 4.0)
                    + (15.0 if confidence == "confirmed" else 5.0 if confidence == "inferred" else 0.0)
                )

                priority_action = PriorityAction(
                    id=f"action-{cluster.cluster_id}",
                    rank=0,
                    title=action_title,
                    summary=canonical.title[:65],
                    urgency_tier=urgency,
                    deadline=deadline_str,
                    deadline_confidence=confidence,
                    supporting_evidence=valid_evidence[:3],
                    source_platforms=list(cluster.platform_breakdown.keys()),
                    cluster_id=cluster.cluster_id,
                    suggested_action_type=action_type,
                    action_draft=action_draft,
                    approved=False,
                    approved_at=None,
                    generation_method="ollama-llm",
                    model_inference_latency_ms=round(latency_ms, 2)
                )

                return composite_score, priority_action, latency_ms

        except Exception as e:
            logger.warning("Ollama inference call failed (%s); engaging rule-based fallback.", e)
            return 0.0, None, None

    def _analyze_cluster_deterministic(
        self,
        cluster: ClusterGroup,
        items: List[NotificationItem],
        combined_text: str
    ) -> Tuple[float, Optional[PriorityAction]]:
        """Deterministic grounded NLP extraction pipeline (reliable fallback)."""
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

        # 4. Generate Action Title & Draft dynamically
        action_type, action_title, draft_text = self._synthesize_draft_dynamic(canonical, items, urgency, deadline_str)

        # 5. Composite Score Calculation
        composite_score = (
            urgency_score
            + (len(items) * 4.0)
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
            generation_method="rule-based-fallback",
            model_inference_latency_ms=None
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

        # Clean title of common email/ticket prefixes
        clean_title = re.sub(r"^(\[.*?\]|Re:\s*|Fwd:\s*|FWD:\s*)+", "", title).strip()

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
