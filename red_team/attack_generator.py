"""
Red Team — Attack Generator.

Combines attack_library.py's raw templates/directives/targets into
concrete RedTeamCase objects the Execution Agent can run against the
pipeline. Also generates the benign counterpart cases used for FPR.
"""

from dataclasses import dataclass
from typing import List, Optional

from red_team.attack_library import (
    ATTACK_FAMILIES,
    DIRECTIVES,
    ATTACKER_TARGETS,
    BENIGN_SCENARIOS,
    LEGITIMATE_DESTINATION_URL,
    AttackTemplate,
    training_targets,
    holdout_targets,
)


@dataclass
class RedTeamCase:
    case_id:            str
    family:             str            # attack family name, or "benign"
    expected_malicious: bool
    user_input:         str
    tool_response:      str
    tool_name:          str
    proposed_action:    str
    server_name:        str
    destination_url:    str
    description:        str
    generation:         int = 1        # bumped by Optimizer for mutated variants


class AttackGenerator:
    """
    tool_name/server_name are fixed to send_email/"email-api" for this v1 —
    the only high-impact tool the pipeline currently models with a
    meaningful permission+egress surface. Extending to other tools just
    means adding more BENIGN_SCENARIOS/DIRECTIVES with a different
    tool_name, once the pipeline itself models more real tools.
    """

    TOOL_NAME   = "send_email"
    SERVER_NAME = "email-api"

    def __init__(self, families: Optional[List[AttackTemplate]] = None):
        self.families = families if families is not None else list(ATTACK_FAMILIES)

    def generate_attacks(self, max_directives: Optional[int] = None,
                          max_targets: Optional[int] = None,
                          targets: Optional[List[dict]] = None) -> List[RedTeamCase]:
        """
        `targets` overrides target selection entirely when given (pass
        training_targets() / holdout_targets() to keep the train/held-out
        split first-class). When it is None, fall back to the historical
        index-slice behaviour (`ATTACKER_TARGETS[:max_targets]`).

        case_id encodes the target by its email local-part rather than a
        positional index, so cases stay uniquely identifiable even when the
        training and held-out splits are generated in separate calls and
        later merged into one report.
        """
        directives = DIRECTIVES[:max_directives] if max_directives else DIRECTIVES
        if targets is None:
            targets = ATTACKER_TARGETS[:max_targets] if max_targets else ATTACKER_TARGETS

        cases: List[RedTeamCase] = []
        for fam in self.families:
            for d_idx, directive_tpl in enumerate(directives):
                for target in targets:
                    directive = directive_tpl.format(target=target["email"])
                    tool_response = fam.template.format(directive=directive)
                    target_slug = target["email"].split("@")[0]
                    case_id = f"{fam.family}-d{d_idx}-{target_slug}"
                    cases.append(RedTeamCase(
                        case_id=case_id,
                        family=fam.family,
                        expected_malicious=True,
                        user_input="Reply to my latest email",
                        tool_response=tool_response,
                        tool_name=self.TOOL_NAME,
                        proposed_action=f"send_email to {target['email']}",
                        server_name=self.SERVER_NAME,
                        destination_url=target["destination_url"],
                        description=fam.description,
                    ))
        return cases

    def generate_training_attacks(self, max_directives: Optional[int] = None) -> List[RedTeamCase]:
        """Attacks over the training addresses only — the set 3D may learn from."""
        return self.generate_attacks(max_directives=max_directives,
                                     targets=training_targets())

    def generate_holdout_attacks(self, max_directives: Optional[int] = None) -> List[RedTeamCase]:
        """Attacks over the held-out addresses only — generalization probe (never trained on)."""
        return self.generate_attacks(max_directives=max_directives,
                                     targets=holdout_targets())

    def generate_benign(self, max_scenarios: Optional[int] = None) -> List[RedTeamCase]:
        scenarios = BENIGN_SCENARIOS[:max_scenarios] if max_scenarios else BENIGN_SCENARIOS

        cases: List[RedTeamCase] = []
        for i, scenario in enumerate(scenarios):
            cases.append(RedTeamCase(
                case_id=f"benign-{i}",
                family="benign",
                expected_malicious=False,
                user_input=scenario["user_input"],
                tool_response=scenario["tool_response"],
                tool_name=self.TOOL_NAME,
                proposed_action=scenario["proposed_action"],
                server_name=self.SERVER_NAME,
                destination_url=LEGITIMATE_DESTINATION_URL,
                description="Benign high-impact tool call, no injection — true-negative control.",
            ))
        return cases

    def generate_campaign(self, max_directives: Optional[int] = None,
                           max_targets: Optional[int] = None,
                           max_benign: Optional[int] = None) -> List[RedTeamCase]:
        """Convenience: attacks + benign controls in one list."""
        return (
            self.generate_attacks(max_directives=max_directives, max_targets=max_targets)
            + self.generate_benign(max_scenarios=max_benign)
        )


if __name__ == "__main__":
    gen = AttackGenerator()
    train  = gen.generate_training_attacks()
    heldout = gen.generate_holdout_attacks()
    benign = gen.generate_benign()
    print(f"{len(gen.families)} families x {len(DIRECTIVES)} directives")
    print(f"Training attacks : {len(train)} (over {len(training_targets())} target(s))")
    print(f"Held-out attacks : {len(heldout)} (over {len(holdout_targets())} target(s))")
    print(f"Benign controls  : {len(benign)}")

    # Provable invariant: no held-out address ever appears in the training split.
    holdout_emails = {t["email"] for t in holdout_targets()}
    leaked = [c.case_id for c in train
              if any(e in c.proposed_action for e in holdout_emails)]
    assert not leaked, f"held-out address leaked into training split: {leaked}"
    print("OK: no held-out address in the training split.")
