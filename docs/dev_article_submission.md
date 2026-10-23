---
title: CalmQueue: The Sloth-Speed AI That Turns 28 Daily Notifications Into 3 Quiet Actions
published: true
tags: devchallenge, hf26challenge, opensource, ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)*

## What I Built

Modern developers, team leads, and open-source maintainers face an exhausting morning ritual: opening their laptops to a wall of 25+ fragmented pings across Slack, GitHub, Linear, Jira, and email.

Triage fatigue is real. Reading, de-duplicating, and prioritizing overlapping alerts often takes more mental energy than writing code. Most AI tools exacerbate this by acting as conversational chatbots that generate another wall of prose—forcing you to read even more text just to figure out what needs attention.

**CalmQueue** was built to do the radical opposite. Guided by the Hacktoberfest "Slow and Steady" ethos, CalmQueue is an open-source, local-first notification assistant that **deliberately shows you less**:

- Ingests raw notification streams from multi-platform inboxes.
- Groups repetitive alerts, automated bot clutter, and duplicate follow-ups using semantic TF-IDF cosine similarity.
- Synthesizes exactly **three actionable priorities (P0, P1, P2)** for the workday.
- Grounds every decision with verifiable verbatim quote evidence from the original source message.
- Enforces strict human-in-the-loop oversight: draft responses require 1-click human review before copying, with zero silent external mutations.

```
[BEFORE CALMQUEUE]
  28 unread messages
  8 duplicate alerts / repeated reminders
  5 ambiguous deadlines
  Too many micro-decisions ➡️ Mental fatigue & paralysis

[AFTER CALMQUEUE]
  3 priority actions (P0, P1, P2)
  Duplicates clustered and deduplicated
  Verifiable source evidence quotes attached
  Draft responses ready for 1-click human approval
  Zero silent external actions
```

## Demo

- **Live Interactive Web Demo (Zero-Install)**: [https://ganeshnair007.github.io/calmqueue/](https://ganeshnair007.github.io/calmqueue/)
- Judges and community members can evaluate CalmQueue instantly in their browser with pre-bundled scenarios (*Chaotic Monday Morning*, *DevOps Alert Storm*, *Maintainer Backlog*) or import custom JSON payloads directly.

### UI Walkthrough:
1. **The Quiet Dashboard**: High-contrast, minimalist interface showing the top 3 priorities, urgency badges (`P0 Critical`, `P1 High`, `P2 Moderate`), and deadline indicators distinguishing confirmed timestamps from inferred cues.
2. **Evidence Grounding Drawer**: Expanding an item reveals exact verbatim source quotes, timestamps, authors, and channel tags.
3. **Review & Approve Modal**: Allows the user to inspect, edit, and approve pre-formulated response drafts with local SQLite audit logging.

## Code

CalmQueue is 100% open-source under the MIT license:

- **GitHub Repository**: [https://github.com/GaneshNair007/calmqueue](https://github.com/GaneshNair007/calmqueue)
- **Live Interactive Demo**: [https://ganeshnair007.github.io/calmqueue/](https://ganeshnair007.github.io/calmqueue/)

### Local Quickstart:
```bash
# 1. Clone the repository
git clone https://github.com/GaneshNair007/calmqueue.git
cd calmqueue

# 2. Install requirements
pip install -r requirements.txt

# 3. (Optional) Run Ollama for local LLM inference
# ollama run gemma2:2b

# 4. Launch CalmQueue
python run.py
```
Open `http://localhost:8000` to run the local FastAPI + React 19 application.

## How I Built It

CalmQueue is engineered as a **local-first** application with an auditable dual-mode architecture:

```
 ┌────────────────────────────────────────────────────────┐
 │                   RAW NOTIFICATIONS                    │
 │         (Slack, GitHub, Linear, Jira, Email)           │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │            1. SEMANTIC CLUSTER ENGINE                  │
 │   - TF-IDF N-Gram Vector Space Cosine Similarity       │
 │   - Noise & Automated Bot Filter                       │
 │   - Multi-platform thread deduplication                │
 └───────────────────────────┬────────────────────────────┘
                             │ Grouped Clusters
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │        2. TASK REASONING & EXTRACTION ENGINE           │
 │   - Local Ollama Bridge (/api/chat structured JSON)    │
 │   - Verbatim Quote Grounding Validation                │
 │   - Transparent Rule-Based Fallback when LLM offline   │
 │   - Generation method & latency explicitly recorded    │
 └───────────────────────────┬────────────────────────────┘
                             │ Structured Actions
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │           3. EVIDENCE GROUNDING & RANKER               │
 │   - Confirmed vs. Inferred Deadline Extraction         │
 │   - Top-3 Priority Selection (P0 -> P1 -> P2)          │
 │   - Substring verification against raw text            │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │       4. QUIET DASHBOARD & HUMAN SAFEGUARD             │
 │   - React 19 + TypeScript (Distraction-Free UI)        │
 │   - FastAPI Async REST Service                         │
 │   - SQLite Human-Approval Audit Trail (calmqueue.db)   │
 └────────────────────────────────────────────────────────┘
```

### Technical Pillars:
1. **Semantic Clustering (`backend/app/clustering.py`)**:
   - Converts message bodies, senders, and thread tags into n-gram TF-IDF vectors.
   - Computes cosine similarity to group duplicate alerts (e.g., 6 Prometheus OOMKill spikes or 4 Jira re-assignments) and isolates automated bot clutter.
2. **Grounded Priority Extraction (`backend/app/gemma_engine.py`)**:
   - **Local Open-Weight LLM Bridge**: When [Ollama](https://ollama.com/) is running locally, CalmQueue connects to `/api/chat` with structured JSON schema constraints, requesting priority classification, concise imperative titles, and draft actions.
   - **Verbatim Quote Grounding Validation**: Extracted evidence must strictly match verbatim substrings in the raw input text. Unsupported or fabricated statements are stripped.
   - **Transparent Rule-Based Fallback**: If Ollama is offline or uninstalled, the engine gracefully executes a deterministic heuristic NLP pipeline, explicitly labeling outputs with `generation_method='rule-based-fallback'` and reporting the active runtime.
   - **True Latency Recording**: Captures true model inference time (`model_inference_latency_ms`) separately from deterministic execution latency.
3. **Quiet Interface & Human Safeguard**:
   - Built with **React 19**, TypeScript, and Vite.
   - Approval events are recorded with local timestamps in SQLite (`calmqueue.db`).
   - Automated tests: 11/11 passing in pytest (`backend/tests/`).

## Why Does Open Innovation Matter?

Open innovation is fundamental to CalmQueue's purpose:

1. **Confidentiality & Data Sovereignty**: Internal Slack messages, security vulnerability disclosures, and production outage alerts contain confidential proprietary business data and PII. Transmitting these message streams to third-party proprietary cloud APIs presents unacceptable compliance, legal, and privacy risks. Running open-weight models locally ensures private data never leaves your computer.
2. **Offline Resilience & Zero Recurring Cost**: Closed cloud APIs require an active internet connection and incur per-token subscription costs that scale with message volume. Open-weight models running on local hardware work seamlessly without an internet connection (e.g. while traveling) and cost nothing in ongoing API bills.
3. **Auditable, Verifiable AI**: Closed APIs change models silently behind version endpoints, causing classification and formatting regressions without warning. Open-source models and deterministic validation pipelines can be pinned, inspected, and verified against reproducible test suites.

## The Lazy Payoff

CalmQueue was built for developers who want to triage their backlog and get back to living their lives.

We evaluated CalmQueue across three authentic synthetic workloads using `benchmarks/run_eval.py`:

| Benchmark Dataset | Raw Influx | Duplicate Clusters | Filtered Noise | Priorities Surfaced | Displayed Volume Reduction | Processing Latency | Active Engine |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Chaotic Monday Morning** | 28 | 3 | 4 | **3** | **89.3%** | ~52 ms | `rule-based-fallback` |
| **DevOps Alert Storm** | 22 | 4 | 1 | **3** | **86.4%** | ~24 ms | `rule-based-fallback` |
| **Maintainer Backlog** | 35 | 5 | 6 | **3** | **91.4%** | ~44 ms | `rule-based-fallback` |

*Average Displayed Volume Reduction: 89.03% across test workloads.*

Instead of sifting through 28 notifications, you review exactly three actionable items, approve the prepared responses in under two minutes, and spend your day doing deep work—or taking it slow like a sloth.

## Prize Categories

- **Overall Winner ($250)**: Built for the **"Slow and Steady"** theme by creating an open-source AI assistant that champions radical cognitive subtraction, protects user attention, and enforces human oversight.
- **DEV Completion Badge**: Fully reproducible open-source AI application meeting all challenge guidelines.
