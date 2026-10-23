"""Standalone benchmark and empirical evaluation runner for CalmQueue."""

import sys
import time
import json
import tracemalloc
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.models import NotificationItem
from app.clustering import SemanticClusterEngine
from app.gemma_engine import GemmaEngine

PRESETS_DIR = Path(__file__).resolve().parent / "sample_inboxes"


def evaluate_dataset(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_items = [NotificationItem(**x) for x in json.load(f)]

    cluster_engine = SemanticClusterEngine()
    gemma_engine = GemmaEngine()

    tracemalloc.start()
    start_time = time.perf_counter()

    items_map = {it.id: it for it in raw_items}
    clusters = cluster_engine.cluster_notifications(raw_items)
    top_actions, model = gemma_engine.extract_priorities(clusters, items_map)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    raw_count = len(raw_items)
    duplicate_clusters = [c for c in clusters if c.count > 1]
    total_duplicates_filtered = sum(c.count - 1 for c in clusters)
    noise_clusters = [c for c in clusters if c.is_noise]
    reduction_pct = ((raw_count - len(top_actions)) / raw_count) * 100

    confirmed_deadlines = sum(1 for a in top_actions if a.deadline_confidence == "confirmed")
    inferred_deadlines = sum(1 for a in top_actions if a.deadline_confidence == "inferred")

    return {
        "filename": file_path.name,
        "raw_messages": raw_count,
        "unique_clusters": len(clusters),
        "duplicate_groups": len(duplicate_clusters),
        "total_duplicates_filtered": total_duplicates_filtered,
        "noise_clusters_filtered": len(noise_clusters),
        "top_priority_actions": len(top_actions),
        "clutter_reduction_pct": round(reduction_pct, 1),
        "confirmed_deadlines": confirmed_deadlines,
        "inferred_deadlines": inferred_deadlines,
        "latency_ms": round(elapsed_ms, 2),
        "peak_memory_kb": round(peak_mem / 1024, 1),
        "model_runtime": model,
        "actions_summary": [f"[{a.urgency_tier}] {a.title} ({a.deadline or 'No deadline'})" for a in top_actions]
    }


def main():
    print("=" * 80)
    print(" CALMQUEUE EMPIRICAL EVALUATION SUITE — SLOW AND STEADY BENCHMARK")
    print("=" * 80)

    dataset_files = [
        PRESETS_DIR / "chaotic_monday.json",
        PRESETS_DIR / "devops_alert_storm.json",
        PRESETS_DIR / "maintainer_backlog.json",
    ]

    results = []
    for d_path in dataset_files:
        if d_path.exists():
            res = evaluate_dataset(d_path)
            results.append(res)
            print(f"\n[Dataset] {res['filename']}")
            print(f"  * Raw Messages Influx:       {res['raw_messages']}")
            print(f"  * Unique Clusters Formed:    {res['unique_clusters']}")
            print(f"  * Duplicate Messages Filtered: {res['total_duplicates_filtered']}")
            print(f"  * Background Noise Filtered: {res['noise_clusters_filtered']} clusters")
            print(f"  * Target Actions Surfaced:   {res['top_priority_actions']}")
            print(f"  * Displayed Volume Reduction: {res['clutter_reduction_pct']}%")
            print(f"  * Confirmed Deadlines:       {res['confirmed_deadlines']}")
            print(f"  * Inferred Deadlines:        {res['inferred_deadlines']}")
            print(f"  * Execution Latency:         {res['latency_ms']} ms")
            print(f"  * Peak Memory Footprint:     {res['peak_memory_kb']} KB")
            print(f"  * Active Inference Engine:   {res['model_runtime']}")
            print("  * Top 3 Selected Priorities:")
            for act in res["actions_summary"]:
                print(f"      - {act}")

    print("\n" + "=" * 80)
    print(" SUMMARY BENCHMARK TABLE")
    print("=" * 80)
    header = f"{'Dataset':<26} | {'Raw':<5} | {'Actions':<7} | {'Reduction':<10} | {'Latency':<9} | {'Memory':<10}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['filename']:<26} | {r['raw_messages']:<5} | {r['top_priority_actions']:<7} | {r['clutter_reduction_pct']}%{'':<4} | {r['latency_ms']} ms{'':<2} | {r['peak_memory_kb']} KB")
    print("=" * 80)


if __name__ == "__main__":
    main()
