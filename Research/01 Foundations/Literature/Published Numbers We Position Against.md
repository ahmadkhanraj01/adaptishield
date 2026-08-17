---
tags: [adaptishield, literature, metric]
type: literature
date: 2026-08-17
---

# Published Numbers We Position Against

*The quantitative half of related work. Source of record is
`paper/external_numbers.json`; the table in §10 (`paper/10-positioning.md`) is
generated from it by `paper/make_positioning_table.py` and cannot be hand-edited.*

Every value below was read out of the primary source and stored with its verbatim
sentence. **A number without a quote does not go in the manuscript** — the
generator drops any row not marked `verified: "verbatim"` and prints it to stderr
as a to-do. This is the same discipline [[Wilson Score Interval]] and
[[Current Numbers]] apply to our own figures, extended to other people's.

## Attack success — [[InjecAgent]]

Zhan et al., Findings of ACL 2024. 1,054 test cases.

| Agent | ASR-valid | Setting |
| :--- | ---: | :--- |
| ReAct-prompted GPT-4 | 24% | base |
| ReAct-prompted GPT-4 | 47% | enhanced (hacking prompt) |
| ReAct-prompted Llama2-70B | >80% | both |
| Fine-tuned GPT-4 / GPT-3.5 | 3.8% / 6.6% | base |

**Ours on the same corpus is 100% undefended** (60/60, `direct_harm_base`). That
is a *floor check*, not a result: our agent is 3–4B local, so it is more
compliant than anything they measured. It earns the right to report a downstream
difference and nothing more.

## Defenses — [[AgentDojo]] and spotlighting

- **Tool filter** (Debenedetti et al., NeurIPS D&B 2024): *"lowering the attack
  success rate to 7.5%"* — verbatim.
- **Spotlighting** (Hines et al., arXiv:2403.14720): *"spotlighting reduces the
  attack success rate from greater than 50% to below 2%"*, GPT-family — verbatim.
  **We measure 34.8% → 33.3%, McNemar p = 1.00** on our harness
  → [[Phase 10 — Spotlighting Has No Measurable Effect]]. Almost certainly a gap in
  setting, not a contradiction, and §4 carries the per-family decomposition.
- 🟡 **AgentDojo's undefended important-instructions ASR is NOT yet verified.**
  It reached us second-hand (~45.8%). Held back by the generator until someone
  reads that table directly.

## Detectors — the FPR/FNR landscape

From PIShield's Tables 1 and 2 (Zou et al., arXiv:2510.14005), averaged over OPI,
Dolly, MMLU, BoolQ, Musique, NarrativeQA. Detection = 100 − FNR.

| Detector | Detection | [[FPR]] |
| :--- | ---: | ---: |
| PIShield | 98.6% | 0.5% |
| PromptGuard | 91.3% | 40.3% |
| DataSentinel | 89.6% | 33.6% |
| TaskTracker | 68.3% | 27.4% |
| PromptArmor | 54.1% | 1.3% |
| AttentionTracker | 44.7% | 32.8% |
| InjecGuard | 33.7% | 8.2% |
| PIGuard | 29.8% | 0.7% |
| ProtectAI-deberta | 24.1% | 10.1% |

## Why this table earns its place

Those detectors sit on an FPR/FNR curve; a contribution is a better point on it.
**Ours does not sit on that curve.** At one fixed FPR (3.3%) it is 96.7% on the
target-bearing stratum and 10.0% on the no-target one — the split is the presence
of a liftable target, not a threshold
→ [[Phase 12 — Detection Is 18% on Someone Else's Attacks]].

None of the nine reports its numbers stratified this way. That is not a claim
they share the failure; it is a claim their evaluations **as reported** could not
show it either way, which is a related-work observation with an experiment behind
it.

## What has no comparator

- **Our campaign detection (96.7%)** — an attack set we wrote is not comparable
  with anyone's published number, and it is still the one headline without an
  artifact under `results/` → [[Current Numbers]].
- **Utility under attack.** Every agent-benchmark paper here reports it; our
  corpus has no benign task-completion metric of comparable construction, so
  there is no honest row. Carried in §9 as a limitation.
