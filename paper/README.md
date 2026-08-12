# Manuscript — draft sections

**Target:** journal (venue 🔵 undecided — see `Phase.md`). **Submission: 14 Sept 2026.**

Format-agnostic Markdown on purpose. The venue decision sets page/figure limits
and whether an artifact-availability statement is required, and none of that
changes the argument — so nothing here is typeset for a template yet.

## Status

| § | Section | Numbers | State |
| :--- | :--- | :--- | :--- |
| 1 | [Introduction + contributions](01-introduction.md) | frozen | ✅ drafted |
| 2 | [Threat model + architecture](02-threat-model-architecture.md) | — | ✅ drafted |
| 3 | [Per-component ablations](03-ablations.md) | frozen | ✅ drafted |
| 4 | [External baselines](04-external-baselines.md) | frozen | ✅ drafted |
| 5 | [External validity](05-external-validity.md) | frozen | ✅ drafted |
| 6 | [Detector generalization](06-severity-generalization.md) | frozen | ✅ drafted |
| 7 | [The adaptive layer](08-adaptive-layer.md) | frozen | ✅ drafted |
| 8 | [Negative results as contribution](07-negative-results.md) | frozen | ✅ drafted |
| 9 | [Limitations](09-limitations.md) | frozen | ✅ drafted |

**All nine drafted, and the four core figures are embedded** (§3, §5, §6, §7 —
see `figures/`, generated from `results/` by `make_figures.py`). What remains is
not writing but two things a draft cannot supply: the venue decision and related
work. The last owed measurement (§5's per-stratum repeats) is done and its
placeholder is replaced.

## The single claim the paper now turns on

Phase 15 resolved §7 and, in doing so, gave the whole paper one spine:

> **The causal contrast carries discriminative signal when the injected content
> contains a liftable target, and close to none otherwise.**

Everything else follows from it — detection collapsing on externally-authored
attacks (§5), a harm taxonomy generalizing about half (§6), and an adaptive layer
whose parameters act on a quantity measured at zero in 80–97% of turns (§7).
Write §1 and §2 to set that claim up, not the architecture.

## The one rule these drafts follow

**Every number carries its source file.** Rules §7 requires each figure to be
regenerable by a committed command, and Phase 10 is the cautionary case: a
published `p = 1.00` reached five documents with no committed implementation. It
happened to be right. That was luck, not process.

So each claim below is written as `value [CI] (source)`, and a claim with no
source has not been measured yet and must not survive into the submission.

## Two framings to keep straight

**This is not a "we built a defense and it works" paper.** The ablation says four
of six components do nothing on our corpus; the external baseline is a null; the
external benchmark drops detection from 96.7% to ~18%. Leading with the
architecture would make every one of those read as a failure. Leading with the
measurements makes them the contribution: *what does a layered causal defense
actually buy, and where does it stop?*

**Negative results are the spine, not an appendix.** Three of them are only
visible because the instrumentation was built to see them, which is itself the
methodological argument (§8).

## Still owed before submission

1. 🔵 **The venue decision** — the only blocking item. Sets page and figure
   limits, whether an artifact-availability statement is required, and author
   order. The architecture figure needs an inverted colour scheme for print.
2. **Related work.** Not draftable from the repository; needs a literature pass.
   The three families in §1 (prompt-level, gate-level, causal) are the frame.
3. **§5's per-stratum repeats.** The 96.7% → 18% collapse is the flagship
   negative result and rests on single-repeat n = 30. §5 carries an explicit
   placeholder that must be replaced or the weakness stated outright — it must
   not survive as written.
4. ✅ **A figure pass — done.** Four figures generated from `results/` and
   embedded in §3/§5/§6/§7 (`make_figures.py`, colorblind-validated, PDF+PNG). A
   fifth candidate — the Layer 5 review console as a figure — is left out pending
   its visibility question, since it currently embeds attacker-authored text.
