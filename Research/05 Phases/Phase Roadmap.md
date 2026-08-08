---
tags: [adaptishield, phase, hub]
type: hub
---

# Phase Roadmap

*Last updated in the repo: 2026-07-26. Rough completion: **~90%**.*

| Phase | Scope | State |
| :--- | :--- | :--- |
| **0** | Defensive pipeline (Layers 0–4, gated sandbox, telemetry) | ✅ Done |
| **1** | Security sub-layer [[3A Policy Engine]] / [[3B Causal Analyzer]] / [[3C Context Sanitizer]] | ✅ Done |
| **2** | [[Red Team Module]] (generator → agent → evaluator → optimizer) | ✅ Done |
| **3** | 3D v1 + adaptive-loop experiment | ✅ Done — **negative result** → [[6d — Adaptive Loop Negative Result]] |
| **4** | Measurement [[Fixes A-D]] | ✅ Done |
| **5** | Re-run the loop on the fixed measurement | ✅ Done — **nothing to close** |
| **5b** | Prove the loop *can* close a knob-matching gap | ✅ Done — closes **and** generalizes → [[6j-6k — The Loop Closes a Matching Gap]] |
| **6** | 3D real GRPO training | ✅ **Executed** → [[Phase 6 — GRPO on Kaggle]] |
| **6b** | Diagnose the 15 residual 3B misses | ✅ Done — one defect, **114/114** → [[6m — The Single-Character Defect]] |
| **6c** | Fix the evaluation corpus | ✅ Done → [[6n — A Corpus That Can Fail]] |
| **6d** | Joint GRPO action space + propose-and-verify | ✅ Done — the one gain was a **corpus artifact** |
| **7** | Eight-vector benchmark | 🟡 **Built & run — first result withdrawn** → [[Phase 7 — Eight-Vector Benchmark]] |
| **8** | [[Layer 5 — Human in the Loop]] | ✅ Done — found [[Inert Blocked Patterns]] on its first run |
| **9** | Grow the pytest suite | 🟡 Ongoing → [[Test Suite]] |

## The shape of the roadmap

Phases 0–2 are construction. **Phase 3 is where the project's character changes**:
the headline experiment returned a negative, and everything from Phase 4 onward is
either repairing the *measurement* that negative exposed, or discovering that
another instrument was lying.

Phases 4, 6b, 6c and 6d are all, in effect, *"fix the thing that was supposed to
tell us whether the thing worked."* → [[Instruments Fail More Than Mechanisms]]

## What is actually left

Phase 7's repair is the only blocking item → [[Next Task — Repair the Phase 7 Benchmark]].
Everything else is in [[Backlog]].
