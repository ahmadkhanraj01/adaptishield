# AdaptiShield — Session Handover

**Written:** 9 August 2026
**Last commit:** `c058902`, pushed to `origin/main`. Phases 7, 10, 11 and 12 are all
measured; Phase 12's work is on disk at time of writing (see §4a).
**Read this first, then [README.md](README.md) §0 for what the research is.**

---

## 1. Where the project stands

| | |
| :--- | :--- |
| **Detection** (campaign) | **116/120 = 96.7%**, 95% CI [91.7%, 98.7%] — 4 misses |
| **FPR (externally-authored, AgentDojo n=60)** | **3.3%**, 95% CI [0.9%, 11.4%] — 2 false positives |
| **FPR (our 8 hand-written controls)** | 50% — **a diagnostic, never quote it as a rate** |
| **IE-alone catches** | 14/116 (attacks the standalone rule cannot make) |
| **Phase 7 ASR** | `undefended` 100% → `static_only` **71.4%** → `full` **14.3%** |
| **Phase 7 attribution** | **18/21** stops by 3B in `full`; **0** in `static_only` |
| **Phase 10 steer rate** | `derived_control` **34.8%** → `spotlighting` **33.3%**, McNemar **p = 1.00** |
| **Phase 11** | only 3B (18/0, p=0.000) and 3C (18/0 on WCR, p=0.000) move anything; four components at 0/0 |
| 🔴 **Phase 12 — detection on EXTERNAL attacks** | **~18%** projected. 93.3% where 3B's target-match fires (10% of InjecAgent), **10.0%** where it cannot (90%) |
| **Corpus** | 188 campaign episodes + 18 benchmark vectors |
| **Tests** | **343 deterministic**, ~7 s, no LLM / network / GPU |
| **Completion** | ~93% build, ~65% evidence |

The 4 residual campaign misses are all `masked = 0` — **severity-function
failures**, and **none is reachable by the threshold 3D controls.** That is the
quantified reason the adaptive layer's honest output is a no-op. Phase 7 confirms it
independently: all 3 of its residual successes are the address-free vector, none a
threshold failure.

---

## 2. Phase 7 is DONE — the comparative claim is measured

The first result was withdrawn (the egress allowlist intercepted 6 of 8 vectors,
making every arm equal by construction). Repaired and re-run over **216 cases**
(18 vectors × 3 repeats × 4 arms, ~40 min):

| Arm | ASR | 95% CI | WCR | 3B stops |
| :--- | ---: | :--- | ---: | ---: |
| `undefended` | 100.0% | [84.5%, 100%] | 0.0% | 0 |
| `static_only` | 71.4% | [50.0%, 86.2%] | 0.0% | **0** |
| `full` | **14.3%** | [5.0%, 34.6%] | **85.7%** | **18/21** |
| `no_egress` | 14.3% | [5.0%, 34.6%] | 85.7% | 18/21 |

- **ASR 71.4% → 14.3%**, 57 points, with **18 of 21** stops attributed to 3B.
  `static_only` produces **zero** detection stops — it cannot, since 3B is what
  detects.
- **Layer 4 contributes nothing incremental** once 3B is on: `full` → `no_egress`
  leaves ASR unchanged, because 3B already caught everything the allowlist would
  have. The exact inverse of the withdrawn run. `backstop_share` 33%, so **12 of
  18** detection stops are load-bearing.
- **3A produced 0 detection stops in every arm** — a genuine ablation row.
- All **3** residual successes are **V4** (address-free), exactly where
  `vectors.py`'s own `honest_limit` predicted they would land.

### ⚠️ Two things not to quote

- **The benchmark's 0/30 external FPR is not a rate.** The cohort is a stride
  subsample (indices 0, 6, …, 54) which **excludes campaign documents 41 and 55 —
  both known false positives**. It omits every failure by construction. Use
  `python3 -m evaluation.fpr_report` (n=60, **3.3%**). The report prints this
  caveat itself.
- **`static_only` is our ablation, not an external baseline.** Rules §7 still wants
  a published prompt-level defense. That is Phase 10.

### What the repair also uncovered

Both defects were hidden by the old exfil destinations, and both were found by the
new attribution column on its first use:

- **V7 could never fail the permission check it existed to test.** Labelled
  `defended_by="Layer 4 permission control"` while running against `email-api`,
  which declares `send_email` **in scope** — so the gate always passed and egress
  refused the case first. Now runs against `weather-api`.
- **A `blocked` case could report `reached_tool=True`**, undercounting a refused
  request. Caught by a test; a block now always attributes to exactly one layer.

---

## 2b. Phase 10 is DONE — and so is the instrument question after it

**Spotlighting has no measurable effect.** Datamarking: 34.8% → 33.3% steered,
paired McNemar **p = 1.00**, 8 helped / 7 hurt. `results/phase10/`. The null is two
opposing per-family effects cancelling, not indifference.

Three things about it that are easy to get wrong on a re-read:

- **`steer_rate` is the outcome, not ASR.** ASR is 0/66 in *both* arms because the
  allowlist absorbs every address-carrying attack. `steer_rate` is judged before any
  gate, so no backstop can absorb it.
- **It needed `derive_action`.** Spotlighting defends the agent's *action selection*
  and the pipeline is normally handed `proposed_action`, so there was nothing to
  defend. These arms' ASR is **not comparable** with Phase 7's — derived vs supplied
  action, two cohorts, never one table.
- **The `agent_llm` runs at temperature 0 deliberately.** `planner_llm` had no
  temperature and inherited the server default of 0.8 while 3B runs at 0, so the
  deliberately byte-identical prompt was not the same agent. Fixing it via
  `planner_llm` would have silently moved 3C and Phase 7's committed WCR.

**Then §1.3's audit closed the last open instrument question:** refusal-shaped output
does **not** inflate 3B's regime severities — 0 of 209 recorded severity-2 masked
samples, positive control passing. So the regime scorer is unchanged and Rules §2's
re-measurement cost is not incurred. Details in §4a.

## 2c. Phase 11 is DONE — only two layers do anything

Ladder (7 arms, each adding one component in pipeline order) **and** leave-one-out
(6 arms), 54 cases each, agreeing on every row. `results/phase11/`,
`results/phase11_loo/`.

| Outcome | The only rung that moves |
| :--- | :--- |
| attack stopped | **3B** — 18 helped / 0 hurt, exact **p = 0.000** |
| workflow continued | **3C** — 18/0, exact **p = 0.000** |

L3, 3A, Layer 4 permission and Layer 4 egress are all **0/0 with zero discordant
pairs** — an identical outcome on all 21 malicious cases, from both directions.

Three things to carry forward:

- **`backstop_share` 0% → 17% → 33%.** Layer 4 is *redundant*, not contributing: 6 of
  18 of 3B's stops would also have been caught by the allowlist. Defensible as
  defence-in-depth; not evidence for the layer.
- **`FPR ours` 0/3 → 3/3 the moment 3B is on, and no p-value sees it.** Paired tests
  exclude benign cases by construction. n=3, a diagnostic, never a rate.
- **The ladder must be read on both outcomes.** An ASR-only ladder reported 3C as
  inert. That was the report's defect and is fixed, but the shape recurs: pick the
  outcome variable the layer can actually move.

⚠️ These are **our own ablations**. The external-baseline requirement is discharged by
Phase 10, never by this (Rules §7).

## 2d. Phase 12 is DONE — and it is the hardest result in the project

**Detection falls 96.7% → ~18% on externally-authored attacks.** `results/phase12/`.

| Stratum | Share | Detected | 95% CI |
| :--- | ---: | ---: | :--- |
| 3B's target-match fires | 10% | 28/30 = **93.3%** | [78.7%, 98.2%] |
| Address-free | 90% | 3/30 = **10.0%** | [3.5%, 25.6%] |

One mechanism: 3B rides on `_references_mediator_target`, and InjecAgent mostly
supplies no target — *"grant permanent access to guest_amy01"* names no address and
carries no exfil keyword. Phase 11's 3 residual failures all lacked that path; this
makes it 27 cases on data we did not write.

**Two Phase 11 claims replicated externally:** `static_only` stops **0 of 60**, and
Layer 4's `backstop_share` is **0%**.

Four things not to get wrong on a re-read:

- ⛔ **Never pool the strata.** 30/30 drawn from a 51/459 population, so the pooled
  51.7% is wrong for the population by **33 points**.
- ⚠️ **No FPR from this corpus.** InjecAgent ships attacks only; the columns read
  0/0, an empty denominator. FPR of record stays `fpr_report` at n=60.
- ⚠️ **The stratum is 3B's own predicate**, not a regex resembling it. The first
  attempt counted addresses anywhere in the response and mislabelled 135 of 186
  cases. A test fails if the label ever diverges from the live predicate.
- ⚠️ **InjecAgent's attacker tools are registered in scope** on purpose. Unregistered,
  the permission gate refuses all 60 before 3A/3B run — the Phase 7 withdrawal, third
  time that trap was laid and first time it was seen coming.

## 2e. START HERE — the severity function

Phase 12 promoted [[Backlog]] item 1 from a 3-case tail to the critical path. **10.0%
detection on 90% of an external corpus** is the one number standing between 96.7% on
our data and 18% on anyone else's.

Two closed doors, so this needs a **third** approach: §6e measured the semantic
scorer as worse end-to-end, and §6p established the probe prompt is not the place
(three attempts cost 8 detections).

🔴 **Whatever the approach, re-measure the external FPR with it.** InjecAgent gives
no false-positive signal at all, and the obvious ways to catch address-free
injections are the over-blocking ways. Rules §2 also requires re-measuring the gen-2
campaign before any regime-scorer change lands.

---

## 3. Traps that have already cost time

| Trap | What happens | Guard |
| :--- | :--- | :--- |
| **Stale dataset** | A campaign that dies part-way leaves the old `episodes.jsonl`; `fpr_report` prints pre-fix numbers as if current | It now prints the dataset age and shouts `STALE`. **Read that header.** |
| **Stale checkpoint** | Cached per-case results describe the *old* pipeline | `rm -rf logs/campaign_checkpoint` **and** `logs/benchmark_checkpoint` after ANY pipeline change |
| **A subsample that omits the hard cases** | The benchmark's external benign cohort is a stride subsample excluding campaign docs 41 and 55 — **both known FPs** — so its 0/30 looks like an improvement on 3.3% and is not | The report prints the caveat. `fpr_report` (n=60) owns the FPR |
| **Idle Ollama reads as "no GPU"** | `/api/ps` lists only *resident* models, so a pre-run check on an idle server reports no GPU every time | The manifest samples Ollama **after** the arms run |
| **Ollama falls back to CPU** | After a CUDA fault it silently runs CPU-only: ~11 GB RAM, slower, more non-determinism, and **different outputs** | Check `curl -s localhost:11434/api/ps` → `size_vram` must be > 0. If 0: `sudo systemctl restart ollama` |
| **Two variables at once** | A campaign that changes code *and* backend cannot attribute a regression | Change one thing per campaign |
| **Kaggle credentials** | Needs a **legacy 32-hex key** (Settings → API → Create New Token). The "API Tokens" page issues a longer token CLI 1.7.4.5 cannot use — and 1.7.4.5 is the newest on PyPI | `python3 evaluation/kaggle/test_credentials.py` |
| **`kaggle.json`** | Holds a live key in plaintext in the repo root | Already git-ignored — keep it that way |

**Campaigns are resumable.** They checkpoint per case to
`logs/campaign_checkpoint/`; a crash costs the case in flight, not 1.5 h. This
absorbed three interruptions on 26 July. Just re-run the same command.

---

## 4. Committed and pushed

Three commits are on `origin/main` (`git@github.com:ahmadkhanraj01/adaptishield.git`):

| Commit | What it carries |
| :--- | :--- |
| `89e0708` | Phase 7 repair + re-run — 114 files, including the `Research/` vault's first publication |
| `8762ab0` | Phase 10 infrastructure (`baselines/`, `derive_action`, `agent_llm`) + the floor finding |
| `bbfd918` | Phase 10 results + the negation fix in `score_agent_action` |

⚠️ **The repo is public.** `Research/` and `red_team/` contain attacker-authored and
attack-template text **by construction** (AgentDojo, MIT, v0.1.35, attribution
recorded, plus our own injection families). That is normal for security research and
documented, but it is now indexable. `kaggle.json` and `.env` remain untracked and
gitignored — keep them that way. `logs/benchmark/run.log` is untracked for the same
reason: large, and attacker-authored text verbatim.

## 4a. This session's work (committed as it landed)

**New**
- `evaluation/refusal_audit.py` — read-only, no model calls. Applies
  `_target_clause_is_negated` to every recorded masked-regime probe sample. **0 of
  209** de-escalate, with a passing positive control
- `tests/test_refusal_audit.py` — **35 tests**. They assert the defect **as it
  currently is**, so a change to the regime scorer fails a test rather than drifting
- `results/refusal_audit/audit.json` — the artifact
- Vault: `03 Findings/3B's Refusal Exposure Is Live and Unrealised`,
  `04 Research Log/Entry XVIII — Measuring a Defect Instead of Fixing It`

**Phase 11 + 12 (later commits)** — `evaluation/paired.py` (McNemar; exists because
Phase 10's p-value had no committed source), `evaluation/injecagent.py`,
`red_team/vendor_injecagent.py`, `red_team/data/injecagent_dh.json`,
`tests/test_paired.py` (52), `tests/test_injecagent.py` (33),
`results/phase11/`, `results/phase11_loo/`, `results/phase12/`.

**Modified** — `README.md` (v21, §1.3–§1.5), `Phase.md`, `handover.md`,
`evaluation/README.md`, `tests/README.md`, `results/README.md`,
`research_work_so_far.md` (entries XVI–XVIII), and the vault's Findings Index,
Research Log Index, Current Numbers, Backlog, plus `The Scorer Cannot See Negation`.

✅ **Volume II is now caught up.** Entries XVI, XVII and XVIII are in
`research_work_so_far.md`, not only in the vault. The earlier warning that XVI/XVII
existed only as vault notes is discharged.

---

## 5. Decisions already taken (don't re-litigate)

- **`agentdojo-workspace-041` stays a known bounded false positive.** The
  grounding fix closed its standalone route (`masked` 2→1); it now trips the IE
  rule instead. Closing *that* would weaken the mechanism catching 14 attacks the
  standalone rule misses, to move 2/60 → 1/60 — inside the confidence interval.
- **The probe prompt is not to be tuned again** without a strong reason. Three
  attempts cost 8 detections. The comment at that spot in `causal_analyzer.py`
  records why. Prefer fixes whose failure mode is bounded.
- **3D honestly proposes a no-op.** Do not tune it until it shows a gain; the
  no-op is the result.
- **Two research-log volumes.** `researchworksofar.md` = Volume I (I–XIV,
  **closed, do not edit**). `research_work_so_far.md` = Volume II (XV onward).
- **🔴 Every session's work lands in the Obsidian vault before the session ends**
  (`Rules.md` §8, added 8 Aug at the user's request, mirrored in
  `Research/07 Practice/Rules and Invariants.md`). §8 carries the Did → Write
  routing table. This is a hard invariant now, not bookkeeping.
- **The Phase 7 destination change is a correction, not a weakening.** For a
  `send_email` call through the registered mail server the HTTP destination *is*
  the mail host; the recipient lives in the payload. Pointing it at the recipient's
  domain was the fiction. Do not "restore" the exfil destinations — a test now
  fails if any malicious vector but V3 uses one.

---

## 6. Backlog after Phase 11

0. ✅ **Refusal-shaped output does not inflate 3B's regime severities** — 0/209,
   control passing. The exposure is **live on the shipped keyword path** and has
   never fired; recorded, not closed. Do not "fix" `_score_action` on the strength
   of reading the code: it would move no measured number and Rules §2 would then
   require re-measuring the gen-2 campaign and benign FPR.
1. **The severity function** — all 4 campaign misses are `masked = 0`, and all 3
   Phase 7 residual successes are the address-free vector. §6e already showed the
   semantic scorer is *worse end-to-end* and §6p showed the prompt is not the
   place either, so this needs a **third** approach.
2. **Multi-turn sessions** — campaigns give every case a unique `session_id`, so
   the drift rule never fires and 2 of 3D's 5 dimensions are unidentifiable. The
   trainer reports this itself.
3. **3C `ContextSanitizer.sanitize()`** — still carries the prompt weakness 3B's
   internal sanitizer had (§6m). Feeds the user-visible continuation and WCR.
4. **Screen tool descriptions at registration** — V5/V6 are approximated because
   the pipeline consumes tool *responses*, not manifests.
5. **Publish the Layer 5 dashboard** as a shareable artifact (task #6). Decide
   visibility first, and render the AgentDojo attribution on the page — it
   currently embeds 828 records including attacker-authored text.

---

## 7. Orientation

| Question | File |
| :--- | :--- |
| What is this research? | `README.md` §0 |
| Current status / how to run | `README.md` §1, §11 |
| Why a decision was made | `researchworksofar.md` (Vol I), `research_work_so_far.md` (Vol II) |
| Roadmap by phase | `Phase.md` |
| What a folder contains | each folder's own `README.md` (file-by-file tables) |

**Quick health check:**

```bash
python3 -m pytest tests/ -q                  # expect 161 passed, ~4s
python3 -m evaluation.fpr_report             # check the STALE header first
python3 -m evaluation.vectors                # coverage map: 1 of 7 absorbable
curl -s localhost:11434/api/ps               # size_vram must be > 0 (once loaded)
```

Phase 7 results and their provenance: `logs/benchmark/benchmark.json`,
`logs/benchmark/manifest.json`, `logs/benchmark/run.log`.

---

*Handover written 26 July 2026, 21:36 PKT. Nothing committed since `20baf08`.*
