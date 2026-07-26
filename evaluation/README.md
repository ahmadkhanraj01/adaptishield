# Evaluation Framework

**Status:** 🟡 Partial — the adaptive-loop experiment ran (negative result,
Sec. 6d), the four causes were fixed (A–D), and the loop was re-run (Phase 5)
and shown to close a controlled gap (Phase 5b). The formal eight-vector
benchmark is still pending.

> **Reading order:** the 6d result below is the **historical** negative result
> that motivated fixes A–D. What happened *after* the fixes is in
> "Post-fix results" (Phase 5 / 5b) further down, and in root README §6i–6k.

## Purpose
The formal benchmark: run a fixed set of attack vectors against a **static
baseline** versus the **full AdaptiShield** and report ASR / FPR / WCR, so
the project can quantify how much the defenses (and eventually 3D's
adaptation) actually help.

## Files

| File | Purpose | Status |
| :--- | :--- | :--- |
| `adaptive_loop_experiment.py` | The headline test: does applying a 3D proposal actually close the gap 3B left? Four phases on fresh pipelines so drift cannot be mistaken for the update's effect. Produced the §6d **negative result** that defined fixes A–D. | ✅ Run |
| `holdout_generalization_test.py` | Re-runs a proposal against attacker addresses never seen in training. This is what exposed the §6d "gain" as memorisation of a training literal. | ✅ Run |
| `mechanism_validation.py` | Deterministic (<1 s) check that the four causal regimes and the takeover rules behave as documented; saves a report. Cheap enough to run before any campaign. | ✅ Run |
| `score_action_ablation.py` | Keyword scorer vs semantic (LLM-judge) scorer, per-action and end-to-end. Result (§6e): the semantic scorer is **more accurate per action and worse end-to-end**, so it ships off by default. | ✅ Run |
| `probe_diagnostic.py` | **Read-only** root-cause tool for 3B misses. Reconstructs each failing case deterministically, replays both regimes, explains every severity, and runs *matched controls* (same family + directive against an address that was caught) so a difference is attributable rather than inferred. Found the single defect behind all 15 misses (§6m). | ✅ Run |
| `fpr_check.py` | Adversarial A/B of the old (exact) vs new (normalized) mediator-target match over benign content, plus a `--live` run of the campaign controls. Used to *measure* the cost of loosening the rule rather than assume it: found exactly one new false-positive class. | ✅ Run |
| `fpr_report.py` | FPR with **Wilson score intervals**, cohorts kept separate (`ours` = diagnostic, `agentdojo` = the estimate). Wilson rather than the normal approximation because at n=60 and p near 0 the normal interval extends below zero. Pooled is printed with an explicit caveat and is never a headline. | ✅ Run |
| `ie_ablation.py` | Is the causal IE measurement redundant with 3C's `instructions_removed` self-report? **Answer: no, structurally** — the pipeline gates 3C on takeover (`adaptishield_pipeline.py:132`), so the self-report does not exist at decision time. Verifies this empirically and refuses to print the tempting-but-invalid detector comparison. | ✅ Run |
| `kaggle/` | Phase 6: episode packager, GRPO trainer (torch + pure-Python), Path A driver, apply/validate. See `kaggle/README.md`. | ✅ Run |
| `__init__.py` | Package marker | ✅ |

### A note on two of these

`ie_ablation.py` and `fpr_report.py` both exist to stop a specific bad inference.
The first refuses to score 3C's self-report as a rival detector, because that
score can only be computed on episodes the detector already caught — a selection
effect, not a sample. The second refuses to pool eight hand-written benign
controls (half written to break the detector) with sixty externally-authored
ones, because the first group is a diagnostic and not a draw from any
distribution.

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

### `holdout_generalization_test.py` — was it learning or memorization? *(historical)*
Re-applies the same proposal, then attacks with a **held-out** attacker
address the update never saw (`leaker@shadow-mail.net`; training used
`attacker@evil.com` only). This is what separated a real defense improvement
from recognition of one memorized string. **Now historical:** it hardcodes the
old memorized proposal, which fix A means 3D no longer produces; retained as the
artifact that motivated fix A.

```bash
python3 -m evaluation.holdout_generalization_test
```

### `mechanism_validation.py` — does the loop close a gap when one exists? *(Phase 5b)*
Deterministic (patched regimes, <1s, no LLM). Constructs an honest gap — a
diagnostic-style injection with `masked=1` so the standalone rule cannot fire,
missed only because `ie_threshold` is set too high — then drives the real loop:
miss → 3D proposes (`1.5→1.0`, no literal address) → apply → catch, on both the
training attack **and a held-out attacker address 3D never saw**. Demonstrates
the loop closing *and* generalizing, in explicit contrast to 6d. Pinned in
`tests/test_adaptive_threat_model.py`. (Root README §6k.)

```bash
python3 -m evaluation.mechanism_validation
```

### `score_action_ablation.py` — keyword vs semantic severity scoring
Regenerates the per-action accuracy figures in root README Section 6e
(semantic 10/10, keyword 9/10; 4 of 10 cases held out of the judge's few-shot
prompt). Its main use is as a caution: the semantic arm wins here and loses
end-to-end, so this script should always be read next to the system numbers.

```bash
python3 -m evaluation.score_action_ablation
```

## Result (2026-07-20, HISTORICAL) — the adaptive loop did **not** close

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

## Post-fix results (2026-07-22) — Phase 5 and 5b

All four causes above were fixed (root README §6d "Immediate" → fixes A–D):
A stopped literal memorization, B made the reward WCR-aware, C tied the
threshold step to the IE resolution, and D rewrote the masked probe so softened
injections produce a signal.

**Fix D result (§6i).** Across five repeated campaigns, 3B's detection of
softened attacks rose from 1/4 to **4/4 in 4 of 5 runs** (3/4 in one), FPR **0%**
throughout, ASR **0%** throughout. `masked_hypothetical` is the only swing case.

**Phase 5 — re-run the loop (§6j).** With the base gap closed by D, the BEFORE
phase already caught 4/4, so 3D saw reward +1.0, **0 missed**, and correctly
proposed a **no-op**. The loop had nothing to close — the leverage was in the
measurement (D) and reward hygiene (A/B/C), not 3D's knobs. 3D is now *honest*
(it fabricates no phantom fix), but its added value is unproven on this set.

**Phase 5b — the loop does close a matching gap (§6k).** `mechanism_validation.py`
constructs a gap 3D's `ie_threshold` knob can close and shows the loop closes it
**and generalizes** to a held-out address — the exact pair 6d failed. This
proves the mechanism; it does not claim such a gap arises naturally on the
current attack set (Phase 5 showed it does not).

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
