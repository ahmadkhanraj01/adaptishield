# Manuscript — draft sections

**Target:** journal (venue 🔵 undecided — see `Phase.md`). **Submission: 14 Sept 2026.**

Format-agnostic Markdown on purpose. The venue decision sets page/figure limits
and whether an artifact-availability statement is required, and none of that
changes the argument — so nothing here is typeset for a template yet.

## Status

| § | Section | Numbers | State |
| :--- | :--- | :--- | :--- |
| 1 | Introduction + contributions | — | 🔲 after §15 lands |
| 2 | Threat model + architecture | — | 🔲 |
| 3 | [Per-component ablations](03-ablations.md) | frozen | ✅ drafted |
| 4 | [External baselines](04-external-baselines.md) | frozen | ✅ drafted |
| 5 | [External validity](05-external-validity.md) | frozen | ✅ drafted |
| 6 | [Detector generalization](06-severity-generalization.md) | frozen | ✅ drafted |
| 7 | The adaptive layer | **pending Phase 15** | 🔲 |
| 8 | [Negative results as contribution](07-negative-results.md) | frozen | ✅ drafted |
| 9 | Limitations | — | 🔲 |

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
