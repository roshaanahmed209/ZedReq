"""
Script to backfill job embeddings for jobs missing embeddings
Processes jobs in batches to avoid API rate limits
"""
import os
import sys
import time
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from config.database_orm import get_db
from models.orm.job_posting import JobPosting
from utils.job_embeddings import generate_job_embedding, store_job_embedding
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def backfill_job_embeddings(
    batch_size: int = None,
    limit: Optional[int] = None,
    dry_run: bool = False
) -> dict:
    """
    Backfill embeddings for jobs missing embeddings.
    
    Args:
        batch_size: Number of jobs to process per batch (default from settings)
        limit: Maximum number of jobs to process (None = all)
        dry_run: If True, only count jobs without generating embeddings
        
    Returns:
        Dictionary with statistics
    """
    batch_size = batch_size or settings.JOB_EMBEDDING_BACKFILL_BATCH_SIZE
    
    db: Session = next(get_db())
    
    try:
        # Find jobs missing embeddings
        query = db.query(JobPosting).filter(
            JobPosting.status == 'active',
            JobPosting.embedding.is_(None)  # Using IS NULL check
        )
        
        if limit:
            query = query.limit(limit)
        
        jobs_missing_embeddings = query.all()
        total_jobs = len(jobs_missing_embeddings)
        
        logger.info(f"Found {total_jobs} active jobs missing embeddings")
        
        if total_jobs == 0:
            return {
                'total_jobs': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': dry_run
            }
        
        if dry_run:
            logger.info(f"[DRY RUN] Would process {total_jobs} jobs in batches of {batch_size}")
            return {
                'total_jobs': total_jobs,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'dry_run': True
            }
        
        # Process in batches
        processed = 0
        successful = 0
        failed = 0
        
        for i in range(0, total_jobs, batch_size):
            batch = jobs_missing_embeddings[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_jobs + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} jobs)")
            
            for job in batch:
                try:
                    logger.debug(f"Generating embedding for job {job.job_id}: {job.title}")
                    embedding = generate_job_embedding(job)
                    
                    if embedding:
                        success = store_job_embedding(job.job_id, embedding, db)
                        if success:
                            successful += 1
                            logger.debug(f"Successfully stored embedding for job {job.job_id}")
                        else:
                            failed += 1
                            logger.warning(f"Failed to store embedding for job {job.job_id}")
                    else:
                        failed += 1
                        logger.warning(f"Failed to generate embedding for job {job.job_id}")
                    
                    processed += 1
                    
                    # Small delay to avoid rate limits
                    time.sleep(0.1)
                    
                except Exception as e:
                    failed += 1
                    processed += 1
                    logger.error(f"Error processing job {job.job_id}: {e}", exc_info=True)
            
            # Longer delay between batches
            if i + batch_size < total_jobs:
                logger.info(f"Batch {batch_num} complete. Waiting 2 seconds before next batch...")
                time.sleep(2)
        
        logger.info(
            f"Backfill complete: {processed} processed, {successful} successful, {failed} failed"
        )
        
        return {
            'total_jobs': total_jobs,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'dry_run': False
        }
        
    except Exception as e:
        logger.error(f"Error in backfill: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill job embeddings')
    parser.add_argument('--batch-size', type=int, default=None, help='Batch size (default from settings)')
    parser.add_argument('--limit', type=int, default=None, help='Maximum number of jobs to process')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (only count, no processing)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Job Embedding Backfill Script")
    print("=" * 60)
    
    result = backfill_job_embeddings(
        batch_size=args.batch_size,
        limit=args.limit,
        dry_run=args.dry_run
    )
    
    print("\nResults:")
    print(f"  Total jobs missing embeddings: {result['total_jobs']}")
    if not result['dry_run']:
        print(f"  Processed: {result['processed']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
    print("=" * 60)
