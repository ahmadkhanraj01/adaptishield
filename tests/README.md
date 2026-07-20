# tests — Automated Test Suite

**Status:** 🟡 Started — `test_temporal_drift.py` (4 tests, passing)

## Purpose
A formal `pytest` suite covering every layer plus end-to-end pipeline cases,
so changes can be regression-checked automatically instead of by running
each module's `__main__` block by hand.

## What's done
| File | Covers | Tests |
| :--- | :--- | :--- |
| `test_temporal_drift.py` | 3B's temporal-drift takeover rule (root README Sec. 6g) — empty boundaries must not fire, genuine drift must still fire, drift must not leak across sessions, history recorded per session | 4, ~0.55s |

## The pattern to follow
`test_temporal_drift.py` patches the four probe regimes out and asserts on the
decision logic directly. **No Ollama, no GPU, sub-second.** That split is
deliberate and worth preserving:

- **`tests/`** — pure decision logic, deterministic, fast enough to run on
  every change. Patch `_run_regime` / `_sanitize_mediator` and drive the
  severities directly.
- **`evaluation/`** — anything needing a live model. Those runs take minutes
  and vary between runs, so they are experiments, not tests, and their
  numbers get recorded in the READMEs rather than asserted on.

Most of what is worth pinning in 3B/3C/3D is decision logic wrapped around an
LLM call, so most of it can live here.

## What's pending — suggested starting points
| Test target | Natural source |
| :--- | :--- |
| Takeover rules | The IE rule and the standalone `masked >= 2` rule (Sec. 6f), same patching approach |
| End-to-end pipeline | The 3 validated episodes in root README Section 6 make ready-made regression cases |
| Layer 0–4 units | Each module's existing `__main__` assertions, promoted to `test_*.py` |
| Red team metrics | `red_team/evaluator.py` ASR/FPR/WCR on a fixed `ExecutionResult` list — no LLM needed |
| 3D reward + proposal | `adaptive_threat_model.py` is already CPU-only and deterministic; its `__main__` demo is nearly a test already |

## Run
```bash
pytest tests/ -v
```

`pytest==8.3.4` and `pytest-asyncio==0.24.0` are pinned in
`requirements.txt`, but were not installed in the venv — `pip install -r
requirements.txt` if `pytest` is missing.
