"""
Script to generate embeddings for all existing jobs and user profiles
Processes in batches to avoid API rate limits
"""
import os
import sys
import time
from typing import Optional, Dict, Any

# Add backend directory to path for imports
# Script is in backend/scripts/, so we need to go up ONE level to get to backend/
_script_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_script_dir)  # Go up one level from scripts/ to backend/

# Add backend directory to path (this is where config, models, utils modules are)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from sqlalchemy.orm import Session
from config.database_orm import get_db
from models.orm.job_posting import JobPosting
from models.orm.user import User
from models.orm.description import Description
from utils.job_embeddings import (
    generate_job_embedding,
    store_job_embedding,
    generate_user_profile_embedding,
    store_user_embedding
)
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_job_embeddings_batch(
    db: Session,
    batch_size: int = None,
    limit: Optional[int] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Generate embeddings for jobs missing embeddings.
    
    Args:
        db: Database session
        batch_size: Number of jobs to process per batch
        limit: Maximum number of jobs to process (None = all)
        dry_run: If True, only count jobs without generating embeddings
        
    Returns:
        Dictionary with statistics
    """
    batch_size = batch_size or settings.JOB_EMBEDDING_BACKFILL_BATCH_SIZE
    
    try:
        # Check if embedding column exists first
        from config.database import get_database
        db_raw = get_database()
        
        # Check if embedding column exists
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'job_postings' 
        AND column_name = 'embedding'
        """
        column_exists = db_raw.fetch_one(check_column_query)
        
        if not column_exists:
            logger.warning("Embedding column does not exist in job_postings table. Please run the migration first.")
            return {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': dry_run,
                'error': 'embedding_column_missing'
            }
        
        # Find jobs missing embeddings using raw SQL (embedding column managed via raw SQL)
        count_query = """
        SELECT COUNT(*) as count
        FROM job_postings
        WHERE status = 'active'
        AND (embedding IS NULL OR embedding = '[]'::vector)
        """
        
        if limit:
            count_query += f" LIMIT {limit}"
        
        count_result = db_raw.fetch_one(count_query)
        total_jobs = count_result['count'] if count_result else 0
        
        logger.info(f"Found {total_jobs} active jobs missing embeddings")
        
        if total_jobs == 0:
            return {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': dry_run
            }
        
        if dry_run:
            logger.info(f"[DRY RUN] Would process {total_jobs} jobs in batches of {batch_size}")
            return {
                'total': total_jobs,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': True
            }
        
        # Get jobs missing embeddings
        query = """
        SELECT job_id
        FROM job_postings
        WHERE status = 'active'
        AND (embedding IS NULL OR embedding = '[]'::vector)
        ORDER BY job_id
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        job_ids_result = db_raw.fetch_all(query)
        job_ids = [row['job_id'] for row in job_ids_result]
        
        # Process in batches
        processed = 0
        successful = 0
        failed = 0
        
        for i in range(0, len(job_ids), batch_size):
            batch_job_ids = job_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(job_ids) + batch_size - 1) // batch_size
            
            logger.info(f"Processing job batch {batch_num}/{total_batches} ({len(batch_job_ids)} jobs)")
            
            for job_id in batch_job_ids:
                try:
                    job = db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
                    if not job:
                        failed += 1
                        processed += 1
                        continue
                    
                    logger.debug(f"Generating embedding for job {job_id}: {job.title}")
                    embedding = generate_job_embedding(job)
                    
                    if embedding:
                        success = store_job_embedding(job_id, embedding, db)
                        if success:
                            successful += 1
                            logger.debug(f"Successfully stored embedding for job {job_id}")
                        else:
                            failed += 1
                            logger.warning(f"Failed to store embedding for job {job_id}")
                    else:
                        failed += 1
                        logger.warning(f"Failed to generate embedding for job {job_id}")
                    
                    processed += 1
                    
                    # Small delay to avoid rate limits
                    time.sleep(0.1)
                    
                except Exception as e:
                    failed += 1
                    processed += 1
                    logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
            
            # Longer delay between batches
            if i + batch_size < len(job_ids):
                logger.info(f"Job batch {batch_num} complete. Waiting 2 seconds before next batch...")
                time.sleep(2)
        
        logger.info(
            f"Job embeddings complete: {processed} processed, {successful} successful, {failed} failed"
        )
        
        return {
            'total': total_jobs,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'dry_run': False
        }
        
    except Exception as e:
        logger.error(f"Error generating job embeddings: {e}", exc_info=True)
        raise


def generate_user_embeddings_batch(
    db: Session,
    batch_size: int = 100,
    limit: Optional[int] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Generate embeddings for user profiles missing embeddings.
    
    Args:
        db: Database session
        batch_size: Number of users to process per batch
        limit: Maximum number of users to process (None = all)
        dry_run: If True, only count users without generating embeddings
        
    Returns:
        Dictionary with statistics
    """
    try:
        # Find users missing embeddings using raw SQL
        from config.database import get_database
        db_raw = get_database()
        
        # Check if embedding column exists
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'description' 
        AND column_name = 'embedding'
        """
        column_exists = db_raw.fetch_one(check_column_query)
        
        if not column_exists:
            logger.warning("Embedding column does not exist in description table. Please run the migration first.")
            return {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': dry_run,
                'error': 'embedding_column_missing'
            }
        
        count_query = """
        SELECT COUNT(*) as count
        FROM users u
        INNER JOIN description d ON u.description_id = d.desc_id
        WHERE (d.embedding IS NULL OR d.embedding = '[]'::vector)
        """
        
        if limit:
            count_query += f" LIMIT {limit}"
        
        count_result = db_raw.fetch_one(count_query)
        total_users = count_result['count'] if count_result else 0
        
        logger.info(f"Found {total_users} users missing embeddings")
        
        if total_users == 0:
            return {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': dry_run
            }
        
        if dry_run:
            logger.info(f"[DRY RUN] Would process {total_users} users in batches of {batch_size}")
            return {
                'total': total_users,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': True
            }
        
        # Get user IDs missing embeddings
        query = """
        SELECT u.uid as user_id
        FROM users u
        INNER JOIN description d ON u.description_id = d.desc_id
        WHERE (d.embedding IS NULL OR d.embedding = '[]'::vector)
        ORDER BY u.uid
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        user_ids_result = db_raw.fetch_all(query)
        user_ids = [row['user_id'] for row in user_ids_result]
        
        # Process in batches
        processed = 0
        successful = 0
        failed = 0
        
        for i in range(0, len(user_ids), batch_size):
            batch_user_ids = user_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(user_ids) + batch_size - 1) // batch_size
            
            logger.info(f"Processing user batch {batch_num}/{total_batches} ({len(batch_user_ids)} users)")
            
            for user_id in batch_user_ids:
                try:
                    logger.debug(f"Generating embedding for user {user_id}")
                    embedding = generate_user_profile_embedding(user_id, db)
                    
                    if embedding:
                        success = store_user_embedding(user_id, embedding, db)
                        if success:
                            successful += 1
                            logger.debug(f"Successfully stored embedding for user {user_id}")
                        else:
                            failed += 1
                            logger.warning(f"Failed to store embedding for user {user_id}")
                    else:
                        failed += 1
                        logger.warning(f"Failed to generate embedding for user {user_id}")
                    
                    processed += 1
                    
                    # Small delay to avoid rate limits
                    time.sleep(0.2)  # Slightly longer for users (more complex)
                    
                except Exception as e:
                    failed += 1
                    processed += 1
                    logger.error(f"Error processing user {user_id}: {e}", exc_info=True)
            
            # Longer delay between batches
            if i + batch_size < len(user_ids):
                logger.info(f"User batch {batch_num} complete. Waiting 3 seconds before next batch...")
                time.sleep(3)
        
        logger.info(
            f"User embeddings complete: {processed} processed, {successful} successful, {failed} failed"
        )
        
        return {
            'total': total_users,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'dry_run': False
        }
        
    except Exception as e:
        logger.error(f"Error generating user embeddings: {e}", exc_info=True)
        raise


def generate_all_embeddings(
    jobs: bool = True,
    users: bool = True,
    job_batch_size: int = None,
    user_batch_size: int = 100,
    job_limit: Optional[int] = None,
    user_limit: Optional[int] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Generate embeddings for all jobs and/or user profiles.
    
    Args:
        jobs: If True, generate embeddings for jobs
        users: If True, generate embeddings for users
        job_batch_size: Batch size for jobs (default from settings)
        user_batch_size: Batch size for users (default 100)
        job_limit: Maximum number of jobs to process (None = all)
        user_limit: Maximum number of users to process (None = all)
        dry_run: If True, only count without generating embeddings
        
    Returns:
        Dictionary with combined statistics
    """
    db: Session = next(get_db())
    
    try:
        results = {
            'jobs': {},
            'users': {},
            'total_processed': 0,
            'total_successful': 0,
            'total_failed': 0
        }
        
        if jobs:
            logger.info("=" * 60)
            logger.info("Generating Job Embeddings")
            logger.info("=" * 60)
            job_results = generate_job_embeddings_batch(
                db, 
                batch_size=job_batch_size,
                limit=job_limit,
                dry_run=dry_run
            )
            results['jobs'] = job_results
            results['total_processed'] += job_results.get('processed', 0)
            results['total_successful'] += job_results.get('successful', 0)
            results['total_failed'] += job_results.get('failed', 0)
        
        if users:
            logger.info("=" * 60)
            logger.info("Generating User Profile Embeddings")
            logger.info("=" * 60)
            user_results = generate_user_embeddings_batch(
                db,
                batch_size=user_batch_size,
                limit=user_limit,
                dry_run=dry_run
            )
            results['users'] = user_results
            results['total_processed'] += user_results.get('processed', 0)
            results['total_successful'] += user_results.get('successful', 0)
            results['total_failed'] += user_results.get('failed', 0)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in generate_all_embeddings: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate embeddings for jobs and user profiles')
    parser.add_argument('--jobs', action='store_true', default=True, help='Generate embeddings for jobs (default: True)')
    parser.add_argument('--no-jobs', dest='jobs', action='store_false', help='Skip job embeddings')
    parser.add_argument('--users', action='store_true', default=True, help='Generate embeddings for users (default: True)')
    parser.add_argument('--no-users', dest='users', action='store_false', help='Skip user embeddings')
    parser.add_argument('--job-batch-size', type=int, default=None, help='Batch size for jobs (default from settings)')
    parser.add_argument('--user-batch-size', type=int, default=100, help='Batch size for users (default: 100)')
    parser.add_argument('--job-limit', type=int, default=None, help='Maximum number of jobs to process')
    parser.add_argument('--user-limit', type=int, default=None, help='Maximum number of users to process')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (only count, no processing)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Embedding Generation Script")
    print("=" * 60)
    print(f"Jobs: {'Yes' if args.jobs else 'No'}")
    print(f"Users: {'Yes' if args.users else 'No'}")
    print(f"Dry Run: {'Yes' if args.dry_run else 'No'}")
    print("=" * 60)
    
    start_time = time.time()
    
    results = generate_all_embeddings(
        jobs=args.jobs,
        users=args.users,
        job_batch_size=args.job_batch_size,
        user_batch_size=args.user_batch_size,
        job_limit=args.job_limit,
        user_limit=args.user_limit,
        dry_run=args.dry_run
    )
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("Final Results")
    print("=" * 60)
    
    if args.jobs:
        print("\nJobs:")
        print(f"  Total missing: {results['jobs'].get('total', 0)}")
        if not args.dry_run:
            print(f"  Processed: {results['jobs'].get('processed', 0)}")
            print(f"  Successful: {results['jobs'].get('successful', 0)}")
            print(f"  Failed: {results['jobs'].get('failed', 0)}")
    
    if args.users:
        print("\nUsers:")
        print(f"  Total missing: {results['users'].get('total', 0)}")
        if not args.dry_run:
            print(f"  Processed: {results['users'].get('processed', 0)}")
            print(f"  Successful: {results['users'].get('successful', 0)}")
            print(f"  Failed: {results['users'].get('failed', 0)}")
    
    print("\nOverall:")
    print(f"  Total Processed: {results['total_processed']}")
    print(f"  Total Successful: {results['total_successful']}")
    print(f"  Total Failed: {results['total_failed']}")
    print(f"  Time Elapsed: {elapsed_time:.2f} seconds")
    print("=" * 60)
