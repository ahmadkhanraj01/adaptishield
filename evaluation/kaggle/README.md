# evaluation/kaggle — Phase 6 GRPO training (local ↔ Kaggle)

This folder is the Phase 6 seam (see [Phase.md](../../Phase.md) §6): it replaces
the v1 directional heuristic inside `AdaptiveThreatModel.propose_update()` with a
**real GRPO policy-gradient loop**, trained off-machine on a free Kaggle P100,
while keeping the exact `LabeledEpisode → ProposedUpdate → apply_update`
contract. Nothing about the live pipeline changes — the trained update comes back
as a `ProposedUpdate` JSON and is applied through the same human-gated seam.

## Why the split exists

The local 4 GB card cannot host torch GRPO; Kaggle's P100 (16 GB) can. But
Kaggle cannot host the live pipeline (no Ollama / MCP there). So:

```
LOCAL (this machine)                       KAGGLE (P100, training only)
────────────────────                       ────────────────────────────
run pipeline + red-team campaigns          GRPO over the labeled episodes,
  → LABELED EPISODES  ──(package)──►         same reward, emits a
apply the trained ProposedUpdate  ◄──────    ProposedUpdate (ie_threshold,
  then re-run campaigns locally               patterns, tools)
```

## Files

| File | Role | Runs where |
| :--- | :--- | :--- |
| `grpo_env.py` | Self-contained reward + **threshold→verdict replay**. Recomputes `final_status` under a candidate `ie_threshold` from recorded causal diagnostics, scores it with the exact `RewardConfig`. No project imports — bundled into the Kaggle dataset. | both |
| `package_episodes.py` | **Packager.** Labeled red-team `ExecutionResult`s → training JSONL (LabeledEpisode fields + causal diagnostics + inferred `ie_separation_consistent`). Writes `dataset-metadata.json`. | local |
| `grpo_train.py` | **GRPO trainer.** Categorical policy over the IE grid, group-relative advantage + REINFORCE. Emits `proposed_update.json`. torch on Kaggle, pure-Python fallback locally. | Kaggle (or local) |
| `kernel-metadata.template.json` | Kaggle **kernel** config template (GPU on, internet off, attaches the dataset). `run_kaggle.sh` fills in your username → generated `kernel/`. | Kaggle |
| `.env.example` | Template for Kaggle credentials — copy to repo-root `.env` (git-ignored). | local |
| `run_kaggle.sh` | **Path A driver.** Loads `.env`, stages + pushes the dataset and kernel, polls, pulls `proposed_update.json`. | local |
| `apply_and_validate.py` | Loads the trained `ProposedUpdate`, applies it via `apply_update(approved=True)`, re-runs the campaign BEFORE/AFTER (caught_by_causal / ASR / WCR / FPR + held-out). | local |

`dataset/`, `kernel/grpo_train.py`, `output/` and `proposed_update.json` are
generated artifacts (git-ignore them; the packager/scripts recreate them).

## Why the off-machine reward is exact

`grpo_env` replays `CausalAnalyzer`'s takeover verdict under a candidate
threshold. Of its three rules, only the IE rule depends on `ie_threshold`; its
sample-consistency input is threshold-invariant and captured once at packaging
time. The standalone (`masked≥2`) rule is threshold-independent, and temporal
drift **cannot fire on campaign episodes** because each case runs under a unique
`session_id` (never 3 boundaries in one session). So `takeover(T)` is exactly
reproducible from the recorded `ie`, `masked_severity`, and the inferred
`ie_separation_consistent` flag. (Details in `grpo_env.py`'s module docstring.)

## The GRPO loop (honest by construction)

The action is which IE-grid value to set `ie_threshold` to. Each step samples a
**group** of thresholds from the current policy, scores each on the full batch
with the exact reward, and uses the group mean as the baseline
(advantage = reward − group_mean — GRPO's defining move, no learned critic). A
tiny minimal-intervention penalty on `|T − current|` breaks ties toward the
smallest move. Consequences, both pinned by tests:

- **Gap exists** (Phase 5b mechanism): a diagnostic miss missed at `1.5` →
  learns `1.5 → 1.0` (the minimal move that closes it).
- **No gap** (Phase 5's natural-set finding): every threshold scores alike,
  advantages vanish, argmax stays at `current` → a **no-op** proposal, which
  `apply_update` refuses. "GRPO adds nothing when there's nothing to learn" is
  itself a valid Phase 6 result.

## Run it

### Local (no Kaggle, no torch — the whole loop is demonstrable here)
```bash
# 1. package a deterministic synthetic gap (no Ollama):
python -m evaluation.kaggle.package_episodes --self-test

# 2. GRPO over it (pure-python backend auto-selected without torch):
python -m evaluation.kaggle.grpo_train --episodes evaluation/kaggle/dataset/episodes.jsonl
#    → proposed_update.json : ie_threshold 1.5 → 1.0
```

### Real data → Kaggle P100 → apply
```bash
# 1. run the expanded campaign and package what it produced (needs Ollama):
python -m evaluation.kaggle.package_episodes --run-campaign

# 2. one manual prerequisite — credentials in a repo-root .env:
#    cp evaluation/kaggle/.env.example .env   &&   $EDITOR .env
#    (installed CLI is 1.7.4.5 → use the LEGACY username+key, NOT the new
#     "API Tokens" access token, which needs CLI >= 1.8.0 / kagglehub)

# 3. push dataset + kernel to a P100, poll, pull the trained ProposedUpdate:
bash evaluation/kaggle/run_kaggle.sh

# 4. apply it locally and validate BEFORE/AFTER (needs Ollama):
python -m evaluation.kaggle.apply_and_validate \
    --proposal evaluation/kaggle/output/proposed_update.json
```

## Tests

`tests/test_grpo_kaggle.py` (deterministic, no LLM/torch/GPU) pins the threshold
replay, the reward contract, the consistency inference, and GRPO's
gap-closing / no-op / no-literal-target (fix A) behavior.

## Status / open questions carried from Phase.md §6

- ✅ Built: env, packager, GRPO trainer (torch + pure-python), Path A scripts,
  apply-and-validate, tests (37 total pass).
- 🔲 **Credentials** — put a legacy `KAGGLE_USERNAME`/`KAGGLE_KEY` in repo-root
  `.env` (the installed CLI 1.7.4.5 can't use the new access token). The only
  thing gating a real P100 run.
- 🔲 **Natural-gap question:** run `package_episodes --run-campaign` on the
  expanded 6-family / 4-directive / held-out set. Phase 5 showed the small set
  had none; if the larger one also has none, GRPO's no-op is the answer.
- 🔲 **Learned vs heuristic:** does GRPO beat the directional heuristic? If the
  heuristic already closes every reachable gap, GRPO may match it — a valid
  finding.
