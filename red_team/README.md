# Red Team Module

**Status:** ✅ v1 scaffolded and validated end-to-end (Optimizer is heuristic, not RL)

## Purpose
Adversarially stress-tests the full pipeline and produces the ASR / FPR /
WCR numbers that justify (and later measure) Component 3D. Four stages,
matching the architecture diagram's Red Team row:
Attack Generator → Execution Agent → Evaluator → Optimizer.

## Files
| File | Purpose | Status |
| :--- | :--- | :--- |
| `attack_library.py` | Raw payloads: 4 attack families (`blunt_override`, `important_instructions`, `tool_knowledge_injection`, `masked_hypothetical`), directives, attacker targets, and benign controls. | ✅ |
| `attack_generator.py` | Combines the library into concrete `RedTeamCase` objects (attacks + benign counterparts for FPR). | ✅ |
| `execution_agent.py` | Runs cases through a live `AdaptiShieldPipeline` (dry-run — no `command`, so the sandbox never fires). Registers `send_email` in-scope so a campaign isolates 3B/3C detection from the egress backstop. | ✅ |
| `evaluator.py` | Computes ASR/FPR/WCR, per-family, plus a `caught_by_causal` vs `caught_by_egress_only` breakdown. | ✅ |
| `optimizer.py` | **v1 heuristic:** takes fully-defended families and keyword-softens their payloads to probe for detection gaps. Not the RL optimizer — that belongs with 3D. | ✅ |
| `run_campaign.py` | Wires all four stages; saves a JSON report per run to `logs/red_team_runs/`. | ✅ |
| `__init__.py` | Package marker | ✅ |

## What's done
- Full generate → execute → evaluate → optimize → re-run loop, validated
  locally.
- **Key finding (root README Section 5c):** keyword-softened generation-2
  attacks dropped 3B's `caught_by_causal` from 2/4 to 0/4 across all four
  families. ASR stayed 0% only because the static egress allowlist caught
  them — concrete evidence for why 3D is needed.

## What's pending
- Scale campaigns up (more directives/targets/families); move bulk runs to
  Kaggle (root README Section 8).
- Extend beyond `send_email` once the pipeline models more real tools.
- Tighten the **WCR proxy** — it currently infers task completion from
  `final_status == safe_continuation` rather than verifying the user's
  original benign intent was served (AgentDojo-style dual-task trajectories).
- Replace the v1 keyword-softening Optimizer with a learned one, once 3D
  exists to close the loop.

## Run
```bash
python3 -m red_team.run_campaign          # local-scale campaign, gen1 + gen2
# scale up via run_campaign(max_directives=2, max_targets=2)
```
