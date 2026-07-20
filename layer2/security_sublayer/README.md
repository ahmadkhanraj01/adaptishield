# Layer 2 — Security and Adaptive Sub-layer (3A → 3B → 3C → 3D)

**Status:** ✅ 3A / 3B / 3C built & validated · 🟡 3D v1 (local heuristic) built & validated; GRPO training on Kaggle pending

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
| **3D** | `adaptive_threat_model.py` | Adaptive learner. Computes the GRPO reward, then proposes bounded updates to `PolicyEngine.blocked_patterns`/`high_impact_tools` and `CausalAnalyzer.ie_threshold` (no LLM weights). **v1 is a CPU-only heuristic** that validates the loop locally; the real GRPO training loop (Kaggle P100) will swap into `propose_update()` behind the same reward + I/O contract. | 🟡 v1 built & validated |
| — | `__init__.py` | Package marker | ✅ |

## What's done
- Full 3A→3B→3C chain validated end-to-end on true-positive **and**
  true-negative cases (root README Section 5).
- 3B's masked-regime investigation is closed; `gemma3:4b` chosen
  specifically because it complies with injections under `masked`, giving a
  measurable causal signal.

## Component 3D — what's done (v1 local heuristic)
- GRPO reward implemented exactly per spec: `+1.0` correct block/safe
  continuation, `+0.8` correct pass, `−1.0` missed attack, `−0.5` false
  positive.
- `propose_update()` turns the reward signal into a bounded, directional
  update — lowers `ie_threshold` when attacks are missed, raises it on false
  positives, and surfaces candidate `blocked_patterns` / `high_impact_tools`
  from missed attacks.
- **Human-in-the-loop:** `apply_update(..., approved=True)` is required to
  mutate the live engines (matches `PolicyEngine.update_rules()`'s "after
  human approval" contract). 3D proposes; Layer 5 disposes.
- Adapters: `from_execution_results()` (labeled red-team data) and
  `load_labeled_from_jsonl()` (replay stored telemetry with a labels map).
- Validated locally, CPU-only, no torch: on a batch mirroring the gen-2
  campaign (4 softened attacks 3B missed), mean reward = −0.4 and 3D
  proposes `ie_threshold 0.5 → 0.4`, recovering the softened markers
  (`"share"`, `"share copies of"`) that evaded 3B.

## Component 3D — what's pending
- Replace the v1 heuristic inside `propose_update()` with the real GRPO/RL
  training loop; train on Kaggle P100 (needs torch + GPU, can't run on the
  local 4GB card). The reward function and I/O contract stay the same.
- **Telemetry-schema limitation:** the softened *phrasing* that evades 3B
  lives in mediator content, which the current `EpisodeRecord` schema does
  not store. 3D learns it here only because the red-team supplies
  `flagged_markers`. Recording the screener's matched markers / a mediator
  snippet in telemetry would let 3D learn paraphrases from live traffic too
  (root README Section 5d).

## Run standalone
```bash
python3 layer2/security_sublayer/policy_engine.py           # approve_direct / send_to_causal / block
python3 -m layer2.security_sublayer.adaptive_threat_model   # 3D reward + proposal demo (no LLM/GPU)
# 3B and 3C are exercised through adaptishield_pipeline.py
```
