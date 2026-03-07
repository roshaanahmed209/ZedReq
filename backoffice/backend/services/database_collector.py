"""Database health metrics collector"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.orm.database_metric import DatabaseMetric
from config.database_orm import engine
from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseCollector:
    """Collects database health metrics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.database_name = "main"
    
    def collect_metrics(self) -> bool:
        """Collect current database metrics"""
        try:
            # --- Connection pool stats (in-memory, no DB query needed) ---
            pool = engine.pool
            pool_size = pool.size()
            checked_out = pool.checkedout()
            active_connections = checked_out
            connection_pool_usage = int((checked_out / pool_size * 100)) if pool_size > 0 else 0
            
            # --- Optional: pg_stat_statements queries (may not be enabled) ---
            slow_queries_count = 0
            query_time_ms = None
            try:
                slow_queries_count = self.db.execute(
                    text("SELECT COUNT(*) FROM pg_stat_statements WHERE mean_exec_time > 1000")
                ).scalar() or 0
                query_time_ms = self.db.execute(
                    text("SELECT AVG(mean_exec_time) FROM pg_stat_statements")
                ).scalar()
            except Exception:
                # pg_stat_statements extension not installed — clear failed transaction
                self.db.rollback()
            
            # --- Database size (safe query, run after any rollback) ---
            database_size_mb = 0
            try:
                database_size_mb = self.db.execute(
                    text("SELECT pg_database_size(current_database()) / (1024 * 1024)")
                ).scalar() or 0
            except Exception:
                self.db.rollback()
            
            # --- Persist metric ---
            metric = DatabaseMetric(
                query_time_ms=query_time_ms,
                slow_queries_count=slow_queries_count,
                connection_pool_usage=connection_pool_usage,
                active_connections=active_connections,
                database_size_mb=database_size_mb,
                database_name=self.database_name
            )
            
            self.db.add(metric)
            self.db.commit()
            
            logger.debug(f"Collected database metrics: pool_usage={connection_pool_usage}%, size={database_size_mb}MB")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}", exc_info=True)
            self.db.rollback()
            return False
