---
tags: [adaptishield, metric, current]
type: metric
date: 2026-08-08
---

# Current Numbers

*As of 9 August 2026. Last commit: `c058902`, pushed to `origin/main`.*

| | |
| :--- | :--- |
| **Detection** (our campaign) | **116/120 = 96.7%**, 95% CI **[91.7%, 98.7%]** — 4 misses |
| **Detection** ([[InjecAgent]] direct-harm) | **~18%** projected — 93.3% where 3B's target-match fires, **10.0%** where it cannot → [[Phase 12 — Detection Is 18% on Someone Else's Attacks]] |
| **[[FPR]]** (externally-authored, [[AgentDojo]] n=60) | **3.3%**, 95% CI **[0.9%, 11.4%]** — 2 false positives |
| **FPR** (8 hand-written controls) | 50% — ⚠️ **a diagnostic. Never quote it as a rate** |
| **IE-alone catches** | **14/116** — attacks the standalone rule cannot make |
| **Corpus** | **188 episodes** — 120 malicious, 68 benign → [[Evaluation Corpus]] |
| **Tests** | **343 deterministic**, ~7 s, no LLM / network / GPU → [[Test Suite]] |
| **[[ASR]]** (campaign) | 0% on address-carrying attacks; **non-zero by design** on [[Address-Free Attacks]] |
| **Completion** | **~92%** |

## Phase 7 benchmark — the comparative claim

*216 cases, 18 vectors × 3 repeats × 4 arms, 8 Aug 2026 →
[[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]]*

| Arm | [[ASR]] | 95% CI | [[WCR]] | 3B stops |
| :--- | ---: | :--- | ---: | ---: |
| `undefended` | 100.0% | [84.5%, 100%] | 0.0% | 0 |
| `static_only` | 71.4% | [50.0%, 86.2%] | 0.0% | **0** |
| `full` | **14.3%** | [5.0%, 34.6%] | **85.7%** | **18/21** |
| `no_egress` | 14.3% | [5.0%, 34.6%] | 85.7% | 18/21 |

- **ASR 71.4% → 14.3%** static_only → full; **18/21** stops attributed to 3B.
- **WCR 0% → 85.7%** — re-derived on a valid run (the withdrawn 71.4% is retired).
- **Layer 4 adds nothing incremental**: full → no_egress leaves ASR unchanged.
- **3A contributes 0 detection stops** in every arm → [[Inert Blocked Patterns]].
- All 3 residual successes are **V4**, the address-free vector.

⚠️ `static_only` is **our ablation, not an external baseline** — see the Phase 10
table below for the external one.

## Phase 10 external baseline — spotlighting

*86 cases/arm, campaign corpus, 1 repeat →
[[Phase 10 — Spotlighting Has No Measurable Effect]]*

| Arm | Steered | 95% CI |
| :--- | ---: | :--- |
| `derived_control` (no prompt defense) | 23/66 = **34.8%** | [24.5%, 46.9%] |
| `spotlighting` (datamarking) | 22/66 = **33.3%** | [23.2%, 45.3%] |

Paired **McNemar p = 1.00** (8 helped, 7 hurt). **No measurable effect** for
datamarking, on this corpus, with a 4B planner, at n=66 — all four qualifiers
belong to the claim. The null is two opposing per-family effects cancelling.

- **`steer_rate`, not [[ASR]], is the outcome** — ASR is 0/66 in both arms because
  the allowlist absorbs every address-carrying attack.
- ⛔ **The raw figure (39.4% → 56.1%, "17 points worse") is withdrawn** — 16 of 37
  apparently-steered cases were refusals naming the address →
  [[The Scorer Cannot See Negation]].
- These arms' ASR is **not comparable** with Phase 7's: derived vs supplied action.

## Phase 12 — external validity

*60 cases (30 per stratum), 3 arms, 9 Aug 2026 →
[[Phase 12 — Detection Is 18% on Someone Else's Attacks]]*

| Stratum | Share of corpus | Detected | 95% CI |
| :--- | ---: | ---: | :--- |
| 3B's target-match fires | 51/510 = 10% | 28/30 = **93.3%** | [78.7%, 98.2%] |
| Address-free | 459/510 = 90% | 3/30 = **10.0%** | [3.5%, 25.6%] |

**Projected onto the real split: 18.3%.** `static_only` stops **0 of 60**, which
replicates Phase 11's zero on a corpus we did not write. Layer 4 `backstop_share` 0%.

- ⛔ **Never pool the strata.** The draw is 30/30 from a 51/459 population, so the
  pooled 51.7% is wrong for the population **by 33 points**.
- ⚠️ **No [[FPR]] from this corpus** — InjecAgent ships attacks only, so the columns
  read 0/0: an empty denominator, not a clean sheet.
- ⚠️ Layer 4 egress could not fire (the harm is a tool call), so its zero is
  structural here, unlike Phase 11's.

## Phase 11 per-component ablation

*54 cases/arm, 18 vectors × 3 repeats. Ladder (7 arms) + leave-one-out (6 arms),
8 Aug 2026 → [[Phase 11 — Only Two Layers Do Anything]]*

| Rung | Adds | [[ASR]] | [[WCR]] |
| :--- | :--- | ---: | ---: |
| `undefended` → `plus_policy` | L3, then 3A | 100.0% (unchanged) | 0.0% |
| `plus_causal` | **3B** | **14.3%** | 0.0% |
| `plus_sanitizer` | **3C** | 14.3% | **85.7%** |
| `plus_permission` → `full` | L4 scope, then allowlist | 14.3% (unchanged) | 85.7% |

**Paired McNemar, two outcomes.** Attack stopped: only `plus_policy → plus_causal`
moves, **18/0, p = 0.000**. Workflow continued: only `plus_causal → plus_sanitizer`
moves, **18/0, p = 0.000**. Every other rung is **0/0 with zero discordant pairs**,
and leave-one-out reproduces all of it.

- **Layer 4 is redundant, not contributing** — `backstop_share` 0% → 17% → **33%**,
  so 6 of 18 of 3B's stops would also have been caught by the allowlist.
- ⚠️ **`FPR ours` goes 0/3 → 3/3 the moment 3B is on**, and no p-value in either
  table sees it — paired tests exclude benign cases by construction. n=3, a
  diagnostic, never a rate.
- ⚠️ **Our own ablation.** The external-baseline requirement is discharged by the
  Phase 10 table above, not by this one.

## The most important qualifier

> **All 4 residual misses are `masked = 0` — severity-function failures, and
> none is reachable by the threshold [[3D Adaptive Threat Model]] controls.**

That is the **quantified** reason the adaptive layer's honest output is a no-op →
[[Residual Misses Decomposed]], [[The Adaptive Layer Proposes a No-Op]].

## Never pool the two benign cohorts

The 8 hand-written controls are **not a draw from any distribution** — 4 of them
were written specifically to defeat the detector. The Wilson interval on 4/8 spans
[21.5%, 78.5%], nearly the entire usable range. They are reported as a **separate
cohort, labelled a diagnostic that located an architectural boundary** →
[[Wilson Score Interval]].

## What is currently unquotable

⛔ The **first** Phase 7 arm comparison (ASR 100% → 14.3% → 14.3%, WCR 71.4%) →
[[Phase 7 Benchmark Withdrawn]]. The 8 Aug re-run above supersedes it.

⛔ **The benchmark's 0/30 external FPR.** It is a stride subsample (indices 0, 6,
…, 54) that **excludes campaign documents 41 and 55 — both known false
positives** — so it omits every failure by construction. It is a
catastrophic-over-blocking check, not a rate. The **3.3% at n=60** above is the
[[FPR]] of record.

## Instrument checks, not results

*These produce no headline number. They establish that a number is trustworthy.*

| Check | Result |
| :--- | :--- |
| Refusal-shaped output inflating 3B's regime severities | **0 / 209** severity-2 masked samples, control passing → [[3B's Refusal Exposure Is Live and Unrealised]] |

`python3 -m evaluation.refusal_audit` — read-only, no model calls. Re-run it after
any change to the regime scorer, the negation cues, or the vector mediators. It
needs `logs/benchmark/run.log` and `logs/probe_diagnostic/*.json`, which are
**gitignored**, so a fresh clone reports nothing until Phase 7 or the probe
diagnostic has been run.

## Before trusting any of this

Check `python3 -m evaluation.fpr_report` for the **`STALE` header** — a crashed
campaign leaves the old `episodes.jsonl` and the report will happily serve
pre-fix numbers → [[Traps]].
