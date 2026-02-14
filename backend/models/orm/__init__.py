"""SQLAlchemy ORM Models"""
# Import User first so other models can reference it
from .user import User
from .connection import Connection
from .connection_request import ConnectionRequest
from .notification import Notification
from .post import Post
from .like import Like
from .description import Description
from .job_posting import JobPosting
from .job_application import JobApplication
from .job_saved import JobSaved
from .live_interview import LiveInterview

# LMS ORM Models
from .lms_course import LMSCourse
from .lms_domain import LMSDomain
from .lms_course_section import LMSCourseSection
from .lms_course_resource import LMSCourseResource
from .lms_question import LMSQuestion
from .lms_user_course import LMSUserCourse
from .lms_user_section_progress import LMSUserSectionProgress
from .lms_user_answer import LMSUserAnswer
from .lms_user_domain_performance import LMSUserDomainPerformance
from .lms_user_course_performance import LMSUserCoursePerformance
from .lms_dashboard import LMSDashboard
from .lms_weekly_performance import LMSWeeklyPerformance
from .lms_activity import LMSActivity
from .lms_recommendation import LMSRecommendation
from .lms_deadline import LMSDeadline
from .lms_certificate import LMSCertificate
from .azel_search_url import AzelSearchUrl
from .reserved_seat import ReservedSeat

# Profile Feature Models
from .user_experience import UserExperience
from .user_education import UserEducation
from .user_project import UserProject
from .user_recommendation import UserRecommendation
from .user_interest import UserInterest
from .profile_analytics import ProfileAnalytics

__all__ = [
    'User',
    'Connection',
    'ConnectionRequest',
    'Notification',
    'Post',
    'Like',
    'Description',
    'JobPosting',
    'JobApplication', 
    'JobSaved',
    'LiveInterview',
    # LMS Models
    'LMSCourse',
    'LMSDomain',
    'LMSCourseSection',
    'LMSCourseResource',
    'LMSQuestion',
    'LMSUserCourse',
    'LMSUserSectionProgress',
    'LMSUserAnswer',
    'LMSUserDomainPerformance',
    'LMSUserCoursePerformance',
    'LMSDashboard',
    'LMSWeeklyPerformance',
    'LMSActivity',
    'LMSRecommendation',
    'LMSDeadline',
    'LMSCertificate',
    'AzelSearchUrl',
    'ReservedSeat',
    # Profile Feature Models
    'UserExperience',
    'UserEducation',
    'UserProject',
    'UserRecommendation',
    'UserInterest',
    'ProfileAnalytics',
]
