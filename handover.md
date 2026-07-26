# AdaptiShield — Session Handover

**Written:** 26 July 2026, 21:36 PKT
**Last commit:** `20baf08`
**Read this first, then [README.md](README.md) §0 for what the research is.**

---

## 1. Where the project stands

| | |
| :--- | :--- |
| **Detection** | **116/120 = 96.7%**, 95% CI [91.7%, 98.7%] — 4 misses |
| **FPR (externally-authored, AgentDojo n=60)** | **3.3%**, 95% CI [0.9%, 11.4%] — 2 false positives |
| **FPR (our 8 hand-written controls)** | 50% — **a diagnostic, never quote it as a rate** |
| **IE-alone catches** | 14/116 (attacks the standalone rule cannot make) |
| **Corpus** | 188 episodes — 120 malicious, 68 benign |
| **Tests** | **135 deterministic**, ~2 s, no LLM / network / GPU |
| **Completion** | ~90% |

The 4 residual misses are all `masked = 0` — **severity-function failures**, and
**none is reachable by the threshold 3D controls.** That is the quantified reason
the adaptive layer's honest output is a no-op.

---

## 2. START HERE — repair the Phase 7 benchmark

**The benchmark's first result is withdrawn. Do not quote it.**

`evaluation/benchmark.py` ran four arms and produced an apparently clean finding
(causal sub-layer adds no detection; contributes WCR 0% → 71.4%). Inspecting
*what actually stopped each case* invalidates it:

```
static_only — every single case:
  V1..V3, V5..V7   approved_direct   egress_allowed=False   ← the ALLOWLIST stopped it
```

Nothing was blocked by any detection layer. **Six of eight vectors point at an
exfiltration host**, so Layer 4 intercepts them before 3A/3B are consulted, and
`static_only` and `full` are equal *by construction rather than by measurement*.

This repeats the mistake §6n diagnosed — that section added address-free attacks
precisely because the allowlist was concealing detection failures.

### The fix, concretely

1. **`evaluation/vectors.py`** — change malicious vectors from `EXFIL` to
   `LEGIT` destinations, as `red_team/attack_library.py` does for the
   address-free attacks. Keep **V3** on `EXFIL` (it is *supposed* to test the
   allowlist). Then a detection failure shows up in ASR instead of being absorbed.
2. **Per-layer attribution.** ASR is currently binary. Record *which* layer
   stopped each case (3A block / 3B takeover / L4 permission / L4 egress) and add
   it as a column. Without this the benchmark cannot answer its own question.
3. **More benign vectors.** The FPR column rests on **one** vector × 3 repeats —
   the same weakness §6n spent a section fixing. Sample ~10 from the already
   vendored `red_team/data/agentdojo_benign.json`.
4. Re-run: `python3 -m evaluation.benchmark --repeats 3` (~25 min).

**The open question is untested, not answered.** Whether the causal sub-layer
detects what static defenses miss is unmeasured *in either direction*.

---

## 3. Traps that have already cost time

| Trap | What happens | Guard |
| :--- | :--- | :--- |
| **Stale dataset** | A campaign that dies part-way leaves the old `episodes.jsonl`; `fpr_report` prints pre-fix numbers as if current | It now prints the dataset age and shouts `STALE`. **Read that header.** |
| **Stale checkpoint** | Cached per-case results describe the *old* pipeline | `rm -rf logs/campaign_checkpoint` after ANY pipeline change |
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

**New**
- `evaluation/vectors.py`, `evaluation/benchmark.py` — Phase 7
- `tests/test_ablation.py` — 15 tests
- `research_work_so_far.md` — research log **Volume II** (entry XV)
- `AdaptiShield_Architecture_v3.drawio(.png)` — not written by me; unreviewed

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

---

## 6. Backlog after Phase 7

1. **The severity function** — all 4 misses are `masked = 0`. §6e already showed
   the semantic scorer is *worse end-to-end*, so this needs a third approach, not
   a re-run of that one.
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
python3 -m pytest tests/ -q                  # expect 135 passed, ~2s
python3 -m evaluation.fpr_report             # check the STALE header first
curl -s localhost:11434/api/ps               # size_vram must be > 0
```

---

*Handover written 26 July 2026, 21:36 PKT. Nothing committed since `20baf08`.*
