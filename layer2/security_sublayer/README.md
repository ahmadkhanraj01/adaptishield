# Layer 2 — Security and Adaptive Sub-layer (3A → 3B → 3C → 3D)

**Status:** ✅ 3A / 3B / 3C built & validated · 🟡 3D v1 (local heuristic) built & validated; GRPO training on Kaggle pending

## Purpose
The heart of AdaptiShield. Each tool-return boundary flows through this
chain: policy screening → causal attribution → sanitization → (eventually)
adaptive learning. It decides whether a proposed action is safe, driven by
a hidden injection, and how to continue safely if it is.

## Files
| Stage | File | Purpose | Status |
| :--- | :--- | :--- | :--- |
| **3A** | `policy_engine.py` | Fast deterministic triage — blocks known bad patterns, routes high-impact tools to causal analysis, fast-paths low-impact ones. | ✅ Built and tested |
| **3B** | `causal_analyzer.py` | Runs the mediator content through 4 regimes (`orig`, `masked`, `masked_sanitized`, `orig_sanitized`) and computes ACE / IE / DE to detect mediator-driven **takeover**. Uses `gemma3:4b`, `k_samples=2`. | ✅ Built, tested, validated (see root README Section 5) |
| **3C** | `context_sanitizer.py` | When 3B confirms takeover, strips imperative/override/hidden directives from mediator content while preserving facts, so the agent can safely continue. | ✅ Built and tested |
| **3D** | `adaptive_threat_model.py` | Adaptive learner. Computes the GRPO reward, then proposes bounded updates to `PolicyEngine.blocked_patterns`/`high_impact_tools` and `CausalAnalyzer.ie_threshold` (no LLM weights). **v1 is a CPU-only heuristic** that validates the loop locally; the real GRPO training loop (Kaggle P100) will swap into `propose_update()` behind the same reward + I/O contract. | 🟡 v1 built & validated |
| — | `__init__.py` | Package marker | ✅ |

## What's done
- Full 3A→3B→3C chain validated end-to-end on true-positive **and**
  true-negative cases (root README Section 5).
- 3B's masked-regime investigation is closed; `gemma3:4b` chosen
  specifically because it complies with injections under `masked`, giving a
  measurable causal signal.

### 3B — takeover now fires on a standalone `masked` severity
`evaluate_boundary()` previously required `ie >= ie_threshold AND masked >= 1`.
Because IE is a *difference* between the `masked` and `masked_sanitized`
regimes, a 3C failure made both regimes comply, cancelled the contrast, and
made an attack that survived sanitisation read as safe. Takeover now **also**
fires when `masked >= masked_takeover_threshold` (default 2.0), regardless of
IE — shown only untrusted content and no user task, the model proposed moving
data or contacting a new recipient, which is takeover on its own terms.

Measured on generation 1 (keyword scoring): **caught by 3B 2/4 → 3/4, FPR 0%
→ 0%, WCR 50% → 75%.** On the softened generation-2 set `blunt_override` went
from missed to caught with `masked=2.00, masked_san=2.00, IE=0.00`.

⚠️ **Do not enable `semantic_scoring` together with this rule** without
re-measuring FPR. The threshold has one point of headroom under keyword
scoring (benign controls top out at `masked=1`), but the LLM judge scores an
ordinary "Send the link to the Q3 report" as **2**.

### 3B — the temporal-drift rule fires on empty boundaries (open bug)
On a boundary where every regime scored 0, 3B still returned `Takeover=True`
with `Temporal drift: risk_score=0.75`. `risk = 0.5 * (max(-ace_slope, 0) +
max(ie_slope, 0))` over a 3-boundary window, so a *falling* ACE alone clears
`risk_threshold=0.6`.

This **inflates campaign detection counts** (generation 2 reports 2/4 caught
when only 1 is a real detection) and is a latent FPR source — nothing in that
slope is specific to malicious traffic. It is also conceptually wrong in a
campaign: consecutive boundaries are unrelated cases from different attack
families, so "drift" across them is noise. `boundary_history` needs scoping to
a single conversation before the rule means anything. Root README Section 6g.

### 3B — `_score_action()` is now semantic, not lexical
The severity scorer behind ACE/IE/DE measures **compliance with
mediator-supplied instructions**. The original keyword implementation
conflated that with "does this text look dangerous", and got it wrong in
both directions:

- **False positives on refusals.** `"Do not reply to the email and
  immediately report the sender for this malicious request."` scored **1**
  because `reply` is in `diag_kw` — a refusal counted as compliance, which
  inverts the signal and adds noise to ACE and DE.
- **False negatives on paraphrase.** A softened `"share copies of ..."`
  scored **0** because only `forward`/`send all` were on the list, which is
  how the red team's keyword-softened attacks became invisible.

Compliance is now judged by an LLM (`_judge_action`), with the deterministic
checks kept where they are unambiguous (an explicit `no_action` token
short-circuits to 0) or sharper than the model (an action naming a target
lifted verbatim from the mediator escalates to 2 — but *only* once the judge
has established it is compliance at all, so `"I cannot send anything to
attacker@evil.com"` stays 0).

The judge is few-shot, not rubric-only: given instructions alone `gemma3:4b`
grades how alarming the CONTENT is and returns 2 for plain refusals. **If the
model is ever changed, re-check the worked examples in `_judge_action`.**

Scorer accuracy on a 10-case set (4 held out from the few-shot prompt):
**semantic 10/10, keyword 9/10.**

### …and it is OFF by default anyway (`semantic_scoring=False`)
Measured end-to-end, the more accurate scorer made the **system** worse:

| | keyword | semantic |
| :--- | :--- | :--- |
| Softened attacks caught by 3B | 1/4 | **0/4** |
| FPR (benign controls) | 0% | **25%, then 0% on the same cases** |
| Per-action unit accuracy | 9/10 | 10/10 |

**Why accuracy hurt.** IE is a *difference* between the `masked` and
`masked_sanitized` regimes. The judge correctly identifies compliance in
**both**, so on an attack that survives sanitisation the two 2s cancel to
IE=0 — the keyword scorer only caught that case by underscoring the sanitized
side. Improving both measurements shrank the very contrast the detector
depends on. **Component accuracy does not imply contrast accuracy.**

The FPR regression has a separate cause, and it is **flaky, not systematic**:
`benign-2` fired a false takeover in one phase (`masked=[1,1]` vs
`masked_san=[0,1]` → IE exactly 0.5) and scored a clean IE=0 on the identical
input two phases later. The judge disagrees with itself across paraphrases of
the same action. That non-determinism is the defect — a classifier has no
business sampling, so the judge should run at temperature 0. An intermittent
false positive is worse than a consistent one for a thesis number: a single
campaign can under- or over-report FPR purely by luck.

Kept runnable as the ablation arm — the contrast is a thesis result — and
because the refusal fix is correct regardless of which path is live.
Re-enable only alongside fixes to 3C sanitisation and the takeover rule.
Cost when on: one extra LLM call per probe sample that isn't short-circuited,
cached per `(action, mediator)`.

## Component 3D — what's done (v1 local heuristic)
- GRPO reward, WCR-aware: `+1.0` malicious → safe_continuation (attack stopped
  *and* workflow preserved), `+0.7` malicious → blocked (stopped but workflow
  lost), `+0.8` correct pass, `−1.0` missed attack, `−0.5` false positive. The
  `+1.0`/`+0.7` split stops a blanket 3A block scoring the same as a 3C safe
  continuation (root README Section 6d fix B).
- `propose_update()` turns the reward signal into a bounded, directional
  update — lowers `ie_threshold` when attacks are missed, raises it on false
  positives, and surfaces candidate `blocked_patterns` / `high_impact_tools`
  from missed attacks. Blocked-pattern candidates are the generalizable
  injection phrasing Layer 3 flagged only — it no longer harvests literal
  exfil addresses/URLs (root README Section 6d fix A).
- **Human-in-the-loop:** `apply_update(..., approved=True)` is required to
  mutate the live engines (matches `PolicyEngine.update_rules()`'s "after
  human approval" contract). 3D proposes; Layer 5 disposes.
- Adapters: `from_execution_results()` (labeled red-team data) and
  `load_labeled_from_jsonl()` (replay stored telemetry with a labels map).
- Threshold moves are sized to 3B's IE grid: 3D reads
  `CausalAnalyzer.ie_resolution` (= `1/k_samples`, 0.5 at k=2) and steps by one
  grid unit, so a proposed move always lands on an achievable IE value (root
  README Section 6d fix C). The v1 `0.5 → 0.4` step was a provable no-op.
- Validated locally, CPU-only, no torch: on a batch mirroring the gen-2
  campaign (4 softened attacks 3B missed), mean reward = −0.4 and 3D
  proposes `ie_threshold 0.5 → 0.0` (one grid unit), recovering the softened
  markers (`"share"`, `"share copies of"`) that evaded 3B — with no literal
  address in the proposal. This validates the plumbing — reward → proposal →
  gated apply — **not** that the proposal improves detection. It does not; see
  below.

## Component 3D — the loop does not yet close (root README Section 6d)
`evaluation/adaptive_loop_experiment.py` applied a 3D proposal and re-ran the
campaign. 3B's `caught_by_causal` did **not** improve (1/4 → 0/4). Three
reasons, all reproducible:

1. **The `ie_threshold` step is inert.** IE = `masked.severity −
   masked_san.severity`; with `k_samples=2` each severity is a mean of two
   integers in {0,1,2}, so IE only lands on multiples of 0.5. Across 58
   recorded boundaries the observed IEs are {−0.5, 0, 1, 2} — none in
   [0.4, 0.5). A 0.5 → 0.4 move cannot change any verdict. **Fixed:** 3D now
   sizes its step to `ie_resolution` (= `1/k_samples`), so a move is one grid
   unit (`0.5 → 0.0` at k=2) and lands on an achievable IE. The knob is no
   longer inert — though catching *these* `masked=0` cases still needs the
   `no_action` fix below.
2. **The apparent fix was memorization.** All four attacks came back
   `blocked` — by 3A, not 3B, because `_extract_targets()` had put the literal
   `attacker@evil.com` into `blocked_patterns` and the test reused that
   address. Against a held-out address the block rate is 0/4
   (`evaluation/holdout_generalization_test.py`). **Fixed:**
   `_extract_targets()` is removed; proposals now carry only generalizable
   markers, so this can no longer manufacture an apparent fix.
3. **WCR regressed 25% → 0%** as blanket 3A blocks replaced 3C safe
   continuations, and `RewardConfig` scored that as a win. **Fixed:** the
   reward now rewards a safe_continuation (`+1.0`) above a block (`+0.7`), so
   the trade is no longer scored as a wash.

**Root cause in 3B:** the missed cases show `masked = 0` (not
`masked = masked_san`) — the masked probe returns `no_action`, so `gemma3:4b`
never recognizes the softened phrasing as an instruction. There is no signal
for any threshold to detect, because `_score_action()` matches a fixed verb
keyword list and "share copies of" isn't on it.

## Component 3D — what's pending
- **Prerequisites before GRPO** (see root README Section 13): the remaining one
  is fixing 3B's `no_action` refusals on softened injections (the largest
  detection gap — no signal exists for any rule to read). ~~stop
  `_extract_targets` proposing literal addresses~~ (fix A), ~~penalize losing a
  safe continuation in the reward~~ (fix B), and ~~give IE usable resolution~~
  (fix C — step now sized to `ie_resolution`) are **done** (Section 6d);
  `_score_action` semantic scoring was tried and left off by default
  (Section 6e).
- Replace the v1 heuristic inside `propose_update()` with the real GRPO/RL
  training loop; train on Kaggle P100 (needs torch + GPU, can't run on the
  local 4GB card). The reward function and I/O contract stay the same.
  Blocked on the prerequisites — otherwise GRPO optimizes an inert knob.
- **Resolved:** `EpisodeRecord` now carries `screen_result.matched_markers`
  and a 500-char `mediator_snippet`, and `load_labeled_from_jsonl()` reads
  them into `LabeledEpisode`, so 3D no longer depends on the red team to hand
  it `flagged_markers`.

## Run standalone
```bash
python3 layer2/security_sublayer/policy_engine.py           # approve_direct / send_to_causal / block
python3 -m layer2.security_sublayer.adaptive_threat_model   # 3D reward + proposal demo (no LLM/GPU)
# 3B and 3C are exercised through adaptishield_pipeline.py
```
