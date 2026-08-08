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
| `phase10/benchmark.json` | `python3 -m evaluation.benchmark --corpus campaign --arms derived_control spotlighting` | Per-arm `steer_rate` with Wilson intervals and the paired McNemar table. **`steer_rate`, not ASR, is the outcome** — ASR is 0/66 in both arms because the allowlist absorbs every address-carrying attack |
| `phase10/manifest.json` | same run | As above, plus the spotlighting variant and the separate `agent_llm` tag — the derived-action agent runs at temperature 0 to match 3B's probe, and a mismatch here is a confound, not a detail |
| `phase11/benchmark.json` | `python3 -m evaluation.benchmark --preset ladder --repeats 3` | The cumulative ladder: per-rung ASR/WCR, per-layer attribution, and **paired McNemar on two outcomes** — an ASR-only ladder reports 3C as inert |
| `phase11/manifest.json` | same run | As above. `replay.fully_replayed: true` — the outcomes are the original run's cached results; the commit describes the reporting code that added the WCR ladder |
| `phase11_loo/benchmark.json` | `python3 -m evaluation.benchmark --preset loo --repeats 3` | Leave-one-out against `full`. Its `full` arm is the **same 54 results** as the ladder's top rung, reused from that checkpoint, which is what makes the two tables comparable rather than merely similar |
| `phase11_loo/manifest.json` | same run | `replay.fully_replayed: false` — only `full` was cached |
| `refusal_audit/audit.json` | `python3 -m evaluation.refusal_audit` | **An instrument check, not a result.** Per-source counts of masked-regime probe samples whose severity the Phase 10 negation predicate would lower, plus the positive control's verdict |

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

## One entry here is not a result

`refusal_audit/` records that a defect **does not fire**, which is why it has no
row in any results table. Read it before quoting any layer-attributed number: 3B's
attributions rest on the four regime severities, and this is the check that those
severities are not inflated by refusal-shaped probe output (0 of 209 severity-2
samples, positive control passing).

It is the only artifact here that depends on **gitignored** inputs —
`logs/benchmark/run.log` and `logs/probe_diagnostic/*.json` — so a fresh clone
cannot regenerate it until Phase 7 or the probe diagnostic has been run. That is a
genuine departure from Rules §7's regenerability requirement, and it is recorded
rather than papered over: the committed `audit.json` carries the commit SHA and
per-source sample counts so the claim can at least be located, and the
non-log-dependent half of the finding is pinned by `tests/test_refusal_audit.py`,
which needs neither logs nor a model.

## What's pending

- **Phase 12** (InjecAgent) will add a subdirectory here. Phase 13's reproducibility
  artifact is this tree plus the deterministic test suite.
- The campaign's own numbers (detection 116/120, FPR 3.3% at n=60) are still only in
  `logs/` + the docs. They should get a `results/campaign/` entry with a manifest,
  for the same reason Phase 7 has one.
