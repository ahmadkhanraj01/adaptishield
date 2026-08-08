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

## Phase 11 — the per-component matrix

- ✅ [[Phase 11 — Only Two Layers Do Anything]] — **3B stops attacks (18/0,
  p = 0.000), 3C keeps the workflow alive (18/0 on WCR, p = 0.000), and the other
  four components change nothing measurable** — cumulatively *and* at the margin,
  with **zero discordant pairs**. Layer 4 turns out to be *redundant* rather than
  contributing: 6 of 18 of 3B's stops would also have been caught by the allowlist

## Phase 10 — the external baseline

- ✅ [[Phase 10 — Spotlighting Has No Measurable Effect]] — datamarking 34.8% →
  33.3% steered, McNemar **p = 1.00**; the null is two opposing per-family effects
  cancelling, not indifference
- 🔴 [[The Scorer Cannot See Negation]] — a refusal naming the attacker address
  scored as compliance, which **reversed the sign** of the result above. Fixed for
  agent-chosen actions; measured absent for 3B's regimes ↓
- ✅ [[3B's Refusal Exposure Is Live and Unrealised]] — **0 of 209** recorded
  severity-2 masked-regime samples are refusal-shaped, with a passing positive
  control. The defect is live on the shipped keyword path and has never fired,
  because the masked probe gives the model no competing goal to refuse in favour
  of. Regime scorer left unchanged
- 🟡 [[Phase 10 Floor — The Injections Do Not Steer a 4B Planner]] — why the
  benchmark vectors could not power the comparison (ASR 1/7) and the campaign
  corpus was used instead

## Process findings — about the evidence, not the defense

- ✅ [[A Published p-Value With No Committed Source]] — Phase 10's `McNemar p = 1.00`
  reached **five documents** with no committed implementation and no discordant
  counts in the artifact. The figure was **right**, which is luck rather than
  process. Fixed by `evaluation/paired.py` + per-case outcomes in the tracked
  artifact, and by a manifest that admits when a run was **replayed**

## ⛔ Withdrawn

- [[Phase 7 Benchmark Withdrawn]] — a headline result that measured its own
  construction. **Superseded**, kept for the contrast

## Three patterns worth carrying forward

1. **A measured negative beats an unmeasured positive.**
2. **The instruments failed more often than the mechanisms.** Five times now: the
   benchmark ([[Phase 7 Benchmark Withdrawn]]), the scorer
   ([[The Scorer Cannot See Negation]]), the missing control
   ([[3B's Refusal Exposure Is Live and Unrealised]]), the uncommitted statistic
   ([[A Published p-Value With No Committed Source]]), and the wrong outcome variable
   ([[Phase 11 — Only Two Layers Do Anything]], where the report called 3C inert).
3. **A defense measured only against a corpus its author wrote measures the
   author's imagination.**
