"""
Background Task Scheduler for Vec Agent and Azel Agent
Uses APScheduler to run Vec agent sync every 24 hours and Azel cleanup every 15 minutes
"""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from agents.Vec_agent import get_vec_agent
from agents.Azel_agent import get_azel_agent

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler = None


def run_vec_sync():
    """Function to run Vec agent sync (optimized for 100k+ users)"""
    try:
        logger.info("Running scheduled Vec agent sync (24-hour cycle)...")
        vec_agent = get_vec_agent()
        
        if not vec_agent.is_available():
            logger.warning("Vec agent not available, skipping sync")
            return
        
        # Sync only new/updated entities from last 24 hours (incremental)
        result = vec_agent.sync_all_entities(force=False)
        
        total_indexed = result.get('total_indexed', 0)
        total_time = result.get('total_time_seconds', 0)
        
        logger.info(
            f"Vec sync completed: {total_indexed} entities indexed in {total_time}s "
            f"({total_indexed/total_time:.1f} entities/sec)" if total_time > 0 else f"Vec sync completed: {total_indexed} entities indexed"
        )
        
    except Exception as e:
        logger.error(f"Error in scheduled Vec sync: {e}", exc_info=True)


def start_scheduler():
    """Start the background scheduler for Vec agent sync"""
    global _scheduler
    
    if _scheduler is not None:
        logger.warning("Scheduler already started")
        return
    
    # Check if scheduler is enabled
    enable_scheduler = os.environ.get('VEC_SCHEDULER_ENABLED', 'true').lower() == 'true'
    if not enable_scheduler:
        logger.info("Vec scheduler is disabled via VEC_SCHEDULER_ENABLED")
        return
    
    # Get sync interval (default: 24 hours)
    interval_hours = int(os.environ.get('VEC_SYNC_INTERVAL_HOURS', 24))
    
    _scheduler = BackgroundScheduler()
    
    # Add Vec sync job
    _scheduler.add_job(
        func=run_vec_sync,
        trigger=IntervalTrigger(hours=interval_hours),
        id='vec_sync_job',
        name='Vec Agent Sync',
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )
    
    # Add Azel cleanup job
    cleanup_enabled = os.environ.get('AZEL_CLEANUP_ENABLED', 'true').lower() == 'true'
    if cleanup_enabled:
        cleanup_interval_minutes = int(os.environ.get('AZEL_CLEANUP_INTERVAL_MINUTES', 15))
        _scheduler.add_job(
            func=run_azel_cleanup,
            trigger=IntervalTrigger(minutes=cleanup_interval_minutes),
            id='azel_cleanup_job',
            name='Azel Collection Cleanup',
            replace_existing=True,
            max_instances=1  # Prevent overlapping runs
        )
        logger.info(f"Azel cleanup job added (interval: {cleanup_interval_minutes} minutes)")
    
    # Add Firebase purge retry job (always enabled)
    _scheduler.add_job(
        func=run_firebase_purge_retries,
        trigger=IntervalTrigger(minutes=15),
        id='firebase_purge_retry_job',
        name='Firebase Purge Retry',
        replace_existing=True,
        max_instances=1,
    )
    logger.info("Firebase purge retry job added (interval: 15 minutes)")

    # Add optional job embedding backfill job
    backfill_enabled = os.environ.get('JOB_EMBEDDING_BACKFILL_ENABLED', 'false').lower() == 'true'
    if backfill_enabled:
        backfill_interval_hours = int(os.environ.get('JOB_EMBEDDING_BACKFILL_INTERVAL_HOURS', 24))
        _scheduler.add_job(
            func=run_job_embedding_backfill,
            trigger=IntervalTrigger(hours=backfill_interval_hours),
            id='job_embedding_backfill_job',
            name='Job Embedding Backfill',
            replace_existing=True,
            max_instances=1  # Prevent overlapping runs
        )
        logger.info(f"Job embedding backfill job added (interval: {backfill_interval_hours} hours)")
    
    _scheduler.start()
    logger.info(f"Vec agent scheduler started (interval: {interval_hours} hours)")
    
    # Run initial sync after a short delay
    import threading
    def run_initial_sync():
        import time
        time.sleep(10)  # Wait 10 seconds for app to fully start
        run_vec_sync()
    
    threading.Thread(target=run_initial_sync, daemon=True).start()


def stop_scheduler():
    """Stop the background scheduler"""
    global _scheduler
    
    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Vec agent scheduler stopped")


def run_azel_cleanup():
    """Function to run Azel agent collection cleanup"""
    try:
        logger.info("Running scheduled Azel collection cleanup...")
        azel_agent = get_azel_agent()
        
        if not azel_agent.is_available():
            logger.warning("Azel agent not available, skipping cleanup")
            return
        
        # Run cleanup
        result = azel_agent.cleanup_expired_collections()
        
        if result.get('success'):
            logger.info(
                f"Azel cleanup completed: {result.get('collections_deleted', 0)} collections deleted, "
                f"{result.get('points_deleted', 0)} points deleted, "
                f"{result.get('collections_checked', 0)} collections checked"
            )
        else:
            logger.warning(f"Azel cleanup completed with errors: {result.get('errors', result.get('error', 'Unknown error'))}")
        
    except Exception as e:
        logger.error(f"Error in scheduled Azel cleanup: {e}", exc_info=True)


def run_job_embedding_backfill():
    """Function to backfill job embeddings for jobs missing embeddings"""
    try:
        logger.info("Running scheduled job embedding backfill...")
        
        # Import here to avoid circular dependencies
        from scripts.backfill_job_embeddings import backfill_job_embeddings
        
        result = backfill_job_embeddings(dry_run=False)
        logger.info(
            f"Job embedding backfill completed: {result.get('processed', 0)} processed, "
            f"{result.get('successful', 0)} successful, {result.get('failed', 0)} failed"
        )
        
    except Exception as e:
        logger.error(f"Error in scheduled job embedding backfill: {e}", exc_info=True)


def run_firebase_purge_retries():
    """Retry failed Firebase conversation purges for deleted users.

    Runs every 15 minutes. Processes rows where succeeded_at IS NULL and
    attempt_count < 5, stops re-trying permanently failed entries after 5 attempts.
    """
    import asyncio
    from config.database import get_connection_params, Database
    from services.messaging_service import MessagingService

    try:
        db = Database(get_connection_params())
        rows = db.fetch_all(
            """
            SELECT id, user_id FROM firebase_purge_retries
            WHERE succeeded_at IS NULL AND attempt_count < 5
            ORDER BY created_at
            """,
        )
        if not rows:
            return

        logger.info("firebase_purge_retries: %d pending rows", len(rows))
        messaging = MessagingService()

        for row in rows:
            row_id = row["id"]
            user_id = row["user_id"]
            try:
                purged = asyncio.run(messaging.purge_conversations_for_user(user_id))
            except Exception as e:
                logger.error("Retry Firebase purge uid=%s: %s", user_id, e, exc_info=True)
                purged = False

            if purged:
                db.execute(
                    "UPDATE firebase_purge_retries SET succeeded_at = NOW(), last_attempt_at = NOW() WHERE id = %s",
                    (row_id,),
                )
                logger.info("Firebase purge retry succeeded for uid=%s", user_id)
            else:
                db.execute(
                    "UPDATE firebase_purge_retries SET attempt_count = attempt_count + 1, last_attempt_at = NOW() WHERE id = %s",
                    (row_id,),
                )

        db.close()
    except Exception as e:
        logger.error("run_firebase_purge_retries failed: %s", e, exc_info=True)


def get_scheduler():
    """Get the scheduler instance"""
    return _scheduler
