"""
Migration: Convert embedding columns from text to vector(3072) for pgvector indexes.

Run on production if vector search fails with:
  operator does not exist: text <=> vector

Requires: CREATE EXTENSION IF NOT EXISTS vector;
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

INSTALL_PGVECTOR = "CREATE EXTENSION IF NOT EXISTS vector;"

ALTER_JOB_EMBEDDINGS = """
ALTER TABLE job_postings
ALTER COLUMN embedding TYPE vector(3072)
USING (
    CASE
        WHEN embedding IS NULL THEN NULL
        WHEN trim(embedding::text) = '' THEN NULL
        ELSE embedding::vector
    END
);
"""

ALTER_DESCRIPTION_EMBEDDINGS = """
ALTER TABLE description
ALTER COLUMN embedding TYPE vector(3072)
USING (
    CASE
        WHEN embedding IS NULL THEN NULL
        WHEN trim(embedding::text) = '' THEN NULL
        ELSE embedding::vector
    END
);
"""

RECREATE_JOB_INDEX = """
CREATE INDEX IF NOT EXISTS idx_job_embeddings
ON job_postings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
"""


def _column_type(db: Database, table: str, column: str) -> str | None:
    row = db.fetch_one(
        """
        SELECT data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND column_name = %s
        """,
        (table, column),
    )
    if not row:
        return None
    return row.get("udt_name") or row.get("data_type")


def run_migration():
    db = Database(get_connection_params())
    print("=" * 60)
    print("Fix embedding column types (text -> vector)")
    print("=" * 60)

    try:
        db.execute(INSTALL_PGVECTOR)
        print("[OK] pgvector extension")

        job_type = _column_type(db, "job_postings", "embedding")
        print(f"  job_postings.embedding udt: {job_type}")
        if job_type and job_type != "vector":
            db.execute(ALTER_JOB_EMBEDDINGS)
            print("[OK] job_postings.embedding -> vector(3072)")
            try:
                db.execute(RECREATE_JOB_INDEX)
                print("[OK] idx_job_embeddings")
            except Exception as e:
                print(f"[WARN] index (re-run after more rows): {e}")
        else:
            print("[SKIP] job_postings.embedding already vector")

        desc_type = _column_type(db, "description", "embedding")
        print(f"  description.embedding udt: {desc_type}")
        if desc_type and desc_type != "vector":
            db.execute(ALTER_DESCRIPTION_EMBEDDINGS)
            print("[OK] description.embedding -> vector(3072)")
        else:
            print("[SKIP] description.embedding already vector")

        print("=" * 60)
        print("Done.")
    except Exception as e:
        print(f"[ERROR] {e}")
        raise


if __name__ == "__main__":
    run_migration()
