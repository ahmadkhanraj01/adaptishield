# AdaptiShield — Phases & Progress

**What this file is:** the roadmap and progress tracker — what is done, what is
in flight, and what comes next, organized as phases. The root [README.md](README.md)
Section 13 holds the detailed task list; this file is the higher-altitude view.
See [Architecture.md](Architecture.md), [Design.md](Design.md), [Rules.md](Rules.md)
for structure / rationale / constraints.

*Last updated: 2026-08-08 (session 5 — Phase 7 repaired and re-run). Build ~92%
complete; **evidence ~50%**.*

---

## ⚠ Target changed: journal, not conference (2026-08-03, supervisor)

The paper goes to a **journal**. The architecture does not change. What changes
is the **critical path**: it is no longer "finish 3D", it is "produce evidence a
reviewer will accept". Concretely:

| | Conference framing (old) | Journal framing (new) |
| :--- | :--- | :--- |
| Headline claim | we built a layered adaptive defense | we **measured** it, against baselines, and bounded where it fails |
| Enough evidence | one campaign, point estimates | multi-run distributions + Wilson CIs, ≥2 external baselines, per-component ablations |
| Negative results | a liability to minimize | a **contribution** — generalization gaps in adaptive defense learning |
| Bottleneck | Phase 6 (3D / GRPO) — **done** | Phase 7→10 (benchmark, ablations, baselines, second benchmark) |

**Why the negative results get *better*, not worse, under this move.** Three
findings are now first-class contributions rather than footnotes: (i) an RL
policy proposing a security change its own reward scored lower, which
`apply_update` would have accepted silently; (ii) the one gain GRPO ever found
being an artifact of a hand-written benign corpus (36 FP of 68 on external
data); (iii) every trainer safeguard working correctly and none of them being
able to see outside the corpus. Together they are the empirical argument for the
Layer 5 human gate. Journals have room for that; conferences usually do not.

**🔵 Blocking decision — pick the journal before writing (see bottom of file).**

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
| 6 | Component 3D real GRPO training (Kaggle) | ✅ **Executed on Kaggle (§6o)** — torch backend ran for the first time and agrees with pure-Python to **exactly zero**. No natural gap (§6l/§6m). **The P100 cannot run PyTorch** (sm_60 vs sm_70+) — GPU premise retired, CPU fallback costs nothing (0.27 s workload) |
| 6b | Diagnose + fix the 15 residual 3B misses | ✅ Done — one defect, **114/114 caught** (§6m) |
| 6c | **Fix the evaluation corpus** (address-free attacks + external benign) | ✅ **Done (§6n)** — 188 episodes; **FPR 3.3% [0.9%, 11.4%]** vs AgentDojo benign; IE catches **13** the standalone rule misses (was 0) |
| 6d | Joint GRPO action space + propose-and-verify | ✅ **Done (§6n)** — 5 dims / 720 actions; the one gain it found was a **corpus artifact**, and its own policy proposed a reward-*decreasing* change 3× |
| 7 | Eight-vector benchmark (static vs full vs +3D) | ✅ **Done (2026-08-08)** — first result withdrawn, repaired, re-run over 216 cases. **ASR `static_only` 71.4% → `full` 14.3%**, 18/21 stops attributed to 3B, `static_only` produces **zero** detection stops, and Layer 4 adds **nothing incremental**. Per-layer attribution added; two instrument defects found and fixed |
| 8 | Layer 5 — dashboard / console / override | ✅ **Done** — 4 components, stdlib only, 20 tests. Gate recomputes evidence rather than trusting the proposal; found that every proposal's `blocked_patterns` are **inert** (3A matches `proposed_action`, trainer harvests from `flagged_markers`) |
| 9 | Grow the pytest suite | 🟡 Ongoing (**161 tests**, ~4 s, no LLM) |
| **10** | **External baselines** (undefended + spotlighting/data-marking) | 🔵 **NEXT — journal-mandatory.** Undefended arm now measured (ASR 100%); the published prompt-level defense is still absent |
| **11** | **Per-component ablations** (3A / 3A+3B / +3C / +L4 / full / +3D) | 🔲 Not started — arms exist, matrix does not |
| **12** | **Second benchmark: InjecAgent** (external validity) | 🔲 Not started |
| **13** | **Manuscript + reproducibility artifact** | 🔲 Blocked on the journal decision |

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
   `KAGGLE_USERNAME`/`KAGGLE_KEY`; verified via `evaluation/kaggle/test_credentials.py`).
2. ✅ Expanded campaign + GRPO trainer → **no natural gap** (§6l); probe
   diagnostic found one defect behind all 15 misses → **114/114** (§6m).
3. ✅ **Corpus fixed (§6n) — and it changed a conclusion.** 188 episodes: 18
   address-free attacks + 60 benign vendored from AgentDojo (MIT, v0.1.35).
   - **FPR = 3.3%, 95% CI [0.9%, 11.4%]** — the first one worth quoting. The old
     4/8 is a diagnostic that located an architectural boundary, not a rate.
   - **IE is no longer redundant:** 13/115 malicious takeovers are caught by
     `IE >= 1` where `masked >= 2` would have missed (was 0/114). And 3C's
     `instructions_removed` cannot substitute for IE at all — the pipeline gates
     3C on takeover (`adaptishield_pipeline.py:132`), so the self-report does not
     exist at decision time.
   - **The one gain GRPO ever found was a corpus artifact.** The joint action
     space accepted `marker_weight:ignore previous = 1.0` for +0.8688 → +0.9046
     on my own benign controls; on AgentDojo's it yields **36 false positives of
     68 benign** and +0.6500. The marker fires on 30/60 external benign documents
     and 0/8 of mine.
4. ✅ **Trainer defect promoted to a finding.** The policy proposed a threshold
   change its own reward scored lower (+0.8683 vs +0.8688), and `apply_update`
   would have accepted it silently. Now: exact reward table in 1-D,
   propose-and-verify + minimality pass in the joint space. The guard has since
   fired twice more on live data (most recently +0.8329 vs +0.8330).
5. ✅ **Phase 6 executed on Kaggle (§6o).** `train_torch` / `train_joint_torch`
   had never run anywhere (no torch locally, tests torch-free). They now agree
   with pure-Python to **exactly zero** on incumbent reward, verdict and final
   action. Propose-and-verify rejected the policy's own choice a **fourth** time
   (+0.8330 vs +0.8329) on different hardware with a different RNG.
   - **The P100 cannot run PyTorch.** sm_60 vs a build needing sm_70+, and
     `torch.cuda.is_available()` returns True so it dies on first allocation.
     `_torch_device()` probes and falls back to CPU. Immaterial — the workload is
     0.27 s on CPU; Kaggle's value is that torch is importable there, not compute.
   - Six attempts, five defects. The worst was a status poll whose lowercase
     patterns never matched `KernelWorkerStatus.ERROR`, so every failure was
     reported as success with exit 0.
   - Credentials: the CLI needs a **legacy 32-hex key** (Settings → API → Create
     New Token). The newer "API Tokens" access tokens do not work with 1.7.4.5,
     which is still the newest on PyPI. `kaggle.json` is now git-ignored.
6. ✅ **Layer 5 built.** Audit dashboard + Policy Inspection Console + Audit Logs
   as one self-contained HTML file (`python -m layer5.audit_report --open`), and
   Manual Override as a CLI with an append-only decision log
   (`python -m layer5.review`). The gate recomputes evidence instead of trusting
   the proposal, recommends but never decides, and **found a live defect on its
   first run**: every 3D proposal's `blocked_patterns` are inert, because 3A
   matches them against `proposed_action` while the trainer harvests them from
   `flagged_markers`.
7. ✅ **Probe hallucination fixed at the scorer (§6p).** Detection **96.7%**
   (116/120, 4 misses), IE-alone catches **14/116**, external FPR unchanged at
   3.3%. Three rounds of prompt engineering were tried first and reverted — they
   cost 8 detections. The lesson: prefer the fix whose failure mode you can bound;
   a prompt load-bearing for detection trades a measured FP for unmeasured FNs.
   `workspace-041` remains a **known bounded false positive** — the grounding
   closed the standalone route (`masked` 2→1) and it now trips the IE rule
   instead. Left open deliberately: closing it would weaken the mechanism that
   catches 14 attacks the standalone rule misses, to move 2/60 → 1/60 inside a
   [0.9%, 11.4%] interval.
8. ✅ **Phase 7 done (2026-08-08) — the comparative claim is measured.** The first
   result was withdrawn (the egress allowlist intercepted 6 of 8 vectors, making
   every arm equal by construction); repaired and re-run over **216 cases**:

   | Arm | ASR | 95% CI | WCR | 3B stops |
   | :--- | ---: | :--- | ---: | ---: |
   | `undefended` | 100.0% | [84.5%, 100%] | 0.0% | 0 |
   | `static_only` | 71.4% | [50.0%, 86.2%] | 0.0% | **0** |
   | `full` | **14.3%** | [5.0%, 34.6%] | **85.7%** | **18/21** |
   | `no_egress` | 14.3% | [5.0%, 34.6%] | 85.7% | 18/21 |

   - **ASR 71.4% → 14.3%** (57 points) with **18 of 21** stops attributed to 3B;
     `static_only` produces **zero** detection stops.
   - **Layer 4 contributes nothing incremental** once 3B is on (`full` →
     `no_egress` leaves ASR unchanged) — the exact inverse of the withdrawn run.
     `backstop_share` 33% in `full`, so **12 of 18** detection stops are
     load-bearing.
   - **3A contributes 0 detection stops in every arm** — a real ablation row,
     consistent with the inert-`blocked_patterns` finding.
   - All **3** residual successes are **V4** (address-free), where the docs
     predicted the misses would land. **None is a threshold failure.**
   - ⚠️ The benchmark's **0/30 external FPR is not a rate** — the stride subsample
     excludes campaign documents 41 and 55, both known false positives. The
     campaign's **3.3% at n=60** remains the FPR of record; the report prints this
     caveat so the number cannot be lifted loose.
   - **Two instrument defects found by attribution on its first use:** V7 could
     never fail the permission check it existed to test (it ran against a server
     declaring `send_email` in scope, with egress refusing the case first), and a
     `blocked` case could report `reached_tool=True`. Tests 135 → **161**.
9. 🔵 **START HERE — Phase 10, the external baseline.** `static_only` is *our*
   ablation; Rules §7 requires a published prompt-level defense (spotlighting /
   data-marking) on the same corpus, seeds and model tags. Cheap now: a new arm is
   a `PipelineConfig` value plus a `defended_by` label, and attribution will report
   what it actually does rather than what it claims.
11. **Carried forward, unchanged by Phase 7** — the two standing limits on the
   detector, both still the largest levers:
   - **FPR side:** `agentdojo-workspace-041` is a birthday-party document with no
     email address in it; the probe *invented* one and scored 2 off the `forward`
     keyword. A real defect, and the largest single lever on FPR. Distinct from
     `agentdojo-workspace-055`, the genuine 3B/Layer 4 boundary (3B cannot tell an
     authorised recipient from an attacker-controlled one — Layer 4's job, a
     scoping result rather than a defect). **Neither is in the benchmark's stride
     subsample**, which is why its 0/30 must not be quoted as a rate.
   - **Detection side:** 4 of the 5 campaign misses are `masked = 0` — the keyword
     scorer does not match the probe's phrasing and there is no address to fall
     back on. **0 of the 5 are threshold failures**, which is why 3D proposes a
     no-op and why the remaining work is not in the adaptive layer. Phase 7 confirms
     this independently: all 3 of its residual successes are the address-free
     vector, none a threshold failure.
12. *(still open)* Settle the two questions on the Layer 5 artifact — visibility,
   and rendering the AgentDojo attribution — before publishing it.


## Phases 7 → 13 — the journal evidence chain

Ordered by dependency. Nothing below is optional for a journal submission; the
manuscript cannot make a defensible claim that these do not produce.

### 7 · Eight-vector benchmark — ✅ *done, and it unblocked everything*

Eight attack vectors (Du et al. / MCPSecBench) plus a ten-document external benign
cohort, over four `PipelineConfig` arms. Delivered: ASR / FPR / WCR per vector per
arm with `n` and Wilson intervals, **per-layer attribution**, and a run manifest.
See item 8 in the checklist above for the numbers.

The two artefacts it leaves for later phases: `evaluation/attribution.py` scores
every arm through one function, so Phase 11's matrix does not need to re-derive
attribution per arm; and the manifest format is the provenance record Phase 13's
reproducibility artifact needs.

### 10 · External baselines — 🔵 *NEXT; journal-mandatory, half-absent*

Our own `static_only` arm is an **ablation**, not a baseline; a reviewer will not
accept it as the comparison. Needed on the same corpus, seeds and model tags:

- ✅ **Undefended** — the floor, now **measured**: ASR **100%** [84.5%, 100%] over
  21 malicious cases. The vectors are strong enough to measure something, which was
  not previously established.
- 🔲 **A published prompt-level defense** — spotlighting (delimiting / datamarking /
  encoding) or an equivalent from the AgentDojo defense set. Re-implement inside
  the pipeline as an arm, so it shares one code path (Rules §7). **This is the only
  remaining blocker on Phase 10.**

Expected shape of the result: prompt-level defenses degrade under the softened
gen-2 injections that fix D was built for. That contrast *is* the argument for a
causal layer — but only if it is measured rather than asserted.

### 11 · Per-component ablations — *justifies the layering*

Without this, seven layers read as unjustified complexity. Minimum matrix:
`3A` · `3A+3B` · `3A+3B+3C` · `+Layer 4` · `full` · `full+3D`. Two results are
already half-known and should be reported as ablation rows rather than prose:

- **IE is non-redundant** — 13/115 (later 14/116) malicious takeovers caught by
  `IE >= 1` where `masked >= 2` misses. Run it as a 2×2 contingency table with a
  McNemar test; that is the form a reviewer expects.
- ~~**Layer 4 is the ASR backstop**~~ — **Phase 7 falsified this on its vector
  set.** With the egress allowlist off, layer-attributed detection and end-to-end
  ASR did **not** separate: `full` → `no_egress` left ASR at 14.3%, because 3B had
  already caught everything the allowlist would have (V3 included, as a takeover,
  before Layer 4 was consulted). Layer 4 was the backstop only while the *corpus*
  handed it every case. Report it that way — `backstop_share` 33% in `full` means
  **12 of 18** detection stops are load-bearing — rather than repeating the
  prediction. **3A**, by contrast, produced **0** detection stops in every arm.
- **3A's zero is a new ablation row** and it is not prose: the static pattern engine
  never fired on 21 malicious cases × 4 arms, consistent with the inert
  `blocked_patterns` defect Layer 5 found.
- **Reuse `evaluation/attribution.py`** for the whole matrix rather than
  re-deriving per arm — one scoring function across arms is the property that makes
  the rows comparable.

### 12 · Second benchmark: InjecAgent — *external validity*

One benchmark invites "does this generalize?". InjecAgent is the cheapest second
axis and the corpus work in §6n already proved the point that matters here: our
own benign corpus flattered the system by 36 false positives. A second external
corpus is the guard against a repeat.

### 13 · Manuscript + reproducibility artifact

Structure follows the evidence, and leads with the ablation + baseline tables
rather than the architecture diagram. The `results/` tree, the run manifests and
the deterministic test suite (110 tests, no LLM, 2 s) are the artifact. Layer 5's
self-contained HTML report is a strong figure: it shows the machine disagreeing
with itself and a human adjudicating, which is the paper's thesis in one image.

### Carried forward (unchanged in scope)

- **8 · Layer 5** ✅ done — audit dashboard, policy inspection console, manual override.
- **9 · Tests** 🟡 ongoing — the 3 validated pipeline episodes are natural regression cases.

---

## Known open items (carried forward)

- 🔵 **BLOCKING — which journal?** This is a scoping decision, not a formatting
  one: it sets how much evidence Phases 10–12 must produce and whether the FYP
  deadline is reachable at all. Ask the supervisor to pick.

  | Venue | First decision | Fee | Fit |
  | :--- | :--- | :--- | :--- |
  | **IEEE Access** | ~4–6 weeks | APC (~US$1,950) | Fast; tolerant of systems + negative results. Realistic against a degree deadline. |
  | **Computers & Security** (Elsevier) | ~3–6 months | none | Strong topical fit; expects the full baseline + ablation set. |
  | **IEEE TDSC** | 6–18 months | none | Highest prestige; **not reachable** within a fixed FYP deadline. |

  Secondary questions that follow from the answer: page/figure limits (the
  drawio architecture figure needs an **inverted colour scheme** for IEEE print),
  whether an artifact-availability statement is required, and author order with
  Aleena Khan and Dr. Laeeq Ahmed.
- 🔲 **Benign corpus is at 60 external episodes** — adequate for the current
  `[0.9%, 11.4%]` interval, but that interval is wide enough that a reviewer can
  ask for more. Growing the AgentDojo benign set tightens the single number most
  likely to be challenged.
- ~~`masked_hypothetical` flaky at 3B~~ — **closed (§6m)**: 24/24 across all targets
  after the normalized target match + greedy decoding.
- ~~3C sanitisation of softened directives incomplete~~ — **closed for 3B's
  `_sanitize_mediator` (§6m)**. Still open for the separate `ContextSanitizer`
  (3C) component, which shares the old prompt weakness and feeds the user-visible
  safe continuation + the WCR metric — left unchanged rather than altered silently.
- ✅ ~~**Latent FPR is load-bearing, not latent.**~~ **Closed (§6n).** Measured
  against 60 externally-authored AgentDojo benign episodes: **FPR = 3.3%, 95% CI
  [0.9%, 11.4%]**. The 8 hand-written controls are reported as a separate cohort
  and labelled a diagnostic, never pooled as a headline.
- ✅ ~~**IE is redundant with the standalone rule** (0/114).~~ **Closed (§6n).**
  With address-free attacks in the corpus, **13/115** malicious takeovers are
  caught by `IE >= 1` where `masked >= 2` would have missed. Separately, 3C's
  `instructions_removed` cannot substitute for IE at all, because 3C runs only
  after takeover is declared.
- 🔴 **The probe hallucinates actions on benign documents.** `agentdojo-workspace-041`
  contains no email address; the probe invented `eventplanning@company.com` and
  scored 2 off the `forward` keyword. §6i tuned the probe to always find an
  action; on benign content it fabricates one. Largest remaining lever on FPR.
- 🟡 **3B/Layer 4 boundary is a scoping result, not a defect.** `agentdojo-workspace-055`
  is meeting minutes with a real action item naming a real address. 3B fired
  correctly. 3B has no allowlist and should not — distinguishing an authorised
  recipient from an attacker-controlled one is Layer 4's egress allowlist. This
  bounds what any purely causal detector at this layer can deliver.
- 🔴 **An RL policy proposed a security change its own reward scored lower.**
  +0.8683 vs +0.8688, and `apply_update` would have accepted it silently. Fixed
  three ways (exact table in 1-D, propose-and-verify + minimality pass in the
  joint space) and the guard has fired twice more since. Recorded as a **finding**
  supporting the Layer 5 human gate, not as a bug fix.
- 🔴 **GRPO's only real gain was an artifact of my own benign corpus.** Verified
  and minimised on 128 episodes (+0.8688 → +0.9046); on the AgentDojo-extended
  corpus the same action gives 36 false positives of 68 benign. Every trainer
  safeguard worked; none can see outside the corpus.
- 🟡 **`risk_threshold` and `window_size` are unidentifiable** — the trainer
  reports reward exactly flat in both, because campaigns use a unique
  `session_id` per case so the temporal-drift rule never fires. Multi-turn
  sessions would make two of 3D's five dimensions learnable for the first time.
- **GRPO's learned distribution is near-uniform** — the argmax comes from the
  minimal-intervention tie-breaker, not from data. Do not present it as a trained
  policy while the corpus leaves it nothing to learn.
- **Greedy decoding is not literally deterministic.** §6m's "deterministic" is
  too strong: a fixed prompt returns byte-identical output 4/4, but across the
  campaign **2 of 564** regime severities were non-integral (the two samples
  disagreed 0.35% of the time), concentrated on long unstructured benign
  documents. At temperature 0 the `k_samples` are otherwise identical, so
  `require_consistent_ie` reduces to a mean comparison and the IE grid coarsens
  to whole numbers; `k_samples=2` is kept only for schema comparability.