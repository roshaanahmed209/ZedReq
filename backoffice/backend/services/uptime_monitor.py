"""Uptime monitoring service"""
import httpx
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.orm.uptime_incident import UptimeIncident
from config.settings import settings

logger = logging.getLogger(__name__)


class UptimeMonitor:
    """Monitors main app uptime and tracks downtime incidents"""
    
    def __init__(self, db: Session):
        self.db = db
        self.main_app_url = settings.MAIN_APP_API_URL
        self._active_incident = None
    
    def check_health(self) -> bool:
        """Check main app health and track incidents"""
        try:
            health_url = f"{self.main_app_url}/health"
            
            with httpx.Client(timeout=5.0) as client:
                response = client.get(health_url)
                
                if response.status_code == 200:
                    # App is healthy
                    if self._active_incident:
                        # End the incident
                        self._end_incident()
                    return True
                else:
                    # App is unhealthy
                    if not self._active_incident:
                        self._start_incident("unhealthy", f"Health check returned status {response.status_code}")
                    return False
                    
        except httpx.TimeoutException:
            # Timeout - app is down
            if not self._active_incident:
                self._start_incident("timeout", "Health check timed out")
            return False
        except Exception as e:
            # Other error - app might be down
            logger.error(f"Error checking uptime: {e}")
            if not self._active_incident:
                self._start_incident("error", f"Health check error: {str(e)}")
            return False
    
    def _start_incident(self, incident_type: str, description: str):
        """Start a new downtime incident"""
        try:
            incident = UptimeIncident(
                incident_type=incident_type,
                start_time=datetime.utcnow(),
                status="active",
                description=description,
                affected_services=["main_app"]
            )
            self.db.add(incident)
            self.db.commit()
            self.db.refresh(incident)
            self._active_incident = incident
            logger.warning(f"Started uptime incident: {incident_type} - {description}")
        except Exception as e:
            logger.error(f"Error starting incident: {e}", exc_info=True)
            self.db.rollback()
    
    def _end_incident(self):
        """End the active incident"""
        if not self._active_incident:
            return
        
        try:
            end_time = datetime.utcnow()
            duration = (end_time - self._active_incident.start_time).total_seconds()
            
            self._active_incident.end_time = end_time
            self._active_incident.duration_seconds = int(duration)
            self._active_incident.status = "resolved"
            
            self.db.commit()
            logger.info(f"Ended uptime incident: duration={duration}s")
            self._active_incident = None
        except Exception as e:
            logger.error(f"Error ending incident: {e}", exc_info=True)
            self.db.rollback()
    
    def get_uptime_metrics(self, days: int = 30) -> dict:
        """Calculate uptime percentage, MTTR, MTBF for the last N days"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get all incidents in the period
            incidents = self.db.query(UptimeIncident).filter(
                UptimeIncident.start_time >= start_date
            ).all()
            
            total_seconds = days * 24 * 60 * 60
            downtime_seconds = sum(
                (inc.duration_seconds or 0) for inc in incidents if inc.duration_seconds
            )
            uptime_seconds = total_seconds - downtime_seconds
            uptime_percent = (uptime_seconds / total_seconds * 100) if total_seconds > 0 else 100.0
            
            # Calculate MTTR (Mean Time To Recovery)
            resolved_incidents = [inc for inc in incidents if inc.duration_seconds]
            mttr_seconds = (
                sum(inc.duration_seconds for inc in resolved_incidents) / len(resolved_incidents)
                if resolved_incidents else 0
            )
            
            # Calculate MTBF (Mean Time Between Failures)
            if len(incidents) > 1:
                # Sort by start time
                sorted_incidents = sorted(incidents, key=lambda x: x.start_time)
                intervals = []
                for i in range(len(sorted_incidents) - 1):
                    interval = (sorted_incidents[i + 1].start_time - sorted_incidents[i].start_time).total_seconds()
                    intervals.append(interval)
                mtbf_seconds = sum(intervals) / len(intervals) if intervals else 0
            else:
                mtbf_seconds = 0
            
            return {
                "uptime_percent": round(uptime_percent, 2),
                "downtime_seconds": downtime_seconds,
                "uptime_seconds": uptime_seconds,
                "total_incidents": len(incidents),
                "mttr_seconds": int(mttr_seconds),
                "mtbf_seconds": int(mtbf_seconds),
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Error calculating uptime metrics: {e}", exc_info=True)
            return {
                "uptime_percent": 0,
                "downtime_seconds": 0,
                "uptime_seconds": 0,
                "total_incidents": 0,
                "mttr_seconds": 0,
                "mtbf_seconds": 0,
                "period_days": days
            }
