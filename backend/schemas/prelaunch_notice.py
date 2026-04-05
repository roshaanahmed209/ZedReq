from pydantic import BaseModel, Field, field_validator


PRELAUNCH_NOTICE_KEY = "prelaunch_notice"


class PrelaunchNoticePublic(BaseModel):
    """Shape returned to the main app (and accepted from admins on save)."""

    enabled: bool = True
    badge_label: str = Field(default="Pre-launch", max_length=80)
    title: str = Field(
        default="ZedReq is not officially live yet",
        max_length=220,
    )
    body: str = Field(
        default=(
            "You are using an early version of the product. Features and data may change, "
            "and you may occasionally run into bugs or rough edges. Thank you for trying "
            "ZedReq—we rely on your feedback to improve."
        ),
        max_length=4000,
    )
    bug_email: str = Field(default="zed.req@yahoo.com", max_length=255)
    primary_button_label: str = Field(default="Continue", max_length=60)
    secondary_button_label: str = Field(default="Email us", max_length=60)
    mailto_subject: str = Field(default="ZedReq bug report", max_length=200)

    @field_validator("bug_email")
    @classmethod
    def email_trim(cls, v: str) -> str:
        s = (v or "").strip()
        if not s or "@" not in s:
            raise ValueError("bug_email must look like an email address")
        return s[:255]
