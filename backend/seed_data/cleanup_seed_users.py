"""
Remove only database rows created by the realistic seed scripts (users with email *@zedreq.dev).

Does not touch other accounts (e.g. @example.com from seed_data.py, admin test users, real users).

From ZedReq/backend:
    python seed_data/cleanup_seed_users.py --dry-run    # show counts only
    python seed_data/cleanup_seed_users.py --yes        # delete without typing confirmation
"""

from __future__ import annotations

import argparse
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
    else:
        load_dotenv()
except ImportError:
    pass

# Must match seed_realistic_users.py + seed_realistic_users_2.py
SEED_EMAIL_PATTERN = "%@zedreq.dev"


def get_db():
    from config.database import Database, get_connection_params

    return Database(get_connection_params())


def _table_exists(db, table: str) -> bool:
    r = db.fetch_one(
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (table,),
    )
    return r is not None


def fetch_seed_uids(db) -> tuple[list[int], list[int]]:
    rows = db.fetch_all(
        """
        SELECT uid, description_id FROM users
        WHERE user_email ILIKE %s
        ORDER BY uid
        """,
        (SEED_EMAIL_PATTERN,),
    )
    uids = [int(r["uid"]) for r in rows]
    desc_ids = [int(r["description_id"]) for r in rows if r.get("description_id") is not None]
    return uids, desc_ids


def _any_bind(ids: list[int]) -> list[int]:
    """For WHERE col = ANY(%s): pass a list — psycopg2 sends a PG array; a tuple is sent as ROW and breaks ANY."""
    return list(ids)


def _count(db, sql: str, params: tuple) -> int:
    r = db.fetch_one(sql, params)
    if not r or r.get("c") is None:
        return 0
    return int(r["c"])


def dry_run_summary(db, uids: list[int]) -> None:
    if not uids:
        print("No users match *@zedreq.dev — nothing to clean.")
        return
    arr = _any_bind(uids)
    print(f"Found {len(uids)} user(s) with email matching *@zedreq.dev: uids {uids}\nRelated row counts:")
    pairs: list[tuple[str, str, tuple]] = [
        ("post", "SELECT COUNT(*) AS c FROM post WHERE uid = ANY(%s)", (arr,)),
        (
            "likes",
            """SELECT COUNT(*) AS c FROM likes
               WHERE uid = ANY(%s)
                  OR post_id IN (SELECT post_id FROM post WHERE uid = ANY(%s))""",
            (arr, arr),
        ),
        (
            "connections",
            """SELECT COUNT(*) AS c FROM connections
               WHERE follower_uid = ANY(%s) OR followed_uid = ANY(%s)""",
            (arr, arr),
        ),
        ("network", "SELECT COUNT(*) AS c FROM network WHERE uid = ANY(%s)", (arr,)),
        (
            "notifications",
            """SELECT COUNT(*) AS c FROM notifications
               WHERE user_id = ANY(%s) OR related_user_id = ANY(%s)""",
            (arr, arr),
        ),
        (
            "connection_requests",
            """SELECT COUNT(*) AS c FROM connection_requests
               WHERE sender_id = ANY(%s) OR receiver_id = ANY(%s)""",
            (arr, arr),
        ),
        ("payment", "SELECT COUNT(*) AS c FROM payment WHERE uid = ANY(%s)", (arr,)),
        ("user_subscriptions", "SELECT COUNT(*) AS c FROM user_subscriptions WHERE user_id = ANY(%s)", (arr,)),
        ("usage_tracking", "SELECT COUNT(*) AS c FROM usage_tracking WHERE user_id = ANY(%s)", (arr,)),
        ("lms_dashboard", "SELECT COUNT(*) AS c FROM lms_dashboard WHERE user_id = ANY(%s)", (arr,)),
        ("lms_user_courses", "SELECT COUNT(*) AS c FROM lms_user_courses WHERE user_id = ANY(%s)", (arr,)),
        ("lms_activities", "SELECT COUNT(*) AS c FROM lms_activities WHERE user_id = ANY(%s)", (arr,)),
        ("lms_deadlines", "SELECT COUNT(*) AS c FROM lms_deadlines WHERE user_id = ANY(%s)", (arr,)),
        ("lms_certificates", "SELECT COUNT(*) AS c FROM lms_certificates WHERE user_id = ANY(%s)", (arr,)),
        ("lms_recommendations", "SELECT COUNT(*) AS c FROM lms_recommendations WHERE user_id = ANY(%s)", (arr,)),
        ("lms_user_domain_performance", "SELECT COUNT(*) AS c FROM lms_user_domain_performance WHERE user_id = ANY(%s)", (arr,)),
        ("lms_weekly_performance", "SELECT COUNT(*) AS c FROM lms_weekly_performance WHERE user_id = ANY(%s)", (arr,)),
        ("lms_user_course_performance", "SELECT COUNT(*) AS c FROM lms_user_course_performance WHERE user_id = ANY(%s)", (arr,)),
        ("lms_user_section_progress", "SELECT COUNT(*) AS c FROM lms_user_section_progress WHERE user_id = ANY(%s)", (arr,)),
        ("lms_user_answers", "SELECT COUNT(*) AS c FROM lms_user_answers WHERE user_id = ANY(%s)", (arr,)),
        ("azel_search_urls", "SELECT COUNT(*) AS c FROM azel_search_urls WHERE user_id = ANY(%s)", (arr,)),
        ("user_experience", "SELECT COUNT(*) AS c FROM user_experience WHERE user_id = ANY(%s)", (arr,)),
        ("user_education", "SELECT COUNT(*) AS c FROM user_education WHERE user_id = ANY(%s)", (arr,)),
        ("user_projects", "SELECT COUNT(*) AS c FROM user_projects WHERE user_id = ANY(%s)", (arr,)),
        (
            "user_recommendations",
            """SELECT COUNT(*) AS c FROM user_recommendations
               WHERE user_id = ANY(%s) OR recommender_id = ANY(%s)""",
            (arr, arr),
        ),
        ("user_interests", "SELECT COUNT(*) AS c FROM user_interests WHERE user_id = ANY(%s)", (arr,)),
        (
            "profile_analytics",
            """SELECT COUNT(*) AS c FROM profile_analytics
               WHERE user_id = ANY(%s) OR viewer_id = ANY(%s)""",
            (arr, arr),
        ),
        ("job_postings", "SELECT COUNT(*) AS c FROM job_postings WHERE poster_id = ANY(%s)", (arr,)),
        ("job_applications (as applicant)", "SELECT COUNT(*) AS c FROM job_applications WHERE applicant_id = ANY(%s)", (arr,)),
        ("job_saved (as saver)", "SELECT COUNT(*) AS c FROM job_saved WHERE user_id = ANY(%s)", (arr,)),
        ("live_interviews (as candidate)", "SELECT COUNT(*) AS c FROM live_interviews WHERE user_id = ANY(%s)", (arr,)),
        ("user_job_preferences", "SELECT COUNT(*) AS c FROM user_job_preferences WHERE user_id = ANY(%s)", (arr,)),
        ("user_job_recommendations_cache", "SELECT COUNT(*) AS c FROM user_job_recommendations_cache WHERE user_id = ANY(%s)", (arr,)),
        ("azel_jobs", "SELECT COUNT(*) AS c FROM azel_jobs WHERE user_id = ANY(%s)", (arr,)),
        ("job (legacy)", "SELECT COUNT(*) AS c FROM job WHERE uid = ANY(%s)", (arr,)),
        ("enterprise_inquiries", "SELECT COUNT(*) AS c FROM enterprise_inquiries WHERE user_id = ANY(%s)", (arr,)),
        ("reserved_seats (linked)", "SELECT COUNT(*) AS c FROM reserved_seats WHERE user_id = ANY(%s)", (arr,)),
    ]
    for label, sql, params in pairs:
        table = label.split()[0]
        if not _table_exists(db, table):
            continue
        c = _count(db, sql, params)
        if c:
            print(f"  {label}: {c}")

    if _table_exists(db, "job_applications") and _table_exists(db, "job_postings"):
        r = db.fetch_one(
            """SELECT COUNT(*) AS c FROM job_applications ja
               WHERE ja.job_id IN (SELECT job_id FROM job_postings WHERE poster_id = ANY(%s))""",
            (arr,),
        )
        c = int(r["c"]) if r and r.get("c") else 0
        if c:
            print(f"  job_applications (on seed users' job postings): {c}")
    if _table_exists(db, "live_interviews") and _table_exists(db, "job_postings"):
        r = db.fetch_one(
            """SELECT COUNT(*) AS c FROM live_interviews li
               WHERE li.job_id IN (SELECT job_id FROM job_postings WHERE poster_id = ANY(%s))""",
            (arr,),
        )
        c = int(r["c"]) if r and r.get("c") else 0
        if c:
            print(f"  live_interviews (on seed users' job postings): {c}")
    if _table_exists(db, "job_saved") and _table_exists(db, "job_postings"):
        r = db.fetch_one(
            """SELECT COUNT(*) AS c FROM job_saved js
               WHERE js.job_id IN (SELECT job_id FROM job_postings WHERE poster_id = ANY(%s))""",
            (arr,),
        )
        c = int(r["c"]) if r and r.get("c") else 0
        if c:
            print(f"  job_saved (on seed users' job postings): {c}")


def delete_seed_users(db, uids: list[int], desc_ids: list[int]) -> None:
    if not uids:
        print("Nothing to delete.")
        return

    uid_arr = _any_bind(uids)

    def run(sql: str, params=None):
        if params is None:
            params = (uid_arr,)
        db.execute(sql, params)

    # Notifications before connection_requests (FK related_request_id)
    if _table_exists(db, "notifications"):
        run(
            """DELETE FROM notifications
               WHERE user_id = ANY(%s) OR related_user_id = ANY(%s)""",
            (uid_arr, uid_arr),
        )
    if _table_exists(db, "connection_requests"):
        run(
            """DELETE FROM connection_requests
               WHERE sender_id = ANY(%s) OR receiver_id = ANY(%s)""",
            (uid_arr, uid_arr),
        )

    # Job portal: children of postings by seed posters first
    if _table_exists(db, "job_postings"):
        if _table_exists(db, "live_interviews"):
            db.execute(
                """DELETE FROM live_interviews
                   WHERE job_id IN (SELECT job_id FROM job_postings WHERE poster_id = ANY(%s))""",
                (uid_arr,),
            )
        if _table_exists(db, "job_applications"):
            db.execute(
                """DELETE FROM job_applications
                   WHERE job_id IN (SELECT job_id FROM job_postings WHERE poster_id = ANY(%s))""",
                (uid_arr,),
            )
        if _table_exists(db, "job_saved"):
            db.execute(
                """DELETE FROM job_saved
                   WHERE job_id IN (SELECT job_id FROM job_postings WHERE poster_id = ANY(%s))""",
                (uid_arr,),
            )
        run("DELETE FROM job_postings WHERE poster_id = ANY(%s)")

    if _table_exists(db, "live_interviews"):
        run("DELETE FROM live_interviews WHERE user_id = ANY(%s)")
    if _table_exists(db, "job_applications"):
        run("DELETE FROM job_applications WHERE applicant_id = ANY(%s)")
    if _table_exists(db, "job_saved"):
        run("DELETE FROM job_saved WHERE user_id = ANY(%s)")

    if _table_exists(db, "likes"):
        db.execute(
            """DELETE FROM likes
               WHERE uid = ANY(%s)
                  OR post_id IN (SELECT post_id FROM post WHERE uid = ANY(%s))""",
            (uid_arr, uid_arr),
        )
    if _table_exists(db, "post"):
        run("DELETE FROM post WHERE uid = ANY(%s)")

    if _table_exists(db, "connections"):
        run(
            """DELETE FROM connections
               WHERE follower_uid = ANY(%s) OR followed_uid = ANY(%s)""",
            (uid_arr, uid_arr),
        )
    if _table_exists(db, "network"):
        run("DELETE FROM network WHERE uid = ANY(%s)")

    for table, clause in [
        ("payment", "uid = ANY(%s)"),
        ("user_subscriptions", "user_id = ANY(%s)"),
        ("usage_tracking", "user_id = ANY(%s)"),
        ("lms_dashboard", "user_id = ANY(%s)"),
        ("lms_user_courses", "user_id = ANY(%s)"),
        ("lms_activities", "user_id = ANY(%s)"),
        ("lms_deadlines", "user_id = ANY(%s)"),
        ("lms_certificates", "user_id = ANY(%s)"),
        ("lms_recommendations", "user_id = ANY(%s)"),
        ("lms_user_domain_performance", "user_id = ANY(%s)"),
        ("lms_weekly_performance", "user_id = ANY(%s)"),
        ("lms_user_course_performance", "user_id = ANY(%s)"),
        ("lms_user_section_progress", "user_id = ANY(%s)"),
        ("lms_user_answers", "user_id = ANY(%s)"),
        ("azel_search_urls", "user_id = ANY(%s)"),
        ("user_experience", "user_id = ANY(%s)"),
        ("user_education", "user_id = ANY(%s)"),
        ("user_projects", "user_id = ANY(%s)"),
        ("user_interests", "user_id = ANY(%s)"),
        ("user_job_preferences", "user_id = ANY(%s)"),
        ("user_job_recommendations_cache", "user_id = ANY(%s)"),
        ("azel_jobs", "user_id = ANY(%s)"),
        ("enterprise_inquiries", "user_id = ANY(%s)"),
        ("job", "uid = ANY(%s)"),
    ]:
        if _table_exists(db, table):
            run(f"DELETE FROM {table} WHERE {clause}")

    if _table_exists(db, "user_recommendations"):
        run(
            """DELETE FROM user_recommendations
               WHERE user_id = ANY(%s) OR recommender_id = ANY(%s)""",
            (uid_arr, uid_arr),
        )
    if _table_exists(db, "profile_analytics"):
        run(
            """DELETE FROM profile_analytics
               WHERE user_id = ANY(%s) OR viewer_id = ANY(%s)""",
            (uid_arr, uid_arr),
        )

    if _table_exists(db, "reserved_seats"):
        db.execute("UPDATE reserved_seats SET user_id = NULL WHERE user_id = ANY(%s)", (uid_arr,))

    run("DELETE FROM users WHERE uid = ANY(%s)")

    if desc_ids and _table_exists(db, "description"):
        db.execute(
            "DELETE FROM description WHERE desc_id = ANY(%s)",
            (_any_bind(desc_ids),),
        )

    print(f"Deleted {len(uids)} user(s) and {len(desc_ids)} profile row(s) (description).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete realistic seed users (*@zedreq.dev) and their data only")
    parser.add_argument("--dry-run", action="store_true", help="List target users and row counts; do not delete")
    parser.add_argument("--yes", "-y", action="store_true", help="Delete without typing confirmation")
    args = parser.parse_args()

    db = get_db()
    try:
        uids, desc_ids = fetch_seed_uids(db)
        if args.dry_run:
            print("Dry run — no changes.\n")
            rows = db.fetch_all(
                "SELECT uid, username, user_email FROM users WHERE user_email ILIKE %s ORDER BY uid",
                (SEED_EMAIL_PATTERN,),
            )
            for r in rows:
                print(f"  uid={r['uid']}  @{r.get('username')}  {r.get('user_email')}")
            print()
            dry_run_summary(db, uids)
            return

        if not uids:
            print("No *@zedreq.dev users found.")
            return

        if not args.yes:
            print(f"This will permanently delete {len(uids)} user(s) and related rows:")
            for uid in uids:
                print(f"  uid {uid}")
            confirm = input("Type DELETE SEED USERS to confirm: ")
            if confirm.strip() != "DELETE SEED USERS":
                print("Aborted.")
                return

        delete_seed_users(db, uids, desc_ids)
    finally:
        db.close()


if __name__ == "__main__":
    main()
