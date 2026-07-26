"""
Phase 7 — the eight-vector benchmark: which layer actually stops what.

    python -m evaluation.benchmark --repeats 3
    python -m evaluation.benchmark --arms undefended,full --repeats 1

Runs the fixed vector set (evaluation/vectors.py) through several ablation arms
of the same pipeline and reports ASR / FPR / WCR per arm, plus a per-vector
breakdown of which arm stopped it.

WHAT THIS IS FOR. "AdaptiShield helps" is not a claim until there is something
it is being compared against. The campaign in §6l–§6p measures the full system
against ground-truth labels, which answers "does it work" but not "which part is
doing the work" — and after §6n, where a marker weight that looked free on a
self-authored corpus produced 36 false positives on an external one, the second
question is the one worth more.

THE ARMS, AND WHAT EACH ISOLATES
  undefended   nothing on. The floor: what this corpus does unopposed. If ASR is
               not ~100% here, the vectors are too weak to measure anything.
  static_only  screener + 3A patterns + Layer 4. A plausible defense WITHOUT this
               project's causal sub-layer — the honest baseline to beat.
  full         complete AdaptiShield.
  no_egress    full minus the allowlist. Separates what 3A/3B/3C detect from what
               a static allowlist was quietly backstopping — the reason §6n added
               address-free attacks in the first place.

The `full` vs `static_only` gap is this project's contribution. The `full` vs
`no_egress` gap is how much of that was really Layer 4.

READ THE COVERAGE MAP BEFORE THE NUMBERS. Two of the eight vectors are
APPROXIMATED — the pipeline consumes tool *responses*, not tool *descriptions* or
server manifests, so tool-poisoning and rug-pull are modelled at the nearest
boundary that exists. Those rows cannot support a claim as strong as the natively
modelled ones, and the report prints them flagged rather than blended in.

Repeats matter: even at temperature 0 the pipeline is not perfectly
deterministic (§6n measured 2/564 regime severities disagreeing; §6p saw which
documents trip the detector vary between runs), so a single observation per
vector cannot tell a defense from a coin flip.
"""

import argparse
import json
import os
import time
from collections import defaultdict
from typing import Dict, List

from adaptishield_pipeline import PipelineConfig
from evaluation.vectors import VECTORS, as_cases, coverage_table

ARMS = {
    "undefended":  PipelineConfig.undefended,
    "static_only": PipelineConfig.static_only,
    "full":        PipelineConfig.full,
    "no_egress":   PipelineConfig.no_egress,
}

DEFAULT_OUT = "logs/benchmark"


def run_arm(name: str, repeats: int, checkpoint_dir: str = None) -> List:
    """Run every vector through one arm and return the ExecutionResults."""
    from red_team.execution_agent import ExecutionAgent
    from adaptishield_pipeline import AdaptiShieldPipeline

    config = ARMS[name]()
    agent = ExecutionAgent(pipeline=AdaptiShieldPipeline(config=config))
    cp = os.path.join(checkpoint_dir, f"{name}.jsonl") if checkpoint_dir else None
    print(f"\n{'#' * 70}\n# ARM: {name}  ({repeats} repeat(s) per vector)\n{'#' * 70}")
    return agent.run_batch(as_cases(repeats), checkpoint=cp)


def summarise(name: str, results: List) -> Dict:
    """
    ASR / FPR / WCR for one arm.

    Defined exactly as red_team/evaluator.py defines them, so the numbers here
    are comparable with every campaign figure elsewhere in the project rather
    than being a second, subtly different metric.
    """
    mal = [r for r in results if r.expected_malicious]
    ben = [r for r in results if not r.expected_malicious]
    asr = sum(1 for r in mal if r.attack_succeeded) / len(mal) if mal else 0.0
    fpr = sum(1 for r in ben if r.false_positive) / len(ben) if ben else 0.0
    wcr = sum(1 for r in mal if r.task_completed) / len(mal) if mal else 0.0
    blocked = sum(1 for r in results if r.final_status == "blocked")
    return {"arm": name, "n": len(results), "asr": asr, "fpr": fpr, "wcr": wcr,
            "n_malicious": len(mal), "n_benign": len(ben),
            "stopped": sum(1 for r in mal if not r.attack_succeeded),
            "blocked_outright": blocked}


def per_vector(results_by_arm: Dict[str, List]) -> Dict[str, Dict[str, str]]:
    """vector id -> arm -> 'stopped k/n' (or the benign equivalent)."""
    table: Dict[str, Dict[str, str]] = defaultdict(dict)
    for arm, results in results_by_arm.items():
        by_vec = defaultdict(list)
        for r in results:
            by_vec[r.family].append(r)
        for vid, rs in by_vec.items():
            if rs[0].expected_malicious:
                k = sum(1 for r in rs if not r.attack_succeeded)
            else:
                k = sum(1 for r in rs if not r.false_positive)   # correctly passed
            table[vid][arm] = f"{k}/{len(rs)}"
    return table


def report(results_by_arm: Dict[str, List]) -> Dict:
    print("\n" + "=" * 96)
    print("  PHASE 7 — EIGHT-VECTOR BENCHMARK")
    print("=" * 96)
    print("\n  COVERAGE MAP — read this before the numbers\n")
    print(coverage_table())
    approx = [v.vid for v in VECTORS if not v.natively_modelled]
    print(f"\n  APPROXIMATED (modelled at the nearest boundary the pipeline has): "
          f"{', '.join(approx)}")
    print("  Those rows cannot support a claim as strong as the natively modelled ones.")

    print("\n  " + "-" * 92)
    print("  PER-ARM METRICS  (ASR lower is better; WCR higher is better)")
    print(f"    {'arm':<14}{'n':>5}{'ASR':>9}{'FPR':>9}{'WCR':>9}   {'stopped':>9}")
    summaries = {}
    for arm in results_by_arm:
        s = summarise(arm, results_by_arm[arm])
        summaries[arm] = s
        print(f"    {arm:<14}{s['n']:>5}{s['asr']:>8.1%}{s['fpr']:>9.1%}"
              f"{s['wcr']:>9.1%}   {s['stopped']:>4}/{s['n_malicious']}")

    print("\n  " + "-" * 92)
    print("  PER-VECTOR — attacks stopped (benign: correctly passed)")
    arms = list(results_by_arm)
    print(f"    {'id':<5}{'vector':<34}" + "".join(f"{a:>13}" for a in arms))
    pv = per_vector(results_by_arm)
    for v in VECTORS:
        row = "".join(f"{pv.get(v.vid, {}).get(a, '-'):>13}" for a in arms)
        flag = " *" if not v.natively_modelled else ""
        print(f"    {v.vid:<5}{(v.name[:30] + flag):<34}{row}")
    print("    * approximated vector")

    # The two comparisons the benchmark exists to make.
    if "full" in summaries and "static_only" in summaries:
        d = summaries["static_only"]["asr"] - summaries["full"]["asr"]
        print(f"\n  CONTRIBUTION OF THE CAUSAL SUB-LAYER (static_only -> full):")
        print(f"    ASR {summaries['static_only']['asr']:.1%} -> "
              f"{summaries['full']['asr']:.1%}   ({d:+.1%})")
        print(f"    WCR {summaries['static_only']['wcr']:.1%} -> "
              f"{summaries['full']['wcr']:.1%}   "
              f"(3C is what keeps the workflow alive after a takeover)")
    if "full" in summaries and "no_egress" in summaries:
        d = summaries["no_egress"]["asr"] - summaries["full"]["asr"]
        print(f"\n  HOW MUCH LAYER 4 WAS BACKSTOPPING (full -> no_egress):")
        print(f"    ASR {summaries['full']['asr']:.1%} -> "
              f"{summaries['no_egress']['asr']:.1%}   ({d:+.1%})")
        print("    A large gap here means detection was leaning on the allowlist.")

    return {"summaries": summaries, "per_vector": pv,
            "approximated": approx, "generated": time.strftime("%Y-%m-%dT%H:%M:%S")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--arms", default="undefended,static_only,full,no_egress")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--checkpoint-dir", default="logs/benchmark_checkpoint",
                    help="resume a crashed run; DELETE after changing the pipeline")
    args = ap.parse_args()

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in arms if a not in ARMS]
    if unknown:
        raise SystemExit(f"[benchmark] unknown arm(s): {unknown}. "
                         f"Available: {list(ARMS)}")

    results_by_arm = {a: run_arm(a, args.repeats, args.checkpoint_dir) for a in arms}
    out = report(results_by_arm)

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "benchmark.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n[benchmark] wrote {path}")


if __name__ == "__main__":
    main()
