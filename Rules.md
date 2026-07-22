# AdaptiShield — Rules & Invariants

**What this file is:** the hard constraints that must hold for anyone (human or
AI) changing this codebase. Breaking one of these has silently broken a result
before — most of them are scars, not preferences. For the reasoning behind them
see [Design.md](Design.md); for structure see [Architecture.md](Architecture.md).

*Last aligned: 2026-07-22 (after fixes A–D).*

> **Legend:** 🔴 hard invariant (breaking it invalidates results or breaks the
> build) · 🟡 strong convention (break only with measurement + a doc update).

---

## 1. Environment

- 🔴 **`numpy==1.26.4` is pinned.** numpy 2.x breaks on Python 3.10.12.
  `requirements.txt` is the source of truth (`installed.txt` shows drift).
- 🔴 **Python 3.10.12**, Ubuntu 24.04, **4 GB VRAM is a hard ceiling** for local
  GPU inference. Anything needing torch or a 7B+ model goes to **Kaggle P100**.
- 🟡 The pipeline runs locally; Kaggle is for training/evaluation only (it
  cannot host a live MCP server).

## 2. Models & probes

- 🔴 **Do not drop `CausalAnalyzer.k_samples` below 2** without re-validating
  3B end-to-end. IE resolution is `1/k_samples`; fewer samples = coarser metric.
- 🔴 **Keep the per-component model split.** 3B = `gemma3:4b` (it complies under
  the masked probe → real signal); 3C/L3/planner = `qwen2.5:3b`. A more
  refusal-prone model on 3B *destroys* the causal signal.
- 🔴 **The masked-probe prompt is calibrated (fix D / README 6i).** It must keep
  refusing the softened escape hatches (polite phrasing, "standard step",
  tool/feature notes, hypotheticals, "no need to actually do it"). Re-measure
  the gen-2 campaign + benign FPR if you touch it.
- 🟡 If `semantic_scoring` is ever revisited, run the judge at **temperature 0**
  (it disagrees with itself across paraphrases, causing flaky FPR).

## 3. 3B takeover-rule invariants (`tests/test_takeover_rules.py` pins these)

- 🔴 **The standalone `masked ≥ 2` rule (6f) must always be able to fire**, even
  when the IE consistency guard suppresses the contrast. Do **not** tighten the
  guard (6h) without the standalone rule in place — on its own the guard turns
  a strong-evidence attack into a false negative.
- 🔴 **"Nothing observed" must never mean takeover.** The drift rule is gated on
  `masked ≥ 1`; the IE rule on `masked ≥ 1` + consistent separation.
- 🔴 **Drift history is per `session_id`.** Never revert to one flat list —
  slopes across unrelated red-team cases are noise, not a trend.
- 🟡 IE rule requires `min(masked) > max(masked_san)` (consistent across
  samples). `require_consistent_ie=False` exists only for ablation.

## 4. Component 3D invariants

- 🔴 **3D never touches LLM weights.** It tunes only 3A `blocked_patterns` /
  `high_impact_tools` and 3B `ie_threshold`.
- 🔴 **`apply_update` requires `approved=True`.** 3D proposes; a human disposes.
- 🔴 **Train on labeled data only** (red-team `ExecutionResult`s or labeled
  telemetry replay). Never infer the attack label from the outcome — it is
  circular.
- 🔴 **No literal exfil targets in proposals (fix A).** `propose_update` must not
  emit raw addresses/URLs into `blocked_patterns` — that is memorization and
  inflates before/after numbers. Layer 4's allowlist covers exact destinations.
- 🔴 **`threshold_step` = `CausalAnalyzer.ie_resolution` (fix C).** A step finer
  than the IE grid is a provable no-op.
- 🔴 **The reward is WCR-aware (fix B).** malicious→`safe_continuation` (+1.0)
  must out-reward malicious→`blocked` (+0.7). Do not collapse them.

## 5. Security & handling

- 🔴 **Layer 4 is defense-in-depth.** Permission, egress, and sandbox each gate
  *independently* of the 3A/3B/3C verdict. The sandbox executes only when
  permission **and** egress both pass.
- 🔴 **Mediator text is untrusted everywhere — including in telemetry.** Episode
  Records now store mediator snippets; treat them as untrusted input anywhere
  they are displayed or replayed.
- 🔴 **Always hold out at least one attacker address/target from training.**
  README Section 6d exists because nothing was held out and memorization looked
  like generalization.

## 6. Testing & measurement

- 🟡 **Deterministic decision logic → `tests/`** (patch the four probe regimes
  out, no Ollama, sub-second). **LLM-dependent checks → `evaluation/`** (minutes,
  vary run-to-run; record numbers in docs, don't assert on them).
- 🟡 **Judge detection by the layer under test** (`caught_by_causal`), not by
  end-to-end ASR — the egress backstop keeps ASR at 0% regardless.
- 🟡 **Report FPR (and any flaky metric) as a distribution over repeated runs**,
  not a single-campaign figure.

## 7. Workflow

- 🟡 **Keep the docs in sync.** On any change, update the root `README.md`, the
  relevant per-folder `README.md`, and — where affected — `Architecture.md`,
  `Design.md`, `Rules.md`, `Phase.md`.
- 🟡 **Commits/pushes only when the user asks.** Branch off `main` first.
