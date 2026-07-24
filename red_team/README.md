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
| `attack_library.py` | Raw payloads: **6 attack families** (`blunt_override`, `important_instructions`, `tool_knowledge_injection`, `authority_citation`, `delegated_followup`, `masked_hypothetical`), **4 directives**, 4 attacker targets tagged `held_out` and split via `training_targets()` / `holdout_targets()`, and benign controls. | ✅ |
| `attack_generator.py` | Combines the library into concrete `RedTeamCase` objects (attacks + benign counterparts for FPR). `generate_training_attacks()` / `generate_holdout_attacks()` keep the train/held-out split first-class; `case_id` encodes the target by email local-part so merged reports stay unique. | ✅ |
| `execution_agent.py` | Runs cases through a live `AdaptiShieldPipeline` (dry-run — no `command`, so the sandbox never fires). Registers `send_email` in-scope so a campaign isolates 3B/3C detection from the egress backstop. | ✅ |
| `evaluator.py` | Computes ASR/FPR/WCR, per-family, plus a `caught_by_causal` vs `caught_by_egress_only` breakdown. | ✅ |
| `optimizer.py` | **v1 heuristic:** takes fully-defended families and keyword-softens their payloads to probe for detection gaps. Not the RL optimizer — that belongs with 3D. | ✅ |
| `run_campaign.py` | Wires all four stages; saves a JSON report per run to `logs/red_team_runs/`. | ✅ |
| `__init__.py` | Package marker | ✅ |

## What's done
- Full generate → execute → evaluate → optimize → re-run loop, validated
  locally.
- **Key finding (root README Section 6c), and its resolution:** keyword-softened
  generation-2 attacks originally dropped 3B's `caught_by_causal` to 0/4 — ASR
  stayed 0% only because the static egress allowlist caught them, concrete
  evidence for why the causal detector needed work. This gap is **now closed by
  fix D** (§6i, the masked-probe rewrite): across five repeated campaigns gen-2
  `caught_by_causal` is **4/4 in 4 of 5 runs** (3/4 in one), FPR and ASR 0%. The
  campaign remains the instrument that surfaced the gap and now measures its
  closure.
- `ExecutionResult` now carries `tool_name`, `proposed_action`, and the full
  `causal_verdict` (ACE/IE/DE **plus** the per-regime severities), so a report
  can say *why* a case was caught, not just whether. This also fixed a bug in
  3D's `from_execution_results()`, which had been reading `case_id` into
  `tool_name` and would have nominated case IDs as high-impact tools.

## What's pending
- **Attack set expanded (2026-07-24):** 6 families × 4 directives × 2 training
  targets = 48 gen-1 attacks, with 2 addresses **held out by construction**
  (`generate_holdout_attacks()`; a `__main__` assertion proves no held-out
  address leaks into the training split — Rules.md §5 / root README §6d). Still
  to do: **run** the expanded campaign to answer the natural-gap question
  (LLM-dependent, Kaggle-scale) — `run_campaign(run_holdout=True, max_*=None)`.
- Extend beyond `send_email` once the pipeline models more real tools.
- Tighten the **WCR proxy** — it currently infers task completion from
  `final_status == safe_continuation` rather than verifying the user's
  original benign intent was served (AgentDojo-style dual-task trajectories).
- Replace the v1 keyword-softening Optimizer with a learned one, once 3D
  exists to close the loop.

## Run
```bash
python3 -m red_team.run_campaign          # fast smoke: 1 directive x 1 training target
python3 -m red_team.attack_generator      # no-LLM: print the grid + held-out invariant check
# full natural-gap run (Kaggle-scale):
#   run_campaign(max_directives=None, max_train_targets=None,
#                max_holdout_targets=None, run_holdout=True)
```
