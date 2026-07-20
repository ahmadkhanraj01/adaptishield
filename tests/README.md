# tests — Automated Test Suite

**Status:** 🟡 Started — `test_takeover_rules.py` (8 tests, passing)

## Purpose
A formal `pytest` suite covering every layer plus end-to-end pipeline cases,
so changes can be regression-checked automatically instead of by running
each module's `__main__` block by hand.

## What's done
| File | Covers | Tests |
| :--- | :--- | :--- |
| `test_takeover_rules.py` | All three of 3B's takeover paths (root README Sec. 6f–6h) | 8, ~0.7s |

What it pins:

- **Temporal drift (6g)** — empty boundaries must not fire, genuine drift must
  still fire, drift must not leak across sessions, history is per-session.
- **IE sample consistency (6h)** — a one-sample paraphrase flip
  (`masked=[1,1]` vs `masked_san=[1,0]`) must be suppressed, while a real
  separation and a partial-sanitisation case must still fire.
- **Rule precedence (6f)** — `masked=[2,2]` with `masked_san=[2,2]` has IE=0
  *and* an inconsistent separation, yet must still fire via the standalone
  rule. The consistency guard must never suppress strong evidence; that
  ordering is the load-bearing invariant between 6f and 6h.

## The pattern to follow
`test_takeover_rules.py` patches the four probe regimes out and asserts on the
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
