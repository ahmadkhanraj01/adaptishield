---
tags: [adaptishield, reference]
type: reference
---

# Test Suite

**135 deterministic tests, ~2 seconds, no LLM / network / GPU.**

| File | n | Covers |
| :--- | :--- | :--- |
| `test_takeover_rules.py` | 9 | [[Takeover Rule Stack]] paths + IE resolution |
| `test_adaptive_threat_model.py` | 14 | 3D reward + proposal + step sizing; the [[6j-6k — The Loop Closes a Matching Gap]] demonstration |
| `test_target_match.py` | 21 | Normalized target match + keyword grounding ([[6m — The Single-Character Defect]], [[6p — Probe Hallucination Fixed at the Scorer]]) |
| `test_probe_diagnostic.py` | 11 | Root-cause tool **+ classifier ordering** (the instrument's own bug) |
| `test_corpus.py` | 22 | Corpus invariants, Wilson, IE-ablation join |
| `test_grpo_kaggle.py` | 23 | GRPO env/trainer + joint space + **no-op guard** |
| `test_layer5.py` | 20 | Human gate + dashboard escaping |
| `test_ablation.py` | 15 | Phase 7 arms + campaign checkpointing |

## The division of labour

🟡 **Deterministic decision logic → `tests/`** — the four probe regimes are
patched out, so no Ollama, sub-second.

🟡 **LLM-dependent checks → `evaluation/`** — minutes, vary run-to-run. **Record
their numbers in the docs; never assert on them.**

## What the suite exists to protect

Every entry in [[Fixes A-D]] and every invariant in [[Rules and Invariants]] is
pinned here — explicitly **so that subsequent training work cannot silently
regress them**. The suite is torch-free by design so it can run on every edit,
which is also what let the torch backend go unexecuted for two entire phases →
[[6o — Phase 6 Executed on Kaggle]].

The 3 validated pipeline episodes are natural regression cases and were the seed
of Phase 9.

## Growth

8 → 22 (after [[Fixes A-D]]) → 23 → 37 → 110 → **135**.
