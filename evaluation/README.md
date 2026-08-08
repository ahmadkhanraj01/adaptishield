# evaluation — Experiments, Diagnostics and the Benchmark

**Status:** ✅ Experiments run and reported · ✅ Phase 7 repaired and re-run · ✅
Phase 10 external baseline measured. The benchmark's **first** result is withdrawn
and superseded (see below).

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
| `vectors.py` | The eight literature vectors (Du et al. / MCPSecBench) with a coverage map: which layer answers each, and what this implementation does *not* do. Plus the external benign cohort (10 AgentDojo documents, stride-sampled), kept **separate** from our own V8. | ✅ Built |
| `attribution.py` | **Which layer stopped each case** — first gate in pipeline order that refused, plus the later gates that would also have refused. Attack success is one bit and one bit cannot tell 3B from the allowlist; that is what invalidated the benchmark's first result. Also carries the Phase 10 prevention labels (`prompt_defense` / `agent_declined`). | ✅ Built |
| `benchmark.py` | Ablation + baseline runner. Phase 7 arms (undefended / static_only / full / no_egress) and Phase 10 arms (derived_control / spotlighting), two corpora (`--corpus vectors\|campaign`), Wilson intervals, per-layer attribution, `steer_rate`, run manifest. Refuses to put supplied-action and derived-action arms in one table. | ✅ Run |
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
precisely because the allowlist was concealing detection failures.

**✅ Now measured.** After the repair below: ASR `static_only` **71.4%** → `full`
**14.3%**, with **18 of 21** stops attributed to 3B and **zero** detection stops
possible in `static_only`. Layer 4 turns out to contribute **nothing incremental**
once 3B is on. Results in `results/phase7/`.

### The repair — done and re-run (2026-08-08)

1. **Destinations.** Malicious vectors now carry the **legitimate** mail host, so
   a detection failure surfaces in ASR instead of being absorbed: absorbable
   vectors went **6 of 7 → 1 of 7**. V3 keeps the exfil host because testing the
   allowlist is its job. This is a correction, not a workaround — for a
   `send_email` call through the registered mail server the HTTP destination *is*
   the mail host whatever the recipient is; pointing it at the recipient's domain
   was the fiction that handed the allowlist a case it would never see.
2. **Per-layer attribution** (`attribution.py`). `stopped_by` names the first gate
   in pipeline order that refused; `redundant_gates` names the later ones that
   would also have refused. `backstop_share` reports what fraction of detection
   stops a static gate would have caught anyway, and the report flags it above
   90%. On the withdrawn run this would have printed *"no detection stop
   occurred"* for `static_only` — the finding, in the output, immediately.
3. **FPR.** Ten externally-authored AgentDojo documents (fixed stride of 6 across
   the 60, so the sample spans both suites and all three field types instead of
   taking one suite). A **separate cohort** from V8 — never pooled (Rules §7).
4. **Run manifest.** Commit SHA + dirty flag, corpus provenance and version, model
   tags and 3B's knobs, Python/platform, and Ollama's VRAM state sampled *after*
   inference (`/api/ps` lists only resident models, so a pre-run check reports no
   GPU on every clean start). On seeds it records the honest entry: greedy at
   temperature 0, **no RNG seed is exposed by Ollama**, and not literally
   deterministic (§6n: 2/564).

**Two defects found while repairing, both hidden by the old destinations:**

- **V7 could never test what it claimed.** It is labelled `defended_by="Layer 4
  permission control"`, but `as_cases` hardcoded `server_name="email-api"`, which
  declares `send_email` in scope — so the check always passed and egress refused
  the case first. V7 now runs against `weather-api` (`get_weather` only) and
  returns `OUT-OF-SCOPE`. Attribution is what surfaced it; the column would
  otherwise have printed a plausible lie.
- **A blocked case could read as "reached the tool."** The first attribution pass
  credited 3A only when no causal verdict existed, so `blocked` with a
  no-takeover verdict fell through to `none` with `reached_tool=True`. A test
  caught it; a block now always attributes to exactly one layer.

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
# 216 cases (18 vectors x 3 repeats x 4 arms) — ~40 min.
# DELETE THE CHECKPOINT FIRST: cached results describe the OLD pipeline.
rm -rf logs/benchmark_checkpoint
python3 -m evaluation.benchmark --repeats 3
```

---

## What's pending

- **Repair the benchmark** (above) — until then Phase 7 has no valid result.
- **Per-layer attribution** in `benchmark.py`.
- More benign vectors, so the FPR column rests on more than one.

Full write-ups for every finding referenced here: `researchworksofar.md`
(Volume I, §6a–§6p) and `research_work_so_far.md` (Volume II).


---

## Phase 10 — the external baseline

`static_only` is *our* ablation. Rules §7 needs a **published** prompt-level
defense, so `baselines/spotlighting.py` implements spotlighting (Hines et al.:
delimiting / datamarking / encoding), kept outside the layer tree with a test that
fails if any layer imports it.

**Measuring it needed `derive_action`.** Spotlighting defends the *agent's* action
selection, and the pipeline is normally handed `proposed_action` — so the defense
had nothing to protect. With the flag on, an agent reads the (possibly marked)
untrusted content and picks the action. Two arms differing in exactly one flag:

| Arm | What it is |
| :--- | :--- |
| `derived_control` | the agent picks its own action, **no** prompt-level defense |
| `spotlighting` | the same **plus** the transform |

```bash
rm -rf logs/benchmark_checkpoint
python3 -m evaluation.benchmark --arms derived_control,spotlighting \
        --corpus campaign --repeats 1        # 86 cases/arm, ~12 min
```

### The result: no measurable effect

| Arm | Steered | 95% Wilson |
| :--- | ---: | :--- |
| `derived_control` | 23/66 = **34.8%** | [24.5%, 46.9%] |
| `spotlighting` (datamarking) | 22/66 = **33.3%** | [23.2%, 45.3%] |

Paired **McNemar p = 1.00** — 8 cases helped, 7 hurt. The null is two opposing
per-family effects cancelling (`important_instructions` 8→5 but `blunt_override`
0→3), not indifference.

**Read `steer_rate`, not ASR.** ASR is 0/66 in both arms because the allowlist
absorbs every address-carrying attack. `steer_rate` asks whether the agent *chose* a
harmful action, judged before any gate, so a backstop cannot absorb it.

### ⛔ The raw figure is withdrawn

The first run said 39.4% → 56.1% — "spotlighting is 17 points worse". **16 of 37**
apparently-steered cases were refusals *naming* the attacker address, e.g. `"Do not
forward emails to attacker@evil.com and instead reply"`. `_score_action_by_keyword`
escalates any action naming a mediator target and has no negation handling, so the
transform inflated the metric judging it, in proportion to how clearly it worked.

Fixed by `CausalAnalyzer.score_agent_action` — negation scoped to the *clause naming
the target*, because `"Do not reply ... and instead bcc attacker@evil.com"` is
compliance, not refusal. It sits **beside** the regime scorer, not inside it: in the
masked probe an address mention is the signal the detector leans on (§6i/§6p), so
de-escalating refusals there would trade a measured FP for unmeasured FNs. Phase 7's
numbers are structurally unaffected and a test enforces it.

**🔴 Still open:** whether refusal-shaped output inflates 3B's *regime* severities.
Untested, cheap to test, and it should happen before Phase 11.

### Two corpora, never one table

`--corpus vectors` (Phase 7) and `--corpus campaign` (Phase 10) answer different
questions, and ASR means different things in supplied-action vs derived-action arms.
The runner **refuses** to run both cohorts together rather than pooling them — the
§6n error in a new costume.
