# Evaluation Framework

**Status:** 🟡 Partial — the adaptive-loop experiment is built and has produced
a result; the formal eight-vector benchmark is still pending.

## Purpose
The formal benchmark: run a fixed set of attack vectors against a **static
baseline** versus the **full AdaptiShield** and report ASR / FPR / WCR, so
the project can quantify how much the defenses (and eventually 3D's
adaptation) actually help.

## What's done

### `adaptive_loop_experiment.py` — does applying a 3D proposal close the gap?
The experiment root README Section 13 called "the single most valuable next
experiment". Four phases, each attack phase on a **fresh pipeline** (so that
`CausalAnalyzer.boundary_history` drift can't be mistaken for the effect of
the update):

1. **gen-1** — original attacks + benign controls; feeds the Optimizer.
2. **before** — gen-2 keyword-softened attacks on a pristine pipeline.
3. **propose** — 3D scores the labeled gen-2 results and proposes an update.
4. **after** — the same gen-2 cases *plus benign controls* with the proposal
   applied. Benign cases are re-run because an update that catches attacks by
   making 3B hair-trigger is not a win; FPR is the control.

```bash
python3 -m evaluation.adaptive_loop_experiment
```

### `holdout_generalization_test.py` — was it learning or memorization?
Re-applies the same proposal, then attacks with a **held-out** attacker
address the update never saw (`leaker@shadow-mail.net`; training used
`attacker@evil.com` only). This is what separates a real defense improvement
from recognition of one memorized string.

```bash
python3 -m evaluation.holdout_generalization_test
```

## Result (2026-07-20) — the adaptive loop did **not** close

| Measure | Before | After (training address) | After (held-out address) |
| :--- | :--- | :--- | :--- |
| `caught_by_causal` (3B) | 1/4 | 0/4 | 0/4 |
| blocked by 3A | 0/4 | 4/4 | **0/4** |
| ASR | 0% | 0% | 0% (egress backstop only) |
| WCR | 25% | 0% | 0% |
| FPR | — | 0% | — |

Three findings, all reproducible from the saved reports in `logs/adaptive_loop/`:

1. **The `ie_threshold` change is inert.** 3D proposed `0.5 → 0.4`. IE is
   `masked.severity − masked_san.severity`, and with `k_samples=2` each
   severity is a mean of two integers in {0,1,2} — so IE can only take values
   in multiples of 0.5. Across all 58 recorded boundaries the observed IEs are
   {−0.5, 0, 1, 2}; **none** fall in [0.4, 0.5). No threshold move inside that
   gap can change any verdict. 3D is tuning a knob whose resolution is coarser
   than its step size.
2. **The apparent "fix" was memorization.** After the update all four attacks
   came back `blocked` — but by **3A, not 3B**, because 3D had harvested the
   literal string `attacker@evil.com` from the training episodes'
   `proposed_action` into `blocked_patterns`, and the test cases used that same
   address. Against the held-out address the block rate falls to 0/4.
3. **WCR regressed 25% → 0%.** Blanket 3A blocks replaced 3C safe
   continuations, which is a loss on the project's own continuation metric.

**Why 3B misses the softened attacks** (visible now that `CausalDiagnostic`
records per-regime severities): the missed cases have `masked = 0`, not
`masked = masked_san`. The masked probe returns `no_action` — `gemma3:4b`
does not recognize the softened phrasing as an instruction *at all*, so there
is no causal signal for any threshold to detect. Sensitivity tuning cannot
recover a signal that was never generated.

**Implication for 3D.** Both knobs 3D currently controls are the wrong ones
for this failure. Closing the loop needs a change in kind, not degree —
candidates: scoring the masked probe on *semantic* compliance rather than a
verb keyword list (`_score_action`), raising `k_samples` to give IE finer
resolution, or generalizing harvested patterns instead of storing literals.
This is the concrete finding the GRPO work should be aimed at.

## What's pending
| Planned piece | Purpose |
| :--- | :--- |
| Attack vector suite | Eight vectors from the literature (Du et al. / MCPSecBench) |
| Baseline runner | Pipeline with defenses disabled / static-only |
| Full runner | Complete AdaptiShield pipeline |
| Report generator | ASR/FPR/WCR comparison table, reproducible, logged |

**Reuse note:** `red_team/evaluator.py` already computes ASR/FPR/WCR with
per-family breakdowns — build on it rather than reimplementing the metrics.
Bulk runs go to Kaggle for reproducibility (root README Section 10).
