"""
One command: seed every realistic user (batch 1 + batch 2), full profiles, posts, and cross-batch connections.

From ZedReq/backend:
    python seed_data/seed_realistic_run_all.py

Options:
    --no-download   Skip mirroring images to seed_data/assets/
    --seed N        Reproducible randomness for posts/connections
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = SCRIPT_DIR.parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent.resolve()

sys.path.insert(0, str(BACKEND_DIR))

try:
    from dotenv import load_dotenv

    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")
    else:
        load_dotenv()
except ImportError:
    pass

from utils.auth import hash_password

from seed_data.seed_realistic_common import get_db_default, run_full_seed
from seed_data.seed_realistic_users import USER_POSTS, USERS as USERS_BATCH1
from seed_data.seed_realistic_users_2 import USER_POST_CANDIDATES, USERS as USERS_BATCH2, pick_posts_for_user


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed all realistic users (both batches) with full graph")
    parser.add_argument("--no-download", action="store_true", help="Do not save copies of images under seed_data/assets/")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for posts and connections")
    args = parser.parse_args()

    master_seed = args.seed if args.seed is not None else random.randrange(2**31)
    rng = random.Random(master_seed)

    users = USERS_BATCH1 + USERS_BATCH2
    posts = dict(USER_POSTS)
    for u in USERS_BATCH2:
        un = u["username"]
        posts[un] = pick_posts_for_user(un, rng)

    print("=" * 65)
    print("  ZedReq — full realistic seed (batch 1 + batch 2)")
    print("=" * 65)

    run_full_seed(
        users,
        posts,
        hash_password_fn=hash_password,
        get_db_fn=get_db_default,
        seed=master_seed,
        download_images=not args.no_download,
        augment_posts=True,
        post_builder=None,
    )


if __name__ == "__main__":
    main()
