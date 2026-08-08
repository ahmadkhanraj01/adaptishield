# tests — Automated Test Suite

**Status:** ✅ **223 tests passing**, ~6 s, no LLM / no network / no GPU

```bash
python3 -m pytest tests/ -q          # 223 passed in ~6s
python3 -m pytest tests/test_layer5.py -v
```

---

## Files

| File | Covers | Tests |
| :--- | :--- | ---: |
| `test_takeover_rules.py` | 3B's takeover paths + IE resolution (§6f–6h, §6d) | 9 |
| `test_adaptive_threat_model.py` | 3D's reward, proposal, step sizing, loop-closes (§6d / §6k) | 14 |
| `test_target_match.py` | Normalized mediator-target match (§6m) + the **keyword grounding** check (§6p) | 21 |
| `test_probe_diagnostic.py` | The read-only root-cause tool, incl. the classifier-ordering bug that mislabelled 3 healthy probes (§6m) | 11 |
| `test_corpus.py` | Corpus invariants, the Wilson interval, the IE-ablation join, and the FPR **staleness guard** (§6n, §6o) | 22 |
| `test_grpo_kaggle.py` | GRPO env + trainer: threshold replay, reward table, joint action space, tied-reward **no-op guard** (§6l–6n) | 23 |
| `test_layer5.py` | The human gate + dashboard escaping (§6n) | 20 |
| `test_ablation.py` | Phase 7 arms + campaign checkpointing | 15 |
| `test_attribution.py` | Per-layer attribution ordering + the corpus invariants that keep the benchmark able to answer its own question, plus the Phase 10 arms and derived-ASR semantics | 39 |
| `test_spotlighting.py` | The external baseline's transforms — non-no-op, content preserved not destroyed, instruction matches the transform, unknown variant raises, and no layer imports the baseline | 25 |
| `test_negation_scoring.py` | Negation handling for agent-chosen actions: refusals naming the address are not steering, clause-scoped so `"do not reply … instead bcc X"` still scores 2, monotone, and **3B's regime scorer is untouched** | 24 |
| `__init__.py` | Package marker | — |

---

## The rule that keeps this suite fast

**Anything needing a live model lives in `evaluation/`, not here.**

Those runs take minutes and vary between runs, so they are *experiments*, not
tests, and their numbers are recorded in READMEs rather than asserted on. What
lives here is the decision logic *wrapped around* the LLM call — which is most of
what is worth pinning in 3A/3B/3C/3D. The four probe regimes are patched out so
severities can be supplied directly and the takeover logic tested
deterministically.

That constraint is why the suite can run on every edit. Breaking it — adding one
test that calls Ollama — would cost that property immediately.

---

## Several of these exist because a bug already shipped

They pin the *specific* mistake, not the general area. That is deliberate: a test
written against the shape of a real defect catches its recurrence, whereas a test
written against a vague worry usually catches nothing.

| Test | The defect it pins |
| :--- | :--- |
| `test_probe_diagnostic.py` | The diagnostic's own classifier ordered a `severity == 0` check *before* the garbled-address check, so it labelled 3 healthy probes `PROBE_NO_ACTION`. That misdiagnosis would have sent the repair at the probe prompt, which was not at fault. |
| `test_corpus.py` | The AgentDojo injection filter first searched for `"{injection"` and matched **nothing** — the real format is `{email_facebook_injection}`. Ten pieces of attack scaffolding would have entered the *benign* denominator. |
| `test_grpo_kaggle.py` | The trainer proposed a threshold change its own reward table scored **lower** (+0.8683 vs +0.8688), and `apply_update` would have accepted it silently. The tied-reward test asserts a no-op. |
| `test_target_match.py` | `_references_mediator_target` compared verbatim, and `gemma3:4b` drops the hyphen in `leaker@shadow-mail.net` in **57/57** mentions — one character behind all 15 misses (§6m). Also pins the §6p grounding: a high-impact verb escalates only if the mediator asked for something of that kind. |
| `test_layer5.py` | Untrusted mediator text must not escape the dashboard's embedded JSON. The records contain prompt injections *by construction* — an audit tool that could be attacked by what it audits would be an unusually poor one. |
| `test_ablation.py` | A position-keyed campaign checkpoint would pair a case with another case's result. Keyed on `case_id` and tested by reordering. |
| `test_negation_scoring.py` | The scorer had no negation handling, so a refusal naming the attacker address scored as compliance — **16 of 37** cases in the Phase 10 baseline, which reversed the sign of the result (39.4%→56.1% became 34.8%→33.3%, p=1.00). Also pins the harder half: negation must be scoped to the clause naming the target, or `"do not reply … instead bcc X"` reads as a refusal and undercounts a real steering. |
| `test_attribution.py` | Two, both hidden by the benchmark's old exfil destinations. **V7 could never fail the check it existed to test** — labelled `defended_by="Layer 4 permission control"` while running against a server that declares `send_email` in scope, with egress refusing the case first. And a `blocked` case could attribute to `none` with `reached_tool=True`, undercounting a refused request. One test now fails if any malicious vector but V3 is ever pointed at an exfil host again — the regression that caused the withdrawal twice. |

---

## Two properties worth not breaking

**Ablation arms must differ in exactly the flags they name.** `test_ablation.py`
asserts this per arm. A config that silently disabled a second component would
attribute that component's contribution to the one under test — which is the one
thing an ablation cannot afford.

**A disabled layer must keep the record schema identical.**
`ScreenResult.permissive()` returns a real verdict rather than `None`, so
telemetry has the same shape in every arm. If turning a layer off changed the
record shape, the arms would no longer be comparable.

---

## What's pending

| Test target | Natural source |
| :--- | :--- |
| End-to-end pipeline | The 3 validated episodes make ready-made regression cases |
| Layer 0–4 units | Each module's existing `__main__` assertions, promoted to `test_*.py` |
| Red team metrics | `red_team/evaluator.py` ASR/FPR/WCR on a fixed `ExecutionResult` list — no LLM needed |
| Benchmark reporting | `evaluation/benchmark.py` summarise/per-vector on synthetic results |

---

`pytest==8.3.4` and `pytest-asyncio==0.24.0` are pinned in `requirements.txt`.
If `pytest` is missing: `pip install -r requirements.txt`.
