# paper/ — Session Handover

**Written:** 17 August 2026 · **Submission target:** 14 September 2026 (28 days)
**Covers:** the positioning work, the review deck, and the manuscript build chain
added this session.

Read `README.md` in this folder for what each file *is*. This document is for the
next person to open the folder: what changed, what it decided, and what it left
undone.

---

## 1. What this session added

| Artifact | Built by | Status |
| :--- | :--- | :--- |
| `10-positioning.md` — §10, our numbers beside published ones | `make_positioning_table.py` | ✅ table generated, prose written |
| `external_numbers.json` — the published side, each value quoted verbatim | hand-maintained | ✅ 4 sources, 1 row held back |
| `manuscript.md` — the paper in submission form | hand-written | ✅ ~8,600 words, 13 sections |
| `AdaptiShield-Manuscript.docx` — 16 pp, 6 figures, 11 tables | `build_manuscript_docx.py` | ✅ regenerates from the markdown |
| `figures/fig0_architecture.{png,pdf}` — print-ready schematic | `make_architecture_figure.py` | ✅ new |
| `AdaptiShield-Full-Review.pptx` — 33-slide technical deck | `build_review_deck.py` | ✅ new |
| `tests/test_positioning_table.py` — 10 tests | — | ✅ passing (484 total) |

Everything above regenerates from a committed command. Nothing in the `.docx` or
the `.pptx` was typed into the file itself.

## 2. The rule the positioning work runs on

§10 is the first place the project prints numbers **it did not measure**, next to
numbers it did. That is the class of error a reviewer can check in one click, so
the generator enforces three things and `tests/test_positioning_table.py` pins
them:

- **Every published value carries the verbatim sentence it came from**, plus a
  URL and a `verified` flag, in `external_numbers.json`. A row with no quote does
  not exist.
- **A row not marked `verified: "verbatim"` is refused, not rendered.** It prints
  to stderr as a to-do. One row is currently held back this way — see §5.
- **A missing artifact raises.** A hole in a positioning table is
  indistinguishable from a measurement.

The same discipline as `results/`, extended to other people's numbers.

## 3. The four questions this session answered

Recorded here because they were decisions, not observations, and the next session
should not re-derive them.

**Are the numbers publishable?** Yes — as a measurement paper at IEEE Access /
*Computers & Security* level. No — as a "we built an adaptive defence that works"
paper. What carries it is the construction: per-stratum reporting with intervals,
paired tests on paired arms, pre-registration on the two experiments that could
have fooled us, withdrawn results reported beside corrected ones, and an artifact
where every number regenerates. Of the four external papers §10 quotes, **none
reports detection stratified the way we do** and two report headline numbers with
no interval at all.

**Continue or publish?** **Publish.** Harden for three weeks; do not extend. The
paper is finished as an argument — what is unfinished is armour. See §4.

**If we continue, what makes it more adaptive?** The bottleneck is the signal, not
the learner, so every real path fixes the signal first. Ranked:

- **D — learn what counts as a target.** *Best.* The entire collapse reduces to
  one mechanism, and "target" is currently a hand-coded URL scheme. Learning the
  class (bare hosts, phone numbers, usernames, file paths, account IDs) has a real
  gradient: schemeless was measured at +2 detections / +3 false positives. The only
  path where the adaptive component would have something to learn on corpora we
  already own.
- **A — continuous IE-only scorer on a larger model.** The logprob probe already
  scouted it: ACE saturates and tracks task relevance, but IE was exactly 0 on all
  6 benign turns and non-zero on 3 of 9 attacks. That is the one surviving thread.
  Needs a 7–14B model and proper calibration. Highest scientific value; a second
  paper, not 28 days.
- **C — adapt 3C instead of 3D.** 3C is one of only two components that moves
  anything (18/0 on WCR). Modest and real.
- **B — GRPO over thresholds (the Kaggle plan).** 🔴 **Do not.** Our own
  measurement kills it: residual misses score 0 on the masked probe, below both
  rules simultaneously, so no threshold reaches them. The reward is flat across the
  entire grid — we replayed it. GRPO on that reward learns a uniform distribution,
  which is exactly what §9 already reports.

**What should the title be?** Keep *AdaptiShield* as the system's name in the body;
keep "adaptive" out of the title, because §7 reports that layer as a measured
no-op and a reviewer who notices the mismatch reads everything after it more
suspiciously. Recommended, and now the title of `manuscript.md`:

> **Causal Prompt-Injection Detection Depends on a Liftable Target: A Stratified,
> Pre-Registered Evaluation in Tool-Integrated LLM Agents**

It states the claim rather than the system, signals the two things that make the
work defendable, and survives unchanged if a second model moves the numbers.

## 4. The hardening pass — three items, in ROI order

1. 🔴 **Re-run the probe on a second model family.** `qwen2.5:7b` or
   `llama3.1:8b`, both InjecAgent strata, n = 30 each; write to
   `results/phase16_model_transfer/` so it slots into §5 as a repeat rather than a
   new claim. Hours of compute. This is the single highest-value item, because
   "one model, one scorer" is the objection that lands first and hardest. **If the
   collapse does not replicate, that is a sharper result, not a lost one** — it
   localises the finding to model scale.
2. **Build `results/campaign/` with a manifest.** The campaign detection headline
   (116/120 = 96.7%) is the one number a reviewer cannot reproduce from the
   repository. Note the external FPR beside it *is* committed — it lives in
   `results/noise_floor/agentdojo_benign.json` (2/60, stable across 3 runs), which
   makes `results/README.md`'s "what's pending" line half stale.
3. **Related-work prose, and one verification.** §10 and manuscript §II supply the
   quantitative half. What is owed is the narrative pass placing the three defence
   families, plus reading AgentDojo's own table for the number in §5 below.

Anything beyond those three is the next paper.

## 5. What is knowingly unfinished

- 🟡 **AgentDojo's undefended important-instructions ASR (~45.8%)** reached us
  second-hand from a summary of their Table 2. It is in `external_numbers.json`
  marked `unverified`, the generator refuses to render it, and
  `test_the_agentdojo_baseline_is_currently_held_back` will tell you when someone
  verifies it. Ten-minute fix: read the table, replace the quote, set
  `verified: "verbatim"`, delete that test.
- 🟡 **The manuscript's author block is a placeholder.** It waits on the venue
  decision, which sets author order.
- 🟡 **Five references are `[TO COMPLETE]`** — AgentSentry, AutoMalTool,
  MCPSecBench, ETDI, MCP-RiskCue and the MCP security survey. The vault has
  reviewed notes on each; it does not have their bibliographic details, and they
  were not invented.
- 🟡 **Manuscript §II Related Work is thin on synthesis.** It covers what we
  measured against and states the stratification gap; the narrative placing the
  three families is the literature pass in item 3 above.
- 🔵 **The venue decision** remains the only genuinely blocking item.

## 6. Rebuilding everything

```bash
python3 paper/make_figures.py                # Figs. 2–5, from results/
python3 paper/make_architecture_figure.py    # Fig. 1, structural schematic
python3 paper/make_positioning_table.py      # rewrites §10's generated block
python3 paper/build_manuscript_docx.py       # → AdaptiShield-Manuscript.docx
python3 paper/build_review_deck.py           # → AdaptiShield-Full-Review.pptx
python3 paper/build_deck.py                  # → AdaptiShield-Overview.pptx
python3 -m pytest tests/ -q                  # 484 deterministic tests, ~10 s
```

Three conventions worth not breaking:

- **Edit `manuscript.md`, never the `.docx`.** The builder overwrites the Word
  file on every run, so an edit made in Word is lost and, until it is, diverges
  silently from the repository.
- **`make_architecture_figure.py` is separate from `make_figures.py` on purpose.**
  The latter guarantees every figure traces to a committed measurement; the
  architecture schematic traces to none, so it does not belong behind that
  guarantee. It does encode one result: 3B and 3C are drawn in colour because they
  are the only components that move an outcome.
- **The deck builders fail rather than ship a bad slide.** A heading longer than
  44 characters raises, and every shape is bounds-checked. Four headings were
  rewritten this session because of it.

## 7. One inconsistency this session found and fixed

Figure 2 plots the **mean** of the three recordings for the no-target stratum
(11%), while §10 and the manuscript quote the **median** run (10.0%). Both are
correct and they are not the same number. Every place that quotes it now states
which it is; if you touch either, keep them in step.
