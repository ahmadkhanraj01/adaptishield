# tests — Automated Test Suite

**Status:** 🔲 Pending — empty folder, no formal tests yet

## Purpose
A formal `pytest` suite covering every layer plus end-to-end pipeline cases,
so changes can be regression-checked automatically instead of by running
each module's `__main__` block by hand.

## Current reality
- **No pytest files exist yet.** Testing today is done via each module's
  own `if __name__ == "__main__"` block (see root README Section 10 for the
  full manual checklist) and the red-team campaign.
- `pytest==8.3.4` and `pytest-asyncio==0.24.0` are already pinned in
  `requirements.txt`, so the harness is ready to use.

## What's pending — suggested starting points
| Test target | Natural source |
| :--- | :--- |
| End-to-end pipeline | The 3 validated episodes in root README Section 5 make ready-made regression cases |
| Layer 0–4 units | Each module's existing `__main__` assertions, promoted to `test_*.py` |
| Red team metrics | `red_team/evaluator.py` ASR/FPR/WCR on a fixed result set |
| 3B causal signal | Guard against regressions in ACE/IE/DE on the true-positive payload |

## What's done
- Nothing in this folder yet — but the manual checklist (root README
  Section 10) already enumerates the expected inputs/outputs to encode.

## Run (once tests exist)
```bash
pytest tests/
```
