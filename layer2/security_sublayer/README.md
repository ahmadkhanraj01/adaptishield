# Layer 2 — Security and Adaptive Sub-layer (3A → 3B → 3C → 3D)

**Status:** 🟡 3A / 3B / 3C ✅ built & validated · 3D 🔲 pending

## Purpose
The heart of AdaptiShield. Each tool-return boundary flows through this
chain: policy screening → causal attribution → sanitization → (eventually)
adaptive learning. It decides whether a proposed action is safe, driven by
a hidden injection, and how to continue safely if it is.

## Files
| Stage | File | Purpose | Status |
| :--- | :--- | :--- | :--- |
| **3A** | `policy_engine.py` | Fast deterministic triage — blocks known bad patterns, routes high-impact tools to causal analysis, fast-paths low-impact ones. | ✅ Built and tested |
| **3B** | `causal_analyzer.py` | Runs the mediator content through 4 regimes (`orig`, `masked`, `masked_sanitized`, `orig_sanitized`) and computes ACE / IE / DE to detect mediator-driven **takeover**. Uses `gemma3:4b`, `k_samples=2`. | ✅ Built, tested, validated (see root README Section 5) |
| **3C** | `context_sanitizer.py` | When 3B confirms takeover, strips imperative/override/hidden directives from mediator content while preserving facts, so the agent can safely continue. | ✅ Built and tested |
| **3D** | `adaptive_threat_model.py` | **Does not exist yet.** GRPO learner that ingests episode records and tunes 3A patterns + 3B thresholds. | 🔲 Pending |
| — | `__init__.py` | Package marker | ✅ |

## What's done
- Full 3A→3B→3C chain validated end-to-end on true-positive **and**
  true-negative cases (root README Section 5).
- 3B's masked-regime investigation is closed; `gemma3:4b` chosen
  specifically because it complies with injections under `masked`, giving a
  measurable causal signal.

## What's pending — Component 3D (the "adaptive" in the project title)
- `adaptive_threat_model.py` — GRPO reward: `+1.0` correct block/safe
  continuation, `+0.8` correct pass, `−1.0` missed attack, `−0.5` false
  positive.
- Ingests `logs/episode_records/episodes.jsonl` (now includes red-team
  campaign episodes).
- Updates `PolicyEngine.blocked_patterns` / `high_impact_tools` and
  `CausalAnalyzer` thresholds only — **no LLM weight updates**.
- Train on Kaggle P100.
- **Motivating evidence:** the red-team campaign showed keyword-softened
  attacks drop 3B's `caught_by_causal` rate from 2/4 to 0/4 — exactly the
  generalization gap 3D is meant to close (root README Section 5c).

## Run standalone
```bash
python3 layer2/security_sublayer/policy_engine.py     # approve_direct / send_to_causal / block
# 3B and 3C are exercised through adaptishield_pipeline.py
```
