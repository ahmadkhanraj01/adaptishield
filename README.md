# AdaptiShield — Session Handover Document

**Project:** Adaptive Threat Modeling for Tool-Orchestrated LLM Systems in MCP Architectures  
**Supervisor:** Dr. Laeeq Ahmed  
**Students:** Muhammad Ahmad Khan (23JZBCS0238) · Aleena Khan (23JZBCS0229)  
**Department:** CS&IT — University of Engineering and Technology Peshawar (Jalozai Campus)  
**Handover Date:** July 2026 (v5 — consolidated, supersedes v4)  

> **Note:** This is the single source of truth. All earlier versions (v1–v4) have been merged and superseded — do not reference them separately. v5 closes out the Causal Analyzer masked-regime investigation opened in v4 with a confirmed, validated fix.

---

## Table of Contents
1. [Machine Specifications](#1-machine-specifications)
2. [Architecture Overview](#2-architecture-overview)
3. [Current Directory Structure (Verified)](#3-current-directory-structure-verified)
4. [Build Status by Component](#4-build-status-by-component)
5. [Resolved — Causal Analyzer Masked Regime Investigation](#5-resolved--causal-analyzer-masked-regime-investigation)
6. [Verified Package Versions](#6-verified-package-versions)
7. [Model Selection — Final Decision](#7-model-selection--final-decision)
8. [Compute Strategy](#8-compute-strategy)
9. [How to Start the Project Fresh](#9-how-to-start-the-project-fresh)
10. [Testing Checklist and Expected Outputs](#10-testing-checklist-and-expected-outputs)
11. [What to Build Next](#11-what-to-build-next)
12. [Key Lessons Learned](#12-key-lessons-learned)

---

## 1. Machine Specifications

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

## 2. Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────┐
│  Layer 5 — Human-in-the-Loop & Observability                     │
│  Audit Dashboard · Policy Inspection Console · Manual Override   │
├──────────────────────────────────────────────────────────────────┤
│  Red Team Module                                                  │
│  Attack Generator · Execution Agent · Evaluator · Optimizer      │
├──────────────────────────────────────────────────────────────────┤
│  Layer 4 — Sandbox and Isolation                                  │
│  gVisor Sandbox · Permission Control · Network Egress Filter     │
│  Telemetry Stream                                                 │
├──────────────────────────────────────────────────────────────────┤
│  Layer 3 — MCP Tool Execution Plane                               │
│  APIs · Databases · File Systems · Tool Response Screener        │
├──────────────────────────────────────────────────────────────────┤
│  Layer 2 — LLM Agent Control Plane                                │
│  Planner Agent · Tool Selector · Execution Agent                 │
│  Feedback Analyzer                                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Security and Adaptive Sub-layer  (3A → 3B → 3C → 3D)    │  │
│  │  3A  Policy Engine                                         │  │
│  │  3B  Causal Analyzer                                       │  │
│  │  3C  Context Sanitizer                                     │  │
│  │  3D  Adaptive Threat Model (GRPO)                          │  │
│  └────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│  Layer 1 — Input and Supply Chain Screening                       │
│  Input Parser · Supply Chain Scanner · Context Builder           │
│  Provenance Memory Store                                          │
├──────────────────────────────────────────────────────────────────┤
│  Layer 0 — MCP Transport and Server Trust                         │
│  Transport Integrity Verifier · Server Trust Registry            │
│  Schema Validator · Name Squatting Guard                          │
└──────────────────────────────────────────────────────────────────┘
```

### Evaluation Metrics

| Metric | Description | Target |
| :--- | :--- | :--- |
| **ASR (Attack Success Rate)** | Fraction of attacks that fully execute | Lower is better |
| **FPR (False Positive Rate)** | Fraction of benign actions incorrectly blocked | Lower is better |
| **WCR (Workflow Continuation Rate)** | Fraction of adversarial trials where the legitimate task still completes | Higher is better |

---

## 3. Current Directory Structure (Verified)

```text
~/adaptishield/
├── requirements.txt
├── dir.py                             (personal use — prints directory tree)
├── findkey.py                         (personal use — greps a keyword across all files)
├── .gitignore
├── adaptishield_pipeline.py           ✅ Built, routes through L1→L3→3A→3B→3C→L4, emits telemetry
├── README.md
├── installed.txt
│
├── layer0/
│   ├── __init__.py
│   └── server_trust_registry.py       ✅ Built and tested
│
├── layer1/
│   ├── __init__.py                    ✅ added
│   └── provenance.py                  ✅ Built and tested; ContextBuilder.reset() added
│
├── layer2/
│   ├── __init__.py
│   └── security_sublayer/
│       ├── __init__.py
│       ├── policy_engine.py           ✅ Built and tested
│       ├── causal_analyzer.py         ✅ Built, tested, validated — see Section 5
│       ├── context_sanitizer.py       ✅ Built and tested
│       └── adaptive_threat_model.py   🔲 Pending
│
├── layer3/
│   ├── __init__.py
│   └── tool_response_screener.py      ✅ Built, wired into pipeline; keyword backstop added
│
├── layer4/
│   ├── __init__.py
│   ├── sandbox.py                     ✅ Built (Docker-based; needs `pip install docker` + daemon), not yet wired into pipeline
│   ├── permission_control.py          ✅ Built and tested
│   ├── network_egress_filter.py       ✅ Built and tested
│   └── telemetry_stream.py            ✅ Built and tested — writes JSONL episodes
│
├── layer5/                            🔲 empty — pending
├── red_team/                          🔲 empty — pending
├── evaluation/                        🔲 empty — pending
├── utils/
│   ├── __init__.py                    ✅ added (moved to project root — see Section 5)
│   └── parsing.py                     ✅ shared tolerant NEXT: parser, used by 3B and pipeline's 3C safe-continuation step
├── logs/
│   └── episode_records/
│       └── episodes.jsonl             ✅ populated on each pipeline run — 3 validated episodes as of this handover
└── tests/                             🔲 empty — pending
```

---

## 4. Build Status by Component

| Component | File | Status |
| :--- | :--- | :--- |
| **Server Trust Registry** | `layer0/server_trust_registry.py` | ✅ Built and tested |
| **Provenance Tagging** | `layer1/provenance.py` | ✅ Built and tested (+ reset() fix) |
| **Policy Engine (3A)** | `layer2/security_sublayer/policy_engine.py` | ✅ Built and tested |
| **Causal Analyzer (3B)** | `layer2/security_sublayer/causal_analyzer.py` | ✅ Built, tested, validated on true-positive and true-negative cases |
| **Context Sanitizer (3C)** | `layer2/security_sublayer/context_sanitizer.py` | ✅ Built and tested — accurate `instructions_removed` reporting confirmed |
| **Shared Parsing Utility** | `utils/parsing.py` | ✅ Built and tested — single source of truth for tolerant `NEXT:` extraction |
| **Tool Response Screener** | `layer3/tool_response_screener.py` | ✅ Built, wired into pipeline |
| **Permission Control** | `layer4/permission_control.py` | ✅ Built and tested |
| **Network Egress Filter** | `layer4/network_egress_filter.py` | ✅ Built and tested |
| **Telemetry Stream** | `layer4/telemetry_stream.py` | ✅ Built and tested — writes JSONL episodes |
| **Docker Sandbox** | `layer4/sandbox.py` | ✅ Built, not yet wired into `_run_layer4` for real command execution |
| **Full Pipeline** | `adaptishield_pipeline.py` | ✅ Built and validated — L1 → L3 screen → 3A → 3B → 3C → L4 → telemetry, three-way test coverage confirmed |
| **Adaptive Threat Model (3D)**| `layer2/security_sublayer/adaptive_threat_model.py`| 🔲 Pending |
| **Red Team Module** | `red_team/` | 🔲 Pending |
| **Evaluation Framework** | `evaluation/` | 🔲 Pending |
| **Layer 5 (Dashboard/Console)**| `layer5/` | 🔲 Pending |
| **Unit tests** | `tests/` | 🔲 Pending |

---

## 5. Resolved — Causal Analyzer Masked Regime Investigation

The open question from v4 (whether `masked` regime returning `'no_action'` was a genuine model finding or an unlanded code fix) is now **closed**. Full resolution path documented below.

### Bug chain fixed this session (in order)

1. **`ScreenResult.flagged` → `.is_flagged`** — attribute name mismatch in pipeline, fixed.
2. **Missing `import re` and `from typing import Tuple`** in `tool_response_screener.py` — fixed.
3. **LLM verdict/reasoning disagreement in the screener** — the LLM sometimes writes a correct diagnosis in `REASON:` text while still emitting `FLAGGED: no`. Fixed with a deterministic keyword backstop (`KEYWORD_MARKERS`) that flags independently of the LLM — a response is flagged if either check fires. **Keep permanently.**
4. **`ContextBuilder` never reset between requests** — `trusted_prefix`/`mediator_view` accumulated across calls, corrupting later test cases with earlier ones' content. Fixed with `ContextBuilder.reset()` called at the top of `process_request()`. This was the true root cause of the original "all severities = 0" symptom.
5. **`_score_action` keyword scoring too coarse** — added `_extract_suspicious_targets()` (regex-extracts emails/URLs from mediator content) so scoring checks whether the proposed action references a specific exfiltration target, not just generic verbs.
6. **Word-boundary bug in `_score_action`** — plain substring matching meant `"forward" in "no forwarding of emails"` → `True`, so refusals containing "forwarding" scored as if they complied. Fixed with `\b`-anchored regex matching (`re.search(rf"\b{re.escape(k)}\b", a)`).
7. **`_extract_next_action`'s markdown-stripping regex ate legitimate underscores** — `re.sub(r"[*_`#>-]", ...)` was meant to strip markdown emphasis but also corrupted plain content like `task_complete` → `taskcomplete`. Fixed by dropping `_` from the strip set: `re.sub(r"[*`#>-]", ...)`.
8. **Three separate ad-hoc `NEXT:` parsers (3B, pipeline's safe-continuation step) were fragile and duplicated** — consolidated into a single `utils/parsing.py::extract_next_action()`, imported by both call sites. First landed in the wrong location (`layer2/security_sublayer/utils/`) due to a relative-path assumption; corrected to project root (`~/adaptishield/utils/`) so the pipeline's absolute import resolves correctly.
9. **Pipeline's 3C safe-continuation prompt lacked format constraints and used a naive `.split("NEXT:", 1)`** — leaked model meta-commentary (e.g. "I have disregarded the harmful instruction...") straight into the safe action string. Fixed by tightening the prompt ("no commentary, no markdown") and switching to `extract_next_action()`.
10. **Incremental patches silently not landing on disk (two separate incidents)** — resolved by adopting "verify with `cat -n` before patching again" as standing practice for the rest of the session; the practice caught a real unlanded-patch case (the pipeline's 3C block still had old code even after the diff was described as applied).

### Root cause of the original `masked` = `'no_action'` finding

Confirmed via raw-response logging (`[3B-RAW]` prints added to `_run_regime_once`): the code was correct the entire time. `qwen2.5:3b` **genuinely refuses to comply** with the injected instruction even under a hypothetical "state the action you would take" framing — not a parsing bug, a real small-model behavior. This is itself a legitimate finding about masked-probe design robustness varying by model size, but it meant `qwen2.5:3b` produced no compliance anywhere in the pipeline (`orig` also refused), so ACE/IE had no true-positive signal to validate against.

### Resolution: switched Causal Analyzer to `gemma3:4b`

`gemma3:4b` **does** comply with the same injected payload under `masked`, producing the first genuine causal divergence: mediator-driven compliance (`masked` severity 2) vs. user-frame-suppressed refusal (`orig` severity 0–1). This unblocked validation of the full 3B → 3C → L4 chain.

### Validated three-episode test suite (current state of `adaptishield_pipeline.py` `__main__`)

| Episode | Scenario | Expected | Actual Result |
| :--- | :--- | :--- | :--- |
| **1** | Benign low-impact (`get_weather`) | `approved_direct` | ✅ `approved_direct`, severity=0 |
| **2** | Malicious high-impact (`send_email` + IPI payload) — **true positive** | `Takeover=True` → `safe_continuation` | ✅ `ACE=-1, IE=2, DE=0, Takeover=True` → sanitizer removed 4 instruction types → safe action correctly derived from purified content → L4 independently blocked out-of-scope tool + non-allowlisted egress destination |
| **3** | Benign high-impact (`send_email`, no injection) — **true negative** | `Takeover=False` → `approved_causal` | ✅ `ACE=0, IE=0, DE=0, Takeover=False` → `approved_causal` |

This gives defensible evidence that 3A/3B/3C/L4 work together correctly on both a true-positive and true-negative case, with L4 demonstrating independent defense-in-depth (blocking the exfiltration attempt on its own merits regardless of the 3B/3C verdict).

### Known remaining nondeterminism (not a bug, documented for awareness)

`gemma3:4b` gives slightly different phrasing/format between reruns of the same test case (e.g. the safe-continuation response once produced `'NEXT: task_complete'`, another time produced filler text with no `NEXT:` line at all, correctly caught by the fallback). `k_samples=2` averaging in the Causal Analyzer absorbs this; **do not reduce `k_samples` below 2** without re-validating, as this would increase ACE/IE noise.

---

## 6. Verified Package Versions

> **Critical:** `numpy` must be pinned to `1.26.4`. `numpy` 2.x is incompatible with Python 3.10.12. `installed.txt` in the repo shows drift (e.g. `numpy==2.2.6`, `langchain==1.3.4`) — reconcile against `requirements.txt` (source of truth) before the next dependency install.

**`requirements.txt`**
```text
fastapi==0.115.5
uvicorn==0.32.1
langchain==0.3.7
langchain-community==0.3.7
langgraph==0.2.53
langchain-ollama==0.2.1
httpx==0.27.2
pydantic==2.10.3
python-dotenv==1.0.1
chromadb==0.5.23
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
prometheus-client==0.21.1
cryptography==44.0.0
numpy==1.26.4
pandas==2.2.3
matplotlib==3.9.3
pytest==8.3.4
pytest-asyncio==0.24.0
rich==13.9.4
docker
```

**Install Commands:**
```bash
cd ~/adaptishield
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 -c "import langchain; import fastapi; import chromadb; import docker; print('All packages OK')"
```

---

## 7. Model Selection — Final Decision

| Model | VRAM | Speed | Quality | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **qwen2.5:3b** | ~2GB | Fast (~1-2s) | Good, but over-resistant to injections even under hypothetical framing | ✅ Primary for Context Sanitizer, Tool Response Screener, planner LLM |
| **gemma3:4b** | ~3.5GB | Fast (~1-2s) | Very Good — complies with injections under `masked` regime, enabling real causal divergence | ✅ **Primary for Causal Analyzer (3B) as of this handover** |
| **gemma2:9b** | 0GB (CPU) | Slow (~30-45s) | Excellent | ✅ Fallback for Causal Analyzer if `gemma3:4b` proves insufficiently sensitive at scale |
| **llama3.2:3b** | ~2GB | Fast | Poor on security | ❌ Rejected — misinterpreted "prompt injection" as cosmetic surgery |
| **llama3.2 (8B) / deepseek-r1:8b** | ~5-6GB | — | — | ❌ Exceeds VRAM |

> **Per-component assignment (current):** `causal_analyzer = CausalAnalyzer(model_name="gemma3:4b", k_samples=2)`; `context_sanitizer`, `tool_screener`, and `planner_llm` remain on `qwen2.5:3b`. This split is deliberate — 3B needs a model susceptible enough to injection to produce a measurable signal for detection, while 3C/screener/planner benefit from `qwen2.5:3b`'s stronger baseline resistance.

---

## 8. Compute Strategy

| Task | Platform | Reason |
| :--- | :--- | :--- |
| **Writing/debugging code** | Local | Instant feedback, offline |
| **Pipeline logic testing** | Local `qwen2.5:3b` / `gemma3:4b` | Fast, free |
| **GRPO/RL training (3D)** | Kaggle P100 | Needs 16GB VRAM |
| **Red team dataset generation at scale**| Kaggle | Speed |
| **Full benchmark (ASR/FPR/WCR)** | Kaggle | Reproducible, logged |

> **Note:** Kaggle cannot host a live MCP server — used purely for training/evaluation. The full pipeline runs locally.

---

## 9. How to Start the Project Fresh

```bash
cd ~/adaptishield
source venv/bin/activate
ollama serve &
sleep 2
ollama list                          # confirm qwen2.5:3b and gemma3:4b are present

python3 layer0/server_trust_registry.py
python3 layer1/provenance.py
python3 layer2/security_sublayer/policy_engine.py
python3 layer3/tool_response_screener.py
python3 layer4/permission_control.py
python3 layer4/network_egress_filter.py
python3 layer4/telemetry_stream.py
python3 adaptishield_pipeline.py
```

> **Standing practice:** before patching any file that has been edited more than once in a session, run `cat -n <file>` first to confirm on-disk state. This caught at least two real bugs this session where a described change hadn't actually landed.

---

## 10. Testing Checklist and Expected Outputs

| Test | Command | Expected Output |
| :--- | :--- | :--- |
| **Server Trust Registry — legitimate** | `python3 layer0/server_trust_registry.py` | `True` — Verified |
| **Server Trust Registry — rug-pull** | *same* | `False` — RUG-PULL DETECTED |
| **Provenance tagging** | `python3 layer1/provenance.py` | Prints trusted and mediator partitions |
| **Policy Engine — low impact** | `python3 layer2/security_sublayer/policy_engine.py` | `approve_direct` |
| **Policy Engine — high impact** | *same* | `send_to_causal` |
| **Policy Engine — injection pattern**| *same* | `block` |
| **Tool Response Screener — clean** | `python3 layer3/tool_response_screener.py` | `is_flagged=False` |
| **Tool Response Screener — IPI** | *same* | `is_flagged=True` (via keyword and/or LLM) |
| **Permission Control — in-scope** | `python3 layer4/permission_control.py` | `allowed=True` |
| **Permission Control — out-of-scope**| *same* | `allowed=False` |
| **Egress Filter — allowlisted** | `python3 layer4/network_egress_filter.py` | `allowed=True` |
| **Egress Filter — non-allowlisted** | *same* | `allowed=False` |
| **Telemetry Stream** | `python3 layer4/telemetry_stream.py` | Episode logged to `logs/episode_records/episodes.jsonl` |
| **Full pipeline — Episode 1 (benign low-impact)** | `python3 adaptishield_pipeline.py` | `approved_direct` ✅ confirmed |
| **Full pipeline — Episode 2 (malicious high-impact, true positive)**| *same* | `safe_continuation`, `Takeover=True` ✅ confirmed |
| **Full pipeline — Episode 3 (benign high-impact, true negative)**| *same* | `approved_causal`, `Takeover=False` ✅ confirmed |

---

## 11. What to Build Next

### Immediate
- [ ] Inspect `logs/episode_records/episodes.jsonl` to confirm all three validated episodes serialized with accurate `causal_verdict` / `sanitization_decision` fields — this is the data Component 3D will eventually train on
- [ ] Wire `layer4/sandbox.py` into `_run_layer4()` for real command execution (currently only Permission Control + Egress Filter are invoked; Sandbox exists standalone but isn't called from the pipeline)

### Short term
- [ ] `layer2/security_sublayer/adaptive_threat_model.py` — Component 3D
  - GRPO reward: +1.0 correct block/safe continuation, +0.8 correct pass, −1.0 missed attack, −0.5 false positive
  - Ingests Episode Records from `logs/episode_records/episodes.jsonl`
  - Updates `PolicyEngine.blocked_patterns`/`high_impact_tools` and `CausalAnalyzer` thresholds only — no LLM weight updates
  - Train on Kaggle P100
- [ ] `red_team/` — Attack Generator → Execution Agent (dry-run) → Evaluator Agent (ASR/FPR/WCR) → Optimizer Agent
  - Use the validated true-positive payload style (blunt "IGNORE PREVIOUS INSTRUCTIONS") as a baseline, then expand to subtler AgentDojo-style "Important Instructions"/"Tool Knowledge" families for a stronger benchmark

### Later
- [ ] `evaluation/` — eight attack vectors (Du et al. / MCPSecBench), static baseline vs. full AdaptiShield, run on Kaggle
- [ ] `layer5/` — Audit Dashboard, Policy Inspection Console, Manual Override, Audit Logs
- [ ] `tests/` — formal pytest suite covering all layers plus end-to-end pipeline cases (the three validated episodes in Section 5 are a natural starting point for regression tests)

---

## 12. Key Lessons Learned

| Finding | Action Taken |
| :--- | :--- |
| **llama3.2:3b cannot reason about security** — answered "prompt injection" with cosmetic surgery info | Rejected. Using `qwen2.5:3b` / `gemma3:4b` instead |
| **numpy 2.x incompatible with Python 3.10.12** | Pinned `numpy==1.26.4` in `requirements.txt` |
| **`installed.txt` shows drift from `requirements.txt`** | Reconcile before next install; treat `requirements.txt` as source of truth |
| **`layer1/` was missing `__init__.py`** | Fixed — added |
| **4GB VRAM cannot run any 7B+ model** | Models above 3–4B go on CPU (via 16GB RAM) or Kaggle |
| **Kaggle cannot host a live server/API** | Kaggle is for training and evaluation only; pipeline runs locally |
| **LLM verdict text can contradict its own structured output** | Added a deterministic keyword backstop alongside the LLM check — flag if either fires. Keep permanently. |
| **`ContextBuilder` accumulated state across unrelated requests**, corrupting Causal Analyzer input | Added `ContextBuilder.reset()`, called at top of `process_request()`. Root cause of the original "all severities = 0" symptom. |
| **Substring keyword matching produces false positives on negated phrases** (`"forward" in "no forwarding"`) | Switched to `\b`-anchored regex word-boundary matching in `_score_action` |
| **Markdown-stripping regex corrupted legitimate underscored content** (`task_complete` → `taskcomplete`) | Removed `_` from the strip character class in `extract_next_action` |
| **Duplicated, fragile `NEXT:` parsers across 3B and the pipeline's 3C step** | Consolidated into `utils/parsing.py::extract_next_action()`, single source of truth |
| **A shared utility module landed in the wrong directory relative to the importing file's working assumptions** | Corrected to project root; confirmed via `dir.py` tree output after the move |
| **Small models (`qwen2.5:3b`) may refuse an injection so completely that Causal Analyzer has no divergence to detect — not a bug, but makes the model unsuitable as the 3B backbone** | Switched Causal Analyzer specifically to `gemma3:4b`, which does comply under `masked`, enabling real ACE/IE signal. Documented as a deliberate per-component model choice, not a global model swap. |
| **Incremental patches to the same file were silently not landing** (multiple `TypeError`s traced back to code described as sent but not actually on disk) | Adopted "verify full file contents with `cat -n` before patching again" as standing practice — caught a real recurrence even after being flagged once already |

---
**AdaptiShield Handover Document — v5 (consolidated, supersedes all prior versions)**  
*Muhammad Ahmad Khan (23JZBCS0238) · Aleena Khan (23JZBCS0229)*  
*Supervisor: Dr. Laeeq Ahmed | UET Peshawar (Jalozai Campus)*