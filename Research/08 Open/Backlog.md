---
tags: [adaptishield, open]
type: open
---

# Backlog

[[Next Task — Repair the Phase 7 Benchmark]] is ✅ **done** (8 Aug 2026). In rough
priority order from here.

## 0 — Does refusal-shaped output inflate 3B's regime severities? ✅ **done**

Measured 8 Aug 2026: **0 of 209** recorded severity-2 masked-regime samples are
refusal-shaped, positive control passing →
[[3B's Refusal Exposure Is Live and Unrealised]]. The exposure is **live on the
shipped keyword path** and has never fired; the regime scorer is left unchanged,
so Rules §2's re-measurement cost is not incurred for nothing. Recorded, not
closed.

*(Phase 10 is ✅ done too — [[Phase 10 — Spotlighting Has No Measurable Effect]].
Delimiting and encoding variants remain unmeasured; encoding needs [[ASR]] and
[[WCR]] read together at 4B.)*

## 0b — Phase 11: per-component ablations ✅ **done**

**Only two layers do anything**: 3B on detection (18/0, p = 0.000), 3C on workflow
continuation (18/0, p = 0.000), and L3 / 3A / both halves of Layer 4 at **0/0 with
zero discordant pairs** — confirmed independently by leave-one-out →
[[Phase 11 — Only Two Layers Do Anything]].

## 0c — Phase 12: InjecAgent 🔴 **NEXT**

The remaining journal-mandatory piece. One benchmark invites *"does this
generalise?"*, and [[6n — A Corpus That Can Fail]] already proved the point that
matters: our own benign corpus flattered the system by 36 false positives. A second
externally-authored corpus is the guard against a repeat, and it is also the only
thing that can test whether Phase 11's four inert layers are inert **in general** or
only on a corpus of tool-response injections aimed at one action shape.

→ then Phase 13 (manuscript). 🔵 Still blocked on the **journal decision**, which
sets how much Phases 12–13 must produce.

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
