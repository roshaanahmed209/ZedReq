"""
Scheduled Script: Sync Vec Database
Runs Vec agent sync on a 24-hour basis to populate Qdrant vector database

This script can be run:
1. Manually: python backend/scripts/sync_vec_db.py
2. Via cron: Add to crontab to run daily
3. Via task scheduler (Windows)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from agents.Vec_agent import get_vec_agent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run Vec agent sync"""
    logger.info("=" * 60)
    logger.info("Starting Vec Agent Sync (24-hour scheduled job)")
    logger.info("=" * 60)
    
    try:
        vec_agent = get_vec_agent()
        
        if not vec_agent.is_available():
            logger.error("Vec agent is not available. Please check Qdrant and OpenAI configuration.")
            sys.exit(1)
        
        # Run sync (only new/updated entities from last 24 hours)
        result = vec_agent.sync_all_entities(force=False)
        
        logger.info("=" * 60)
        logger.info("Vec Agent Sync Completed")
        logger.info(f"Jobs indexed: {result.get('jobs_indexed', 0)}")
        logger.info(f"Users indexed: {result.get('users_indexed', 0)}")
        logger.info(f"Posts indexed: {result.get('posts_indexed', 0)}")
        logger.info(f"Total indexed: {result.get('total_indexed', 0)}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Vec Agent Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
