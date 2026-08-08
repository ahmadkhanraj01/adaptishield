---
tags: [adaptishield, metric, current]
type: metric
date: 2026-08-08
---

# Current Numbers

*As of 8 August 2026. Last commit: `01335ac` (working tree dirty — Phase 7 repair
is uncommitted).*

| | |
| :--- | :--- |
| **Detection** | **116/120 = 96.7%**, 95% CI **[91.7%, 98.7%]** — 4 misses |
| **[[FPR]]** (externally-authored, [[AgentDojo]] n=60) | **3.3%**, 95% CI **[0.9%, 11.4%]** — 2 false positives |
| **FPR** (8 hand-written controls) | 50% — ⚠️ **a diagnostic. Never quote it as a rate** |
| **IE-alone catches** | **14/116** — attacks the standalone rule cannot make |
| **Corpus** | **188 episodes** — 120 malicious, 68 benign → [[Evaluation Corpus]] |
| **Tests** | **161 deterministic**, ~4 s, no LLM / network / GPU → [[Test Suite]] |
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

## Before trusting any of this

Check `python3 -m evaluation.fpr_report` for the **`STALE` header** — a crashed
campaign leaves the old `episodes.jsonl` and the report will happily serve
pre-fix numbers → [[Traps]].
