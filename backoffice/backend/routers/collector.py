"""Collector API Router - Receives metrics and events from main app and frontend"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import re
import hmac

from dependencies.database import get_db
from config.settings import settings
from models.orm import (
    APIMetric, UserSession, PageView, LinkClick, UserInteraction, ErrorLog, SecurityEvent
)
from utils.input_sanitizer import sanitize_string, validate_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/collect", tags=["Collector"])

# Valid HTTP methods
VALID_HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}

# Valid severity levels
VALID_SEVERITY_LEVELS = {"low", "medium", "high", "critical", "error", "warning", "info"}


def verify_collector_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify collector API key - FAIL SECURE (deny if not configured)"""
    if not settings.COLLECTOR_API_KEY:
        logger.error("COLLECTOR_API_KEY not configured - denying access for security")
        raise HTTPException(
            status_code=503,
            detail="Collector API is not configured. Contact administrator."
        )
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Timing-safe comparison to prevent timing attacks
    if not hmac.compare_digest(x_api_key, settings.COLLECTOR_API_KEY):
        logger.warning(f"Invalid API key attempt from {Request.client.host if hasattr(Request, 'client') else 'unknown'}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True


def validate_ip_address(ip: Optional[str]) -> Optional[str]:
    """Validate IP address format"""
    if not ip:
        return None
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    # IPv6 pattern (simplified)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$'
    
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return ip
    elif re.match(ipv6_pattern, ip):
        return ip
    
    logger.warning(f"Invalid IP address format: {ip}")
    return None


# Request Models
class APIMetricRequest(BaseModel):
    endpoint: str = Field(..., max_length=500, description="API endpoint path")
    method: str = Field(..., max_length=10, description="HTTP method")
    status_code: int = Field(..., ge=100, le=599, description="HTTP status code")
    response_time_ms: int = Field(..., ge=0, le=300000, description="Response time in milliseconds")
    user_id: Optional[int] = Field(None, ge=1, description="User ID")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address")
    user_agent: Optional[str] = Field(None, max_length=500, description="User agent string")
    error_message: Optional[str] = Field(None, max_length=2000, description="Error message")
    
    @validator('method')
    def validate_method(cls, v):
        v = v.upper().strip()
        if v not in VALID_HTTP_METHODS:
            raise ValueError(f"Invalid HTTP method: {v}")
        return v
    
    @validator('endpoint')
    def validate_endpoint(cls, v):
        v = sanitize_string(v, max_length=500)
        # Prevent path traversal
        if '..' in v or v.startswith('/'):
            v = v.lstrip('/')
        return v
    
    @validator('ip_address')
    def validate_ip(cls, v):
        if v:
            if not validate_ip(v):
                raise ValueError("Invalid IP address format")
            return v
        return v
    
    @validator('user_agent', 'error_message')
    def sanitize_strings(cls, v):
        if v:
            return sanitize_string(v, max_length=500 if 'user_agent' in str(cls.__fields__) else 2000)
        return v


class PageViewRequest(BaseModel):
    user_id: Optional[int] = Field(None, ge=1, description="User ID")
    session_id: str = Field(..., min_length=1, max_length=255, description="Session ID")
    page_path: str = Field(..., max_length=500, description="Page path")
    page_title: Optional[str] = Field(None, max_length=255, description="Page title")
    referrer: Optional[str] = Field(None, max_length=500, description="Referrer URL")
    load_time_ms: Optional[int] = Field(None, ge=0, le=300000, description="Page load time in milliseconds")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        # Session ID should be alphanumeric with some special chars
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid session ID format")
        return sanitize_string(v, max_length=255)
    
    @validator('page_path', 'page_title', 'referrer')
    def sanitize_paths(cls, v):
        if v:
            max_len = 500 if 'page_path' in str(cls.__fields__) or 'referrer' in str(cls.__fields__) else 255
            return sanitize_string(v, max_length=max_len)
        return v


class LinkClickRequest(BaseModel):
    user_id: Optional[int] = Field(None, ge=1, description="User ID")
    session_id: str = Field(..., min_length=1, max_length=255, description="Session ID")
    link_url: str = Field(..., max_length=1000, description="Link URL")
    link_text: Optional[str] = Field(None, max_length=500, description="Link text")
    page_path: Optional[str] = Field(None, max_length=500, description="Page path")
    is_external: bool = Field(False, description="Is external link")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid session ID format")
        return sanitize_string(v, max_length=255)
    
    @validator('link_url')
    def validate_link_url(cls, v):
        v = sanitize_string(v, max_length=1000)
        # Basic URL validation (allow relative URLs for internal links)
        if v.startswith(('http://', 'https://')):
            if not validate_url(v):
                raise ValueError("Invalid or unsafe URL")
        elif not v.startswith('/') and not v.startswith('#'):
            # Relative URLs should start with / or #
            raise ValueError("Invalid URL format")
        return v
    
    @validator('link_text', 'page_path')
    def sanitize_strings(cls, v):
        if v:
            return sanitize_string(v, max_length=500)
        return v


class UserInteractionRequest(BaseModel):
    user_id: Optional[int] = Field(None, ge=1, description="User ID")
    session_id: str = Field(..., min_length=1, max_length=255, description="Session ID")
    interaction_type: str = Field(..., max_length=50, description="Interaction type")
    element_id: Optional[str] = Field(None, max_length=255, description="Element ID")
    element_type: Optional[str] = Field(None, max_length=50, description="Element type")
    page_path: Optional[str] = Field(None, max_length=500, description="Page path")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid session ID format")
        return sanitize_string(v, max_length=255)
    
    @validator('interaction_type', 'element_type')
    def validate_types(cls, v):
        if v:
            # Allow alphanumeric, underscores, hyphens
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError("Invalid format: only alphanumeric, underscore, and hyphen allowed")
            return sanitize_string(v, max_length=50)
        return v
    
    @validator('element_id', 'page_path')
    def sanitize_strings(cls, v):
        if v:
            max_len = 255 if 'element_id' in str(cls.__fields__) else 500
            return sanitize_string(v, max_length=max_len)
        return v
    
    @validator('metadata')
    def sanitize_metadata(cls, v):
        if v and isinstance(v, dict):
            from utils.input_sanitizer import sanitize_dict
            return sanitize_dict(v, max_string_length=1000)
        return v


class ErrorLogRequest(BaseModel):
    error_type: str = Field(..., max_length=100, description="Error type")
    error_message: str = Field(..., max_length=2000, description="Error message")
    stack_trace: Optional[str] = Field(None, max_length=10000, description="Stack trace")
    endpoint: Optional[str] = Field(None, max_length=500, description="Endpoint")
    user_id: Optional[int] = Field(None, ge=1, description="User ID")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address")
    severity: str = Field("error", max_length=20, description="Severity level")
    
    @validator('severity')
    def validate_severity(cls, v):
        v = v.lower()
        if v not in VALID_SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity level. Must be one of: {VALID_SEVERITY_LEVELS}")
        return v
    
    @validator('error_type', 'error_message', 'stack_trace', 'endpoint')
    def sanitize_strings(cls, v):
        if v:
            max_len = 100 if 'error_type' in str(cls.__fields__) else (2000 if 'error_message' in str(cls.__fields__) else (10000 if 'stack_trace' in str(cls.__fields__) else 500))
            return sanitize_string(v, max_length=max_len)
        return v
    
    @validator('ip_address')
    def validate_ip(cls, v):
        if v:
            if not validate_ip(v):
                raise ValueError("Invalid IP address format")
            return v
        return v


class SecurityEventRequest(BaseModel):
    event_type: str = Field(..., max_length=50, description="Event type")
    user_id: Optional[int] = Field(None, ge=1, description="User ID")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address")
    user_agent: Optional[str] = Field(None, max_length=500, description="User agent")
    details: Optional[Dict[str, Any]] = Field(None, description="Event details")
    severity: str = Field("medium", max_length=20, description="Severity level")
    blocked: bool = Field(False, description="Was request blocked")
    
    @validator('severity')
    def validate_severity(cls, v):
        v = v.lower()
        if v not in VALID_SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity level. Must be one of: {VALID_SEVERITY_LEVELS}")
        return v
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid event type format")
        return sanitize_string(v, max_length=50)
    
    @validator('ip_address')
    def validate_ip(cls, v):
        if v:
            if not validate_ip(v):
                raise ValueError("Invalid IP address format")
            return v
        return v
    
    @validator('user_agent')
    def sanitize_user_agent(cls, v):
        if v:
            return sanitize_string(v, max_length=500)
        return v
    
    @validator('details')
    def sanitize_details(cls, v):
        if v and isinstance(v, dict):
            from utils.input_sanitizer import sanitize_dict
            return sanitize_dict(v, max_string_length=1000)
        return v


class SessionRequest(BaseModel):
    user_id: Optional[int] = Field(None, ge=1, description="User ID")
    session_id: str = Field(..., min_length=1, max_length=255, description="Session ID")
    device_type: Optional[str] = Field(None, max_length=50, description="Device type")
    browser: Optional[str] = Field(None, max_length=100, description="Browser")
    os: Optional[str] = Field(None, max_length=100, description="Operating system")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid session ID format")
        return sanitize_string(v, max_length=255)
    
    @validator('device_type', 'browser', 'os', 'country')
    def sanitize_strings(cls, v):
        if v:
            max_len = 50 if 'device_type' in str(cls.__fields__) else 100
            return sanitize_string(v, max_length=max_len)
        return v
    
    @validator('ip_address')
    def validate_ip(cls, v):
        if v:
            if not validate_ip(v):
                raise ValueError("Invalid IP address format")
            return v
        return v


@router.post("/metrics")
async def collect_metrics(
    metrics: List[APIMetricRequest],
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_collector_api_key)
):
    """Receive API metrics from main app"""
    try:
        # Limit batch size to prevent DoS
        if len(metrics) > 100:
            raise HTTPException(status_code=400, detail="Too many metrics in batch (max 100)")
        
        ip_address = validate_ip_address(request.client.host if request.client else None)
        
        for metric in metrics:
            api_metric = APIMetric(
                endpoint=metric.endpoint,
                method=metric.method,
                status_code=metric.status_code,
                response_time_ms=metric.response_time_ms,
                user_id=metric.user_id,
                ip_address=metric.ip_address or ip_address,
                user_agent=metric.user_agent,
                error_message=metric.error_message
            )
            db.add(api_metric)
        
        db.commit()
        return {"success": True, "count": len(metrics)}
    except Exception as e:
        db.rollback()
        logger.error(f"Error collecting metrics: {e}", exc_info=True)
        # Don't expose internal error details
        raise HTTPException(
            status_code=500,
            detail="Failed to process metrics. Please try again later."
        )


class EventRequest(BaseModel):
    """Validated event request model"""
    type: str = Field(..., max_length=50)
    user_id: Optional[int] = Field(None, ge=1)
    session_id: str = Field(..., min_length=1, max_length=255)
    page_path: Optional[str] = Field(None, max_length=500)
    page_title: Optional[str] = Field(None, max_length=255)
    referrer: Optional[str] = Field(None, max_length=500)
    load_time_ms: Optional[int] = Field(None, ge=0, le=300000)
    link_url: Optional[str] = Field(None, max_length=1000)
    link_text: Optional[str] = Field(None, max_length=500)
    is_external: Optional[bool] = False
    interaction_type: Optional[str] = Field(None, max_length=50)
    element_id: Optional[str] = Field(None, max_length=255)
    element_type: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = {"page_view", "link_click", "interaction"}
        if v not in valid_types:
            raise ValueError(f"Invalid event type. Must be one of: {valid_types}")
        return v
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid session ID format")
        return sanitize_string(v, max_length=255)


@router.post("/events")
async def collect_events(
    events: List[EventRequest],
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_collector_api_key)
):
    """Receive user events from frontend (page views, link clicks, interactions)"""
    try:
        ip_address = validate_ip_address(request.client.host if request.client else None)
        user_agent = request.headers.get("user-agent")
        if user_agent:
            user_agent = sanitize_string(user_agent, max_length=500)
        
        # Limit batch size to prevent DoS
        if len(events) > 100:
            raise HTTPException(status_code=400, detail="Too many events in batch (max 100)")
        
        for event in events:
            if event.type == "page_view":
                page_view = PageView(
                    user_id=event.user_id,
                    session_id=event.session_id,
                    page_path=sanitize_string(event.page_path or "", max_length=500),
                    page_title=sanitize_string(event.page_title or "", max_length=255) if event.page_title else None,
                    referrer=sanitize_string(event.referrer or "", max_length=500) if event.referrer else None,
                    load_time_ms=event.load_time_ms
                )
                db.add(page_view)
                
            elif event.type == "link_click":
                link_url = sanitize_string(event.link_url or "", max_length=1000)
                if link_url.startswith(('http://', 'https://')) and not validate_url(link_url):
                    logger.warning(f"Invalid URL in link click: {link_url}")
                    continue
                
                link_click = LinkClick(
                    user_id=event.user_id,
                    session_id=event.session_id,
                    link_url=link_url,
                    link_text=sanitize_string(event.link_text or "", max_length=500) if event.link_text else None,
                    page_path=sanitize_string(event.page_path or "", max_length=500) if event.page_path else None,
                    is_external=event.is_external or False
                )
                db.add(link_click)
                
            elif event.type == "interaction":
                interaction = UserInteraction(
                    user_id=event.user_id,
                    session_id=event.session_id,
                    interaction_type=sanitize_string(event.interaction_type or "", max_length=50),
                    element_id=sanitize_string(event.element_id or "", max_length=255) if event.element_id else None,
                    element_type=sanitize_string(event.element_type or "", max_length=50) if event.element_type else None,
                    page_path=sanitize_string(event.page_path or "", max_length=500) if event.page_path else None,
                    interaction_metadata=event.metadata
                )
                db.add(interaction)
        
        db.commit()
        return {"success": True, "count": len(events)}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error collecting events: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process events. Please try again later."
        )


@router.post("/errors")
async def collect_errors(
    errors: List[ErrorLogRequest],
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_collector_api_key)
):
    """Receive error logs from main app"""
    try:
        # Limit batch size to prevent DoS
        if len(errors) > 50:
            raise HTTPException(status_code=400, detail="Too many errors in batch (max 50)")
        
        ip_address = validate_ip_address(request.client.host if request.client else None)
        
        for error in errors:
            error_log = ErrorLog(
                error_type=error.error_type,
                error_message=error.error_message,
                stack_trace=error.stack_trace,
                endpoint=error.endpoint,
                user_id=error.user_id,
                ip_address=error.ip_address or ip_address,
                severity=error.severity
            )
            db.add(error_log)
        
        db.commit()
        return {"success": True, "count": len(errors)}
    except Exception as e:
        db.rollback()
        logger.error(f"Error collecting errors: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process error logs. Please try again later."
        )


@router.post("/security")
async def collect_security_events(
    events: List[SecurityEventRequest],
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_collector_api_key)
):
    """Receive security events from main app"""
    try:
        # Limit batch size to prevent DoS
        if len(events) > 50:
            raise HTTPException(status_code=400, detail="Too many security events in batch (max 50)")
        
        ip_address = validate_ip_address(request.client.host if request.client else None)
        user_agent = request.headers.get("user-agent")
        if user_agent:
            user_agent = sanitize_string(user_agent, max_length=500)
        
        for event in events:
            security_event = SecurityEvent(
                event_type=event.event_type,
                user_id=event.user_id,
                ip_address=event.ip_address or ip_address,
                user_agent=event.user_agent or user_agent,
                details=event.details,
                severity=event.severity,
                blocked=event.blocked
            )
            db.add(security_event)
        
        db.commit()
        return {"success": True, "count": len(events)}
    except Exception as e:
        db.rollback()
        logger.error(f"Error collecting security events: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process security events. Please try again later."
        )


@router.post("/session/start")
async def start_session(
    session_data: SessionRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_collector_api_key)
):
    """Start a new user session"""
    try:
        ip_address = session_data.ip_address or (request.client.host if request.client else None)
        
        # Check if session already exists
        existing = db.query(UserSession).filter(
            UserSession.session_id == session_data.session_id
        ).first()
        
        if existing:
            # Update last activity
            existing.last_activity = datetime.utcnow()
            db.commit()
            return {"success": True, "session_id": existing.session_id}
        
        session = UserSession(
            user_id=session_data.user_id,
            session_id=session_data.session_id,
            device_type=session_data.device_type,
            browser=session_data.browser,
            os=session_data.os,
            country=session_data.country,
            ip_address=ip_address
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {"success": True, "session_id": session.session_id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to start session. Please try again later."
        )


@router.post("/session/update")
async def update_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_collector_api_key)
):
    """Update session last activity"""
    try:
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            if hasattr(session, 'page_views'):
                session.page_views = (session.page_views or 0) + 1
            db.commit()
            return {"success": True}
        
        return {"success": False, "message": "Session not found"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update session. Please try again later."
        )


@router.post("/session/end")
async def end_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_collector_api_key)
):
    """End a user session"""
    try:
        # Validate and sanitize session_id
        if not session_id or len(session_id) > 255:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        session_id = sanitize_string(session_id, max_length=255)
        
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id
        ).first()
        
        if session:
            session.end_time = datetime.utcnow()
            if session.start_time:
                duration = (session.end_time - session.start_time).total_seconds()
                session.duration_seconds = int(duration)
            db.commit()
            return {"success": True}
        
        return {"success": False, "message": "Session not found"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error ending session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to end session. Please try again later."
        )
