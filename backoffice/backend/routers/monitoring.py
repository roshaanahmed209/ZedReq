"""Monitoring API Router - Exposes all analytics endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from dependencies.database import get_db
from dependencies.auth import get_current_admin
from services.analytics_service import AnalyticsService
from services.alerting_service import AlertingService
from models.orm import AlertRule, AlertHistory
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Get analytics service instance"""
    return AnalyticsService(db)


def get_alerting_service(db: Session = Depends(get_db)) -> AlertingService:
    """Get alerting service instance"""
    return AlertingService(db)


@router.get("/uptime")
async def get_uptime(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get uptime metrics"""
    service = get_analytics_service(db)
    return service.get_uptime_metrics(days)


@router.get("/infrastructure")
async def get_infrastructure(
    hours: int = Query(24, ge=1, le=168),
    server_name: str = Query("main"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get infrastructure metrics"""
    service = get_analytics_service(db)
    return service.get_infrastructure_metrics(hours, server_name)


@router.get("/performance")
async def get_performance(
    hours: int = Query(24, ge=1, le=168),
    endpoint: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get API performance metrics"""
    service = get_analytics_service(db)
    return service.get_api_performance(hours, endpoint)


@router.get("/users")
async def get_users(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get user analytics"""
    service = get_analytics_service(db)
    return service.get_user_analytics(days)


@router.get("/pages")
async def get_pages(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get page view analytics"""
    service = get_analytics_service(db)
    return service.get_page_analytics(days)


@router.get("/interactions")
async def get_interactions(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get interaction analytics"""
    service = get_analytics_service(db)
    return service.get_interaction_analytics(days)


@router.get("/links")
async def get_links(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get link click analytics"""
    service = get_analytics_service(db)
    return service.get_link_analytics(days)


@router.get("/errors")
async def get_errors(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get error analytics"""
    service = get_analytics_service(db)
    return service.get_error_analytics(days)


@router.get("/security")
async def get_security(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get security event analytics"""
    service = get_analytics_service(db)
    return service.get_security_analytics(days)


@router.get("/database")
async def get_database(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get database health metrics"""
    service = get_analytics_service(db)
    return service.get_database_health(hours)


@router.get("/growth")
async def get_growth(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get growth metrics"""
    service = get_analytics_service(db)
    return service.get_growth_metrics(days)


# Alert endpoints
class AlertRuleCreate(BaseModel):
    rule_name: str
    metric_type: str
    threshold: float
    condition: str
    enabled: bool = True
    channels: List[str] = ["email"]


@router.get("/alerts/rules")
async def get_alert_rules(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get all alert rules"""
    rules = db.query(AlertRule).all()
    return [rule.to_dict() for rule in rules]


@router.post("/alerts/rules")
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new alert rule"""
    service = get_alerting_service(db)
    rule = service.create_alert_rule(
        rule_name=rule_data.rule_name,
        metric_type=rule_data.metric_type,
        threshold=rule_data.threshold,
        condition=rule_data.condition,
        enabled=rule_data.enabled,
        channels=rule_data.channels
    )
    return rule.to_dict()


@router.get("/alerts/history")
async def get_alert_history(
    rule_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get alert history"""
    service = get_alerting_service(db)
    return service.get_alert_history(rule_id, limit)


@router.post("/alerts/check")
async def check_alerts(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Manually trigger alert check"""
    service = get_alerting_service(db)
    triggered = service.check_alerts()
    return {"triggered": triggered, "count": len(triggered)}
