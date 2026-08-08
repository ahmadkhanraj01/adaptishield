---
tags: [adaptishield, finding, hub]
type: hub
---

# Findings Index

Every result the project has produced, positive and negative. **Negatives are
first-class** — several of them are the contribution.

## The numbered findings (§6d–§6p)

| § | Subject | Outcome |
| :--- | :--- | :--- |
| 6d | [[6d — Adaptive Loop Negative Result]] | **Negative** — the apparent gain was memorisation of a training address |
| 6e | [[6e — Semantic Scoring Ablation]] | More accurate per action, **worse end-to-end**; ships off |
| 6f | [[6f — Standalone Severity Rule]] | First change that improved the *system* rather than a component |
| 6g | [[6g — Temporal Drift Scoping]] | Fixed — history scoped per session |
| 6h | [[6h — IE Consistency Guard]] | Fixed — requires consistent separation across samples |
| 6i | [[6i — Masked Probe Rewrite]] | **Largest detection gain**; introduced a latent false positive |
| 6j–6k | [[6j-6k — The Loop Closes a Matching Gap]] | Yes when its knob matches one — **and it generalises** |
| 6l | [[6l — No Natural Gap at Scale]] | **No gap** — GRPO converges to a no-op |
| 6m | [[6m — The Single-Character Defect]] | **One defect** — a single character of string comparison |
| 6n | [[6n — A Corpus That Can Fail]] | **GRPO's only gain was an artifact of our own benign corpus** |
| 6o | [[6o — Phase 6 Executed on Kaggle]] | Backends agree to exactly zero; **the P100 cannot run PyTorch** |
| 6p | [[6p — Probe Hallucination Fixed at the Scorer]] | Detection 96.7%; the false positive **survived via a second route** |

## Cross-cutting results

- [[Fixes A-D]] — the four measurement corrections that had to land before training
- [[The Adaptive Layer Proposes a No-Op]] — the honest headline
- [[Reward-Decreasing Proposals]] — four times, on different hardware
- [[Inert Blocked Patterns]] — a rule that presents as protection while providing none
- [[Instruments Fail More Than Mechanisms]] — the pattern across the whole project
- [[Backstops Mask Progress]] — why ASR is nearly useless here
- [[Residual Misses Decomposed]] — where the remaining 4 failures actually live
- [[Known Bounded False Positive]] — deliberately left open, and why
- [[3B Layer 4 Boundary]] — a scoping result, not a defect
- [[Address-Free Attacks]] — the corpus change that made IE non-redundant
- [[Design Lessons]] — the ones that generalize beyond this project

## Phase 7 — the comparative claim

- ✅ [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]] — **ASR
  71.4% → 14.3%**, 18/21 stops attributed to 3B, **zero** detection stops in
  `static_only`, and Layer 4 contributes **nothing incremental** once 3B is on

## Phase 10 — the external baseline

- 🔴 [[Phase 10 Floor — The Injections Do Not Steer a 4B Planner]] — the baseline
  is built, but the undefended derived agent already resists (ASR **1/7**), so
  there is almost nothing for spotlighting to improve. Blocking a well-powered run

## ⛔ Withdrawn

- [[Phase 7 Benchmark Withdrawn]] — a headline result that measured its own
  construction. **Superseded**, kept for the contrast

## Three patterns worth carrying forward

1. **A measured negative beats an unmeasured positive.**
2. **The instruments failed more often than the mechanisms.**
3. **A defense measured only against a corpus its author wrote measures the
   author's imagination.**
