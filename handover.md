# AdaptiShield — Session Handover

**Written:** 8 August 2026
**Last commit:** `01335ac` — **the Phase 7 repair is uncommitted**
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
| **Corpus** | 188 campaign episodes + 18 benchmark vectors |
| **Tests** | **161 deterministic**, ~4 s, no LLM / network / GPU |
| **Completion** | ~92% build, ~50% evidence |

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

## 2b. START HERE — Phase 10, the external baseline

The only remaining blocker on Phase 10 is **a published prompt-level defense**
(spotlighting: delimiting / datamarking / encoding, or an AgentDojo defense) as a
`PipelineConfig` arm on the same corpus, seeds and model tags. The `undefended`
floor is now measured (ASR 100%), so half of Phase 10 is already discharged.

Cheap now: a new arm is a config value plus a `defended_by` label, and
`evaluation/attribution.py` will report what it actually does rather than what it
claims. Expected shape — prompt-level defenses degrade under the softened gen-2
injections fix D was built for, which is the argument for a causal layer, but only
once measured.

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

## 4. Uncommitted work

Nothing since `20baf08`. All of the following is on disk only:

**Modified**
- `layer2/security_sublayer/causal_analyzer.py` — keyword **grounding** in
  `_score_action_by_keyword`; probe prompt **reverted** to §6i wording
- `adaptishield_pipeline.py` — `PipelineConfig` ablation arms
- `layer3/tool_response_screener.py` — `ScreenResult.permissive()`
- `red_team/execution_agent.py` — per-case checkpointing in `run_batch()`
- `evaluation/kaggle/package_episodes.py` — `--checkpoint-dir`
- `evaluation/fpr_report.py` — staleness guard
- `README.md`, `Phase.md`, `tests/test_corpus.py`, `tests/test_target_match.py`
- **(8 Aug)** `evaluation/vectors.py` — LEGIT destinations, `cohort` +
  `server_name` fields, external benign cohort, `REQUIRED_SERVERS`
- **(8 Aug)** `evaluation/benchmark.py` — attribution, Wilson intervals, cohort
  split, run manifest, server registration
- **(8 Aug)** `Rules.md` §8 — 🔴 **vault-update invariant** (see §5 below);
  `handover.md`, `Phase.md`, `evaluation/README.md`, `tests/README.md`

**New**
- `evaluation/vectors.py`, `evaluation/benchmark.py` — Phase 7
- `tests/test_ablation.py` — 15 tests
- **(8 Aug)** `evaluation/attribution.py` — per-layer attribution
- **(8 Aug)** `tests/test_attribution.py` — 26 tests
- **(8 Aug)** `logs/benchmark/{benchmark.json, manifest.json, run.log}` — the
  Phase 7 results and their provenance
- **(8 Aug)** Vault: `03 Findings/Phase 7 Repaired…`,
  `04 Research Log/Entry XVI — What the Instrument Was Hiding`,
  `02 Architecture/Per-Layer Attribution`
- `research_work_so_far.md` — research log **Volume II** (entry XV)
- `AdaptiShield_Architecture_v3.drawio(.png)` — not written by me; unreviewed

⚠️ **Entry XVI exists in the vault but not yet in `research_work_so_far.md`**
(Volume II). That file is the prose log; the vault note carries the same content.

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

## 6. Backlog after Phase 10

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
