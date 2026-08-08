# results — Tracked Numbers and Their Provenance

**Status:** ✅ Active — one subdirectory per phase whose numbers are quotable

> Unlike `logs/` (gitignored working output), **this tree is tracked**. Rules.md §7
> requires that *every number in the paper is regenerable by one committed command
> whose artifact is committed here with a run manifest*. A table that cannot be
> regenerated cannot be claimed.

## Purpose

`logs/` is where a run writes; `results/` is where a run's **conclusions** live
once they are worth citing. The distinction matters because `logs/` is
append-only, machine-local and easily stale — the §6n staleness trap is exactly a
crashed run leaving an old dataset that reports pre-fix numbers as current.
Copying a result here is the act of saying *this one is the number of record*.

## Contents

| Path | Produced by | Holds |
| :--- | :--- | :--- |
| `phase7/benchmark.json` | `python3 -m evaluation.benchmark --repeats 3` | Per-arm ASR / FPR / WCR with Wilson intervals, per-layer attribution counts, per-vector breakdown |
| `phase7/manifest.json` | same run | Commit SHA + dirty flag, corpus provenance and version, model tags, 3B's knobs, Ollama VRAM state, Python/platform, seeding statement |

## Reading a manifest before trusting a result

Four fields decide whether a number is usable:

- **`commit` + `dirty`** — `dirty: true` means the tree had uncommitted changes, so
  the result is **not** reproducible from the recorded commit alone. Phase 7's
  first manifest carries `dirty: true`; the code landed in the commit that added
  this directory.
- **`ollama.on_gpu`** — after a CUDA fault Ollama silently falls back to CPU, which
  changes *outputs* as well as speed. Sampled **after** the arms run, because
  `/api/ps` lists only resident models and an idle server reports no GPU.
- **`corpus.external_benign.sampled_indices`** — which documents the external
  cohort actually contains. Phase 7's stride subsample **excludes indices 41 and 55,
  both known false positives**, which is why its FPR column is a
  catastrophic-over-blocking check and not a rate.
- **`seeding`** — there is no RNG seed. Ollama exposes none, so determinism comes
  from greedy decoding at temperature 0, and that is *not* literally deterministic
  (§6n measured 2 of 564 regime severities disagreeing). Repeats exist for this
  reason.

## Regenerating

```bash
rm -rf logs/benchmark_checkpoint          # cached results describe the OLD pipeline
python3 -m evaluation.benchmark --repeats 3
cp logs/benchmark/{benchmark.json,manifest.json} results/phase7/
```

Raw run logs stay in `logs/benchmark/run.log` and are **not** tracked — they are
large and contain attacker-authored text verbatim.

## What's pending

- **Phase 10** (external baseline) and **Phase 11** (per-component ablations) will
  each add a subdirectory here. Phase 13's reproducibility artifact is this tree
  plus the deterministic test suite.
- The campaign's own numbers (detection 116/120, FPR 3.3% at n=60) are still only in
  `logs/` + the docs. They should get a `results/campaign/` entry with a manifest,
  for the same reason Phase 7 has one.
