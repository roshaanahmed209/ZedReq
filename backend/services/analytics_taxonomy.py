"""
Event taxonomy for ZedReq product analytics (main app copy).

Naming convention: ``object_action``, lower_snake_case - ``page_viewed``,
``cta_clicked``, ``signup_started``, ``mock_interview_completed``,
``payment_succeeded``. Never ``clickedCTA`` / ``CTA_Click`` / ``heroButtonPressed``.

Variants of one action are expressed as event *properties*, not as new event names:
there is a single ``cta_clicked`` with a ``cta_id``, not ``hero_cta_clicked`` plus
``navbar_cta_clicked`` plus ``footer_cta_clicked``.

This list mirrors
``zedreq_backoffice/backend/services/product_analytics_config.py``. The back office
is the enforcing side; this copy lets the main app reject junk before it crosses the
network. Keep the two in step when adding events.
"""

ACQUISITION_EVENTS = [
    "landing_page_viewed",
    "page_viewed",
    "cta_clicked",
    "referral_link_clicked",
]

AUTH_EVENTS = [
    "login_page_viewed",
    "login_started",
    "login_submitted",
    "login_succeeded",
    "login_failed",
    "signup_page_viewed",
    "signup_started",
    "signup_submitted",
    "signup_succeeded",
    "signup_failed",
    "signup_abandoned",
    "logout",
]

ONBOARDING_EVENTS = [
    "onboarding_started",
    "onboarding_step_viewed",
    "onboarding_step_completed",
    "onboarding_skipped",
    "onboarding_completed",
    "onboarding_abandoned",
]

INTERVIEW_EVENTS = [
    "mock_interview_viewed",
    "mock_interview_started",
    "mock_interview_question_answered",
    "mock_interview_completed",
    "mock_interview_abandoned",
    "mock_interview_feedback_viewed",
]

LMS_EVENTS = [
    "lms_viewed",
    "course_viewed",
    "course_enrolled",
    "lesson_started",
    "lesson_completed",
    "lesson_abandoned",
    "course_completed",
]

PRODUCT_EVENTS = [
    "feed_viewed",
    "jobs_viewed",
    "job_viewed",
    "job_applied",
    "job_saved",
    "ai_mode_viewed",
    "ai_mode_query_sent",
    "network_viewed",
    "profile_viewed",
    "connection_requested",
    "post_created",
]

BILLING_EVENTS = [
    "pricing_page_viewed",
    "pricing_plan_viewed",
    "upgrade_cta_clicked",
    "checkout_started",
    "checkout_abandoned",
    "payment_submitted",
    "payment_succeeded",
    "payment_failed",
    "subscription_started",
    "subscription_cancelled",
    "subscription_renewed",
    "subscription_upgraded",
    "subscription_downgraded",
]

LIFECYCLE_EVENTS = [
    "user_registered",
    "user_authenticated",
    "user_activated",
    "user_returned",
    "user_deactivated",
    "referral_signup",
    "referral_conversion",
]

ERROR_EVENTS = [
    "frontend_error",
    "api_error",
    "authentication_error",
    "payment_error",
    "feature_error",
]

EVENT_NAMES = frozenset(
    ACQUISITION_EVENTS
    + AUTH_EVENTS
    + ONBOARDING_EVENTS
    + INTERVIEW_EVENTS
    + LMS_EVENTS
    + PRODUCT_EVENTS
    + BILLING_EVENTS
    + LIFECYCLE_EVENTS
    + ERROR_EVENTS
)

# Events a browser may not assert. These carry business meaning (a conversion, a
# payment, an activation) and are only accepted when emitted by trusted backend code,
# so a crafted request cannot invent paying customers in the dashboard.
SERVER_ONLY_EVENTS = frozenset(
    {
        "signup_succeeded",
        "login_succeeded",
        "user_registered",
        "user_authenticated",
        "user_activated",
        "payment_succeeded",
        "subscription_started",
        "subscription_cancelled",
        "subscription_renewed",
        "subscription_upgraded",
        "subscription_downgraded",
        "referral_conversion",
    }
)
