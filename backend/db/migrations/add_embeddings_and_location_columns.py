"""
Migration: Add user embeddings and location columns for recommendations
- Add embedding column to description table (for user profile embeddings)
- Add city and country columns to description table
- Add city and country columns to job_postings table
- Create vector index for user embeddings
- Create indexes for city and country columns
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

ADD_USER_EMBEDDING_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS embedding vector(3072);
'''

ADD_USER_CITY_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS city VARCHAR(150);
'''

ADD_USER_COUNTRY_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS country VARCHAR(150);
'''

ADD_JOB_CITY_COLUMN = '''
ALTER TABLE job_postings 
ADD COLUMN IF NOT EXISTS city VARCHAR(150);
'''

ADD_JOB_COUNTRY_COLUMN = '''
ALTER TABLE job_postings 
ADD COLUMN IF NOT EXISTS country VARCHAR(150);
'''

CREATE_USER_EMBEDDING_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_description_embeddings 
ON description 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
'''

CREATE_LOCATION_INDEXES = '''
CREATE INDEX IF NOT EXISTS idx_description_city 
ON description(city) 
WHERE city IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_description_country 
ON description(country) 
WHERE country IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_job_postings_city 
ON job_postings(city) 
WHERE city IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_job_postings_country 
ON job_postings(country) 
WHERE country IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_job_postings_city_country 
ON job_postings(city, country) 
WHERE city IS NOT NULL AND country IS NOT NULL;
'''

def run_migration():
    """Run the migration to add embeddings and location columns"""
    db = Database(get_connection_params())
    
    print("=" * 60)
    print("Running Migration: Add embeddings and location columns")
    print("=" * 60)
    
    try:
        # Check if pgvector extension is available
        print("  [1/8] Checking for pgvector extension...")
        try:
            db.execute(INSTALL_PGVECTOR_EXTENSION)
            print("  [OK] pgvector extension installed/available")
            pgvector_available = True
        except Exception as e:
            print(f"  [WARNING] pgvector extension not available: {e}")
            print("  [INFO] Skipping embedding columns. Install pgvector to enable embeddings.")
            print("  [INFO] To install pgvector:")
            print("         - On Windows: Download from https://github.com/pgvector/pgvector/releases")
            print("         - On Linux: sudo apt-get install postgresql-XX-pgvector")
            print("         - On macOS: brew install pgvector")
            print("         - Or use Docker image: pgvector/pgvector:pg16")
            pgvector_available = False
        
        # Add embedding column to description table (only if pgvector is available)
        if pgvector_available:
            print("  [2/8] Adding embedding column to description table...")
            try:
                db.execute(ADD_USER_EMBEDDING_COLUMN)
                print("  [OK] User embedding column added")
            except Exception as e:
                print(f"  [WARNING] Failed to add embedding column: {e}")
                pgvector_available = False
        else:
            print("  [2/8] Skipping embedding column (pgvector not available)")
        
        # Add city column to description table
        print("  [3/8] Adding city column to description table...")
        db.execute(ADD_USER_CITY_COLUMN)
        print("  [OK] User city column added")
        
        # Add country column to description table
        print("  [4/8] Adding country column to description table...")
        db.execute(ADD_USER_COUNTRY_COLUMN)
        print("  [OK] User country column added")
        
        # Add city column to job_postings table
        print("  [5/8] Adding city column to job_postings table...")
        db.execute(ADD_JOB_CITY_COLUMN)
        print("  [OK] Job city column added")
        
        # Add country column to job_postings table
        print("  [6/8] Adding country column to job_postings table...")
        db.execute(ADD_JOB_COUNTRY_COLUMN)
        print("  [OK] Job country column added")
        
        # Create vector index for user embeddings
        print("  [7/8] Creating vector index for user embeddings...")
        try:
            db.execute(CREATE_USER_EMBEDDING_INDEX)
            print("  [OK] User embedding vector index created")
        except Exception as e:
            print(f"  [WARNING] Vector index creation failed (may need existing data): {e}")
            print("  [INFO] You can create the index later when there are embeddings")
        
        # Create location indexes
        print("  [8/8] Creating location indexes...")
        db.execute(CREATE_LOCATION_INDEXES)
        print("  [OK] Location indexes created")
        
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update existing records to parse and populate city/country from location")
        print("2. Generate embeddings for existing users")
        print("3. Update job creation/update logic to populate city/country")
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
