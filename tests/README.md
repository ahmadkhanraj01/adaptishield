# tests — Automated Test Suite

**Status:** ✅ **110 tests passing**, ~2 s, no LLM / network / GPU required

## Purpose
A formal `pytest` suite covering every layer plus end-to-end pipeline cases,
so changes can be regression-checked automatically instead of by running
each module's `__main__` block by hand.

## What's done
| File | Covers | Tests |
| :--- | :--- | :--- |
| `test_takeover_rules.py` | 3B's takeover paths + IE resolution (root README §6f–6h, §6d) | 9, ~1.4s |
| `test_adaptive_threat_model.py` | 3D's reward + proposal + step sizing + loop-closes (§6d / §6k / §13) | 14, ~1.0s |
| `test_target_match.py` | The normalized mediator-target match and the one new false-positive class it introduced (§6m) | 14, ~1.7s |
| `test_probe_diagnostic.py` | The read-only root-cause tool, including the classifier-ordering bug that mislabelled 3 healthy probes (§6m) | 11, ~0.9s |
| `test_corpus.py` | Corpus invariants that are easy to destroy by editing a directive: address-free attacks must expose no target, benign controls must carry one, AgentDojo cases must carry no `{*_injection}` placeholder; plus the Wilson interval and the IE-ablation join (§6n) | 19, ~0.9s |
| `test_grpo_kaggle.py` | GRPO env + trainer: threshold replay, reward table, the joint action space, and the tied-reward no-op regression guard (§6l–§6n) | 23, ~0.7s |
| `test_layer5.py` | The human gate: evidence recomputation, regression/claim-mismatch/inert-pattern warnings, "recommends but never decides", append-only decision log, and that untrusted mediator text cannot escape the dashboard's embedded JSON (§6n) | 20, ~0.6s |
| `__init__.py` | Package marker | — |

**110 tests, ~2 s for the whole suite, no LLM / no network / no GPU.** That
constraint is deliberate: anything requiring Ollama lives in `evaluation/`, so
this suite can run on every edit. The four probe regimes are patched out so 3B's
decision logic is tested deterministically.

### Why several of these exist at all

Three were written *because* a bug had already shipped, and they pin the exact
mistake rather than the general area:

- `test_probe_diagnostic.py` — the diagnostic's own classifier ordered a
  `severity == 0` check before the garbled-address check, so it labelled 3
  healthy probes `PROBE_NO_ACTION`. That misdiagnosis would have sent the repair
  at the probe prompt, which was not at fault.
- `test_corpus.py` — the AgentDojo injection filter first searched for
  `"{injection"` and matched **nothing**; the real format is
  `{email_facebook_injection}`. Without the test, 10 pieces of attack
  scaffolding would have entered the benign denominator, one of them inside
  otherwise ordinary prose.
- `test_grpo_kaggle.py` — the trainer proposed a threshold change its own reward
  table scored *lower*. The tied-reward test asserts a no-op, so that cannot
  return silently.

What `test_takeover_rules.py` pins:

- **Temporal drift (6g)** — empty boundaries must not fire, genuine drift must
  still fire, drift must not leak across sessions, history is per-session.
- **IE sample consistency (6h)** — a one-sample paraphrase flip
  (`masked=[1,1]` vs `masked_san=[1,0]`) must be suppressed, while a real
  separation and a partial-sanitisation case must still fire.
- **Rule precedence (6f)** — `masked=[2,2]` with `masked_san=[2,2]` has IE=0
  *and* an inconsistent separation, yet must still fire via the standalone
  rule. The consistency guard must never suppress strong evidence; that
  ordering is the load-bearing invariant between 6f and 6h.

What `test_adaptive_threat_model.py` pins:

- **No literal memorization (6d fix A)** — a missed attack naming
  `attacker@evil.com` must never turn that literal address into a
  `blocked_pattern`; only generalizable injection phrasing (`flagged_markers`)
  survives. No `@` may appear in any proposed pattern.
- **WCR guard in the reward (6d fix B)** — for a malicious episode, a 3C
  `safe_continuation` must reward strictly above a blanket 3A `block`; both
  stay positive (still a correct stop), and a block is surfaced in
  `evaluate_batch()`'s `workflow_lost` list while benign scoring is untouched.
- **IE step sizing (6d fix C)** — 3D's `threshold_step` equals the IE grid
  (`CausalAnalyzer.ie_resolution` = `1/k_samples`), so a proposed move is one
  grid unit (`0.5 → 0.0` at k=2), never the v1 inert `0.5 → 0.4` that fell
  between achievable IE values. `test_takeover_rules.py` pins the resolution
  itself (`ie_resolution` tracks `k_samples`).

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

## Run
```bash
pytest tests/ -v
```

`pytest==8.3.4` and `pytest-asyncio==0.24.0` are pinned in
`requirements.txt`, but were not installed in the venv — `pip install -r
requirements.txt` if `pytest` is missing.
