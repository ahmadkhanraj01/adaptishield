"""
Red Team — Campaign Runner.

Wires Attack Generator -> Execution Agent -> Evaluator -> Optimizer into
one run: generate cases, execute them against a live pipeline, evaluate
ASR/FPR/WCR, then let the Optimizer propose keyword-softened mutations of
whatever was fully defended and run a second generation to see if ASR
moves. Saves both generations' reports to logs/red_team_runs/.

Local default is intentionally small (1 directive x 1 target per family +
all benign scenarios = ~8 cases) since each high-impact case costs
several LLM calls through the Causal Analyzer (~15-20s locally). Scale up
via max_directives/max_targets for a full run on Kaggle.
"""

import json
import os
from datetime import datetime

from red_team.attack_generator import AttackGenerator
from red_team.execution_agent import ExecutionAgent
from red_team.evaluator import Evaluator
from red_team.optimizer import MutationOptimizer

LOG_DIR = "logs/red_team_runs"


def run_campaign(max_directives=1, max_targets=1, max_benign=None, run_gen2=True):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().isoformat()

    gen = AttackGenerator()
    agent = ExecutionAgent()
    evaluator = Evaluator()

    attacks = gen.generate_attacks(max_directives=max_directives, max_targets=max_targets)
    benign = gen.generate_benign(max_scenarios=max_benign)
    cases = attacks + benign

    print(f"[Campaign] Generation 1: {len(attacks)} attack case(s), {len(benign)} benign case(s)")
    results_gen1 = agent.run_batch(cases)
    report_gen1 = evaluator.evaluate(results_gen1)
    evaluator.print_report(report_gen1)

    campaign_record = {
        "timestamp": timestamp,
        "generation_1": evaluator.to_dict(report_gen1),
    }

    if run_gen2:
        optimizer = MutationOptimizer()
        mutated_cases = optimizer.propose_next_generation(report_gen1, attacks)

        if mutated_cases:
            print(f"\n[Campaign] Generation 2: {len(mutated_cases)} mutated attack case(s)")
            results_gen2 = agent.run_batch(mutated_cases)
            # Gen-2 report only makes sense over attacks (no fresh benign
            # run needed — FPR doesn't change when only attacks mutate).
            report_gen2 = evaluator.evaluate(results_gen2)
            evaluator.print_report(report_gen2)
            campaign_record["generation_2"] = evaluator.to_dict(report_gen2)

            print(f"\n{'='*60}")
            print("[Campaign] Generation 1 vs 2 — ASR by family")
            print(f"{'='*60}")
            gen1_by_fam = {f.family: f.asr for f in report_gen1.by_family}
            gen2_by_fam = {f.family: f.asr for f in report_gen2.by_family}
            for fam in sorted(set(gen1_by_fam) | set(gen2_by_fam)):
                g1 = gen1_by_fam.get(fam)
                g2 = gen2_by_fam.get(fam)
                g1_s = f"{g1:.0%}" if g1 is not None else "n/a"
                g2_s = f"{g2:.0%}" if g2 is not None else "n/a"
                print(f"  {fam:<28} gen1={g1_s:<6} gen2={g2_s}")
        else:
            print("\n[Campaign] Nothing for the Optimizer to mutate this round.")

    out_path = os.path.join(LOG_DIR, f"campaign_{timestamp.replace(':', '-')}.json")
    with open(out_path, "w") as f:
        json.dump(campaign_record, f, indent=2)
    print(f"\n[Campaign] Report saved to {out_path}")

    return campaign_record


if __name__ == "__main__":
    run_campaign()
