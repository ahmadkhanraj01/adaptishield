---
tags: [adaptishield, rule]
type: reference
---

# Traps

**Things that have already cost time.** Every one of these produced a wrong number
or a wasted campaign at least once.

| Trap | What happens | Guard |
| :--- | :--- | :--- |
| **Stale dataset** | A campaign that dies part-way leaves the old `episodes.jsonl`; `fpr_report` prints **pre-fix numbers as if current** | It now prints the dataset age and shouts **`STALE`**. **Read that header.** |
| **Stale checkpoint** | Cached per-case results describe the **old** pipeline | `rm -rf logs/campaign_checkpoint` **and** `logs/benchmark_checkpoint` after **any** pipeline change |
| **A subsample that omits the hard cases** | The benchmark's external benign cohort is a stride subsample (indices 0, 6, …, 54) that **excludes campaign documents 41 and 55 — both known false positives**. Its 0/30 reads as an improvement on 3.3% and is not | The report prints the caveat itself. [[FPR]] of record comes from `fpr_report` at n=60 → [[Current Numbers]] |
| **Idle Ollama reads as "no GPU"** | `/api/ps` lists only *resident* models, so checking before a run reports no GPU on every clean start | The run manifest samples Ollama **after** the arms run |
| **Ollama falls back to CPU** | After a CUDA fault it silently runs CPU-only: ~11 GB RAM, slower, more non-determinism, and **different outputs** | `curl -s localhost:11434/api/ps` → **`size_vram` must be > 0**. If 0: `sudo systemctl restart ollama` |
| **Two variables at once** | A campaign changing code **and** backend cannot attribute a regression | **Change one thing per campaign** |
| **Kaggle credentials** | Needs a **legacy 32-hex key** (Settings → API → *Create New Token*). The newer "API Tokens" page issues a longer token CLI 1.7.4.5 cannot use — and 1.7.4.5 is the newest on PyPI | `python3 evaluation/kaggle/test_credentials.py` |
| **`kaggle.json`** | Holds a live key in **plaintext in the repo root** | Already git-ignored — **keep it that way**. `origin` is now a **public** repo |
| **A defense's own output inflating the metric** | Spotlighting's instruction induces refusals *naming* the attacker address, and the keyword scorer escalates on any target mention. It reported the defense as **17 points worse** when it was neutral | `score_agent_action` scopes negation to the clause naming the target → [[The Scorer Cannot See Negation]] |
| **A zero with no positive control** | A broken parser, an empty join, or a predicate that never fires all print the same reassuring zero | `refusal_audit` synthesises the case it is hunting against a real mediator and **withholds the result** if the control fails → [[3B's Refusal Exposure Is Live and Unrealised]] |
| **Auditing only the malicious half** | The attacks are where a detection defect costs a miss; the **benign** cohort is where it costs a false positive — the expensive direction | Join `all_vectors()`, never `VECTORS`. Pinned by a test |

## The one that nearly cost a conclusion

The CPU-fallback and one-variable traps fired **together** in
[[6p — Probe Hallucination Fixed at the Scorer]]: a campaign testing a prompt
change also happened to run on CPU, so the observed regression could not be
attributed. Restoring the GPU and reverting **only** the prompt isolated it — the
prompt was the cause. Without that isolation the wrong component would have been
blamed.

## Campaigns are resumable

They checkpoint **per case** to `logs/campaign_checkpoint/`, so a crash costs the
case in flight, **not 1.5 hours**. This absorbed three interruptions on 26 July.
Just re-run the same command.

## The general form

Most of these are instances of [[Instruments Fail More Than Mechanisms]] — a tool
that reads whatever is present and reports a verdict it did not test.
