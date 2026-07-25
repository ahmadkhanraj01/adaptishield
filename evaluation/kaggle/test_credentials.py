"""
Tiny Kaggle credential check — does the token in repo-root .env actually work?

Loads KAGGLE_USERNAME / KAGGLE_KEY from .env (no secret is ever printed), then
makes ONE lightweight authenticated API call. Prints PASS/FAIL only.

  python -m evaluation.kaggle.test_credentials
"""

import os
import sys


def _load_dotenv(path):
    """Minimal .env loader (project is dependency-free — no python-dotenv)."""
    if not os.path.exists(path):
        return False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)
    return True


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    env_path = os.path.join(root, ".env")

    loaded = _load_dotenv(env_path)
    print(f"[test] .env {'loaded from ' + env_path if loaded else 'NOT FOUND at ' + env_path}")

    user = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    if not user or not key:
        print("[test] FAIL — KAGGLE_USERNAME / KAGGLE_KEY not set "
              "(check .env has both, no quotes needed).")
        sys.exit(1)
    # Show only the username and a masked key length — never the secret itself.
    print(f"[test] username={user!r}  key=<{len(key)} chars, hidden>")

    # Env vars must be set BEFORE importing kaggle (it authenticates on import).
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception as e:  # noqa: BLE001
        print(f"[test] FAIL — could not import kaggle CLI: {e}")
        sys.exit(1)

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as e:  # noqa: BLE001
        print(f"[test] FAIL — authenticate() error: {e}")
        sys.exit(1)

    # One cheap authenticated call. 401/403 => bad credentials.
    try:
        datasets = api.dataset_list(user=user, page=1)
        print(f"[test] PASS — authenticated as {user!r}. "
              f"API reachable (your dataset list returned {len(list(datasets))} item(s)).")
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        if "401" in msg or "403" in msg or "Unauthorized" in msg or "Forbidden" in msg:
            print(f"[test] FAIL — credentials rejected (auth error): {e}")
            print("[test] The installed CLI (1.7.4.5) needs a LEGACY username+key. "
                  "The new 'API Tokens' access token will NOT work here.")
        else:
            print(f"[test] FAIL — API call error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
