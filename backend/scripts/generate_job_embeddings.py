"""
Simple script to generate embeddings for all job postings missing embeddings.
Run this script to backfill embeddings for jobs in your database.

Usage:
    python backend/scripts/generate_job_embeddings.py
    python backend/scripts/generate_job_embeddings.py --limit 10  # Process only 10 jobs
    python backend/scripts/generate_job_embeddings.py --dry-run   # See how many jobs need embeddings
"""
import os
import sys
import time
import argparse
from typing import Optional

# Add backend directory to path for imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_script_dir)  # Go up one level from scripts/ to backend/

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from sqlalchemy.orm import Session
from config.database_orm import get_db
from models.orm.job_posting import JobPosting
from utils.job_embeddings import generate_job_embedding, store_job_embedding
from config.database import get_database
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_job_embeddings(
    batch_size: int = 10,
    limit: Optional[int] = None,
    dry_run: bool = False,
    status_filter: str = 'active'
) -> dict:
    """
    Generate embeddings for all job postings missing embeddings.
    
    Args:
        batch_size: Number of jobs to process per batch (default: 10)
        limit: Maximum number of jobs to process (None = all)
        dry_run: If True, only count jobs without generating embeddings
        status_filter: Filter by job status (default: 'active')
        
    Returns:
        Dictionary with statistics
    """
    db: Session = next(get_db())
    db_raw = get_database()
    
    try:
        # Check if embedding column exists
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'job_postings' 
        AND column_name = 'embedding'
        """
        column_exists = db_raw.fetch_one(check_column_query)
        
        if not column_exists:
            logger.error("Embedding column does not exist in job_postings table. Please run the migration first.")
            return {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'error': 'embedding_column_missing'
            }
        
        # Find jobs missing embeddings using raw SQL (pgvector requires raw SQL)
        # Note: We only check for NULL, not empty vectors (pgvector doesn't allow empty vectors)
        count_query = """
        SELECT COUNT(*) as count
        FROM job_postings
        WHERE status = %s
        AND embedding IS NULL
        """
        
        count_result = db_raw.fetch_one(count_query, (status_filter,))
        total_jobs = count_result['count'] if count_result else 0
        
        logger.info(f"Found {total_jobs} {status_filter} jobs missing embeddings")
        
        if total_jobs == 0:
            logger.info("No jobs need embeddings. All done!")
            return {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': dry_run
            }
        
        if dry_run:
            logger.info(f"[DRY RUN] Would process {total_jobs} jobs in batches of {batch_size}")
            if limit:
                logger.info(f"[DRY RUN] Limited to first {limit} jobs")
            return {
                'total': total_jobs,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': True
            }
        
        # Get job IDs missing embeddings
        # Note: We only check for NULL, not empty vectors (pgvector doesn't allow empty vectors)
        query = """
        SELECT job_id, title
        FROM job_postings
        WHERE status = %s
        AND embedding IS NULL
        ORDER BY job_id
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        job_rows = db_raw.fetch_all(query, (status_filter,))
        job_ids = [(row['job_id'], row.get('title', 'Unknown')) for row in job_rows]
        
        if not job_ids:
            logger.info("No jobs to process")
            return {
                'total': total_jobs,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': False
            }
        
        # Process in batches
        processed = 0
        successful = 0
        failed = 0
        
        total_batches = (len(job_ids) + batch_size - 1) // batch_size
        
        logger.info(f"Starting to process {len(job_ids)} jobs in {total_batches} batches...")
        
        for i in range(0, len(job_ids), batch_size):
            batch_job_ids = job_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_job_ids)} jobs)")
            logger.info(f"{'='*60}")
            
            for job_id, job_title in batch_job_ids:
                try:
                    logger.info(f"[{processed + 1}/{len(job_ids)}] Processing job {job_id}: {job_title}")
                    
                    # Get job from database
                    job = db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
                    if not job:
                        logger.warning(f"Job {job_id} not found in database")
                        failed += 1
                        processed += 1
                        continue
                    
                    # Generate embedding
                    logger.debug(f"Generating embedding for job {job_id}...")
                    embedding = generate_job_embedding(job)
                    
                    if embedding:
                        # Store embedding
                        logger.debug(f"Storing embedding for job {job_id}...")
                        success = store_job_embedding(job_id, embedding, db)
                        if success:
                            successful += 1
                            logger.info(f"✓ Successfully generated and stored embedding for job {job_id}")
                        else:
                            failed += 1
                            logger.warning(f"✗ Failed to store embedding for job {job_id}")
                    else:
                        failed += 1
                        logger.warning(f"✗ Failed to generate embedding for job {job_id}")
                    
                    processed += 1
                    
                    # Small delay to avoid rate limits
                    time.sleep(0.2)
                    
                except Exception as e:
                    failed += 1
                    processed += 1
                    logger.error(f"✗ Error processing job {job_id}: {e}", exc_info=True)
            
            # Longer delay between batches
            if i + batch_size < len(job_ids):
                logger.info(f"\nBatch {batch_num} complete. Waiting 2 seconds before next batch...")
                time.sleep(2)
        
        logger.info(f"\n{'='*60}")
        logger.info("Job Embedding Generation Complete!")
        logger.info(f"{'='*60}")
        logger.info(f"Total jobs: {total_jobs}")
        logger.info(f"Processed: {processed}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {(successful/processed*100) if processed > 0 else 0:.1f}%")
        
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
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate embeddings for job postings missing embeddings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # See how many jobs need embeddings (dry run)
  python backend/scripts/generate_job_embeddings.py --dry-run
  
  # Generate embeddings for all jobs
  python backend/scripts/generate_job_embeddings.py
  
  # Generate embeddings for first 10 jobs only
  python backend/scripts/generate_job_embeddings.py --limit 10
  
  # Process with larger batch size
  python backend/scripts/generate_job_embeddings.py --batch-size 20
        """
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of jobs to process per batch (default: 10)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of jobs to process (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run - only count jobs without generating embeddings'
    )
    parser.add_argument(
        '--status',
        type=str,
        default='active',
        help='Filter by job status (default: active)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("Job Embedding Generation Script")
    print("="*60)
    print(f"Batch Size: {args.batch_size}")
    print(f"Limit: {args.limit if args.limit else 'All jobs'}")
    print(f"Status Filter: {args.status}")
    print(f"Dry Run: {'Yes' if args.dry_run else 'No'}")
    print("="*60 + "\n")
    
    if args.dry_run:
        print("Running in DRY RUN mode - no embeddings will be generated\n")
    
    start_time = time.time()
    
    try:
        result = generate_job_embeddings(
            batch_size=args.batch_size,
            limit=args.limit,
            dry_run=args.dry_run,
            status_filter=args.status
        )
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("Final Results")
        print("="*60)
        print(f"Total jobs missing embeddings: {result['total']}")
        
        if not result['dry_run']:
            print(f"Processed: {result['processed']}")
            print(f"Successful: {result['successful']}")
            print(f"Failed: {result['failed']}")
            if result['processed'] > 0:
                success_rate = (result['successful'] / result['processed']) * 100
                print(f"Success rate: {success_rate:.1f}%")
        
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        print("="*60 + "\n")
        
        if result.get('error'):
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        elif result['failed'] > 0 and not args.dry_run:
            print(f"WARNING: {result['failed']} jobs failed. Check logs for details.")
            sys.exit(1)
        elif result['successful'] == 0 and not args.dry_run and result['total'] > 0:
            print("WARNING: No embeddings were generated. Check logs for details.")
            sys.exit(1)
        else:
            print("✓ Script completed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        logger.exception("Script failed with error")
        sys.exit(1)
