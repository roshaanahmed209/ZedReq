"""Alerting service for monitoring alerts"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from models.orm import AlertRule, AlertHistory
from services.analytics_service import AnalyticsService
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class AlertingService:
    """Service for managing and sending alerts"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all enabled alert rules and trigger alerts if needed"""
        triggered = []
        
        try:
            rules = self.db.query(AlertRule).filter(
                AlertRule.enabled == True
            ).all()
            
            for rule in rules:
                try:
                    metric_value = self._get_metric_value(rule.metric_type)
                    
                    if metric_value is None:
                        continue
                    
                    should_alert = self._evaluate_condition(
                        metric_value,
                        rule.threshold,
                        rule.condition
                    )
                    
                    if should_alert:
                        # Check if we've already sent an alert recently (within last hour)
                        recent_alert = self.db.query(AlertHistory).filter(
                            and_(
                                AlertHistory.rule_id == rule.id,
                                AlertHistory.triggered_at >= datetime.utcnow() - timedelta(hours=1),
                                AlertHistory.sent == True
                            )
                        ).first()
                        
                        if not recent_alert:
                            # Trigger alert
                            message = f"Alert: {rule.rule_name}\n\n"
                            message += f"Metric: {rule.metric_type}\n"
                            message += f"Current Value: {metric_value}\n"
                            message += f"Threshold: {rule.condition} {rule.threshold}\n"
                            message += f"Time: {datetime.utcnow().isoformat()}\n"
                            
                            alert_sent = False
                            for channel in (rule.channels or ['email']):
                                if channel == 'email':
                                    alert_sent = self._send_email_alert(rule.rule_name, message)
                                # Add other channels here (Slack, Telegram, etc.)
                            
                            # Log alert history
                            alert_history = AlertHistory(
                                rule_id=rule.id,
                                metric_value=metric_value,
                                message=message,
                                channel=rule.channels[0] if rule.channels else 'email',
                                sent=alert_sent,
                                sent_at=datetime.utcnow() if alert_sent else None
                            )
                            self.db.add(alert_history)
                            self.db.commit()
                            
                            triggered.append({
                                "rule_id": rule.id,
                                "rule_name": rule.rule_name,
                                "metric_type": rule.metric_type,
                                "metric_value": float(metric_value),
                                "threshold": float(rule.threshold),
                                "sent": alert_sent
                            })
                except Exception as e:
                    logger.error(f"Error checking alert rule {rule.id}: {e}", exc_info=True)
                    continue
            
            return triggered
        except Exception as e:
            logger.error(f"Error checking alerts: {e}", exc_info=True)
            return []
    
    def _get_metric_value(self, metric_type: str) -> Optional[float]:
        """Get current value for a metric type"""
        try:
            if metric_type == "cpu_percent":
                infra = self.analytics_service.get_infrastructure_metrics(hours=1)
                return infra.get("cpu_avg", 0)
            
            elif metric_type == "ram_percent":
                infra = self.analytics_service.get_infrastructure_metrics(hours=1)
                return infra.get("ram_avg", 0)
            
            elif metric_type == "disk_percent":
                infra = self.analytics_service.get_infrastructure_metrics(hours=1)
                return infra.get("disk_avg", 0)
            
            elif metric_type == "error_rate":
                perf = self.analytics_service.get_api_performance(hours=1)
                return perf.get("error_rate", 0)
            
            elif metric_type == "response_time":
                perf = self.analytics_service.get_api_performance(hours=1)
                return perf.get("avg_response_time", 0)
            
            elif metric_type == "uptime":
                uptime = self.analytics_service.get_uptime_metrics(days=1)
                return uptime.get("uptime_percent", 100)
            
            return None
        except Exception as e:
            logger.error(f"Error getting metric value for {metric_type}: {e}")
            return None
    
    def _evaluate_condition(self, value: float, threshold: float, condition: str) -> bool:
        """Evaluate if condition is met"""
        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "equals":
            return abs(value - threshold) < 0.01
        return False
    
    def _send_email_alert(self, subject: str, message: str) -> bool:
        """Send email alert with input sanitization"""
        try:
            if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
                logger.warning("SMTP not configured, cannot send email alert")
                return False
            
            to_emails = settings.get_smtp_to_emails()
            if not to_emails:
                logger.warning("No recipient emails configured")
                return False
            
            # Sanitize subject and message to prevent injection
            from utils.input_sanitizer import sanitize_string
            subject = sanitize_string(subject, max_length=200)
            message = sanitize_string(message, max_length=5000)
            
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM_EMAIL
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"ZedReq Alert: {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {subject}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email alert: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email alert: {e}", exc_info=True)
            return False
    
    def create_alert_rule(
        self,
        rule_name: str,
        metric_type: str,
        threshold: float,
        condition: str,
        enabled: bool = True,
        channels: List[str] = None
    ) -> AlertRule:
        """Create a new alert rule"""
        try:
            rule = AlertRule(
                rule_name=rule_name,
                metric_type=metric_type,
                threshold=threshold,
                condition=condition,
                enabled=enabled,
                channels=channels or ['email']
            )
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            return rule
        except Exception as e:
            logger.error(f"Error creating alert rule: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    def get_alert_history(
        self,
        rule_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get alert history"""
        try:
            query = self.db.query(AlertHistory)
            
            if rule_id:
                query = query.filter(AlertHistory.rule_id == rule_id)
            
            alerts = query.order_by(AlertHistory.triggered_at.desc()).limit(limit).all()
            
            return [alert.to_dict() for alert in alerts]
        except Exception as e:
            logger.error(f"Error getting alert history: {e}", exc_info=True)
            return []
