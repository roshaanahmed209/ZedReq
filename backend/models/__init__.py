# Core models
from .user import User
from .connection import Connection
from .connection_request import ConnectionRequest
from .notification import Notification
from .base import BaseModel

# Job Portal ORM models (SQLAlchemy)
from .orm import JobPosting, JobApplication, JobSaved

# Legacy models (for backwards compatibility)
from . import payment
from . import description
from . import job
from . import post
from . import like
from . import network

# LMS ORM models (SQLAlchemy)
from .orm import (
    LMSCourse, LMSDomain, LMSCourseSection, LMSCourseResource,
    LMSQuestion, LMSUserCourse, LMSUserSectionProgress, LMSUserAnswer,
    LMSUserDomainPerformance, LMSDashboard, LMSWeeklyPerformance,
    LMSActivity, LMSRecommendation, LMSDeadline, LMSCertificate
)

__all__ = [
    # Core
    'User', 'Connection', 'ConnectionRequest', 'Notification', 'BaseModel',
    # Job Portal
    'JobPosting', 'JobApplication', 'JobSaved',
    # Legacy
    'payment', 'description', 'job', 'post', 'like', 'network',
    # LMS ORM Models
    'LMSCourse', 'LMSDomain', 'LMSCourseSection', 'LMSCourseResource',
    'LMSQuestion', 'LMSUserCourse', 'LMSUserSectionProgress', 'LMSUserAnswer',
    'LMSUserDomainPerformance', 'LMSDashboard', 'LMSWeeklyPerformance',
    'LMSActivity', 'LMSRecommendation', 'LMSDeadline', 'LMSCertificate',
]
