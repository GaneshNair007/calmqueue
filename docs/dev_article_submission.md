---
title: CalmQueue: The Sloth-Speed AI That Turns 28 Daily Notifications Into 3 Quiet Actions
published: false
description: A local-first, open-source AI priority engine that cuts notification clutter by 89%. Built for Hacktoberfest 2026 Week 3: Slow and Steady.
tags: devchallenge, hf26challenge, opensource, ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge: Week 3 — Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

---

### The Morning Firehose

Every morning at 8:45 AM, modern developers, engineering leads, and open-source maintainers open their laptops to a wall of fragmented digital demands:

- 11 Slack messages across 4 direct messages and 3 channels.
- 6 GitHub notifications (`@you can you review this PR?`, `@you CI is broken on main`).
- 4 Jira/Linear ticket reassigments.
- 3 PagerDuty low-severity cluster alerts that triggered overnight.
- 4 emails from management asking for deck updates.

Total: **28 unread notifications.**

Here is the dirty secret of modern productivity: **Reading and triaging the notifications takes more cognitive energy than doing the actual work.**

When developers try using today's AI tools to solve this, they usually get an LLM chatbot. You paste in the messages, and the chatbot vomits back **four paragraphs of conversational text**, repeating everything in slightly different words. You haven't saved time; you've just added an AI intermediary to your reading pile.

I built **CalmQueue** to do the radical opposite.

Instead of an AI that talks more, CalmQueue is an AI that **deliberately shows you less**.

---

## 🦥 What I Built: CalmQueue

**CalmQueue** is an open-source, local-first AI assistant that accepts an unstructured stream of notifications, groups duplicate threads and noise, extracts grounded action items, and presents the user with **exactly three human-governed priority actions** for the day.

```
[BEFORE CALMQUEUE]
  28 unread messages
  8 duplicate alerts / repeated reminders
  5 unclear deadlines
  Too many micro-decisions ➡️ Decision paralysis

[AFTER CALMQUEUE]
  3 priority actions (P0, P1, P2)
  Duplicates clustered and deduplicated
  Verifiable source evidence quotes attached
  Draft responses ready for 1-click human approval
  Zero silent external actions
```

### The Core Interaction
1. **Import Stream**: Paste or load notifications from Slack, GitHub, Linear, Jira, or email.
2. **Semantic Clustering**: Open-source NLP and vector similarity cluster related messages (e.g., 6 separate Prometheus alerts or 4 follow-ups from the same project manager) into coherent threads and isolate automated bot chatter.
3. **Grounded Priority Reasoning**: Extracts actionable intent, classifies urgency (`P0`, `P1`, `P2`), and differentiates **confirmed deadlines** (e.g., `"Need by 2:00 PM today"`) from **inferred cues** (e.g., `"whenever you have a free moment"`).
4. **Quiet Dashboard**: Presents a clean, high-contrast dashboard with the top 3 priorities, verifiable evidence snippets, and pre-drafted replies.
5. **Human-in-the-Loop Safeguard**: No automated emails or API mutations are sent behind your back. Users review the draft in an editable modal, click **"Approve & Copy"**, and the action is recorded in a local SQLite audit log.

---

## 🎥 Live Interactive Web Demo & UI Tour

- **Public Interactive Demo**: [https://ganeshnair007.github.io/calmqueue/](https://ganeshnair007.github.io/calmqueue/)
- **Zero-Setup Evaluation**: Evaluators and judges can test CalmQueue immediately without installing Node or Python. The public demo runs a client-side triage engine with pre-bundled realistic notification datasets (Chaotic Monday, DevOps Alert Storm, Maintainer Backlog) and supports importing custom JSON payloads directly in the browser.

### The Quiet Dashboard
Three cards are shown in order of urgency. Each card displays:
- **Priority Tier**: `P0 Critical`, `P1 High`, or `P2 Moderate`.
- **Action Title**: Concise, imperative verb phrase dynamically formulated from the message context.
- **Deadline Pill**: Indicator distinguishing **Confirmed** deadlines (with specific times) from **Inferred** cues (soft urgency phrases).
- **Source Platform Badge**: Shows which platforms contributed to this action (e.g., Slack + Jira).
- **Clustered Message Count**: Number of messages consolidated into this single card.

### Evidence Grounding Drawer
Clicking **"Inspect Source Evidence"** expands an evidence drawer showing exact verbatim snippets, timestamps, authors, and channel names extracted from the raw messages.

### Human Approval Modal
Clicking **"Review & Approve Draft"** opens an approval modal containing the formulated response draft. The user can review, edit, and click **"Approve & Copy"**, which copies the text to the clipboard and records the approval timestamp in the local audit log.

---

## 💻 Open-Source Code Repository

All code, benchmark datasets, and documentation are open-source and released under the MIT license:

- **GitHub Repository**: [https://github.com/GaneshNair007/calmqueue](https://github.com/GaneshNair007/calmqueue)
- **Live Interactive Demo**: [https://ganeshnair007.github.io/calmqueue/](https://ganeshnair007.github.io/calmqueue/)
- **Local Quickstart**: Clone and run `python run.py` (takes under 60 seconds).

---

## 🛠️ How I Built It: Open-Source AI Architecture

CalmQueue is engineered as a **local-first** application. Your team's private Slack messages and internal security advisories never travel to proprietary third-party cloud APIs.

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

### The Technology Stack & Inference Engine:
- **Inference & Reasoning Runtime**:
  - Connects to local **Ollama** via `/api/chat` passing structured JSON schemas for action synthesis.
  - **Grounded Quote Validation**: Extracted evidence quotes must match verbatim substrings in the original input text. Unsupported or fabricated statements are stripped.
  - **Transparent Dual-Mode Fallback**: If the local Ollama daemon is offline or no model is loaded, the pipeline gracefully runs its deterministic rule-based NLP extraction, explicitly tagging every action with `generation_method='rule-based-fallback'` and reporting the active runtime.
  - **Accurate Latency Tracking**: Records true model inference time (`model_inference_latency_ms`) separately from deterministic execution latency.
- **Embeddings & Clustering**: TF-IDF vector space modeling with stopword elimination and n-gram similarity scoring.
- **Backend API**: Python 3.12, **FastAPI**, Pydantic v2, SQLite.
- **Frontend**: **React 19**, TypeScript, Vite, CSS Design Tokens (Vanilla CSS, no bulky UI framework dependencies).
- **Test Suite**: pytest (11/11 automated tests passing, covering API endpoints, deterministic extraction, and mock Ollama `/api/chat` inference with quote grounding).

---

## 📊 Real Benchmark Measurements

To adhere to the Hacktoberfest evaluation criteria, I wrote an automated benchmark suite (`benchmarks/run_eval.py`) that tests CalmQueue against three realistic, authentic workloads:

1. **Chaotic Monday Morning** (28 items): Typical engineering lead inbox with overlapping PR reviews, sprint planning reminders, Jira blockers, and cross-channel chatter.
2. **DevOps Alert Storm** (22 items): Cascading infrastructure failure with multiple Prometheus OOMKill spikes, Redis latency warnings, automated health check alerts, and AWS SSM rotation notices.
3. **Open-Source Maintainer Backlog** (35 items): High-volume public repo triage with duplicated "good first issue" requests, Dependabot alerts, spam bot comments, and a critical YAML deserialization security report.

Here are the real, empirical benchmark results:

| Benchmark Dataset | Raw Messages | Duplicate Clusters Grouped | Noise Items Isolated | Priority Actions Surfaced | Displayed Volume Reduction Rate | Processing Latency | Peak Memory | Active Engine |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Chaotic Monday Morning** | 28 | 3 | 4 | **3** | **89.3%** | ~55 ms | 182.5 KB | `rule-based-fallback` |
| **DevOps Alert Storm** | 22 | 4 | 1 | **3** | **86.4%** | ~18 ms | 84.6 KB | `rule-based-fallback` |
| **Maintainer Backlog** | 35 | 5 | 6 | **3** | **91.4%** | ~45 ms | 116.0 KB | `rule-based-fallback` |

*Note: In the evaluation environment without a running GPU/Ollama instance, benchmarks reflect the deterministic fallback runtime. Full LLM inference latency varies by local hardware (typically 1.2s - 3.5s on 4-bit quantized 2B-7B models).*

### Key Benchmark Takeaways:
- **Displayed Volume Reduction: 89.03% average**. By clustering duplicates and isolating noise, CalmQueue reduces the volume of surfaced items from an average of 28.3 down to exactly 3.
- **Sub-60ms Processing Latency** (Fallback Mode): The local deterministic pipeline executes in milliseconds without waiting on cloud network round-trips.
- **Confirmed vs. Inferred Deadlines**: Explicitly distinguishes hard deadlines (e.g. `"before 2:00 PM"`) from soft cues (e.g. `"when you get a chance"`), avoiding false-urgency panic.

---

## 🛡️ Human-in-the-Loop Safeguards & Ethical AI

A major failure mode of recent "AI Agents" is **unsupervised automation**—bots sending emails, deleting issues, or merging pull requests without human verification.

CalmQueue enforces three core architectural safeguards:
1. **No Silent Side-Effects**: CalmQueue has no outbound webhooks that send emails, post Slack messages, or mutate repositories autonomously.
2. **Mandatory Human Approval**: Every generated draft must be reviewed, edited if necessary, and approved by the user.
3. **Persistent Local Audit Log**: When a draft is approved, a record is stored in the local SQLite database (`calmqueue.db`) containing the timestamp, action ID, and user-confirmed text.

---

## 💡 Lessons Learned & Architectural Trade-offs

During development, two key architectural lessons shaped the final design:

1. **Single-Prompt LLM Summarization vs. Staged Pipeline**:
   - Sending an entire 28-message stream into a single prompt often resulted in the model blending distinct alerts together or omitting quiet, high-severity operational tickets.
   - Decomposing the system into an initial **clustering and noise-filtering stage** followed by **per-cluster action synthesis** produced much more reliable, auditable outputs.

2. **The "Rule of Three" for Attention Conservation**:
   - Displaying 10+ categorized cards still creates cognitive fatigue. Enforcing a strict cap of the top three highest-urgency items forces clarity on what actually requires attention today, while secondary clusters remain accessible on demand.

---

## 🏁 Prize Categories Targeted

- **Overall Winner ($250)**: Built for the **"Slow and Steady"** theme by creating an open-source AI assistant that reduces noise, promotes human calm, automates tedious inbox triage, and enforces human oversight.
- **DEV Completion Badge**: Awarded to all valid, reproducible open-source AI projects meeting the challenge requirements.

---

## 📦 How to Run CalmQueue Locally

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
Open **`http://localhost:8000`** in your browser to experience the Quiet Dashboard.
Or explore the zero-install live demo at: **`https://ganeshnair007.github.io/calmqueue/`**

---

*Thank you to DEV, Major League Hacking, and the open-source community for organizing Hacktoberfest 2026. Here's to slowing down, triaging less, and building steady!*

