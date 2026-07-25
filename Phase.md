# AdaptiShield — Phases & Progress

**What this file is:** the roadmap and progress tracker — what is done, what is
in flight, and what comes next, organized as phases. The root [README.md](README.md)
Section 13 holds the detailed task list; this file is the higher-altitude view.
See [Architecture.md](Architecture.md), [Design.md](Design.md), [Rules.md](Rules.md)
for structure / rationale / constraints.

*Last updated: 2026-07-25 (session 2). Rough completion: ~78%.*

---

## Snapshot

| Phase | Scope | State |
| :--- | :--- | :--- |
| 0 | Defensive pipeline (Layers 0–4, gated sandbox, telemetry) | ✅ Done |
| 1 | Security sub-layer 3A / 3B / 3C | ✅ Done |
| 2 | Red Team Module (generator → agent → evaluator → optimizer) | ✅ Done |
| 3 | Component 3D v1 + adaptive-loop experiment | ✅ Done — **negative result** |
| 4 | Measurement fixes A / B / C / D | ✅ **Done (current)** |
| 5 | Re-run the adaptive loop on the fixed measurement | ✅ Done — loop had nothing to close (§6j) |
| 5b | Prove the loop *can* close a knob-matching gap | ✅ Done — closes **and** generalizes (§6k) |
| 6 | Component 3D real GRPO training (Kaggle) | 🟡 Pipeline built + run locally; **natural-gap answered: no gap** (§6l), re-confirmed after the probe fixes (§6m) |
| 6b | Diagnose + fix the 15 residual 3B misses | ✅ Done — one defect, **114/114 caught** (§6m) |
| 6c | **Fix the evaluation corpus** (benign-with-address, address-free attacks) | 🔴 **Blocking** — corpus is at its ceiling, FPR unmeasured (§6m) |
| 7 | Eight-vector benchmark (static vs full vs +3D) | 🔲 Pending |
| 8 | Layer 5 — dashboard / console / override | 🔲 Pending |
| 9 | Grow the pytest suite | 🟡 Ongoing (62 tests) |

---

## Phase 3 — the negative result (context for everything after)

Applying a 3D proposal did **not** recover the softened attacks 3B missed. The
apparent gain was memorization of a training address; it vanished on a held-out
address. Post-mortem found the adaptive loop could not close the gap for
concrete, reproducible reasons — which defined Phase 4. (README 6d.)

## Phase 4 — measurement fixes (done)

The prerequisites that had to land *before* any GRPO training, because training
a policy over a broken measurement produces a confident no-op.

| Fix | What | Result |
| :--- | :--- | :--- |
| **A** | Stop 3D memorizing literal exfil targets | Proposals carry generalizable phrasing only; before/after no longer gameable |
| **B** | Make the reward WCR-aware | `safe_continuation` (+1.0) > `blocked` (+0.7); no longer scores killing the workflow as a win |
| **C** | Size 3D's step to the IE grid (`ie_resolution`) | Threshold move is non-inert (`0.5→0.0`, not the dead `0.5→0.4`) |
| **D** | Rewrite the masked probe so softened injections produce signal | **gen-2 `caught_by_causal` 1/4 → 3/4, gen-1 3/4 → 4/4, FPR 0%** |

Tests: 8 → **22 deterministic** (`test_takeover_rules.py`, `test_adaptive_threat_model.py`).

### D — headline before/after (red-team campaign, distribution over 5 post-D runs)

| Metric | Before D | After D (5 runs) | Δ |
| :--- | :--- | :--- | :--- |
| **ASR** gen-1 / gen-2 | 0% / 0% | **0% / 0% — 5/5 runs** | stable |
| FPR gen-1 / gen-2 | 0% / 0% | 0% / 0% — 5/5 | — |
| gen-1 caught by 3B | 3/4 | **4/4 — 5/5** | +25 pts |
| gen-2 caught by 3B (softened) | 1/4 | **4/4 in 4/5, 3/4 in 1/5** | **up to +75 pts** |
| WCR (gen-1 / gen-2) | 75% / 75% | **100% / 100% (75% in 1/5)** | +25 / up to +25 |

`masked_hypothetical` is the only swing case: caught by 3B in **4 of 5** runs;
when missed, the egress backstop holds ASR at 0%.

---

## Phase 5 — re-run the adaptive loop (done: the gap is already closed)

Re-ran `evaluation/adaptive_loop_experiment.py` with A–D in place. **Result: the
loop had nothing to close.** BEFORE caught_by_3B = **4/4** (was 1/4 in 6d), so
3D saw reward +1.0, 0 missed, 0 false positives → proposed a **no-op**;
`apply_update` refused. AFTER = 4/4. (Root README §6j.)

- *Good:* 3D no longer fabricates a phantom update (contrast 6d's memorized
  address). Given nothing to fix, it correctly proposes nothing.
- *Unsatisfying:* the loop's **value** (an update that *improves* detection) is
  still unproven — the base fixes (measurement D + reward hygiene A/B/C) closed
  the gap, not 3D's knobs. Every failure mode that mattered was outside those
  knobs.

**Open question this raised → Phase 5b (done).** `evaluation/mechanism_validation.py`
supplies the controlled test: a diagnostic-style injection (masked=1 → IE=1.0,
so the standalone rule is out by construction) missed at an over-high
`ie_threshold=1.5`. 3D observes the miss, proposes `1.5 → 1.0` with **no
memorized address** (fix A), applies it, and **both** the training attack **and
a held-out attacker address** (which 3D never saw) are then caught — the loop
closes *and* generalizes, the exact pair 6d failed. Deterministic; pinned in
`tests/test_adaptive_threat_model.py`. (Root README §6k.)

**Scope:** this proves the *mechanism*, not that such a gap arises naturally on
the current attack set (Phase 5 showed it does not). The natural-gap question
and the learned-vs-heuristic comparison move to Phase 6.

## Phase 6 — real GRPO training on Kaggle (unblocked, pending)

Now cleared: the measurement carries signal (D), the knob is non-inert (C), the
reward is honest (A/B), and the loop demonstrably closes a knob-matching gap
(5b). Replace the v1 heuristic inside `propose_update()` with a policy-gradient
loop (torch, Kaggle P100), keeping the **same reward + `LabeledEpisode →
ProposedUpdate → apply_update` contract** (already pinned by the deterministic
tests, so training cannot silently regress it).

**Two open questions Phase 6 had to answer:** (1) does a knob-matching gap arise
*naturally* on a larger, held-out attack set — **ANSWERED: no** (§6l; the 118-
episode expanded campaign has no gap the `ie_threshold` knob can close, so GRPO
proposes a no-op); and (2) does a *learned* GRPO policy beat the directional
heuristic — **moot for this knob**: with no reachable gap, neither the heuristic
nor GRPO can improve detection, so they agree on the no-op (itself the valid
finding). The remaining detection leverage is in the probe, not the knob.

### Why Kaggle, and the hard boundary

The local card is 4 GB — it cannot host torch GRPO or 7B+ models. Kaggle gives a
free **P100 (16 GB)**. But **Kaggle cannot host the live pipeline** (no Ollama /
MCP server there). So the split is fixed:

```
LOCAL (this machine)                     KAGGLE (P100, training/eval only)
────────────────────                     ─────────────────────────────────
run pipeline + red-team campaigns        GRPO training (torch) over the
  → generate LABELED EPISODES     ──►      labeled episodes, same reward
apply the trained ProposedUpdate   ◄──   → emits a ProposedUpdate
  via existing apply_update()               (ie_threshold, patterns, tools)
  then re-run campaigns locally
```

The `LabeledEpisode → ProposedUpdate → apply_update` seam is exactly what lets
training live elsewhere and the result come back. Nothing about the local
pipeline changes.

### Data flow / artifacts to move

1. **Local → Kaggle:** a serialized labeled-episode dataset. Source it from
   `AdaptiShield.from_execution_results()` (red-team `ExecutionResult`s, which
   carry ground-truth labels) or `load_labeled_from_jsonl()` (telemetry replay
   with a labels map). Ship as JSONL in a Kaggle **Dataset**.
2. **Kaggle → Local:** the trained `ProposedUpdate` (JSON: `new_ie_threshold`,
   `new_blocked_patterns`, `new_high_impact_tools`, rationale, mean_reward),
   applied locally via `AdaptiveThreatModel.apply_update(..., approved=True)`,
   then validated by re-running the campaign (`caught_by_causal` before/after,
   FPR distribution — same protocol as §6i/§6k).

### How Kaggle is driven — **decided: Path A** (2026-07-24)

**Path A — Kaggle API, driven from the Claude Code session.** Chosen over the
manual Path B for tight train→pull→apply→re-run iteration. Setup status:

- ✅ `kaggle` CLI 1.7.4.5 installed in the project venv; `~/.kaggle/` created.
- 🔲 **Only remaining step (human, browser):** kaggle.com → Settings → API →
  *Create New Token* → `! mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600
  ~/.kaggle/kaggle.json`. After that, push dataset + run GPU kernel + pull the
  `ProposedUpdate` are all automatable from Bash here.

*(Path B — self-contained `.ipynb` uploaded/run/downloaded by hand — was the
rejected alternative; no credentials but manual every cycle.)*

### Buildable now, independent of Kaggle access

**All built (2026-07-25) in `evaluation/kaggle/`:**

- [x] **Episode-dataset packager** (`package_episodes.py`): campaign
  `ExecutionResult`s → training JSONL (LabeledEpisode fields + causal
  diagnostics + inferred `ie_separation_consistent`). `--self-test` (no LLM) /
  `--run-campaign` (live). Reuses existing adapters.
- [x] **GRPO trainer** (`grpo_train.py`): reads the JSONL, keeps the exact
  `RewardConfig`, outputs a `ProposedUpdate` JSON. Categorical policy over the IE
  grid, group-relative advantage + REINFORCE. torch backend (Kaggle P100) **+ a
  pure-Python fallback** so the loop runs on the 4 GB box. Plus `grpo_env.py`
  (self-contained reward + threshold→verdict replay, bundled into the dataset).
- [x] **(Path A)** `run_kaggle.sh` (loads repo-root `.env`, stages + pushes
  dataset & kernel, polls, pulls the `ProposedUpdate`) + `kernel-metadata.template.json`.
- [x] **Apply-and-validate** (`apply_and_validate.py`): load the trained
  proposal, apply via `apply_update(approved=True)`, re-run before/after + held-out.
- [x] Pinned by `tests/test_grpo_kaggle.py` (+14 → **37 tests pass**).

### Do FIRST — the expanded held-out attack set (gates Phase 6's value)

Phase 5 showed the current 4-family / 1-directive / 1-target set has **no natural
gap** for 3D's knobs. Training GRPO over a knob with nothing to learn is a
confident no-op. So before (or alongside) the notebook:

- [x] **Attack set expanded** (2026-07-24): **6 families** (added
  `authority_citation`, `delegated_followup`), **4 directives** (added two
  subtler single-recipient "bcc / add a recipient" phrasings with no
  "forward all" keyword), **4 targets split first-class** into
  `training_targets()` = {attacker@evil.com, exfil@darkpost.io} and
  `holdout_targets()` = {leaker@shadow-mail.net, siphon@nullroute.org}. The
  held-out split is enforced by construction (`generate_training_attacks()` /
  `generate_holdout_attacks()`), not by index-slicing — a `__main__` assertion
  proves no held-out address enters the training split (Rules.md §5). Full
  training grid = 6 × 4 × 2 = **48 gen-1 attacks** + gen-2 mutations + a
  held-out generalization pass. `run_campaign(run_holdout=True, max_*=None)`
  drives it; deterministic tests still 23/23.
- [x] **Ran the expanded campaign — natural-gap question answered: NO GAP**
  (2026-07-25, §6l). 118 labeled episodes (114 malicious, 4 benign) packaged
  from the live pipeline. `caught_by_causal` **99/114 (87%)**, 15 missed by 3B,
  **0/4 benign false positives**. Replaying the reward across the whole IE grid,
  lowering `ie_threshold` below 0.5 catches **zero** more attacks (missed flat at
  15) — so the real GRPO trainer converges to a **no-op**. The 15 misses are
  measurement-layer noise (14/15 inconsistent IE separation; some `masked=0` or
  negative IE), unreachable by the threshold knob. Confirms Phase 5 at ~6× scale.

### Session-continuity checklist (start here next time)

1. ✅ Path A chosen; CLI installed; **credentials work** (`.env` with legacy
   `KAGGLE_USERNAME`/`KAGGLE_KEY` — the new "API Tokens" access token needs CLI
   ≥ 1.8.0, not on PyPI; verified via `evaluation/kaggle/test_credentials.py`).
2. ✅ Expanded campaign run + packaged (118 episodes) + GRPO trainer built and
   run locally → **no natural gap; GRPO proposes a no-op** (§6l).
3. ✅ **Pivoted to the probe (chosen over the P100 demo) — and it paid off.**
   `evaluation/probe_diagnostic.py` found **one** deterministic defect behind all
   15 misses: `_references_mediator_target` compared verbatim, and `gemma3:4b`
   restates `leaker@shadow-mail.net` as `leaker@shadowmail.net` in **57/57**
   mentions. Every miss was that one address (the only one with a hyphen in its
   domain). Fixed with a normalized match + greedy decoding + a sanitizer
   rewrite → campaign re-run: **114/114 caught** (was 99/114), IE firing
   **17% → 86%**, 0/4 benign FPs, generalizes to both held-out addresses (§6m).
   GRPO re-run on the new data: still a **no-op**, now with nothing left to close.
4. 🔴 **START HERE — the corpus is the bottleneck now, not the defense.** At 100%
   catch the campaign cannot discriminate between defense configurations. Two
   prerequisites before any further detection or 3D claim is measurable:
   - **benign controls that name a legitimate recipient** — the 4 current ones
     contain no address/URL, so they cannot exercise the rule that now does the
     detecting; the 0/4 FPR is structural, not a finding. `evaluation/fpr_check.py`
     already shows `priya@legit-corp.com` benign content reaching severity 2.
   - **attacks whose harmful action names no address** ("delete the audit log") —
     the only way to show the IE rule catching what `masked >= 2` cannot
     (currently 0/114 do).
5. *(optional, unchanged)* Ship to the P100 for a full-loop demonstration — it
   will reproduce the no-op. A demo, not an improvement.

## Phases 7–9 — later

- **7 · Benchmark:** eight attack vectors (Du et al. / MCPSecBench), static
  baseline vs full AdaptiShield vs AdaptiShield+3D; reuse `red_team/evaluator.py`.
- **8 · Layer 5:** audit dashboard, policy inspection console, manual override
  (data already emitted by telemetry + campaigns).
- **9 · Tests:** grow the suite; the 3 validated pipeline episodes are natural
  regression cases.

---

## Known open items (carried forward)

- ~~`masked_hypothetical` flaky at 3B~~ — **closed (§6m)**: 24/24 across all targets
  after the normalized target match + greedy decoding.
- ~~3C sanitisation of softened directives incomplete~~ — **closed for 3B's
  `_sanitize_mediator` (§6m)**. Still open for the separate `ContextSanitizer`
  (3C) component, which shares the old prompt weakness and feeds the user-visible
  safe continuation + the WCR metric — left unchanged rather than altered silently.
- 🔴 **Latent FPR is now load-bearing, not latent.** Detection reduces in practice
  to "did the probe name an address from the content?", and no benign control
  contains an address — so FPR is **unmeasured**, not zero. The normalized match
  added one known exposure (benign hyphenated-domain recipient restated without
  the hyphen: 1 → 2), pinned in `tests/test_target_match.py`. Needs the
  send-to-named-recipient benign control + distributional FPR.
- **IE is redundant with the standalone rule**: `caught by IE rule alone = 0/114`.
  Every family embeds the address inside the directive, so IE tracks `masked`
  mechanically. Needs address-free attacks to separate them.
- **GRPO's learned distribution is uniform** — the argmax comes from the
  minimal-intervention tie-breaker, not from data. Do not present it as a trained
  policy while the corpus leaves it nothing to learn.
- At temperature 0 the `k_samples` are identical, so `require_consistent_ie`
  reduces to a mean comparison and the IE grid coarsens to whole numbers;
  `k_samples=2` is kept only for schema comparability (free 2× speedup by
  dropping it to 1).
