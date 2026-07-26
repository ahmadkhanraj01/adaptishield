# evaluation — Experiments, Diagnostics and the Benchmark

**Status:** ✅ Experiments run and reported · 🟡 Phase 7 benchmark built, but its
first result is **withdrawn** (see below)

This folder is where claims get tested. Every figure in the root README's status
table traces back to a script here — and several of these scripts exist because a
claim made *without* one turned out to be wrong.

---

## Files

| File | Purpose | Status |
| :--- | :--- | :--- |
| `adaptive_loop_experiment.py` | The headline test: does applying a 3D proposal actually close the gap 3B left? Four phases on fresh pipelines, so drift cannot be mistaken for the update's effect. Produced the §6d **negative result** that defined fixes A–D. | ✅ Run |
| `holdout_generalization_test.py` | Re-runs a proposal against attacker addresses never seen in training. This is what exposed §6d's apparent gain as memorisation of a training literal. | ✅ Run |
| `mechanism_validation.py` | Deterministic (<1 s) check that the four causal regimes and the takeover rules behave as documented. Cheap enough to run before any campaign. | ✅ Run |
| `score_action_ablation.py` | Keyword scorer vs semantic (LLM-judge) scorer. Result (§6e): the semantic scorer is **more accurate per action and worse end-to-end**, so it ships off by default. | ✅ Run |
| `probe_diagnostic.py` | **Read-only** root-cause tool for 3B misses. Replays both regimes, explains every severity, and runs *matched controls*. Found the single defect behind all 15 misses (§6m). | ✅ Run |
| `fpr_check.py` | Adversarial A/B of the old (exact) vs new (normalized) mediator-target match over benign content. Used to *measure* the cost of loosening a rule rather than assume it. | ✅ Run |
| `fpr_report.py` | FPR with **Wilson intervals**, cohorts kept separate, plus a **staleness guard**. | ✅ Run |
| `ie_ablation.py` | Is the causal IE measurement redundant with 3C's `instructions_removed` self-report? **Answer: no, structurally.** | ✅ Run |
| `vectors.py` | The eight literature vectors (Du et al. / MCPSecBench) with a coverage map: which layer answers each, and what this implementation does *not* do. | ✅ Built |
| `benchmark.py` | Four-arm ablation benchmark (undefended / static_only / full / no_egress). | 🟡 **First result withdrawn** |
| `kaggle/` | Phase 6 — episode packager, GRPO trainer, Path A driver. See its own README. | ✅ Run |
| `__init__.py` | Package marker | ✅ |

---

## Why three of these exist at all

Each was written because a number had already been reported that turned out not
to mean what it appeared to.

### `ie_ablation.py` — refusing an invalid comparison

The obvious way to ask *"is IE redundant?"* is to score 3C's self-report as a
rival detector. **That comparison is invalid**, because the pipeline runs 3C
**only after a takeover has been declared** (`adaptishield_pipeline.py:132`), so
the self-report can only be computed on cases the detector already caught — a
selection effect, not a sample.

This script verifies the gating empirically (the set carrying a
`sanitization_decision` is *exactly* the takeover set, element for element) and
deliberately **does not print** the tempting comparison. An earlier version did,
and reported a conclusion that could not have been true.

### `fpr_report.py` — refusing to pool, and refusing stale data

Eight hand-written benign controls cannot support a rate, especially when four
were written specifically to break the detector: the Wilson interval on 4/8 spans
[21.5%, 78.5%] — the whole usable range. The script keeps `ours` (a
**diagnostic**) and `agentdojo` (the **estimate**) separate, and prints the
pooled figure only with an explicit caveat.

It also carries a **staleness guard**, added after it burned us. A campaign that
dies part-way leaves the previous dataset in place, and the report happily
printed pre-fix numbers as though they were current. It now prints the dataset's
age and shouts `STALE` if the live record log is newer. **Read that header.**

### `probe_diagnostic.py` — read-only by design

It alters no rule and patches nothing; it observes. The *matched controls* are
the load-bearing part: for each failure it runs the same family and directive
against an address that **was** caught, so a behavioural difference is
attributable to the one token that differs rather than inferred from the failures
alone.

Its own classifier once ordered a `severity == 0` check before the
garbled-address check and mislabelled three healthy probes — which would have
sent the repair at the probe prompt, which was not at fault. That ordering is now
pinned by tests.

---

## Phase 7 — the benchmark, and why its first result is withdrawn

`benchmark.py` runs the fixed vector set through four ablation arms of the *same*
pipeline. Ablation lives in `adaptishield_pipeline.py` (`PipelineConfig`) rather
than here, so every arm shares one code path and differs only in flags — a runner
that monkey-patched the layers would be measuring the patch as much as the
defense.

| Arm | What it isolates |
| :--- | :--- |
| `undefended` | The floor: what the vectors do unopposed. If ASR is not ~100% here, the vectors are too weak to measure anything |
| `static_only` | Screener + 3A patterns + Layer 4 — a plausible defense **without** this project's causal sub-layer. The honest baseline to beat |
| `full` | Complete AdaptiShield |
| `no_egress` | Full minus the allowlist. Separates what 3A/3B/3C detect from what a static allowlist was quietly backstopping |

### The first run produced a clean-looking finding that is not true

It reported ASR 100% → 14.3% under static defenses, the full system matching that
exactly, and WCR rising 0% → 71.4% — apparently showing the causal sub-layer
contributes usability but no extra detection.

**Inspecting which component actually stopped each case invalidates it:**

```
static_only — every case:
  V1..V3, V5..V7   approved_direct   egress_allowed=False   ← the ALLOWLIST
```

Nothing was blocked by any detection layer. Six of the eight vectors point at an
exfiltration host, so Layer 4 intercepts them before 3A or 3B is consulted, and
`static_only` and `full` are equal **by construction rather than by
measurement**.

This repeats the mistake §6n diagnosed — that section added address-free attacks
precisely because the allowlist was concealing detection failures. **The question
"does the causal sub-layer detect what static defenses miss" is untested in
either direction.** We do not claim the answer is negative; we have not measured
it.

### The repair

1. Point malicious vectors at the **legitimate** destination (keep V3 on the
   exfil host — it is *supposed* to test the allowlist), so a detection failure
   surfaces in ASR instead of being absorbed.
2. Add **per-layer attribution** — record *which* layer stopped each case, not
   just whether it was stopped. ASR is binary and cannot answer the question.
3. Add ~10 benign vectors from the vendored AgentDojo corpus; the FPR column
   currently rests on **one** vector × 3 repeats.

---

## Historical results retained here

These are kept runnable rather than deleted, because the before/after contrast is
itself a thesis result:

- **§6d — the adaptive loop does not close the gap.** The apparent gain was
  memorisation of a training address and vanished on a held-out one. This defined
  measurement fixes A–D.
- **Phase 5 (§6j) — after the fixes, the loop has nothing to close.** The gap it
  was built for had already been closed by the measurement repairs.
- **Phase 5b (§6k) — the loop *does* close a gap its knob matches, and
  generalises.** This proves the mechanism; it does not claim such a gap arises
  naturally (§6l showed it does not).
- **§6e — semantic scoring is more accurate per action and worse end-to-end.**
  Ships off by default; the ablation stays runnable.

---

## Running

```bash
# Deterministic, no LLM
python3 -m evaluation.mechanism_validation        # <1s
python3 -m evaluation.vectors                     # coverage map

# Reads existing results, no LLM
python3 -m evaluation.fpr_report                  # READ THE STALE HEADER FIRST
python3 -m evaluation.ie_ablation
python3 -m evaluation.probe_diagnostic

# Needs Ollama + gemma3:4b
python3 -m evaluation.adaptive_loop_experiment
python3 -m evaluation.holdout_generalization_test
python3 -m evaluation.score_action_ablation
python3 -m evaluation.benchmark --repeats 3       # ~25 min
```

---

## What's pending

- **Repair the benchmark** (above) — until then Phase 7 has no valid result.
- **Per-layer attribution** in `benchmark.py`.
- More benign vectors, so the FPR column rests on more than one.

Full write-ups for every finding referenced here: `researchworksofar.md`
(Volume I, §6a–§6p) and `research_work_so_far.md` (Volume II).
