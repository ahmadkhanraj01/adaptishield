---
tags: [adaptishield, open]
type: open
---

# Backlog

[[Next Task — Repair the Phase 7 Benchmark]] is ✅ **done** (8 Aug 2026). In rough
priority order from here.

## 0 — Phase 10: an external baseline 🔵 **NEXT — journal-mandatory**

`static_only` is **our own ablation**; a reviewer will not accept it as the
comparison (Rules §7). Needed on the **same corpus, seeds and model tags**: a
published prompt-level defense — spotlighting (delimiting / datamarking /
encoding) or an equivalent from the AgentDojo defense set — implemented as a
`PipelineConfig` arm so it shares one code path.

Cheap now that the Phase 7 infrastructure exists: a new arm is a config value plus
a `defended_by` label, and [[Per-Layer Attribution|attribution]] will report what
it actually does rather than what it claims. Expected shape: prompt-level defenses
degrade under the softened gen-2 injections [[Fixes A-D|fix D]] was built for —
which is the argument for a causal layer, but only once measured.

→ then Phase 11 (per-component ablations, with 3A's **zero detection stops** and
IE's non-redundancy as rows), Phase 12 (InjecAgent), Phase 13 (manuscript).

## 1 — The severity function 🔴

All **4** residual campaign misses are `masked = 0` → [[Residual Misses Decomposed]].
Phase 7 confirms this independently: **all 3** of the `full` arm's residual attack
successes are **V4**, the [[Address-Free Attacks|address-free]] vector, and **none**
is a threshold failure.

⚠️ [[6e — Semantic Scoring Ablation]] already showed the semantic scorer is
**worse end-to-end**, so this needs a **third approach**, not a re-run of that
one. And [[6p — Probe Hallucination Fixed at the Scorer]] establishes that the
*prompt* is not where to try it either.

This is the largest remaining detection lever, and the hardest.

## 2 — Multi-turn sessions 🟡

Campaigns give every case a unique `session_id`, so the drift rule never fires and
**two of 3D's five dimensions are unidentifiable** — the trainer reports this
itself → [[6g — Temporal Drift Scoping]].

Sharing a session across cases would make the temporal-drift rule learnable **for
the first time**.

## 3 — 3C `ContextSanitizer.sanitize()` 🟡

Still carries the prompt weakness 3B's internal sanitizer had, fixed in
[[6m — The Single-Character Defect]]. It feeds the **user-visible continuation**
and the [[WCR]] metric, so it was left unchanged rather than altered silently →
[[3C Context Sanitizer]].

## 4 — Screen tool descriptions at registration

Benchmark vectors **V5/V6 are approximated** because the pipeline consumes tool
*responses*, not manifests. The Supply Chain Scanner specified in
[[Layer 1 — Input and Supply Chain Screening]] (per [[AutoMalTool]]) is the
missing piece.

## 5 — Publish the Layer 5 dashboard

Two questions must be settled **first**:
- **Visibility** — it currently embeds **828 records including attacker-authored
  text**
- **Attribution** — render the [[AgentDojo]] credit on the page

→ [[Layer 5 — Human in the Loop]]

## 6 — The inert-pattern namespace mismatch 🔴

The gate *detects* [[Inert Blocked Patterns]]; it does not make them fire.
Whether [[3A Policy Engine]] should match mediator markers, or
[[3D Adaptive Threat Model]] should harvest from proposed actions, is **undecided**.

## 7 — Externally-authored *malicious* data

The benign side was fixed by importing [[AgentDojo]]. The attack side has no
equivalent import, so [[6n — A Corpus That Can Fail]]'s central lesson is only
half-applied → [[Evaluation Corpus]].
