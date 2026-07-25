"""
GRPO trainer for Component 3D — the Kaggle P100 kernel (Phase 6 step 2).

Replaces the *internals* of `AdaptiveThreatModel.propose_update()` (the v1
directional heuristic) with a real policy-gradient loop, while keeping the exact
same reward and the same `LabeledEpisode → ProposedUpdate → apply_update`
contract. It reads the JSONL the packager produced, learns a distribution over
the `ie_threshold` grid by GRPO, and writes a `proposed_update.json` in the
`ProposedUpdate` schema for `apply_and_validate.py` to apply locally.

Why GRPO here is honest, not theatre
────────────────────────────────────
The action space is the one knob the whole Phase 5b story is about: which IE
grid value to set `ie_threshold` to. Each step samples a *group* of candidate
thresholds from the current policy, scores each on the full batch with the exact
project reward (grpo_env.evaluate_policy), and uses the group mean as the
baseline — advantage = reward − group_mean. That group-relative advantage is
GRPO's defining move (no learned critic); the update is REINFORCE on the policy
logits. If the data has no threshold gap (Phase 5's natural-set finding), every
candidate scores alike, advantages vanish, and the policy stays put → a no-op
proposal, which `apply_update` refuses. That "GRPO adds nothing when there's
nothing to learn" outcome is itself a valid Phase 6 result.

Runs on a P100 if `torch.cuda` is available, else CPU (the categorical policy is
tiny — GPU is not required for correctness, only for parity with the eventual
larger policies). No Ollama/pipeline here: the reward is replayed from the
recorded diagnostics, which is exact for campaign episodes (see grpo_env.py).
"""

import argparse
import glob
import json
import os
import sys
from statistics import mode
from typing import List, Optional

# grpo_env sits beside this file locally and inside the attached Kaggle Dataset.
try:
    from grpo_env import (RewardConfig, Policy, EpisodeFeatures,
                          load_episodes, evaluate_policy, ie_grid,
                          status_under_policy)
except ImportError:  # running as a module, or on Kaggle with a nested input dir
    _here = os.path.dirname(os.path.abspath(__file__))
    for cand in [_here, *glob.glob("/kaggle/input/*"), *glob.glob("/kaggle/input/*/*")]:
        if os.path.exists(os.path.join(cand, "grpo_env.py")):
            sys.path.insert(0, cand)
            break
    from grpo_env import (RewardConfig, Policy, EpisodeFeatures,   # noqa: E402
                          load_episodes, evaluate_policy, ie_grid,
                          status_under_policy)


def _find_episodes() -> Optional[str]:
    for cand in ["episodes.jsonl",
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "episodes.jsonl"),
                 *glob.glob("/kaggle/input/*/episodes.jsonl"),
                 *glob.glob("/kaggle/input/*/*/episodes.jsonl")]:
        if os.path.exists(cand):
            return cand
    return None


def _default_out() -> str:
    return "/kaggle/working/proposed_update.json" if os.path.isdir("/kaggle/working") \
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), "proposed_update.json")


# ── generalizable pattern / tool extraction (mirrors fix A) ──────────
def _looks_like_literal_target(marker: str) -> bool:
    """Reject anything that pins a concrete destination — fix A (no memorizing)."""
    m = marker.lower()
    return "@" in m or "http://" in m or "https://" in m or m.startswith("www.")


def _candidate_patterns(missed: List[EpisodeFeatures]) -> List[str]:
    pats = set()
    for ep in missed:
        for marker in ep.flagged_markers:
            marker = marker.lower().strip()
            if marker and not _looks_like_literal_target(marker):
                pats.add(marker)
    return sorted(pats)


def _candidate_tools(missed: List[EpisodeFeatures]) -> List[str]:
    return sorted({ep.tool_name for ep in missed})


def _missed_under(episodes, policy) -> List[EpisodeFeatures]:
    out = []
    for ep in episodes:
        if ep.is_malicious and status_under_policy(ep, policy) not in ("blocked", "safe_continuation"):
            out.append(ep)
    return out


# ── GRPO ──────────────────────────────────────────────────────────────
# Two backends implementing the IDENTICAL algorithm — sample a group of
# thresholds from the current categorical policy, use the group mean as the
# baseline (advantage = reward − group_mean), and take a policy-gradient step on
# the logits. torch is used on Kaggle (GPU parity / room for larger policies);
# the pure-Python backend lets the exact same loop run on the 4 GB dev box,
# which has neither torch nor numpy. Both maximize expected reward.

def _base_rewards(episodes, grid, rc, min_intervention_eps, current):
    # Each grid threshold's mean batch reward (env is deterministic in the
    # threshold), minus a tiny minimal-intervention penalty proportional to the
    # distance from the CURRENT threshold. This breaks reward-ties toward the
    # smallest move: no gap → argmax stays at `current` → a no-op proposal
    # (which apply_update refuses), matching the v1 heuristic's "unchanged when
    # missed == false_pos". When a gap exists the reward difference dwarfs eps,
    # so it still moves — and among equally-good thresholds picks the one
    # closest to current (e.g. 1.5 → 1.0, not 1.5 → 0.0).
    return [evaluate_policy(episodes, Policy(ie_threshold=t), rc)["mean_reward"]
            - min_intervention_eps * abs(t - current) for t in grid]


def train_torch(episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed, current):
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(seed)
    reward_t = torch.tensor(_base_rewards(episodes, grid, rc, min_intervention_eps, current),
                            dtype=torch.float32, device=device)
    logits = torch.zeros(len(grid), requires_grad=True, device=device)
    opt = torch.optim.Adam([logits], lr=lr)
    for _ in range(steps):
        dist = torch.distributions.Categorical(logits=logits)
        idx = dist.sample((group_size,))                   # a GRPO group
        advantages = reward_t[idx] - reward_t[idx].mean()  # group-relative baseline
        loss = -(advantages.detach() * dist.log_prob(idx)).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        probs = torch.softmax(logits, dim=0).cpu().tolist()
    return probs, _base_rewards(episodes, grid, rc, min_intervention_eps, current), device


def train_pure(episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed, current):
    import math, random
    random.seed(seed)
    base = _base_rewards(episodes, grid, rc, min_intervention_eps, current)
    n = len(grid)
    logits = [0.0] * n
    for _ in range(steps):
        m = max(logits)
        exps = [math.exp(l - m) for l in logits]
        Z = sum(exps)
        probs = [e / Z for e in exps]
        idxs = random.choices(range(n), weights=probs, k=group_size)  # GRPO group
        rewards = [base[i] for i in idxs]
        mean_r = sum(rewards) / len(rewards)                 # group-relative baseline
        grad = [0.0] * n
        for i, r in zip(idxs, rewards):
            adv = r - mean_r
            for j in range(n):                               # ∇ log π: [i==j] − p_j
                grad[j] += adv * ((1.0 if i == j else 0.0) - probs[j])
        logits = [l + lr * (g / group_size) for l, g in zip(logits, grad)]  # ascent
    m = max(logits)
    exps = [math.exp(l - m) for l in logits]
    Z = sum(exps)
    probs = [e / Z for e in exps]
    return probs, base, "cpu(pure-python)"


def train(episodes: List[EpisodeFeatures], grid: List[float],
          current_ie_threshold: float, rc: RewardConfig,
          group_size: int = 8, steps: int = 300, lr: float = 0.1,
          min_intervention_eps: float = 1e-3, seed: int = 0,
          backend: str = "auto"):
    if backend == "torch" or (backend == "auto" and _torch_available()):
        probs, base_rewards, device = train_torch(
            episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed,
            current_ie_threshold)
    else:
        probs, base_rewards, device = train_pure(
            episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed,
            current_ie_threshold)
    chosen = grid[int(max(range(len(grid)), key=lambda i: probs[i]))]
    return chosen, probs, base_rewards, device


def _torch_available() -> bool:
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


def build_proposal(episodes, chosen_threshold, current_ie_threshold,
                   probs, grid, rc, device) -> dict:
    """Assemble a ProposedUpdate-schema dict from the learned threshold."""
    final_policy = Policy(ie_threshold=chosen_threshold)
    missed_after = _missed_under(episodes, final_policy)
    patterns = _candidate_patterns(missed_after)
    tools = _candidate_tools(missed_after)
    stats = evaluate_policy(episodes, final_policy, rc)

    rationale = [
        f"GRPO over IE grid {grid} on {len(episodes)} labeled episode(s) "
        f"[device={device}]",
        f"learned distribution: " +
        ", ".join(f"{g:.1f}:{p:.2f}" for g, p in zip(grid, probs)),
        f"chosen ie_threshold {current_ie_threshold:.2f} -> {chosen_threshold:.2f} "
        f"(argmax of the policy)",
        f"post-update batch: mean_reward={stats['mean_reward']:+.3f} "
        f"missed={stats['missed']} false_pos={stats['false_pos']} "
        f"workflow_lost={stats['workflow_lost']}",
    ]
    if patterns:
        rationale.append(f"generalizable blocked_patterns from still-missed attacks: {patterns}")
    if tools:
        rationale.append(f"tools in still-missed attacks, nominate high-impact: {tools}")

    return {
        "old_ie_threshold": current_ie_threshold,
        "new_ie_threshold": chosen_threshold,
        "new_blocked_patterns": patterns,
        "new_high_impact_tools": tools,
        "rationale": rationale,
        "mean_reward": stats["mean_reward"],
        # provenance (ignored by apply_update; recorded for the report)
        "_meta": {
            "trainer": "grpo",
            "grid": grid,
            "learned_probs": probs,
            "device": device,
            "n_episodes": len(episodes),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="GRPO trainer for Component 3D (Kaggle P100)")
    ap.add_argument("--episodes", default=None, help="path to packaged episodes.jsonl")
    ap.add_argument("--out", default=None, help="output proposed_update.json path")
    ap.add_argument("--current-ie-threshold", type=float, default=None,
                    help="threshold to move from (default: mode of capture_ie_threshold)")
    ap.add_argument("--ie-resolution", type=float, default=0.5)
    ap.add_argument("--group-size", type=int, default=8)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--lr", type=float, default=0.1)
    ap.add_argument("--min-intervention-eps", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--backend", choices=["auto", "torch", "pure"], default="auto",
                    help="auto uses torch when importable (Kaggle), else pure-python")
    args = ap.parse_args()

    episodes_path = args.episodes or _find_episodes()
    if not episodes_path:
        sys.exit("[grpo] no episodes.jsonl found — run package_episodes.py first, "
                 "or pass --episodes.")
    out_path = args.out or _default_out()

    episodes = load_episodes(episodes_path)
    if not episodes:
        sys.exit(f"[grpo] {episodes_path} is empty.")

    # Default the starting threshold to what the data was captured at.
    if args.current_ie_threshold is not None:
        current = args.current_ie_threshold
    else:
        caps = [ep.causal["capture_ie_threshold"] for ep in episodes
                if ep.causal and ep.causal.get("capture_ie_threshold") is not None]
        current = mode(caps) if caps else 0.5

    grid = ie_grid(args.ie_resolution)
    rc = RewardConfig()

    backend = args.backend
    if backend == "torch" and not _torch_available():
        sys.exit("[grpo] --backend torch requested but torch is not importable.")
    resolved = "torch" if (backend == "torch" or (backend == "auto" and _torch_available())) \
        else "pure-python"

    print(f"[grpo] episodes={len(episodes)} from {episodes_path}")
    print(f"[grpo] IE grid={grid}  current ie_threshold={current}  backend={resolved}")

    chosen, probs, base_rewards, device = train(
        episodes, grid, current, rc,
        group_size=args.group_size, steps=args.steps, lr=args.lr,
        min_intervention_eps=args.min_intervention_eps, seed=args.seed,
        backend=backend)

    print(f"[grpo] per-threshold mean reward (+ intervention bonus):")
    for g, r in zip(grid, base_rewards):
        print(f"        ie_threshold={g:.1f}  reward={r:+.4f}")
    print(f"[grpo] learned argmax ie_threshold = {chosen}  (was {current})")

    proposal = build_proposal(episodes, chosen, current, probs, grid, rc, device)
    with open(out_path, "w") as f:
        json.dump(proposal, f, indent=2)
    print(f"[grpo] wrote {out_path}")
    for line in proposal["rationale"]:
        print(f"        - {line}")


if __name__ == "__main__":
    main()
