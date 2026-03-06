"""Infrastructure metrics collector using psutil"""
import psutil
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models.orm.infrastructure_metric import InfrastructureMetric
from config.settings import settings

logger = logging.getLogger(__name__)


class InfrastructureCollector:
    """Collects infrastructure metrics (CPU, RAM, disk, network)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.server_name = "main"
    
    def collect_metrics(self) -> bool:
        """Collect current infrastructure metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            ram_used_mb = memory.used / (1024 * 1024)
            ram_total_mb = memory.total / (1024 * 1024)
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            
            # Network (bytes sent/received since boot)
            net_io = psutil.net_io_counters()
            network_in_mb = net_io.bytes_recv / (1024 * 1024)
            network_out_mb = net_io.bytes_sent / (1024 * 1024)
            
            # Create metric record
            metric = InfrastructureMetric(
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                ram_used_mb=ram_used_mb,
                ram_total_mb=ram_total_mb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_in_mb=network_in_mb,
                network_out_mb=network_out_mb,
                server_name=self.server_name
            )
            
            self.db.add(metric)
            self.db.commit()
            
            logger.debug(f"Collected infrastructure metrics: CPU={cpu_percent}%, RAM={ram_percent}%, Disk={disk_percent}%")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting infrastructure metrics: {e}", exc_info=True)
            self.db.rollback()
            return False
