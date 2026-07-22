# AdaptiShield — Phases & Progress

**What this file is:** the roadmap and progress tracker — what is done, what is
in flight, and what comes next, organized as phases. The root [README.md](README.md)
Section 13 holds the detailed task list; this file is the higher-altitude view.
See [Architecture.md](Architecture.md), [Design.md](Design.md), [Rules.md](Rules.md)
for structure / rationale / constraints.

*Last updated: 2026-07-22. Rough completion: ~70%.*

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
| 6 | Component 3D real GRPO training (Kaggle) | 🔲 Pending — now unblocked |
| 7 | Eight-vector benchmark (static vs full vs +3D) | 🔲 Pending |
| 8 | Layer 5 — dashboard / console / override | 🔲 Pending |
| 9 | Grow the pytest suite | 🟡 Ongoing (22 tests) |

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

## Phase 6 — real GRPO training (unblocked, pending)

Now cleared: the measurement carries signal (D), the knob is non-inert (C), the
reward is honest (A/B), and the loop demonstrably closes a knob-matching gap
(5b). Replace the v1 heuristic inside `propose_update()` with a policy-gradient
loop (torch, Kaggle P100), same reward + `LabeledEpisode → ProposedUpdate →
apply_update` contract. Open question to answer with it: does the *learned*
policy beat the directional heuristic, and does a knob-matching gap arise
naturally on a larger, held-out attack set? Scale red-team campaigns (more
directives/targets/families) on Kaggle.

## Phases 7–9 — later

- **7 · Benchmark:** eight attack vectors (Du et al. / MCPSecBench), static
  baseline vs full AdaptiShield vs AdaptiShield+3D; reuse `red_team/evaluator.py`.
- **8 · Layer 5:** audit dashboard, policy inspection console, manual override
  (data already emitted by telemetry + campaigns).
- **9 · Tests:** grow the suite; the 3 validated pipeline episodes are natural
  regression cases.

---

## Known open items (carried forward)

- `masked_hypothetical` flaky at 3B — caught in 4/5 runs; egress backstop holds ASR=0% when missed.
- 3C sanitisation of softened directives incomplete.
- Latent FPR: benign mail naming a recipient can score 2 under the fix-D probe;
  needs a "send-to-named-recipient" benign control and distributional FPR.
