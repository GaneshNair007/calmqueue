"""Semantic deduplication and clustering engine for CalmQueue."""

from __future__ import annotations

import re
import math
from collections import Counter, defaultdict
from typing import List, Tuple, Dict, Set
from .models import NotificationItem, ClusterGroup

# Common noise patterns that do not require user decisions
NOISE_PATTERNS = [
    r"\+1",
    r"lunch menu",
    r"cafeteria",
    r"coffee",
    r"closed inactive",
    r"marked as stale",
    r"scheduled security scan.*0",
    r"daily spend.*within expected",
    r"monitor up: api healthcheck",
    r"discussion.*pre-alpha",
    r"nevermind figured it out",
    r"weekly tech newsletter",
    r"all checks green",
    r"ruff format check passed",
]


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into clean lowercase terms."""
    clean = re.sub(r"[^\w\s-]", " ", text.lower())
    tokens = [t.strip("-") for t in clean.split() if len(t) > 2]
    # Filter common stop words
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "you", "are", "have", "not", "your",
        "has", "was", "will", "all", "can", "been", "would", "about", "what", "which", "there"
    }
    return [t for t in tokens if t not in stopwords]


def compute_tf_idf_vector(tokens: List[str], idf_dict: Dict[str, float]) -> Dict[str, float]:
    """Calculate normalized TF-IDF vector."""
    tf = Counter(tokens)
    total_tokens = len(tokens) or 1
    vec = {}
    for term, count in tf.items():
        weight = (count / total_tokens) * idf_dict.get(term, 1.0)
        vec[term] = weight
    # Normalize
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {k: v / norm for k, v in vec.items()}


def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    common_keys = set(vec1.keys()) & set(vec2.keys())
    if not common_keys:
        return 0.0
    return sum(vec1[k] * vec2[k] for k in common_keys)


def is_noise_item(item: NotificationItem) -> bool:
    """Determine if a notification is low-value routine background noise."""
    combined = f"{item.title} {item.body}".lower()
    for pat in NOISE_PATTERNS:
        if re.search(pat, combined):
            return True
    return False


class SemanticClusterEngine:
    """Clusters notifications by semantic similarity and platform deduplication."""

    def __init__(self, similarity_threshold: float = 0.58):
        self.similarity_threshold = similarity_threshold

    def cluster_notifications(self, items: List[NotificationItem]) -> List[ClusterGroup]:
        """Groups notification items into semantic clusters."""
        if not items:
            return []

        # 1. Build document frequency for IDF
        doc_count = len(items)
        df_counter: Counter = Counter()
        item_tokens: Dict[str, List[str]] = {}

        for item in items:
            text = f"{item.title} {item.title} {item.body}"
            toks = tokenize(text)
            item_tokens[item.id] = toks
            for t in set(toks):
                df_counter[t] += 1

        idf_dict = {term: math.log((doc_count + 1) / (df + 1)) + 1.0 for term, df in df_counter.items()}
        vectors = {item.id: compute_tf_idf_vector(item_tokens[item.id], idf_dict) for item in items}

        # 2. Greedy clustering by semantic similarity
        assigned_clusters: Dict[str, int] = {}
        clusters: List[List[NotificationItem]] = []

        for i, item in enumerate(items):
            if item.id in assigned_clusters:
                continue

            current_cluster = [item]
            assigned_clusters[item.id] = len(clusters)
            vec_i = vectors[item.id]

            for j in range(i + 1, len(items)):
                candidate = items[j]
                if candidate.id in assigned_clusters:
                    continue

                vec_j = vectors[candidate.id]
                sim = cosine_similarity(vec_i, vec_j)

                # Keyword exact title match bonus
                if item.title.strip().lower() == candidate.title.strip().lower():
                    sim = max(sim, 0.95)

                # Key phrase match (e.g. CVE, JIRA ticket ID, incident ID)
                id_pat = r"(CVE-\d+-\d+|ENG-\d+|PROD-\d+|PR\s*#\d+|#[0-9]+|Incident\s*#\d+)"
                ids_i = set(re.findall(id_pat, f"{item.title} {item.body}", re.I))
                ids_j = set(re.findall(id_pat, f"{candidate.title} {candidate.body}", re.I))
                if ids_i and ids_j and (ids_i & ids_j):
                    sim = max(sim, 0.85)

                if sim >= self.similarity_threshold:
                    current_cluster.append(candidate)
                    assigned_clusters[candidate.id] = len(clusters)

            clusters.append(current_cluster)

        # 3. Format as ClusterGroup models
        result: List[ClusterGroup] = []
        for idx, group in enumerate(clusters):
            # Sort by informative content length & recency
            group.sort(key=lambda x: (len(x.body), x.timestamp), reverse=True)
            canonical = group[0]
            platform_counts = Counter(x.source for x in group)
            is_noise = all(is_noise_item(x) for x in group)

            sample_text = canonical.body[:140] + ("..." if len(canonical.body) > 140 else "")

            result.append(
                ClusterGroup(
                    cluster_id=f"cluster-{idx+1:03d}",
                    canonical_title=canonical.title,
                    canonical_id=canonical.id,
                    item_ids=[x.id for x in group],
                    count=len(group),
                    platform_breakdown=dict(platform_counts),
                    duplicate_score=round(1.0 - (1.0 / len(group)), 2) if len(group) > 1 else 0.0,
                    is_noise=is_noise,
                    sample_text=sample_text,
                )
            )

        return result
