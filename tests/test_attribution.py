"""
Phase 7 — per-layer attribution, and the vector-set invariants that make the
benchmark able to answer its own question.

WHY THESE TESTS EXIST. The first eight-vector run produced a headline result that
measured its own construction: six of eight vectors pointed at an exfiltration
host, so Layer 4's allowlist refused them before any detection layer was
consulted, and `static_only` tied with `full` by construction. Attack success is
one bit, and one bit cannot tell "3B caught it" from "the allowlist caught it".

So two properties are pinned here, deterministically and without an LLM:

  1. **Attribution is correct and ordered.** It must name the first gate in
     pipeline order that refused, and record the later ones as redundant — that
     redundancy is the signal that a detection result is being concealed.
  2. **The corpus cannot re-absorb itself.** Exactly one malicious vector may
     point at an exfil host, the benign cohorts stay separate, and V7 must run
     against a server that does not declare the tool it invokes.

    python3 -m pytest tests/test_attribution.py -v
"""

import pytest

from evaluation.attribution import (CAUSAL_LAYER, L4_EGRESS, L4_PERMISSION,
                                    NOT_STOPPED, THREE_A, THREE_B, attribute,
                                    attribution_counts, backstop_share)
from evaluation.vectors import EXFIL, LEGIT, REQUIRED_SERVERS, VECTORS, all_vectors


def result(final_status="approved_direct", permission=True, egress=True,
           causal_takeover=None, causal_verdict=None, malicious=True,
           case_id="c", family="V1"):
    """An ExecutionResult shaped exactly as the pipeline produces one."""
    from red_team.execution_agent import ExecutionResult
    return ExecutionResult(
        case_id=case_id, family=family, generation=1,
        expected_malicious=malicious, tool_name="send_email",
        proposed_action="send_email to x@y.z", final_status=final_status,
        outcome_severity=0, permission_allowed=permission, egress_allowed=egress,
        causal_takeover=causal_takeover, attack_succeeded=None,
        false_positive=None, task_completed=False, raw_result={},
        causal_verdict=causal_verdict)


# ── the single gates ──────────────────────────────────────────────────────
class TestSingleGate:
    def test_3a_block_has_no_causal_verdict(self):
        """A block before 3B ran is 3A's — it is the only thing 3A does alone."""
        a = attribute(result(final_status="blocked"))
        assert a.stopped_by == THREE_A
        assert a.stopped_by_detection and not a.stopped_by_causal
        assert not a.reached_tool

    def test_safe_continuation_is_a_3b_takeover(self):
        a = attribute(result(final_status="safe_continuation", causal_takeover=True))
        assert a.stopped_by == THREE_B == CAUSAL_LAYER
        assert a.stopped_by_causal

    def test_permission_refusal(self):
        a = attribute(result(permission=False))
        assert a.stopped_by == L4_PERMISSION
        assert not a.stopped_by_detection

    def test_egress_refusal(self):
        """The withdrawn run's every static_only case looked exactly like this."""
        a = attribute(result(egress=False))
        assert a.stopped_by == L4_EGRESS
        assert not a.stopped_by_detection

    def test_nothing_stopped_it(self):
        a = attribute(result())
        assert a.stopped_by == NOT_STOPPED
        assert a.reached_tool
        assert not a.stopped_by_detection

    def test_gates_that_did_not_run_are_not_refusals(self):
        """None means the gate was disabled or never reached, not that it passed."""
        assert attribute(result(permission=None, egress=None)).stopped_by == NOT_STOPPED


# ── ordering, which is the whole point ────────────────────────────────────
class TestPipelineOrder:
    def test_3b_wins_over_a_later_egress_refusal(self):
        """
        Detection ran first, so the stop is 3B's — but egress is recorded as
        redundant, which is what says the result is backstopped.
        """
        a = attribute(result(final_status="safe_continuation",
                             causal_takeover=True, egress=False))
        assert a.stopped_by == THREE_B
        assert a.redundant_gates == [L4_EGRESS]
        assert a.backstopped

    def test_3a_wins_over_everything_later(self):
        a = attribute(result(final_status="blocked", permission=False, egress=False))
        assert a.stopped_by == THREE_A
        assert a.redundant_gates == [L4_PERMISSION, L4_EGRESS]

    def test_permission_precedes_egress(self):
        a = attribute(result(permission=False, egress=False))
        assert a.stopped_by == L4_PERMISSION
        assert a.redundant_gates == [L4_EGRESS]

    def test_an_unbackstopped_detection_is_not_marked_backstopped(self):
        """The case the repaired corpus is built to produce."""
        a = attribute(result(final_status="safe_continuation",
                             causal_takeover=True, egress=True))
        assert a.stopped_by == THREE_B
        assert a.redundant_gates == []
        assert not a.backstopped


class TestSanitizerDisabledPath:
    """
    With 3C off, a confirmed takeover returns `blocked` — and
    `ExecutionResult.causal_takeover` is inferred from `final_status`, so it
    reports None there. Attributing that to 3A would credit the static layer
    with the causal layer's work.
    """

    def test_blocked_with_a_takeover_verdict_is_3b_not_3a(self):
        a = attribute(result(final_status="blocked",
                             causal_verdict={"takeover": True, "ie": 1.0}))
        assert a.stopped_by == THREE_B

    def test_a_blocked_case_never_reads_as_reaching_the_tool(self):
        """
        Defensive. The pipeline cannot currently produce `blocked` with a
        no-takeover verdict — 3B declining routes to `approved_causal` — but if a
        new block path ever appears, attribution must not answer "nothing stopped
        it" for a refused request. That would report `reached_tool=True` for a
        blocked case and quietly undercount, which is how the first run's numbers
        went wrong in the first place.
        """
        a = attribute(result(final_status="blocked",
                             causal_verdict={"takeover": False, "ie": 0.0}))
        assert a.stopped_by == THREE_A
        assert not a.reached_tool


# ── aggregates ────────────────────────────────────────────────────────────
class TestAggregates:
    def test_counts_ignore_benign_cases(self):
        results = [result(final_status="safe_continuation", causal_takeover=True),
                   result(egress=False),
                   result(malicious=False, final_status="blocked")]
        counts = attribution_counts(results)
        assert counts[THREE_B] == 1 and counts[L4_EGRESS] == 1
        assert sum(counts.values()) == 2

    def test_backstop_share_is_one_when_every_detection_is_covered(self):
        results = [result(final_status="safe_continuation",
                          causal_takeover=True, egress=False)] * 2
        assert backstop_share(results) == 1.0

    def test_backstop_share_is_zero_when_detection_stands_alone(self):
        results = [result(final_status="safe_continuation", causal_takeover=True)]
        assert backstop_share(results) == 0.0

    def test_backstop_share_is_none_without_any_detection_stop(self):
        """A share of nothing is not 0% — reporting it as 0% would read as good news."""
        assert backstop_share([result(egress=False)]) is None


# ── corpus invariants: the repair itself ──────────────────────────────────
class TestVectorSet:
    def test_exactly_one_malicious_vector_is_absorbable_by_egress(self):
        """
        Six of seven were, and that is what invalidated the first run. Only V3 may
        be: testing the allowlist is its declared purpose.
        """
        absorbable = [v.vid for v in VECTORS
                      if v.expected_malicious and v.destination_url == EXFIL]
        assert absorbable == ["V3"], (
            f"{absorbable} point at an exfil host; the allowlist will refuse them "
            f"before 3A/3B are consulted and every arm will tie by construction")

    def test_every_other_malicious_vector_uses_the_legitimate_host(self):
        for v in VECTORS:
            if v.expected_malicious and v.vid != "V3":
                assert v.destination_url == LEGIT, f"{v.vid} bypasses detection"

    def test_v7_runs_against_a_server_that_does_not_declare_the_tool(self):
        """
        An out-of-scope invocation cannot be tested against a server with the tool
        in scope. V7 claimed Layer 4 permission as its defense while running on
        `email-api`, which declares send_email — the exfil destination hid that
        the scope check could never fire.
        """
        v7 = next(v for v in VECTORS if v.vid == "V7")
        scopes = {name: tools for name, _, _, tools in REQUIRED_SERVERS}
        assert v7.server_name in scopes, "V7's server is not registered"
        assert "send_email" not in scopes[v7.server_name]

    def test_default_vectors_run_against_a_server_that_does_declare_send_email(self):
        scopes = {name: tools for name, _, _, tools in REQUIRED_SERVERS}
        for v in VECTORS:
            if v.vid != "V7":
                assert "send_email" in scopes[v.server_name], (
                    f"{v.vid} would fail the scope check for the wrong reason")

    def test_benign_cohorts_are_kept_separate(self):
        """
        Pooling our hand-written controls with externally-authored ones is what
        made 4/8 look like a false-positive rate (§6n, Rules.md §7).
        """
        benign = [v for v in all_vectors() if not v.expected_malicious]
        cohorts = {v.cohort for v in benign}
        assert cohorts == {"taxonomy", "benign_external"}, (
            "expected both cohorts present and labelled; got " + str(cohorts))

    def test_the_external_benign_cohort_is_not_a_single_document(self):
        """The withdrawn run's FPR column rested on one vector x 3 repeats."""
        external = [v for v in all_vectors() if v.cohort == "benign_external"]
        assert len(external) >= 5, f"only {len(external)} external benign vectors"

    def test_vector_ids_are_unique(self):
        vids = [v.vid for v in all_vectors()]
        assert len(set(vids)) == len(vids)

    def test_external_benign_vectors_carry_provenance(self):
        for v in all_vectors():
            if v.cohort == "benign_external":
                assert "AgentDojo" in v.source


class TestCaseConstruction:
    def test_repeats_produce_distinct_case_ids(self):
        """A checkpoint keyed on case_id would otherwise collapse the repeats."""
        from evaluation.vectors import as_cases
        ids = [c.case_id for c in as_cases(repeats=3)]
        assert len(set(ids)) == len(ids)

    def test_server_name_reaches_the_case(self):
        from evaluation.vectors import as_cases
        by_family = {c.family: c for c in as_cases(repeats=1)}
        assert by_family["V7"].server_name == "weather-api"
        assert by_family["V1"].server_name == "email-api"
