"""
Migration: Add embedding column to post table (for personalized post feed)
- Add embedding column to post table (pgvector, 3072 dimensions)
- Create HNSW vector index on a halfvec(3072) cast for cosine search

Notes:
- OpenAI text-embedding-3-large produces 3072-dim vectors. IVFFlat/HNSW on the
  `vector` type cap at 2000 dims, so (matching job_postings) we index a
  halfvec(3072) cast with HNSW (requires pgvector 0.7+).
- Posts vectors share the same model/dimension as description.embedding so a
  user interest vector can be compared to posts with cosine directly.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
INSTALL_PGVECTOR_EXTENSION = '''
CREATE EXTENSION IF NOT EXISTS vector;
'''

ADD_POST_EMBEDDING_COLUMN = '''
ALTER TABLE post
ADD COLUMN IF NOT EXISTS embedding vector(3072);
'''

# IVFFlat/HNSW on `vector` type cap at 2000 dimensions; text-embedding-3-large uses 3072.
# Use HNSW on a halfvec cast (pgvector 0.7+) for index acceleration.
CREATE_POST_EMBEDDING_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_post_embeddings_hnsw
ON post
USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops);
'''


def run_migration():
    """Run the migration to add the post embedding column and index"""
    db = Database(get_connection_params())

    print("=" * 60)
    print("Running Migration: Add post embeddings")
    print("=" * 60)

    try:
        # Check if pgvector extension is available
        print("  [1/3] Checking for pgvector extension...")
        try:
            db.execute(INSTALL_PGVECTOR_EXTENSION)
            print("  [OK] pgvector extension installed/available")
            pgvector_available = True
        except Exception as e:
            print(f"  [WARNING] pgvector extension not available: {e}")
            print("  [INFO] Skipping embedding column. Install pgvector to enable the personalized feed.")
            print("  [INFO] To install pgvector:")
            print("         - On Windows: Download from https://github.com/pgvector/pgvector/releases")
            print("         - On Linux: sudo apt-get install postgresql-XX-pgvector")
            print("         - On macOS: brew install pgvector")
            print("         - Or use Docker image: pgvector/pgvector:pg16")
            pgvector_available = False

        # Add embedding column to post table (only if pgvector is available)
        if pgvector_available:
            print("  [2/3] Adding embedding column to post table...")
            try:
                db.execute(ADD_POST_EMBEDDING_COLUMN)
                print("  [OK] Post embedding column added")
            except Exception as e:
                print(f"  [WARNING] Failed to add embedding column: {e}")
                pgvector_available = False
        else:
            print("  [2/3] Skipping embedding column (pgvector not available)")

        # Create HNSW vector index for post embeddings
        if pgvector_available:
            print("  [3/3] Creating HNSW vector index for post embeddings...")
            try:
                db.execute(CREATE_POST_EMBEDDING_INDEX)
                print("  [OK] Post embedding vector index created")
            except Exception as e:
                print(f"  [WARNING] Vector index creation failed (may need pgvector 0.7+ / existing data): {e}")
                print("  [INFO] You can create the index later; cosine search works without it (seq scan).")
        else:
            print("  [3/3] Skipping vector index (pgvector not available)")

        print("=" * 60)
        print("Migration completed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Backfill embeddings for existing posts:")
        print("   python backend/scripts/backfill_post_embeddings.py")
        print("2. Enable the nightly backfill (POST_EMBEDDING_BACKFILL_ENABLED=true)")
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
