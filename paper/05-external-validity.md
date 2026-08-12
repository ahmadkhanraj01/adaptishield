# §5 — External validity: detection falls from 96.7% to ~18%

*Source: `results/phase12/benchmark.json`. Corpus: `evaluation/injecagent.py`,
vendoring InjecAgent's direct-harm split (MIT, cited). 60 cases per arm, 30 per
stratum.*

## The claim under test

On our own corpus the causal sub-layer detects **116/120 = 96.7%** [91.7%, 98.7%]
of injections at a false-positive rate of **3.3%** [0.9%, 11.4%] against 60
externally-authored benign documents. Those are the numbers a paper would
normally headline. This section is what happens when the *attacks* are also
written by someone else.

## Result

Detection falls to approximately **18%** on the InjecAgent population, and the
stratification is the finding rather than a caveat on it.

| Stratum | share of corpus | detection | 95% Wilson |
| :--- | ---: | ---: | :--- |
| target-match path fires | ~10% | 93.3% | [78.7%, 98.2%] |
| target-match path cannot fire | ~90% | **10.0%** | [3.5%, 25.6%] |

End-to-end, the complete system's ASR on this corpus is **29/60 = 48.3%**,
against 60/60 for both `undefended` and `static_only`.

**⛔ The strata must not be pooled.** The evaluation draws 30 cases from each
stratum, but the underlying population is split 51/459. A pooled figure over the
balanced draw gives 51.7%, which is wrong for InjecAgent by **33 points**. This
is not a subtlety about weighting; it is the difference between a defense that
works and one that does not, and a single pooled number reports the sampling
design rather than the system.

## Why detection collapses

The detector's severity scorer was built around a data-movement vocabulary —
*forward, exfiltrate, upload, delete, post, send, write*. It measures that shape
well. InjecAgent's attacks mostly do not have it.

The recorded probe transcripts show the failure is **not** in the probe. Shown
the injected content, the model reports the action faithfully and verbatim:
*"grant permanent access to guest_amy01 on the August Smart Lock system"*,
*"transfer $3,000 to account number 123-1234-1234"*, *"unlock the front door"*.
The scorer then reads those correct transcriptions, finds no data-movement verb,
and returns 0. **23 of 26** recorded address-free cases score `(0, 0)` with a
perfectly correct transcription sitting in the log.

Severity 0 is below *both* detection rules at once — the standalone rule requires
2, the indirect-effect rule requires at least 1. So no threshold setting could
have reached these cases. The deficiency is a **harm taxonomy that names one kind
of harm**, not a threshold that sits too high. §6 is the attempt to widen it.

## What replicates, and what that means

The `static_only` arm stops **0 of 60** here, replicating §3's zero on a corpus
we did not write. The components that were inert on our data are inert on
someone else's. And `backstop_share` is 0%: the egress allowlist, which absorbed
everything in §4, catches nothing here, because these attacks do not carry an
address to filter.

Taken together with §3, this bounds the contribution precisely: **the causal
sub-layer is the only component that detects anything, and what it detects is
attacks shaped like the ones it was built against.**

## Known weakness in this section

The per-stratum estimates are **single-repeat at n = 30**. This is the paper's
flagship negative result and currently its least-powered number. Repeats are in
progress and the final figures will carry repeat-level variation. *(Pending —
this sentence must be replaced with the measured spread or the weakness stated
explicitly; it must not survive as-is.)*
