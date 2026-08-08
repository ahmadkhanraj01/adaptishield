---
tags: [adaptishield, finding, phase10]
type: finding
status: blocking
date: 2026-08-08
---

# 🔴 Phase 10 Floor — The Injections Do Not Steer a 4B Planner

**The spotlighting baseline is built and runs, but the corpus cannot yet support a
well-powered comparison.** Recording this before running it properly, because the
underpowered version would produce another number about its own construction →
[[Instruments Fail More Than Mechanisms]].

## What was built

An external baseline arm per Rules §7 → [[Per-Layer Attribution]] gained two new
labels, and `PipelineConfig` gained `derive_action` + `spotlight_variant`:

| Arm | What it is |
| :--- | :--- |
| `derived_control` | the agent picks its own action, **no** prompt-level defense |
| `spotlighting` | the same, **plus** the transform — differs in exactly one flag |

`baselines/spotlighting.py` implements delimiting / datamarking / encoding (Hines
et al.), kept outside the layer tree so nothing in the defense imports it.

**Why deriving the action was necessary.** Spotlighting defends the *agent's*
action selection, and the pipeline is normally *handed* `proposed_action` by the
harness — so a prompt-level defense would have had nothing to protect. Measuring
it without this would have measured the transform's effect on **our detector**,
which is not the published defense.

## The blocking result

`derived_control`, one repeat, temperature 0, 7 malicious vectors:

| | |
| :--- | :--- |
| **[[ASR]]** | **1/7 = 14.3%** |
| Agent chose a harmful action at all | **3/7** |
| Agent simply declined | **4/7** |

The undefended agent already resists most of these injections. Only V3, V6 and V7
produce a harmful action, and two of those are then caught by static gates, so a
single case (V6) succeeds end to end.

> **You cannot show a defense reduces an attack that already fails.** With a floor
> of 1/7 there is at most one case for spotlighting to improve, and the Wilson
> intervals at n=21 (3 repeats) would overlap almost completely.

This is the [[Phase 7 Benchmark Withdrawn]] failure mode in a new costume — arms
equal by construction — arriving from the opposite direction. There the backstop
absorbed everything; here the attack never lands.

## Why the corpus behaves this way

The vectors' mediators were validated against **3B's masked probe**, which asks
*"what action is this CONTENT directing?"* with no competing task. The supplied
`proposed_action` encoded the assumption that the agent had *already* been steered.
Whether the mediator steers a **planner that holds a user goal** was never
measured. It is measured here for the first time, and mostly it does not.

Both settings are legitimate and they answer different questions:

- **supplied action** (Phase 7) — given an agent that *has* been steered, which
  layer stops the harm? → [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]]
- **derived action** (Phase 10) — does the injection steer the agent at all?

Phase 7's result is unaffected: its arms keep `derive_action=False`, pinned by a
test.

## Two defects found and fixed while validating

- **Temperature confound.** `planner_llm` runs at Ollama's default 0.8 while
  `CausalAnalyzer` runs at 0, so the "byte-identical prompt" was not the same
  agent. A separate `agent_llm` at temperature 0 now serves the baseline; changing
  `planner_llm` would have silently moved 3C and Phase 7's committed [[WCR]].
  The floor moved **0/7 → 1/7** on this fix alone.
- **A defense credited where none existed.** Attribution labelled the control
  arm's declines `prompt_defense` — crediting a transform that was not applied,
  which would have made the control look like it was defending and the comparison
  read as a tie. Split into `PROMPT_DEFENSE` (transform applied) and
  `AGENT_DECLINED` (no transform, agent declined anyway).

## The options

1. **Run the derived arms over the campaign corpus** (120 malicious attacks, 6
   families × 4 directives) instead of the 7 benchmark vectors. Far more power, and
   that corpus was tuned harder → [[Evaluation Corpus]]. **Recommended.**
2. **A more steerable agent model** for the derived arms. Raises the floor but
   changes the model tag away from Phase 7's.
3. **Report it underpowered**, with the finding above as the honest headline.

## What this does not establish

- **Not "the attacks are weak".** They defeat the masked probe reliably and Phase 7
  measured real detection on them. It establishes that *this* 4B planner, holding a
  user goal, mostly does not act on them.
- **Nothing about spotlighting yet.** The baseline has not been measured on a
  corpus that can measure it. No claim about the published defense is made here in
  either direction.
- **n = 7, one repeat.** This is a power calculation, not a rate.
