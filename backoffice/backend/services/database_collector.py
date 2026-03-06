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
            # Get connection pool stats
            pool = engine.pool
            pool_size = pool.size()
            checked_in = pool.checkedin()
            checked_out = pool.checkedout()
            overflow = pool.overflow()
            active_connections = checked_out
            connection_pool_usage = int((checked_out / pool_size * 100)) if pool_size > 0 else 0
            
            # Get database size
            size_query = text("""
                SELECT pg_database_size(current_database()) / (1024 * 1024) as size_mb
            """)
            result = self.db.execute(size_query)
            database_size_mb = result.scalar() or 0
            
            # Get slow queries count (queries > 1 second in last hour)
            # Note: This requires pg_stat_statements extension
            slow_queries_count = 0
            try:
                slow_query = text("""
                    SELECT COUNT(*) 
                    FROM pg_stat_statements 
                    WHERE mean_exec_time > 1000
                    AND query_start > NOW() - INTERVAL '1 hour'
                """)
                slow_queries_count = self.db.execute(slow_query).scalar() or 0
            except Exception:
                # pg_stat_statements might not be enabled
                pass
            
            # Average query time (if available)
            query_time_ms = None
            try:
                avg_query = text("""
                    SELECT AVG(mean_exec_time)
                    FROM pg_stat_statements
                    WHERE query_start > NOW() - INTERVAL '1 hour'
                """)
                query_time_ms = self.db.execute(avg_query).scalar()
            except Exception:
                pass
            
            # Create metric record
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
