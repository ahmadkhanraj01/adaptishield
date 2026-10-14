---
tags: [adaptishield, open]
type: open
---

# Paper 2 Plan

🔲 **Proposal only, not started, not approved** (6 Oct 2026). Full text in the
repo: `paper2-plan.md`. Paper 1 is submitted first.

**Core idea:** the adaptive layer was a no-op because the *signal* was flat, not
because the learner was weak. Fix the signal, then adapt on it.

1. **Track 1 ⭐** — task-scope scorer: flag actions outside what the user asked,
   which needs no liftable target. Aimed at the address-free stratum ([[Address-Free Attacks]]).
2. **Track 2** — continuous (log-probability) scores instead of integer severity,
   on a 7–14B model via Kaggle ([[Phase 6 — GRPO on Kaggle]]).
3. **Track 3** — learner tunes target classes, task-scope strictness and 3C
   settings, behind the Layer 5 human gate ([[Reward-Decreasing Proposals]]).
4. **Track 4** — second external benign corpus, a real multi-turn corpus, a larger model.

Not doing: GRPO over current thresholds (flat reward), more harm keywords
(90.0% → 43.3% on holdout).

Logged in [[Entry XXX — A Plan for Paper 2]].
