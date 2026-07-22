# Layer 2 — LLM Agent Control Plane

**Status:** 🟡 Partial — Security Sub-layer 3A/3B/3C built; 3D v1 heuristic built (GRPO training pending)

## Purpose
The decision-making layer. In the full architecture this hosts the Planner
Agent, Tool Selector, Execution Agent, and Feedback Analyzer — but the part
that actually exists today is the **Security and Adaptive Sub-layer**
(`security_sublayer/`), which is where AdaptiShield's novel defenses live.

## Contents
| Path | Purpose | Status |
| :--- | :--- | :--- |
| `security_sublayer/` | The 3A→3B→3C→3D defense chain — see its own README | 🟡 3A/3B/3C done; 3D v1 built, GRPO pending |
| `__init__.py` | Package marker | ✅ |

## What's done
- The Security Sub-layer's first three stages (Policy Engine, Causal
  Analyzer, Context Sanitizer) are built, tested, and wired into
  `adaptishield_pipeline.py`.
- **Component 3D v1** (CPU heuristic) is built and validated: reward → bounded,
  human-gated proposal. Fixes A–D corrected the measurement, reward, step
  sizing, and masked probe (root README §6d, §6i–6k), and the loop is now shown
  to close a controlled gap. See `security_sublayer/README.md`.

## What's pending
- **Component 3D — real GRPO/RL training** — replace the v1 heuristic inside
  `propose_update()` with a policy-gradient loop on Kaggle, same reward and I/O
  contract. Prerequisites (A–D) are now cleared.
- The general-purpose Planner / Tool Selector / Execution Agent / Feedback
  Analyzer boxes in the diagram are represented today only by the simple
  `planner_llm` calls inside the pipeline, not as standalone modules.

See `layer2/security_sublayer/README.md` for the detailed breakdown.
