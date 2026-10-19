"""
Server-side derivation of client context for analytics events.

Device, browser, OS and country are parsed here from request headers rather than
accepted from the browser. A client can lie about all of them, and a dashboard that
reports whatever JavaScript claimed is worth very little.

Deliberately dependency-free: a handful of substring checks covers the browsers and
platforms that matter, and adding a UA-parsing library for this would not earn its
place in the dependency tree.
"""
from typing import Dict, Optional

# Order matters: several browsers impersonate others in their UA string. Edge claims
# Chrome and Safari; Chrome claims Safari. Always test the most specific first.
_BROWSERS = [
    ("edg/", "Edge"),
    ("edga/", "Edge"),
    ("edgios/", "Edge"),
    ("opr/", "Opera"),
    ("opera", "Opera"),
    ("samsungbrowser", "Samsung Internet"),
    ("firefox/", "Firefox"),
    ("fxios/", "Firefox"),
    ("crios/", "Chrome"),
    ("chrome/", "Chrome"),
    ("chromium/", "Chrome"),
    ("safari/", "Safari"),
]

_OPERATING_SYSTEMS = [
    ("windows nt", "Windows"),
    ("android", "Android"),
    ("iphone", "iOS"),
    ("ipad", "iOS"),
    ("ipod", "iOS"),
    ("mac os x", "macOS"),
    ("macintosh", "macOS"),
    ("cros", "ChromeOS"),
    ("linux", "Linux"),
]

_BOT_MARKERS = (
    "bot",
    "crawler",
    "spider",
    "slurp",
    "headlesschrome",
    "phantomjs",
    "curl/",
    "wget/",
    "python-requests",
    "httpx/",
    "go-http-client",
    "lighthouse",
    "pingdom",
    "uptimerobot",
)

# CDN / proxy headers that carry a resolved country. Checked in order; the first hit
# wins. No GeoIP database is bundled, so if the deployment sits behind none of these
# the country is simply left unknown rather than guessed.
_COUNTRY_HEADERS = (
    "cf-ipcountry",           # Cloudflare
    "x-vercel-ip-country",    # Vercel
    "x-geo-country",
    "x-country-code",
    "cloudfront-viewer-country",
    "fastly-client-country",
)


def parse_user_agent(user_agent: Optional[str]) -> Dict[str, Optional[str]]:
    """Return ``device_type`` / ``browser`` / ``operating_system`` for a UA string."""
    if not user_agent:
        return {"device_type": None, "browser": None, "operating_system": None}

    ua = user_agent.lower()

    browser = next((name for needle, name in _BROWSERS if needle in ua), None)
    operating_system = next((name for needle, name in _OPERATING_SYSTEMS if needle in ua), None)

    if "ipad" in ua or ("tablet" in ua and "mobile" not in ua) or ("android" in ua and "mobile" not in ua):
        device_type = "tablet"
    elif any(marker in ua for marker in ("mobi", "iphone", "ipod", "android", "windows phone")):
        device_type = "mobile"
    else:
        device_type = "desktop"

    return {
        "device_type": device_type,
        "browser": browser,
        "operating_system": operating_system,
    }


def is_bot(user_agent: Optional[str]) -> bool:
    """
    True for obvious automated traffic.

    Bot page views would inflate every visitor count and every funnel denominator, so
    their events are dropped at ingest rather than filtered at query time.
    """
    if not user_agent:
        return False
    ua = user_agent.lower()
    return any(marker in ua for marker in _BOT_MARKERS)


def extract_country(headers) -> Optional[str]:
    """Read a two-letter country code from CDN headers, or None if unavailable."""
    for header in _COUNTRY_HEADERS:
        value = headers.get(header)
        if value:
            code = value.strip().upper()
            if len(code) == 2 and code.isalpha() and code != "XX":
                return code
    return None
