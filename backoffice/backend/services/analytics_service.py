"""Comprehensive analytics service for all monitoring metrics"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract
from datetime import datetime, timedelta
from models.orm import (
    InfrastructureMetric, UptimeIncident, APIMetric, UserSession, PageView,
    LinkClick, UserInteraction, ErrorLog, SecurityEvent, DatabaseMetric
)
from services.uptime_monitor import UptimeMonitor
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for comprehensive analytics across all metric types"""
    
    def __init__(self, db: Session):
        self.db = db
        self.uptime_monitor = UptimeMonitor(db)
    
    # ========================================================================
    # Uptime & Infrastructure Metrics
    # ========================================================================
    
    def get_uptime_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get uptime metrics (uptime %, MTTR, MTBF)"""
        return self.uptime_monitor.get_uptime_metrics(days)
    
    def get_infrastructure_metrics(
        self,
        hours: int = 24,
        server_name: str = "main"
    ) -> Dict[str, Any]:
        """Get infrastructure metrics (CPU, RAM, disk, network)"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            metrics = self.db.query(InfrastructureMetric).filter(
                and_(
                    InfrastructureMetric.timestamp >= start_time,
                    InfrastructureMetric.server_name == server_name
                )
            ).order_by(InfrastructureMetric.timestamp.desc()).all()
            
            if not metrics:
                return {
                    "cpu_avg": 0,
                    "cpu_max": 0,
                    "ram_avg": 0,
                    "ram_max": 0,
                    "disk_avg": 0,
                    "disk_max": 0,
                    "network_in_total": 0,
                    "network_out_total": 0,
                    "data_points": []
                }
            
            # Calculate averages and maxes
            cpu_values = [float(m.cpu_percent) for m in metrics]
            ram_values = [float(m.ram_percent) for m in metrics]
            disk_values = [float(m.disk_percent) for m in metrics]
            
            return {
                "cpu_avg": round(sum(cpu_values) / len(cpu_values), 2),
                "cpu_max": round(max(cpu_values), 2),
                "ram_avg": round(sum(ram_values) / len(ram_values), 2),
                "ram_max": round(max(ram_values), 2),
                "disk_avg": round(sum(disk_values) / len(disk_values), 2),
                "disk_max": round(max(disk_values), 2),
                "network_in_total": sum(float(m.network_in_mb or 0) for m in metrics),
                "network_out_total": sum(float(m.network_out_mb or 0) for m in metrics),
                "data_points": [m.to_dict() for m in metrics[:100]]  # Limit to 100 points
            }
        except Exception as e:
            logger.error(f"Error getting infrastructure metrics: {e}", exc_info=True)
            return {}
    
    # ========================================================================
    # Application Performance Metrics (APM)
    # ========================================================================
    
    def get_api_performance(
        self,
        hours: int = 24,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get API performance metrics (response times, error rates, throughput)"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = self.db.query(APIMetric).filter(
                APIMetric.timestamp >= start_time
            )
            
            if endpoint:
                query = query.filter(APIMetric.endpoint == endpoint)
            
            metrics = query.all()
            
            if not metrics:
                return {
                    "total_requests": 0,
                    "requests_per_minute": 0,
                    "avg_response_time": 0,
                    "p50_response_time": 0,
                    "p95_response_time": 0,
                    "p99_response_time": 0,
                    "error_rate": 0,
                    "error_count": 0,
                    "status_codes": {},
                    "slow_endpoints": []
                }
            
            response_times = sorted([m.response_time_ms for m in metrics])
            total = len(response_times)
            
            # Calculate percentiles
            p50 = response_times[int(total * 0.5)] if total > 0 else 0
            p95 = response_times[int(total * 0.95)] if total > 0 else 0
            p99 = response_times[int(total * 0.99)] if total > 0 else 0
            avg = sum(response_times) / total if total > 0 else 0
            
            # Error rate
            error_count = sum(1 for m in metrics if m.status_code >= 400)
            error_rate = (error_count / total * 100) if total > 0 else 0
            
            # Status code distribution
            status_codes = {}
            for m in metrics:
                status_codes[m.status_code] = status_codes.get(m.status_code, 0) + 1
            
            # Slow endpoints (avg response time > 1s)
            endpoint_times = {}
            for m in metrics:
                if m.endpoint not in endpoint_times:
                    endpoint_times[m.endpoint] = []
                endpoint_times[m.endpoint].append(m.response_time_ms)
            
            slow_endpoints = [
                {
                    "endpoint": ep,
                    "avg_time": sum(times) / len(times),
                    "request_count": len(times)
                }
                for ep, times in endpoint_times.items()
                if sum(times) / len(times) > 1000
            ]
            slow_endpoints.sort(key=lambda x: x["avg_time"], reverse=True)
            
            # Requests per minute
            minutes = hours * 60
            rpm = total / minutes if minutes > 0 else 0
            
            return {
                "total_requests": total,
                "requests_per_minute": round(rpm, 2),
                "avg_response_time": round(avg, 2),
                "p50_response_time": p50,
                "p95_response_time": p95,
                "p99_response_time": p99,
                "error_rate": round(error_rate, 2),
                "error_count": error_count,
                "status_codes": status_codes,
                "slow_endpoints": slow_endpoints[:10]  # Top 10
            }
        except Exception as e:
            logger.error(f"Error getting API performance: {e}", exc_info=True)
            return {}
    
    # ========================================================================
    # User Analytics
    # ========================================================================
    
    def get_user_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get user analytics (DAU, WAU, MAU, active users)"""
        try:
            now = datetime.utcnow()
            
            # Daily Active Users (DAU)
            dau_start = now - timedelta(days=1)
            dau = self.db.query(func.count(func.distinct(UserSession.user_id))).filter(
                and_(
                    UserSession.start_time >= dau_start,
                    UserSession.user_id.isnot(None)
                )
            ).scalar() or 0
            
            # Weekly Active Users (WAU)
            wau_start = now - timedelta(days=7)
            wau = self.db.query(func.count(func.distinct(UserSession.user_id))).filter(
                and_(
                    UserSession.start_time >= wau_start,
                    UserSession.user_id.isnot(None)
                )
            ).scalar() or 0
            
            # Monthly Active Users (MAU)
            mau_start = now - timedelta(days=30)
            mau = self.db.query(func.count(func.distinct(UserSession.user_id))).filter(
                and_(
                    UserSession.start_time >= mau_start,
                    UserSession.user_id.isnot(None)
                )
            ).scalar() or 0
            
            # Real-time active users (sessions active in last 5 minutes)
            active_threshold = now - timedelta(minutes=5)
            active_users = self.db.query(func.count(func.distinct(UserSession.user_id))).filter(
                and_(
                    UserSession.last_activity >= active_threshold,
                    UserSession.end_time.is_(None),
                    UserSession.user_id.isnot(None)
                )
            ).scalar() or 0
            
            # New vs returning users
            new_users_start = now - timedelta(days=days)
            first_time_users = self.db.query(func.count(func.distinct(UserSession.user_id))).filter(
                and_(
                    UserSession.start_time >= new_users_start,
                    UserSession.user_id.isnot(None)
                )
            ).scalar() or 0
            
            return {
                "dau": dau,
                "wau": wau,
                "mau": mau,
                "active_users": active_users,
                "new_users": first_time_users,
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}", exc_info=True)
            return {}
    
    def get_page_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get page view analytics"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Total page views
            total_views = self.db.query(func.count(PageView.id)).filter(
                PageView.timestamp >= start_time
            ).scalar() or 0
            
            # Popular pages
            popular_pages = self.db.query(
                PageView.page_path,
                func.count(PageView.id).label('views')
            ).filter(
                PageView.timestamp >= start_time
            ).group_by(PageView.page_path).order_by(desc('views')).limit(10).all()
            
            return {
                "total_views": total_views,
                "popular_pages": [
                    {"path": page, "views": views}
                    for page, views in popular_pages
                ]
            }
        except Exception as e:
            logger.error(f"Error getting page analytics: {e}", exc_info=True)
            return {}
    
    # ========================================================================
    # Interaction Analytics
    # ========================================================================
    
    def get_link_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get link click analytics"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Total clicks
            total_clicks = self.db.query(func.count(LinkClick.id)).filter(
                LinkClick.timestamp >= start_time
            ).scalar() or 0
            
            # Top links
            top_links = self.db.query(
                LinkClick.link_url,
                func.count(LinkClick.id).label('clicks')
            ).filter(
                LinkClick.timestamp >= start_time
            ).group_by(LinkClick.link_url).order_by(desc('clicks')).limit(20).all()
            
            # External vs internal
            external_clicks = self.db.query(func.count(LinkClick.id)).filter(
                and_(
                    LinkClick.timestamp >= start_time,
                    LinkClick.is_external == True
                )
            ).scalar() or 0
            
            return {
                "total_clicks": total_clicks,
                "external_clicks": external_clicks,
                "internal_clicks": total_clicks - external_clicks,
                "top_links": [
                    {"url": url, "clicks": clicks}
                    for url, clicks in top_links
                ]
            }
        except Exception as e:
            logger.error(f"Error getting link analytics: {e}", exc_info=True)
            return {}
    
    def get_interaction_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get user interaction analytics"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Total interactions
            total = self.db.query(func.count(UserInteraction.id)).filter(
                UserInteraction.timestamp >= start_time
            ).scalar() or 0
            
            # By type
            by_type = self.db.query(
                UserInteraction.interaction_type,
                func.count(UserInteraction.id).label('count')
            ).filter(
                UserInteraction.timestamp >= start_time
            ).group_by(UserInteraction.interaction_type).all()
            
            return {
                "total_interactions": total,
                "by_type": [
                    {"type": itype, "count": count}
                    for itype, count in by_type
                ]
            }
        except Exception as e:
            logger.error(f"Error getting interaction analytics: {e}", exc_info=True)
            return {}
    
    # ========================================================================
    # Error Analytics
    # ========================================================================
    
    def get_error_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get error analytics"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Total errors
            total = self.db.query(func.count(ErrorLog.id)).filter(
                ErrorLog.timestamp >= start_time
            ).scalar() or 0
            
            # By type
            by_type = self.db.query(
                ErrorLog.error_type,
                func.count(ErrorLog.id).label('count')
            ).filter(
                ErrorLog.timestamp >= start_time
            ).group_by(ErrorLog.error_type).order_by(desc('count')).limit(10).all()
            
            # By severity
            by_severity = self.db.query(
                ErrorLog.severity,
                func.count(ErrorLog.id).label('count')
            ).filter(
                ErrorLog.timestamp >= start_time
            ).group_by(ErrorLog.severity).all()
            
            # Unresolved
            unresolved = self.db.query(func.count(ErrorLog.id)).filter(
                and_(
                    ErrorLog.timestamp >= start_time,
                    ErrorLog.resolved == False
                )
            ).scalar() or 0
            
            return {
                "total_errors": total,
                "unresolved": unresolved,
                "by_type": [
                    {"type": etype, "count": count}
                    for etype, count in by_type
                ],
                "by_severity": {
                    sev: count for sev, count in by_severity
                }
            }
        except Exception as e:
            logger.error(f"Error getting error analytics: {e}", exc_info=True)
            return {}
    
    # ========================================================================
    # Security Analytics
    # ========================================================================
    
    def get_security_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get security event analytics"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Total events
            total = self.db.query(func.count(SecurityEvent.id)).filter(
                SecurityEvent.timestamp >= start_time
            ).scalar() or 0
            
            # By type
            by_type = self.db.query(
                SecurityEvent.event_type,
                func.count(SecurityEvent.id).label('count')
            ).filter(
                SecurityEvent.timestamp >= start_time
            ).group_by(SecurityEvent.event_type).order_by(desc('count')).all()
            
            # Blocked events
            blocked = self.db.query(func.count(SecurityEvent.id)).filter(
                and_(
                    SecurityEvent.timestamp >= start_time,
                    SecurityEvent.blocked == True
                )
            ).scalar() or 0
            
            return {
                "total_events": total,
                "blocked_events": blocked,
                "by_type": [
                    {"type": etype, "count": count}
                    for etype, count in by_type
                ]
            }
        except Exception as e:
            logger.error(f"Error getting security analytics: {e}", exc_info=True)
            return {}
    
    # ========================================================================
    # Database Health
    # ========================================================================
    
    def get_database_health(self, hours: int = 24) -> Dict[str, Any]:
        """Get database health metrics"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            metrics = self.db.query(DatabaseMetric).filter(
                DatabaseMetric.timestamp >= start_time
            ).order_by(DatabaseMetric.timestamp.desc()).limit(100).all()
            
            if not metrics:
                return {}
            
            latest = metrics[0]
            
            return {
                "query_time_avg": float(latest.query_time_ms) if latest.query_time_ms else None,
                "slow_queries_count": latest.slow_queries_count,
                "connection_pool_usage": latest.connection_pool_usage,
                "active_connections": latest.active_connections,
                "database_size_mb": float(latest.database_size_mb) if latest.database_size_mb else None,
                "replication_lag_ms": latest.replication_lag_ms
            }
        except Exception as e:
            logger.error(f"Error getting database health: {e}", exc_info=True)
            return {}
    
    # ========================================================================
    # Growth Metrics
    # ========================================================================
    
    def get_growth_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get growth metrics (user growth, signups, retention, churn)"""
        try:
            # This would need to query the main app database for user signups
            # For now, return placeholder structure
            # TODO: Integrate with main app database
            
            return {
                "user_growth_rate": 0,
                "signups_per_day": 0,
                "retention_rate": 0,
                "churn_rate": 0,
                "conversion_rate": 0,
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Error getting growth metrics: {e}", exc_info=True)
            return {}
