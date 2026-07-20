# Evaluation Framework

**Status:** 🔲 Pending — empty folder, nothing built yet

## Purpose
The formal benchmark: run a fixed set of attack vectors against a **static
baseline** versus the **full AdaptiShield** and report ASR / FPR / WCR, so
the project can quantify how much the defenses (and eventually 3D's
adaptation) actually help.

## Planned contents (none implemented yet)
| Planned piece | Purpose |
| :--- | :--- |
| Attack vector suite | Eight vectors from the literature (Du et al. / MCPSecBench) |
| Baseline runner | Pipeline with defenses disabled / static-only |
| Full runner | Complete AdaptiShield pipeline |
| Report generator | ASR/FPR/WCR comparison table, reproducible, logged |

## What's done
- Nothing in this folder yet.

## What's pending
- Everything above. **Reuse note:** `red_team/evaluator.py` already computes
  ASR/FPR/WCR with per-family breakdowns — the evaluation framework should
  build on it rather than reimplementing the metrics.
- Runs on Kaggle for reproducibility (root README Section 8).

## Recommended order
Build **after** the Red Team Module (done) and ideally alongside Component
3D, so the baseline-vs-adaptive comparison is the headline result (root
README Section 11).
