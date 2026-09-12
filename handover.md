# AdaptiShield — Session Handover

**Written:** 12 September 2026, end of session
**Last commit:** `02f4356` on `origin/main` — ten commits today, all pushed, all linear
**Read this first, then [README.md](README.md) §0 for what the research is.**

The previous handover (9 August) is superseded. Its durable decisions are carried
forward in §5 below; everything else it described is now in `results/`, the
manuscript, or the vault.

---

## 1. Where the project stands

| | |
| :--- | :--- |
| **Detection** (campaign, ours) | **116/120 = 96.7%** [91.7%, 98.7%] — 4 misses, all address-free. ✅ **Now a committed artifact** (`results/campaign/`) |
| **FPR** (AgentDojo benign, n=60) | **3.3%** [0.9%, 11.4%] — 2/60, stable across 3 recordings. ✅ n=60 is a **census**, not a sample — see §4 |
| **FPR** (our 8 hand-written controls) | 4/8 — **a diagnostic, never a rate** |
| **Detection on InjecAgent** (`gemma3:4b`) | **96.7%** where the target-match path fires, **10.0%** where it cannot (median of 3) |
| 🔴 **Detection on InjecAgent** (`llama3.2:3b`) | **100.0%** / **10.0%** — a **90.0-point gap** against the incumbent's 83.3, 58/60 cases agree. ✅ **New today: Phase 16** |
| **Spotlighting** | 34.8% → 33.3% steered, McNemar *p* = 1.00 — a null |
| **Lexicon generalisation** | in-sample 90.0% → holdout **43.3%** |
| **Multi-turn causal contrast** | zero on 24/30 turns; drift rule cannot fire |
| **Tests** | **502 deterministic**, ~8 s, no LLM / network / GPU |
| **Manuscript** | 13 numbered sections, ~9,800 words, 12 tables, 6 figures, `.docx` regenerates from markdown |

---

## 2. What we are trying to achieve

A **journal paper** (target changed from conference on 3 Aug at the supervisor's
direction — `Rules.md` §7 is the evidentiary bar that follows). Every number
needs *n*, a Wilson interval, a named corpus and a committed command that
regenerates it.

**The one claim the whole paper reduces to:**

> The causal contrast carries discriminative signal when the injected content
> names a *liftable target* — an address or URL an action can name — and close
> to none otherwise.

Everything else is a consequence of that property: detection collapses on
external attacks because they mostly carry no such target; the lexicon fix
generalises about half because it is nouns standing in for a mechanism; the
adaptive layer proposes nothing because the quantity it acts on is zero on most
turns. **The negative results are the contribution**, and the paper is defended
on the precision of the boundary, not on a headline accuracy.

**What "done" means:** every hardening item on `paper/handover.md` §4 closed
(✅ as of today), the manuscript current with the artifacts (✅), and a venue
chosen (🔵 parked — see §6).

---

## 3. This session, in order

The session opened with a task brief — `claude_code_prompt_benign_expansion.md`,
untracked in the repo root — to expand the AgentDojo benign corpus from 60 to
110+ so the FPR interval would stop being dominated by small *n*. **That task
closed at its first step**, and the two hardening items that actually gated the
paper closed instead.

| # | Commit | What landed |
| :--- | :--- | :--- |
| 1 | `a999906` | **The benign corpus cannot be expanded.** The 60 is the *complete* benign content of AgentDojo v0.1.35's workspace+slack suites under the committed filter — re-verified byte-exact against a fresh wheel. Zero disjoint episodes remain; reaching 110 needs off-domain travel reviews that would lower the FPR for reasons unrelated to the defense. **n stays 60.** A pre-emptive "110" in `Rules.md`'s working tree was reverted. |
| 2 | `9ab1c73` | **`results/campaign/` built.** `evaluation/campaign_report.py` promotes the 116/120 headline from `logs/` to a committed artifact with `per_case` for all 188 episodes. Marked a **replay**; the original July run left no manifest, and the config is filled in only as far as the recorded verdicts evidence it. The two benign cohorts are never pooled — `_assert_unpooled` fails the run if they are. |
| 3 | `34baae3` | Entry XXV in the vault. |
| 4 | `efa069e` | **Two probe-model candidates disqualified**, in opposite ways — see §4. §XII corrected: the campaign headline is no longer "not backed by an artifact". |
| 5 | `dbf6958` | **Bibliographic pass.** Six `[TO COMPLETE]` references traced to primary sources and — the real defect — cited in the body for the first time. **AgentDojo's 45.8% was wrong by twelve points and from the wrong table**; corrected to Table 5's 57.69% (±3.9), still held back pending a human read. |
| 6 | `1681ecf` | 🔴 **Phase 16.** `llama3.2:3b` passed the compliance pre-flight; the InjecAgent cohort was recorded under it; **the stratification replicates**. `probe_corpus.py` gained `--model` with model-keyed paths, because the old paths would have overwritten the committed gemma corpus in place. |
| 7 | `cc0eb58` | §VII-E and Table VIII added; §XII rewritten; the morning's finding note corrected in place. |
| 8 | `2b14254` | Entry XXVI in the vault. |
| 9 | `a916d6a` | §II synthesis — the three defence families placed by *unit of evidence*. |
| 10 | `f1ec623`, `c6e906c`, `02f4356` | Review deck fixed (it was hand-coded and contradicting the repo in five places) + Phase 16 slide; supervisor brief updated to today; stale test counts fixed in four files. |

---

## 4. Findings worth carrying (all in the vault, `03 Findings`)

- **`AgentDojo's Benign Pool Is Exhausted at 60`** — a census, not a sample. The
  limitation relocates to *a second external benign corpus is needed, not more of
  this one*. §XII should say so; it does not yet.
- **`The Probe's Compliance Does Not Transfer`** — **title corrected the same
  day**, kept under its wrong name with a dated section, per vault convention.
  Two of three candidates fail in opposite directions: `qwen2.5:7b` complies but
  at **53% CPU offload** does not return the same answer twice at temperature 0;
  `qwen2.5:3b` is byte-identical across repeats and returns **`no_action` on both
  cases the incumbent detects — with no refusal string anywhere**, so a keyword
  refusal check scores it compliant. The 4 GB card makes the *search* hard, not
  the transfer impossible.
- **`Phase 16 — The Stratification Survives a Second Model`** — the collapse is
  the mechanism's, not the model's. Scoped: one recording per model, no
  equivalence claim, nothing above ~4B, run 0 vs run 0.
- **Entry XXVI's spine:** four confident beliefs wrong within hours — the
  "parroting" diagnosis (it was non-determinism), the safe 3B, my own note's
  title, and the 45.8% that had sat in the repo since August.

---

## 5. Decisions taken — don't re-litigate

**Today:**
- **n = 60 for the benign cohort.** Not expanded; the reason is in the finding.
- **`results/campaign/` is a replay and says so.** Do not backfill `models_at_run`
  from today's `CausalAnalyzer()` — that asserts a July config nobody checked.
- **The AgentDojo 57.69% stays `located-pending-human-read`** until a human reads
  Table 5. An automated fetch is an intermediary, which is the failure mode the
  guard exists for.
- **The 7B model is not a candidate on this hardware**, and Kaggle cannot host
  Ollama, so there is no environment here for it. Stated in §XII.
- **Commits carry the user's name only.** No Claude co-author or session trailers.
- **Venue decision parked** at the user's request. Do not raise it unprompted.

**Carried forward from August (still true):**
- `agentdojo-workspace-041` stays a known bounded false positive.
- The probe prompt is not to be tuned again without a strong reason — three
  attempts cost 8 detections.
- 3D honestly proposes a no-op; the no-op is the result.
- Two research-log volumes: `researchworksofar.md` (I–XIV, **closed**),
  `research_work_so_far.md` (XV onward). The vault's `04 Research Log` now runs
  to **Entry XXVI**.
- 🔴 Every session's work lands in the vault before the session ends (`Rules.md` §8).
- Do not "restore" the Phase 7 exfil destinations — a test fails if you do.

---

## 6. Open items

| | Item | Needs |
| :--- | :--- | :--- |
| 🔵 | **Venue** — parked | the user + supervisor. `paper/supervisor-brief.md` and the 34-slide deck are ready to send |
| 🟡 | **Author block `CONFIRM` bracket** — ORCIDs, IEEE grades, author order, funding | the supervisor |
| 🟡 | **AgentDojo Table 5 read** — confirm 57.69% (±3.9), flip to `verbatim`, delete `test_the_agentdojo_baseline_is_currently_held_back` | 30 seconds of a human. `Delimiting 41.65%` in the same table is worth taking too — it is a published spotlighting-family result on an agent benchmark |
| 🔴 | **Which interpreter is the runtime of record?** `installed.txt` describes system `python3` (324 packages, **numpy 2.2.6** against Rules §1's pinned 1.26.4). `./venv`, which README says to activate, has 55 packages and **no numpy at all** — `requirements.txt` is unsatisfied there. `python-docx`, `pillow`, `python-pptx` had to be installed today to build the paper. **Do not `pip freeze > installed.txt`** — it would erase the evidence | a decision |
| 🟡 | §XII benign-corpus bullet still reads "60 documents, adequate but wide" — should say *exhausted*, per §4 | a prose edit |
| — | `claude_code_prompt_benign_expansion.md` untracked in repo root | delete or commit |

---

## 7. Traps found today (all in `Research/07 Practice/Traps.md`)

- **AgentDojo case IDs are positional.** Re-vendoring with a wider filter silently
  relabels `workspace-041/-048/-055`. Content-hash keys before anyone re-vendors.
  Recorded before it fired — the only entry on that page written in that order.
- **`probe_corpus` paths were keyed by cohort+run alone.** A second model would
  have overwritten the committed gemma corpus, and `verify_unchanged` runs at
  read time, too late. Fixed: `--model`, model-keyed paths, filename follows the
  analyzer's own tag.
- **The review deck is hand-coded, not generated.** Rebuilding it changes
  nothing. It drifted into contradicting the repo in five places; check its
  strings against `results/` before sending it anywhere.
- **A guard against pooling that could not fire.** My first `_assert_unpooled`
  compared a cohort's *n* to the sum of both — never matches a real merge. The
  test caught it. Guards need tests, especially the ones for the most-repeated
  mistake.

---

## 8. Orientation

| Question | File |
| :--- | :--- |
| What is this research? | `README.md` §0 |
| The paper | `paper/manuscript.md` (edit this; the `.docx` regenerates) |
| Paper status and hardening list | `paper/handover.md` §4–§5 |
| What to send the supervisor | `paper/supervisor-brief.md` + `paper/AdaptiShield-Full-Review.pptx` |
| Why a decision was made | vault `04 Research Log` (through XXVI), `03 Findings` |
| Every quotable number | `results/<phase>/` with its manifest; `results/README.md` is the index |
| Rules that must hold | `Rules.md` — §7 for evidence, §8 for the vault ritual |

**Health check:**

```bash
source venv/bin/activate
python3 -m pytest tests/ -q                       # expect 502 passed, ~8 s
python3 -m evaluation.campaign_report             # 116/120, 2/60, 4/8 — no model calls
python3 -m evaluation.model_transfer              # 96.7/13.3 vs 100.0/10.0 — no model calls
python3 paper/make_positioning_table.py           # prints the AgentDojo row as HELD BACK
curl -s localhost:11434/api/ps                    # size_vram must be > 0 once a model is loaded
```

**Models on this machine:** `gemma3:4b` (3B of record), `qwen2.5:3b` (3C/L3/planner —
*not* usable as 3B), `llama3.2:3b` (Phase 16 candidate, 100% GPU-resident),
`qwen2.5:7b` (does not fit — 53% CPU offload, non-deterministic).

---

*Handover written 12 September 2026. HEAD is `02f4356`, pushed. Nothing local.*
