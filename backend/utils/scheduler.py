"""
Background Task Scheduler for Vec Agent
Uses APScheduler to run Vec agent sync every 24 hours
"""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from agents.Vec_agent import get_vec_agent

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
    _scheduler.add_job(
        func=run_vec_sync,
        trigger=IntervalTrigger(hours=interval_hours),
        id='vec_sync_job',
        name='Vec Agent Sync',
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )
    
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


def get_scheduler():
    """Get the scheduler instance"""
    return _scheduler
