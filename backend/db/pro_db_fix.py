"""
Production one-off: align FKs so user deletes cascade from PostgreSQL.

Fixes legacy databases where connection_requests, connections, or notifications
foreign keys to users(uid) were created without ON DELETE CASCADE. Safe to re-run:
skips constraints that already match.

Run on Render (or any host) from the backend root with env loaded, e.g.:

    cd backend && python db/pro_db_fix.py

Requires DATABASE_URL or the same POSTGRES_* vars as the app.
"""
from __future__ import annotations

import os
import re
import sys

_SAFE_IDENT = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# backend/ on sys.path
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from config.database import get_connection_params  # noqa: E402


def _connect():
    params = get_connection_params()
    try:
        import psycopg
    except ImportError:
        import psycopg2

        if "conninfo" in params:
            return psycopg2.connect(params["conninfo"], connect_timeout=30)
        return psycopg2.connect(**{k: v for k, v in params.items() if k != "conninfo"}, connect_timeout=30)

    if "conninfo" in params:
        return psycopg.connect(params["conninfo"], connect_timeout=30)
    return psycopg.connect(
        host=params["host"],
        port=params["port"],
        dbname=params["dbname"],
        user=params["user"],
        password=params["password"],
        connect_timeout=30,
    )


def _fk_name(cur, table: str, column: str) -> str | None:
    cur.execute(
        """
        SELECT tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_schema = kcu.constraint_schema
         AND tc.constraint_name = kcu.constraint_name
        WHERE tc.table_schema = 'public'
          AND tc.table_name = %s
          AND tc.constraint_type = 'FOREIGN KEY'
          AND kcu.column_name = %s
        LIMIT 1
        """,
        (table, column),
    )
    row = cur.fetchone()
    if not row:
        return None
    return row[0] if not isinstance(row, dict) else row["constraint_name"]


def _fk_def(cur, constraint_name: str) -> str | None:
    cur.execute(
        """
        SELECT pg_get_constraintdef(c.oid, true)
        FROM pg_constraint c
        JOIN pg_namespace n ON n.oid = c.connamespace
        WHERE c.conname = %s AND n.nspname = 'public'
        """,
        (constraint_name,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return row[0] if not isinstance(row, dict) else row["pg_get_constraintdef"]


def _recreate_fk_cascade(
    cur,
    table: str,
    column: str,
    ref_table: str,
    ref_column: str,
    new_constraint_name: str,
) -> str:
    name = _fk_name(cur, table, column)
    if not name:
        return f"  [skip] {table}.{column}: no FK found"

    definition = (_fk_def(cur, name) or "").upper()
    if "ON DELETE CASCADE" in definition:
        return f"  [ok] {table}.{column}: already ON DELETE CASCADE ({name})"

    if not _SAFE_IDENT.match(name) or not _SAFE_IDENT.match(new_constraint_name):
        raise ValueError(f"Unsafe constraint name from DB: {name!r} / {new_constraint_name!r}")

    cur.execute(
        f'ALTER TABLE "{table}" DROP CONSTRAINT "{name}"'  # noqa: S608
    )
    cur.execute(
        f"""
        ALTER TABLE "{table}"
        ADD CONSTRAINT "{new_constraint_name}"
        FOREIGN KEY ("{column}") REFERENCES "{ref_table}"("{ref_column}")
        ON DELETE CASCADE
        """
    )
    return f"  [fixed] {table}.{column}: recreated as CASCADE (was {name})"


def main() -> None:
    print("=" * 60)
    print("pro_db_fix: connection_requests / connections / notifications.user_id FK → CASCADE")
    print("=" * 60)

    conn = _connect()
    was_autocommit = getattr(conn, "autocommit", None)
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'users'
                """
            )
            if not cur.fetchone():
                raise RuntimeError("Table public.users not found; wrong database?")

            messages = [
                _recreate_fk_cascade(
                    cur,
                    "connection_requests",
                    "sender_id",
                    "users",
                    "uid",
                    "connection_requests_sender_id_fkey",
                ),
                _recreate_fk_cascade(
                    cur,
                    "connection_requests",
                    "receiver_id",
                    "users",
                    "uid",
                    "connection_requests_receiver_id_fkey",
                ),
                _recreate_fk_cascade(
                    cur,
                    "connections",
                    "follower_uid",
                    "users",
                    "uid",
                    "connections_follower_uid_fkey",
                ),
                _recreate_fk_cascade(
                    cur,
                    "connections",
                    "followed_uid",
                    "users",
                    "uid",
                    "connections_followed_uid_fkey",
                ),
                _recreate_fk_cascade(
                    cur,
                    "notifications",
                    "user_id",
                    "users",
                    "uid",
                    "notifications_user_id_fkey",
                ),
            ]

        conn.commit()
        for m in messages:
            print(m)
        print("=" * 60)
        print("Done.")
    except Exception:
        conn.rollback()
        print("ERROR: rolled back. See traceback.")
        raise
    finally:
        if was_autocommit is not None:
            conn.autocommit = was_autocommit
        conn.close()


if __name__ == "__main__":
    main()
