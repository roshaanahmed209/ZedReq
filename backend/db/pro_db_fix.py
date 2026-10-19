"""
Production one-off: ensure every FK to users(uid) is ON DELETE CASCADE.

Two categories are fixed:
  A. Tables with ORM backrefs to User (NOT NULL FK) — pre-deleted by the app
     before session.delete(user). These FKs still need CASCADE so that manual
     psql deletions and future schema additions stay consistent.
  B. Tables WITHOUT a backref (NOT NULL FK) — relied upon by DB CASCADE when
     session.delete(user) fires. These MUST have ON DELETE CASCADE or the
     user delete will fail with a FK violation.

This script is idempotent: constraints already set to CASCADE are reported as
[ok] and left untouched.  Constraints that are missing entirely are reported as
[skip] (table/column likely doesn't exist yet — run app startup migrations first).

Run from the backend root with the environment loaded:
    cd /opt/render/project/src/backend && python db/pro_db_fix.py

Requires DATABASE_URL or the same POSTGRES_* env vars as the app.
"""
from __future__ import annotations

import os
import re
import sys

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from config.database import get_connection_params  # noqa: E402

_SAFE_IDENT = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_$]*$")

# ── FK pairs to enforce as ON DELETE CASCADE ──────────────────────────────────
# (table, fk_column, ref_table, ref_column, desired_constraint_name)
#
# Group A: tables pre-deleted explicitly in user_deletion_service.py
_GROUP_A = [
    ("notifications",       "user_id",        "users", "uid", "notifications_user_id_fkey"),
    ("connection_requests", "sender_id",       "users", "uid", "connection_requests_sender_id_fkey"),
    ("connection_requests", "receiver_id",     "users", "uid", "connection_requests_receiver_id_fkey"),
    ("connections",         "follower_uid",    "users", "uid", "connections_follower_uid_fkey"),
    ("connections",         "followed_uid",    "users", "uid", "connections_followed_uid_fkey"),
    ("profile_analytics",   "user_id",         "users", "uid", "profile_analytics_user_id_fkey"),
    ("users_context",       "user_id",         "users", "uid", "users_context_user_id_fkey"),
    ("user_experience",     "user_id",         "users", "uid", "user_experience_user_id_fkey"),
    ("user_education",      "user_id",         "users", "uid", "user_education_user_id_fkey"),
    ("user_projects",       "user_id",         "users", "uid", "user_projects_user_id_fkey"),
    ("user_interests",      "user_id",         "users", "uid", "user_interests_user_id_fkey"),
    ("user_recommendations","user_id",         "users", "uid", "user_recommendations_user_id_fkey"),
    ("user_recommendations","recommender_id",  "users", "uid", "user_recommendations_recommender_id_fkey"),
    ("post_comment",        "uid",             "users", "uid", "post_comment_uid_fkey"),
    ("live_interviews",     "user_id",         "users", "uid", "live_interviews_user_id_fkey"),
    ("payment",             "uid",             "users", "uid", "payment_uid_fkey"),
]

# Group B: tables handled by DB CASCADE (no ORM backref on User)
_GROUP_B = [
    ("user_subscriptions",          "user_id",    "users", "uid", "user_subscriptions_user_id_fkey"),
    ("usage_tracking",              "user_id",    "users", "uid", "usage_tracking_user_id_fkey"),
    ("job_postings",                "poster_id",  "users", "uid", "job_postings_poster_id_fkey"),
    ("job_applications",            "applicant_id","users","uid", "job_applications_applicant_id_fkey"),
    ("job_saved",                   "user_id",    "users", "uid", "job_saved_user_id_fkey"),
    ("lms_user_courses",            "user_id",    "users", "uid", "lms_user_courses_user_id_fkey"),
    ("lms_user_section_progress",   "user_id",    "users", "uid", "lms_user_section_progress_user_id_fkey"),
    ("lms_user_answers",            "user_id",    "users", "uid", "lms_user_answers_user_id_fkey"),
    ("lms_user_domain_performance", "user_id",    "users", "uid", "lms_user_domain_performance_user_id_fkey"),
    ("lms_user_course_performance", "user_id",    "users", "uid", "lms_user_course_performance_user_id_fkey"),
    ("lms_dashboard",               "user_id",    "users", "uid", "lms_dashboard_user_id_fkey"),
    ("lms_weekly_performance",      "user_id",    "users", "uid", "lms_weekly_performance_user_id_fkey"),
    ("lms_activities",              "user_id",    "users", "uid", "lms_activities_user_id_fkey"),
    ("lms_recommendations",         "user_id",    "users", "uid", "lms_recommendations_user_id_fkey"),
    ("lms_deadlines",               "user_id",    "users", "uid", "lms_deadlines_user_id_fkey"),
    ("lms_certificates",            "user_id",    "users", "uid", "lms_certificates_user_id_fkey"),
    ("azel_search_urls",            "user_id",    "users", "uid", "azel_search_urls_user_id_fkey"),
    ("lms_rate_limits",             "user_id",    "users", "uid", "lms_rate_limits_user_id_fkey"),
]


# ── DB helpers ────────────────────────────────────────────────────────────────

def _connect():
    params = get_connection_params()
    try:
        import psycopg
        if "conninfo" in params:
            return psycopg.connect(params["conninfo"], connect_timeout=30)
        return psycopg.connect(
            host=params["host"], port=params["port"], dbname=params["dbname"],
            user=params["user"], password=params["password"], connect_timeout=30,
        )
    except ImportError:
        import psycopg2
        if "conninfo" in params:
            return psycopg2.connect(params["conninfo"], connect_timeout=30)
        return psycopg2.connect(
            **{k: v for k, v in params.items() if k != "conninfo"}, connect_timeout=30
        )


def _fetchone(cur, query: str, params: tuple):
    cur.execute(query, params)
    row = cur.fetchone()
    if row is None:
        return None
    return row if not isinstance(row, dict) else list(row.values())


def _current_fk_name(cur, table: str, column: str) -> str | None:
    row = _fetchone(
        cur,
        """
        SELECT tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_schema = kcu.constraint_schema
         AND tc.constraint_name   = kcu.constraint_name
        WHERE tc.table_schema  = 'public'
          AND tc.table_name    = %s
          AND tc.constraint_type = 'FOREIGN KEY'
          AND kcu.column_name  = %s
        LIMIT 1
        """,
        (table, column),
    )
    return row[0] if row else None


def _fk_def(cur, constraint_name: str) -> str | None:
    row = _fetchone(
        cur,
        """
        SELECT pg_get_constraintdef(c.oid, true)
        FROM pg_constraint c
        JOIN pg_namespace n ON n.oid = c.connamespace
        WHERE c.conname = %s AND n.nspname = 'public'
        """,
        (constraint_name,),
    )
    return row[0] if row else None


def _table_exists(cur, table: str) -> bool:
    row = _fetchone(
        cur,
        "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
        (table,),
    )
    return row is not None


def _ensure_cascade(cur, table: str, column: str, ref_table: str, ref_column: str, new_name: str) -> str:
    if not _table_exists(cur, table):
        return f"  [skip] {table}.{column}: table not found"

    name = _current_fk_name(cur, table, column)
    if not name:
        # Constraint missing entirely — add it
        if not _SAFE_IDENT.match(new_name):
            raise ValueError(f"Unsafe constraint name: {new_name!r}")
        cur.execute(
            f'ALTER TABLE "{table}" ADD CONSTRAINT "{new_name}" '
            f'FOREIGN KEY ("{column}") REFERENCES "{ref_table}"("{ref_column}") ON DELETE CASCADE'
        )
        return f"  [added] {table}.{column}: new CASCADE constraint ({new_name})"

    defn = (_fk_def(cur, name) or "").upper()
    if "ON DELETE CASCADE" in defn:
        return f"  [ok]    {table}.{column}: already ON DELETE CASCADE ({name})"

    if not _SAFE_IDENT.match(name) or not _SAFE_IDENT.match(new_name):
        raise ValueError(f"Unsafe constraint name from DB: {name!r}")

    cur.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT "{name}"')
    cur.execute(
        f'ALTER TABLE "{table}" ADD CONSTRAINT "{new_name}" '
        f'FOREIGN KEY ("{column}") REFERENCES "{ref_table}"("{ref_column}") ON DELETE CASCADE'
    )
    return f"  [fixed] {table}.{column}: replaced {name} → {new_name} with CASCADE"


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("pro_db_fix: enforce ON DELETE CASCADE on all user-owned FK columns")
    print("=" * 70)

    conn = _connect()
    orig_autocommit = getattr(conn, "autocommit", None)
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name='users'"
            )
            if not cur.fetchone():
                raise RuntimeError("Table public.users not found — wrong database?")

            results: list[str] = []

            print("\n-- Group A: tables with ORM backref (pre-deleted by app) --")
            for args in _GROUP_A:
                msg = _ensure_cascade(cur, *args)
                results.append(msg)
                print(msg)

            print("\n-- Group B: tables without backref (rely on DB CASCADE) --")
            for args in _GROUP_B:
                msg = _ensure_cascade(cur, *args)
                results.append(msg)
                print(msg)

        conn.commit()
        fixed = sum(1 for r in results if "[fixed]" in r or "[added]" in r)
        print(f"\n{'=' * 70}")
        print(f"Done. {fixed} constraint(s) updated, {len(results) - fixed} already correct or skipped.")
    except Exception:
        conn.rollback()
        print("\nERROR: transaction rolled back. See traceback above.")
        raise
    finally:
        if orig_autocommit is not None:
            conn.autocommit = orig_autocommit
        conn.close()


if __name__ == "__main__":
    main()
