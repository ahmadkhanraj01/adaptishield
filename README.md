# AdaptiShield — Project Status & Handover

**Project:** Adaptive Threat Modeling for Tool-Orchestrated LLM Systems in MCP Architectures
**Supervisor:** Dr. Laeeq Ahmed
**Students:** Muhammad Ahmad Khan (23JZBCS0238) · Aleena Khan (23JZBCS0229)
**Department:** CS&IT — University of Engineering and Technology Peshawar (Jalozai Campus)
**Doc version:** v9 (July 2026) — current-state handover, supersedes all prior versions

> This README is the single source of truth for **where the code stands today**. It records the current architecture, what is built and validated, how to run it, and what to build next. Every architecture folder also has its own `README.md` with a per-component breakdown. The academic research narrative lives in `researchworksofar.md`.

---

## Table of Contents
1. [Status at a Glance](#1-status-at-a-glance)
2. [Machine Specifications](#2-machine-specifications)
3. [Architecture Overview](#3-architecture-overview)
4. [Directory Structure](#4-directory-structure)
5. [Build Status by Component](#5-build-status-by-component)
6. [What Is Implemented and Validated](#6-what-is-implemented-and-validated)
7. [Key Design Decisions](#7-key-design-decisions)
8. [Package Versions](#8-package-versions)
9. [Models in Use](#9-models-in-use)
10. [Compute Strategy](#10-compute-strategy)
11. [How to Run](#11-how-to-run)
12. [Testing Checklist](#12-testing-checklist)
13. [What to Build Next](#13-what-to-build-next)

---

## 1. Status at a Glance

The full defensive pipeline (Layers 0–4) and the complete Security Sub-layer (3A→3B→3C→3D) are built and validated locally end-to-end. The Red Team Module runs against the live pipeline and produces ASR/FPR/WCR numbers. The one remaining core piece is the **real GRPO/RL training loop for Component 3D**, which must run on Kaggle (the local 4 GB GPU cannot host it) — 3D's reward function and update loop are already built and validated as a CPU-only heuristic.

| Area | State |
| :--- | :--- |
| Layer 0 — Server Trust Registry | ✅ Built & tested |
| Layer 1 — Provenance / context partition | ✅ Built & tested |
| Layer 2 — 3A Policy Engine | ✅ Built & tested |
| Layer 2 — 3B Causal Analyzer | ✅ Built & validated |
| Layer 2 — 3C Context Sanitizer | ✅ Built & tested |
| Layer 2 — 3D Adaptive Threat Model | 🟡 v1 CPU heuristic built & validated; GRPO/Kaggle pending |
| Layer 3 — Tool Response Screener | ✅ Built & wired |
| Layer 4 — Permission / Egress / Sandbox / Telemetry | ✅ Built, wired & validated (real gated Docker execution) |
| Red Team Module | ✅ v1 built & validated (found a real 3B gap) |
| Full pipeline (`adaptishield_pipeline.py`) | ✅ Validated on true-positive + true-negative + benign cases |
| Evaluation framework · Layer 5 dashboard · pytest suite | 🔲 Pending |

**Rough completion: ~65%.** Crucially, the adaptive mechanism — the project's central thesis claim — is demonstrated working end-to-end, not just designed.

---

## 2. Machine Specifications

| Component | Detail |
| :--- | :--- |
| **Machine** | Dell Vostro 7500 |
| **OS** | Ubuntu 24.04.4 LTS |
| **Python** | 3.10.12 |
| **GPU** | NVIDIA GTX 1650 Ti |
| **VRAM** | 4 GB *(hard limit for GPU inference)* |
| **RAM** | 16 GB |
| **CPU** | Intel i7-10750H (6 cores) |

---

## 3. Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────┐
│  Layer 5 — Human-in-the-Loop & Observability        [pending]     │
│  Audit Dashboard · Policy Inspection Console · Manual Override    │
├──────────────────────────────────────────────────────────────────┤
│  Red Team Module                                    [v1 built]    │
│  Attack Generator · Execution Agent · Evaluator · Optimizer      │
├──────────────────────────────────────────────────────────────────┤
│  Layer 4 — Sandbox and Isolation                    [built]       │
│  Docker Sandbox · Permission Control · Network Egress Filter     │
│  Telemetry Stream                                                 │
├──────────────────────────────────────────────────────────────────┤
│  Layer 3 — MCP Tool Execution Plane                 [built]       │
│  APIs · Databases · File Systems · Tool Response Screener        │
├──────────────────────────────────────────────────────────────────┤
│  Layer 2 — LLM Agent Control Plane                  [built]       │
│  Planner Agent · Tool Selector · Execution Agent                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Security and Adaptive Sub-layer  (3A → 3B → 3C → 3D)      │  │
│  │  3A  Policy Engine            ✅                            │  │
│  │  3B  Causal Analyzer          ✅                            │  │
│  │  3C  Context Sanitizer        ✅                            │  │
│  │  3D  Adaptive Threat Model    🟡 v1 heuristic (GRPO pending)│  │
│  └────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│  Layer 1 — Input and Supply Chain Screening         [built]       │
│  Input Parser · Context Builder · Provenance Memory Store        │
├──────────────────────────────────────────────────────────────────┤
│  Layer 0 — MCP Transport and Server Trust           [built]       │
│  Server Trust Registry (rug-pull detection · allowlist)          │
└──────────────────────────────────────────────────────────────────┘
```

### Evaluation Metrics

| Metric | Description | Target |
| :--- | :--- | :--- |
| **ASR (Attack Success Rate)** | Fraction of attacks that fully execute | Lower is better |
| **FPR (False Positive Rate)** | Fraction of benign actions incorrectly blocked | Lower is better |
| **WCR (Workflow Continuation Rate)** | Fraction of adversarial trials where the legitimate task still completes | Higher is better |

---

## 4. Directory Structure

```text
~/adaptishield/
├── adaptishield_pipeline.py            ✅ Full pipeline: L1→L3→3A→3B→3C→L4 (+gated sandbox) → telemetry
├── requirements.txt
├── README.md                           (this file)
├── researchworksofar.md                academic research journal (dated entries)
│
├── layer0/  server_trust_registry.py   ✅ + README.md
├── layer1/  provenance.py              ✅ + README.md
├── layer2/
│   ├── README.md
│   └── security_sublayer/
│       ├── README.md
│       ├── policy_engine.py            ✅ 3A
│       ├── causal_analyzer.py          ✅ 3B  (gemma3:4b, k_samples=2)
│       ├── context_sanitizer.py        ✅ 3C
│       └── adaptive_threat_model.py    🟡 3D  (v1 CPU heuristic; GRPO/Kaggle pending)
├── layer3/  tool_response_screener.py  ✅ + README.md
├── layer4/
│   ├── README.md
│   ├── permission_control.py           ✅
│   ├── network_egress_filter.py        ✅
│   ├── sandbox.py                      ✅ wired into _run_layer4 (gated Docker execution)
│   └── telemetry_stream.py             ✅ writes JSONL Episode Records (+ sandbox_result field)
├── red_team/
│   ├── README.md
│   ├── attack_library.py               ✅ 4 attack families + benign controls
│   ├── attack_generator.py             ✅ builds RedTeamCase objects
│   ├── execution_agent.py              ✅ runs cases through the live pipeline (dry-run)
│   ├── evaluator.py                    ✅ ASR/FPR/WCR + per-layer breakdown
│   ├── optimizer.py                    ✅ v1 heuristic keyword-softening mutator
│   └── run_campaign.py                 ✅ wires all four stages; saves reports
├── utils/   parsing.py                 ✅ shared tolerant NEXT: parser + README.md
├── logs/
│   ├── episode_records/episodes.jsonl  ✅ populated on every run (gitignored)
│   └── red_team_runs/campaign_*.json   ✅ one report per campaign (gitignored)
├── layer5/                             🔲 pending (README.md placeholder)
├── evaluation/                         🔲 pending (README.md placeholder)
└── tests/                              🔲 pending (README.md placeholder)
```

---

## 5. Build Status by Component

| Component | File | Status |
| :--- | :--- | :--- |
| Server Trust Registry | `layer0/server_trust_registry.py` | ✅ Built & tested |
| Provenance Tagging | `layer1/provenance.py` | ✅ Built & tested |
| Policy Engine (3A) | `layer2/security_sublayer/policy_engine.py` | ✅ Built & tested |
| Causal Analyzer (3B) | `layer2/security_sublayer/causal_analyzer.py` | ✅ Built & validated |
| Context Sanitizer (3C) | `layer2/security_sublayer/context_sanitizer.py` | ✅ Built & tested |
| Adaptive Threat Model (3D) | `layer2/security_sublayer/adaptive_threat_model.py` | 🟡 v1 heuristic built & validated; GRPO/Kaggle pending |
| Shared Parsing Utility | `utils/parsing.py` | ✅ Built & tested |
| Tool Response Screener | `layer3/tool_response_screener.py` | ✅ Built & wired |
| Permission Control | `layer4/permission_control.py` | ✅ Built & tested |
| Network Egress Filter | `layer4/network_egress_filter.py` | ✅ Built & tested |
| Docker Sandbox | `layer4/sandbox.py` | ✅ Built & wired (gated execution) |
| Telemetry Stream | `layer4/telemetry_stream.py` | ✅ Built & tested |
| Full Pipeline | `adaptishield_pipeline.py` | ✅ Built & validated |
| Red Team Module | `red_team/` | ✅ v1 built & validated |
| Evaluation Framework | `evaluation/` | 🔲 Pending |
| Layer 5 (Dashboard/Console) | `layer5/` | 🔲 Pending |
| Unit tests | `tests/` | 🔲 Pending |

---

## 6. What Is Implemented and Validated

### Full pipeline (3-case validation)
`adaptishield_pipeline.py` routes each request through L1 → L3 screen → 3A → 3B → 3C → L4 → telemetry. Validated on three cases:

| Case | Scenario | Result |
| :--- | :--- | :--- |
| Benign low-impact (`get_weather`) | expect approve | ✅ `approved_direct`, severity 0 — **sandbox executed the command** in an isolated container |
| Malicious high-impact (`send_email` + IPI) — **true positive** | expect takeover | ✅ `Takeover=True` → sanitizer removed 4 instruction types → safe action derived → L4 independently blocked out-of-scope tool + exfil destination |
| Benign high-impact (`send_email`, no injection) — **true negative** | expect no takeover | ✅ `approved_causal`, `Takeover=False` |

### Layer 4 — gated Docker sandbox
`layer4/sandbox.py` is wired into `_run_layer4()`. A supplied `command` runs in a short-lived, memory/CPU-limited, network-disabled container **only if Permission Control and the Egress Filter both pass** — so the sandbox stays defense-in-depth, never an unconditional executor. Telemetry gained a `sandbox_result` field. Requires the `docker` SDK + daemon + `python:3.10-slim` image (already pulled).

### Red Team Module (v1)
Four stages — Attack Generator → Execution Agent → Evaluator → Optimizer — run against the live pipeline (dry-run, no side effects) and save ASR/FPR/WCR reports to `logs/red_team_runs/`. Four attack families of increasing subtlety: `blunt_override`, `important_instructions` (AgentDojo-style), `tool_knowledge_injection`, `masked_hypothetical`.

**Key finding:** a keyword-softened generation-2 pass dropped 3B's causal-detection rate (`caught_by_causal`) from **2/4 to 0/4** across all families — ASR stayed 0% only because the static egress allowlist caught the attacks. This is concrete, reproducible evidence that 3B's fixed thresholds don't generalize to paraphrased injections — exactly the gap Component 3D exists to close.

### Component 3D — Adaptive Threat Model (v1 local heuristic)
`layer2/security_sublayer/adaptive_threat_model.py` implements the closed adaptive loop, CPU-only (no torch), so it can be validated on the 4 GB machine:
- **GRPO reward, exactly per spec:** `+1.0` malicious→blocked/safe-continuation, `+0.8` benign→approved, `−1.0` malicious→approved (a 3B miss), `−0.5` benign→blocked (false positive).
- **`propose_update()`** lowers `CausalAnalyzer.ie_threshold` when attacks are missed, raises it on false positives, and surfaces candidate `blocked_patterns` / `high_impact_tools`. Updates only the static knobs of 3A/3B — **never LLM weights**.
- **Human-in-the-loop:** `apply_update()` refuses unless `approved=True`.
- **Labeled data:** telemetry has no ground-truth label, so 3D trains on labeled red-team `ExecutionResult`s (`from_execution_results()`) or replays telemetry with a `boundary_index → is_malicious` map (`load_labeled_from_jsonl()`).

**Validation:** on a batch mirroring the gen-2 campaign (4 softened attacks 3B missed), mean reward = **−0.40** and 3D proposed `ie_threshold 0.5 → 0.4`, recovered the softened markers (`"share"`, `"share copies of"`), nominated `send_email` as high-impact, refused to apply without approval, then committed on approval.

**Limitation (open):** the softened *phrasing* that evades 3B lives in mediator content, which the current `EpisodeRecord` schema does not store. 3D learns it here only because the red-team supplies `flagged_markers`. Recording the screener's matched markers / a mediator snippet in `telemetry_stream.py` would let 3D learn paraphrases from live traffic too.

---

## 7. Key Design Decisions

- **numpy pinned to `1.26.4`** — numpy 2.x is incompatible with Python 3.10.12. Treat `requirements.txt` as the source of truth (`installed.txt` shows drift).
- **Per-component model split** — 3B (Causal Analyzer) runs `gemma3:4b` because it *complies* with injections under the masked probe, producing a measurable causal signal; the Context Sanitizer, Screener, and planner run `qwen2.5:3b` for stronger baseline resistance. Do **not** reduce 3B's `k_samples` below 2 without re-validating.
- **Keyword backstop in the Screener** — small local models sometimes write a correct diagnosis in prose while emitting the wrong structured verdict, so a response is flagged if *either* the LLM or a deterministic keyword check fires. Keep permanently.
- **Layer 4 is defense-in-depth** — permission, egress, and sandbox each gate independently of the 3A/3B/3C verdict; the sandbox executes only when the other two gates pass.
- **3D never touches LLM weights** and is human-gated — it tunes Policy Engine rules and Causal Analyzer thresholds only, and proposals require explicit approval before they apply.
- **3D trains on labeled data, never inferred labels** — a reward needs ground truth; inferring "was this an attack?" from the outcome would be circular.
- **GPU-heavy work goes to Kaggle** — the local 4 GB card cannot host GRPO training or 7B+ models; the pipeline itself runs locally.

---

## 8. Package Versions

> `numpy==1.26.4` is a hard pin (numpy 2.x breaks on Python 3.10.12).

```text
fastapi==0.115.5        uvicorn==0.32.1         langchain==0.3.7
langchain-community==0.3.7   langgraph==0.2.53   langchain-ollama==0.2.1
httpx==0.27.2           pydantic==2.10.3        python-dotenv==1.0.1
chromadb==0.5.23        sqlalchemy==2.0.36      psycopg2-binary==2.9.10
prometheus-client==0.21.1    cryptography==44.0.0    numpy==1.26.4
pandas==2.2.3           matplotlib==3.9.3       pytest==8.3.4
pytest-asyncio==0.24.0  rich==13.9.4            docker
```

```bash
cd ~/adaptishield && source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
python3 -c "import langchain, fastapi, chromadb, docker; print('All packages OK')"
```

---

## 9. Models in Use

| Model | VRAM | Role |
| :--- | :--- | :--- |
| **gemma3:4b** | ~3.5 GB | Causal Analyzer (3B) — complies under masked probe, giving real causal divergence |
| **qwen2.5:3b** | ~2 GB | Context Sanitizer, Tool Response Screener, planner LLM |
| **gemma2:9b** | CPU | Fallback for 3B if `gemma3:4b` proves insufficiently sensitive at scale |

Rejected: `llama3.2:3b` (poor security reasoning), any 7B+ GPU model (exceeds 4 GB VRAM).

---

## 10. Compute Strategy

| Task | Platform | Reason |
| :--- | :--- | :--- |
| Writing/debugging, pipeline logic, red-team campaigns | Local | Fast, free, offline |
| GRPO/RL training (3D) | Kaggle P100 | Needs torch + ≥16 GB VRAM |
| Red-team dataset generation at scale | Kaggle | Speed |
| Full benchmark (ASR/FPR/WCR) | Kaggle | Reproducible, logged |

> Kaggle cannot host a live MCP server — it is for training/evaluation only. The pipeline runs locally.

---

## 11. How to Run

```bash
cd ~/adaptishield
source venv/bin/activate
ollama serve &
sleep 2
ollama list                                                 # confirm qwen2.5:3b and gemma3:4b

# per-component self-tests
python3 layer0/server_trust_registry.py
python3 layer1/provenance.py
python3 layer2/security_sublayer/policy_engine.py
python3 layer3/tool_response_screener.py
python3 layer4/permission_control.py
python3 layer4/network_egress_filter.py
python3 layer4/telemetry_stream.py

# end-to-end
python3 adaptishield_pipeline.py                            # full pipeline, 3 validated cases
python3 -m red_team.run_campaign                            # red-team campaign (gen1 + gen2)
python3 -m layer2.security_sublayer.adaptive_threat_model   # 3D reward + proposal demo (no LLM/GPU)
```

---

## 12. Testing Checklist

| Test | Command | Expected |
| :--- | :--- | :--- |
| Server Trust Registry | `python3 layer0/server_trust_registry.py` | legit `True`, rug-pull `False` |
| Provenance tagging | `python3 layer1/provenance.py` | trusted + mediator partitions |
| Policy Engine | `python3 layer2/security_sublayer/policy_engine.py` | approve_direct / send_to_causal / block |
| Tool Response Screener | `python3 layer3/tool_response_screener.py` | clean vs FLAGGED |
| Permission Control | `python3 layer4/permission_control.py` | in-scope `True`, out-of-scope `False` |
| Egress Filter | `python3 layer4/network_egress_filter.py` | allowlisted `True`, else `False` |
| Telemetry Stream | `python3 layer4/telemetry_stream.py` | episode appended to JSONL |
| Full pipeline | `python3 adaptishield_pipeline.py` | approved_direct · safe_continuation (Takeover=True) · approved_causal |
| Red team campaign | `python3 -m red_team.run_campaign` | ASR=0%/FPR=0%/WCR=50%; gen-2 `caught_by_causal` drops to 0/4 |
| Component 3D | `python3 -m layer2.security_sublayer.adaptive_threat_model` | mean reward −0.40; proposes `ie_threshold 0.5→0.4`; apply gated on approval |

---

## 13. What to Build Next

### Immediate — close the adaptive loop (the headline thesis result)
- [ ] Apply a 3D proposal, re-run the red-team campaign, and confirm the previously-missed softened attacks are now caught by 3B (ASR / `caught_by_causal` before vs after). This is the single most valuable next experiment.
- [ ] Add the screener's matched markers / a mediator snippet to `EpisodeRecord` so 3D can learn paraphrased patterns from live telemetry, not just red-team `flagged_markers`.

### Short term — Component 3D real training
- [ ] Replace the v1 heuristic inside `propose_update()` with the real GRPO/RL loop (torch); train on Kaggle P100. Keep the same reward function and `LabeledEpisode → ProposedUpdate → apply_update` contract.
- [ ] Scale red-team campaigns up (more directives/targets/families); move bulk runs to Kaggle.

### Later
- [ ] `evaluation/` — eight attack vectors (Du et al. / MCPSecBench), static baseline vs full AdaptiShield vs AdaptiShield+3D, on Kaggle. Reuse `red_team/evaluator.py` for the metrics.
- [ ] `layer5/` — Audit Dashboard, Policy Inspection Console, Manual Override, Audit Logs (data already emitted by telemetry + campaigns).
- [ ] `tests/` — pytest suite; the 3 validated pipeline episodes are natural regression cases.

---
**AdaptiShield — v9 current-state handover**
*Muhammad Ahmad Khan (23JZBCS0238) · Aleena Khan (23JZBCS0229) · Supervisor: Dr. Laeeq Ahmed · UET Peshawar (Jalozai Campus)*
