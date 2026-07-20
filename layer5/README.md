# Layer 5 — Human-in-the-Loop and Observability

**Status:** 🔲 Pending — empty folder, nothing built yet

## Purpose
The top layer of the architecture: where a human operator observes,
inspects, and overrides the system. Consumes the telemetry that Layer 4
already emits.

## Planned contents (none implemented yet)
| Planned module | Purpose |
| :--- | :--- |
| Audit Dashboard | Visualize episode records, ASR/FPR/WCR trends, blocked events |
| Policy Inspection Console | View/edit `PolicyEngine.blocked_patterns` and `high_impact_tools` |
| Manual Override | Let an operator approve/deny a held action |
| Audit Logs | Human-readable rendering of `logs/episode_records/episodes.jsonl` |

## What's done
- Nothing in this folder yet. **But the data it needs already exists:**
  `layer4/telemetry_stream.py` writes structured `EpisodeRecord`s, and
  `red_team/` produces campaign reports — both are ready to be visualized.

## What's pending
- Everything above. Recommended **after** Component 3D and the evaluation
  framework, since a dashboard is presentation, not proof-of-concept (root
  README Section 11).

## Note
The data source (`logs/`) and a possible starting point (the validated
episodes and red-team campaign JSON) are already in place whenever this
layer is picked up.
