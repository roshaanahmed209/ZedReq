"""
Shared realistic seeding: full profiles, LinkedIn-style posts, dense connections, optional image downloads.

Profile/cover URLs must stay https — the app validates http(s) only. We optionally mirror files under seed_data/assets/
for your own hosting later; the DB still stores the public https URLs.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = SCRIPT_DIR.parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent.resolve()

ASSETS_DIR = SCRIPT_DIR / "assets"

# Stable https avatars (deterministic look per username hash — not randomuser rotation)
def avatar_url(seed: str, size: int = 256) -> str:
    """Stable headshot-style URL per username (randomuser.me portraits, https)."""
    h = int(hashlib.md5(seed.encode("utf-8"), usedforsecurity=False).hexdigest(), 16)
    leg = "women" if h % 2 == 0 else "men"
    n = (h % 99) + 1
    return f"https://randomuser.me/api/portraits/{leg}/{n}.jpg"

# Unsplash direct (license-friendly); distinct moods for covers
COVER_URLS = [
    "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=85",
    "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1600&q=85",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=85",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1600&q=85",
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1600&q=85",
    "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=1600&q=85",
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1600&q=85",
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=85",
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1600&q=85",
    "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1600&q=85",
]

POST_MEDIA_URLS = [
    ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "image"),
    ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80", "image"),
    ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&q=80", "image"),
    ("https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1200&q=80", "image"),
    ("https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200&q=80", "image"),
    ("https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1200&q=80", "image"),
]

# Text-only LinkedIn cadence: personal moments, advice, mundane wins, questions
TEXT_POST_POOL: list[str] = [
    "Coffee with a former teammate this morning — we talked more about kids and sleep schedules than work. Still valuable.",
    "If you're job searching: send the thank-you note. It doesn't guarantee anything, but people remember courtesy.",
    "Rough week. Logging off early today. The deck will still be there Monday.",
    "Reminder: your calendar doesn't have to look like a game of Tetris to prove you're productive.",
    "Read something yesterday that stuck with me — 'competence builds confidence faster than the reverse.' Still thinking about it.",
    "Shoutout to whoever fixed the flaky CI job. You saved the team a lot of collective sighing.",
    "Three things that helped me this quarter: a paper notebook, saying no once a week, and one walk without a podcast.",
    "Not every meeting needs slides. Sometimes a doc link and 25 minutes is enough.",
    "Parent-teacher night ran long. Grateful for managers who don't ping after 7 unless it's urgent.",
    "If you're early career and afraid to ask questions — ask. The senior people who judge you for it aren't the ones you want to learn from anyway.",
    "Took PTO for a long weekend. Phone stayed in a drawer. Highly recommend.",
    "We shipped something small this week that only internal teams see. Still proud — it removes a daily annoyance for ~200 people.",
    "Hot take: most 'urgent' emails aren't urgent tomorrow morning either.",
    "Volunteered at a resume workshop last Saturday. Met someone switching careers at 41. Rooting for them hard.",
    "My dog learned nothing new this week but looked supportive during standup. Good enough.",
    "Budget season is messy. If you're in finance adjacent roles — solidarity.",
    "Learned that our vendor contract auto-renews in Q4. Added a calendar reminder 60 days out. Future me says thanks.",
    "Grateful post: a colleague covered for me when daycare called. Team culture shows up in moments like that.",
    "Trying to leave Slack statuses honest — 'focused' actually means focused.",
    "If you manage people: tell them what you appreciated specifically, not just 'good job.'",
    "Rain delay on my commute meant I finally listened to that podcast episode everyone recommended. Worth it.",
    "Year-end reflection — I said 'I don't know' more often this year and things got better, not worse.",
    "Someone on the team proposed we cancel a recurring meeting nobody needed. Hero behavior.",
    "Working from the kitchen table today because the office AC sounds like a helicopter. Small joys.",
    "Posted a dumb question in the internal forum and got three helpful answers in an hour. Culture matters.",
    "If you're writing specs: one clear example beats five paragraphs of theory.",
    "Took a mentee for lunch (their pick, cheap place). They asked better questions than some VPs I've met.",
    "Deadlines slip. How you communicate the slip is what people remember.",
    "Signed up for a night class. Nervous and excited in equal measure.",
    "We lost a bid. Debrief was blame-free and focused on what we'd change next time. That's how you keep good people.",
    "Trying to reply to emails in under 24h even when the answer is 'I'll get back to you Tuesday.'",
    "My plant survived six months. This is not a metaphor. I'm just happy.",
    "Conference hallway conversations > half the sessions. Fight me (politely).",
    "If onboarding docs are outdated, fix one page this week. Compound interest.",
    "Said no to a project that stretched us too thin. Hard conversation. Right call.",
    "Bike commute resumed — forgot how much clearer my head feels afterward.",
    "Celebrated a teammate's promotion properly. Lifts the whole floor.",
    "Writing this while waiting for a build. Classic.",
    "Therapy isn't a career strategy but it helps my judgment at work. Normalize it.",
    "We whiteboarded for 20 minutes and solved what email couldn't in two weeks.",
    "Snow day = kids home = meeting on mute with occasional chaos. Thanks for grace, team.",
    "Reminder to file expenses before finance chases you. Speaking for a friend.",
    "Good 1:1s end with one clear next step. Everything else is a nice chat.",
    "Industry news is loud this week. Stepping back to focus on customers and teammates.",
    "Left work on time twice this week. Trying to make it a habit.",
    "If you're hiring: speed matters. Good candidates have options.",
    "Backup your stuff. Learned the annoying way last year. You're welcome.",
    "Quietly fixed a typo in the wiki that confused new hires for months. Felt good.",
    "Networking doesn't have to mean events — sometimes it's one thoughtful DM.",
    "Grateful for a boss who asks 'what do you need from me' and listens.",
    "End of quarter always feels like a sprint. Hydrate and eat something green. Or don't — I'm not your mom.",
    "Someone thanked me in public for help I barely remembered giving. Be that person when you can.",
    "Trying to read one non-work book a month. January: done. February: optimistic.",
    "If the meeting could be an email, send the email. Revolutionary, I know.",
    "Our ERG hosted a talk on financial wellness. Packed room. People are hungry for practical support.",
    "Small win: cleared inbox to zero for exactly eleven minutes.",
    "Mentor told me to document decisions, not just outcomes. Game changer for reviews.",
    "Weekend hike cleared my head. Back Monday with slightly fewer sharp edges.",
    "Apologized for a curt message. Relationship repair > being technically right.",
    "New hire asked why we do something a certain way. Good question — we updated the doc.",
    "Burnout isn't a badge. Rest is part of the job.",
    "Celebrated a vendor who actually hit a deadline. Positive reinforcement works on adults too.",
    "Trying 'no meeting Wednesdays.' Week one: partial success. Still calling it a win.",
    "If you're presenting: rehearse once out loud. Catches awkward transitions every time.",
    "Team lunch was awkward at first, then someone mentioned cats. Instant bonding.",
    "Reflecting on a mistake from last month. Owning it openly built more trust than hiding it would have.",
    "Coffee machine broke. Minor crisis. We survived.",
    "Posted an internal job opening — please share with anyone who's been on the fence about applying.",
    "Grateful the office has decent headphones. Open floor plans need diplomacy.",
    "Sometimes the right answer is 'let's sleep on it.'",
    "Helped someone prep for an interview at another company. Rooting for them even if we lose a great person.",
    "Quarterly planning is messy. Clear priorities > long wishlists.",
    "Trying to leave Slack threads with a summary when I close a topic. Small courtesy.",
    "If you work remotely: change rooms once a day. Sounds silly, helps focus.",
    "Acknowledged a mistake in a group channel. The relief in the replies was visible.",
    "Good feedback is specific and timely. Vague praise feels hollow.",
    "Weekend project: organized home office cables. Monday me is already calmer.",
    "We debated a feature for weeks. User research settled it in 45 minutes.",
    "Shoutout to IT for the quick laptop swap. Downtime under an hour.",
    "Trying not to schedule meetings before 9:30. Not everyone is a morning person.",
    "If you're stuck: talk to someone outside your team. Fresh eyes spot assumptions.",
    "Left a thank-you note for the cleaning crew. They keep the place humane.",
    "Sometimes progress is invisible. Document small wins for yourself.",
    "Negotiated a deadline instead of silently drowning. Should have done it sooner.",
    "Team retro was actually useful — we picked two experiments for next sprint.",
    "Rain + deadline day = mood. Still shipped.",
    "If onboarding buddy programs exist, volunteer. You learn as much as they do.",
    "Celebrated a quiet release — no drama, no rollback. Those count.",
    "Trying to batch email twice a day. Inbox anxiety down slightly.",
    "Good design is when nobody tweets about it because it just works.",
    "Someone brought donuts. Morale scientifically improved.",
    "If you're a manager reading this: block focus time on your calendar too. Model it.",
    "Wrote a doc instead of a meeting. Three people commented async. Efficient.",
    "Grateful for flexible hours on dentist day. Small policies matter.",
    "We had a hard customer conversation. Handled with empathy. Proud of the team.",
    "Trying one new recipe a week. Unrelated to work but brain needs variety.",
    "If you ghost candidates, they remember. Communicate even when it's a no.",
    "Sprint goal felt ambitious. We hit 80% and learned what to cut. Honest retro helped.",
    "Coffee chat turned into a referral for someone great. Network quietly.",
    "Sometimes the best productivity hack is closing the laptop.",
    "Documented a runbook after an incident. Future on-call you sends thanks.",
    "If you're senior: make space in meetings for quieter voices.",
    "Weekend: family, chores, zero Slack. Monday energy noticeably better.",
    "We simplified a form — completion rate jumped. Small UX wins compound.",
    "Trying to give feedback in person when it's nuanced. Tone gets lost in text.",
    "Applauded someone for pushing back on scope creep. Protect the team.",
    "If you're learning something new: find a buddy. Accountability helps.",
    "Office dog visited. Productivity questionable. Happiness improved.",
    "Reflected on what I'd tell myself five years ago: ask for help sooner.",
    "Good leaders say 'I don't know' and then find out.",
    "We celebrated a launch with bad pizza and genuine smiles. I'll take it.",
    "Trying to end days with a 2-line journal: one win, one tension. Patterns emerge.",
    "If your team is distributed: rotate meeting times. Fairness matters.",
    "Someone shared a failure story in all-hands. More of that, please.",
    "Hydrated. Stretched. Emailed. Adulting complete.",
    "Quarterly OKR check — we're green on two, yellow on one. Adjusting plan, not panicking.",
    "If you're new: over-communicate early. You can't read the room you don't know yet.",
    "Grateful for teammates who cover when life happens. Pay it forward.",
    "Trying 'walk and think' instead of 'stare at screen and panic.'",
    "We cut a feature nobody used. Data-backed decisions feel good.",
    "Someone asked for async updates before a meeting. Saved 20 minutes for everyone.",
    "If you're burned out: tell someone safe. Silence makes it heavier.",
    "Small team ritual: Friday wins thread. Cheesy but it lands.",
    "Negotiated scope with stakeholders. Everyone left aligned. Rare and nice.",
    "Trying to praise effort in public, critique in private. Still practicing.",
    "Backup worked when I needed it. Test restores, people.",
    "If you hire: write the job post like you're talking to one person.",
    "Community event this weekend — met neighbors I usually only nod at. Felt human.",
    "We improved error messages users actually see. Support tickets dropped. Obvious in hindsight.",
    "Trying one deep-work block daily. Phone in another room. Works half the time — still worth it.",
    "If you're leading a project: name a deputy. Bus factor is real.",
    "Grateful for clear writing. Saves meetings.",
    "End of thread: be kind to yourself this week.",
]

_desc_columns_cache: set[str] | None = None


def _get_desc_columns(db) -> set[str]:
    global _desc_columns_cache
    if _desc_columns_cache is not None:
        return _desc_columns_cache
    rows = db.fetch_all(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'description'
        """
    )
    _desc_columns_cache = {r["column_name"] for r in rows}
    return _desc_columns_cache


def _table_exists(db, name: str) -> bool:
    r = db.fetch_one(
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (name,),
    )
    return r is not None


def xp(
    title: str,
    company: str,
    location: str | None,
    start: str,
    end: str | None,
    current: bool,
    desc: str,
    emp: str = "Full-time",
) -> dict[str, Any]:
    return {
        "title": title,
        "company": company,
        "location": location,
        "start_date": start,
        "end_date": end,
        "is_current": current,
        "description": desc,
        "employment_type": emp,
    }


def edu(school: str, degree: str, field: str, sy: int, ey: int | None, **kw: Any) -> dict[str, Any]:
    return {
        "school": school,
        "degree": degree,
        "field_of_study": field,
        "start_year": sy,
        "end_year": ey,
        **kw,
    }


def proj(title: str, desc: str, url: str | None = None, tech: list[str] | None = None, **kw: Any) -> dict[str, Any]:
    return {
        "title": title,
        "description": desc,
        "url": url,
        "technologies": tech or [],
        **kw,
    }


def intr(name: str, t: str = "personal", url: str | None = None) -> dict[str, Any]:
    return {"name": name, "type": t, "url": url}


def ensure_asset_dirs() -> Path:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    return ASSETS_DIR


def download_to_assets(url: str, dest: Path, timeout: int = 25) -> bool:
    """Save a copy under assets/ (optional). DB still uses https URL."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = Request(url, headers={"User-Agent": "ZedReqSeed/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return True
    except (URLError, HTTPError, OSError, ValueError) as e:
        print(f"    [SKIP] download {dest.name}: {e}")
        return False


def mirror_user_images(user: dict, username: str, download: bool) -> None:
    if not download:
        return
    ensure_asset_dirs()
    base = ASSETS_DIR / username.replace("/", "_")
    pp = user.get("profile_pic")
    cp = user.get("cover_pic")
    if pp and pp.startswith("http"):
        ext = ".jpg" if "jpg" in pp.lower() or "jpeg" in pp.lower() else ".png"
        download_to_assets(pp, base / f"avatar{ext}")
    if cp and cp.startswith("http"):
        download_to_assets(cp, base / "cover.jpg")
    time.sleep(0.15)  # be polite to image hosts


def seed_user(
    db,
    user: dict,
    hash_password_fn: Callable[[str], str],
) -> tuple[int, int] | None:
    try:
        desc = db.execute_returning(
            """INSERT INTO description
               (short_desc, about, certificates, skills, current_status, profile_pic, cover_pic)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING desc_id""",
            (
                user["short_desc"],
                user["about"],
                user.get("certificates", ""),
                user["skills"],
                user["current_status"],
                user["profile_pic"],
                user["cover_pic"],
            ),
        )
        if not desc:
            print(f"  [WARN] Could not create description for {user['name']}")
            return None
        desc_id = desc["desc_id"]

        cols = _get_desc_columns(db)
        updates: list[str] = []
        params: list[Any] = []
        mapping = [
            ("location", user.get("location")),
            ("city", user.get("city")),
            ("country", user.get("country")),
            ("role", user.get("title")),
            ("company", user.get("company")),
            ("industry", user.get("industry")),
        ]
        for col, val in mapping:
            if val and col in cols:
                updates.append(f"{col} = %s")
                params.append(val)
        if updates:
            params.append(desc_id)
            db.execute(
                f"UPDATE description SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE desc_id = %s",
                tuple(params),
            )

        result = db.execute_returning(
            """INSERT INTO users
               (username, name, user_email, password_hash, email_verified, description_id)
               VALUES (%s, %s, %s, %s, TRUE, %s)
               ON CONFLICT (username) DO NOTHING
               RETURNING uid""",
            (
                user["username"],
                user["name"],
                user["email"],
                hash_password_fn(user["password"]),
                desc_id,
            ),
        )
        if not result:
            existing = db.fetch_one(
                "SELECT uid FROM users WHERE username = %s", (user["username"],)
            )
            if existing:
                uid = existing["uid"]
                print(f"  [SKIP] User already exists: {user['username']} (uid {uid})")
                return uid, desc_id
            return None

        uid = result["uid"]
        print(f"  [OK]   Created {user['name']} (@{user['username']}) → uid {uid}")
        return uid, desc_id

    except Exception as e:
        print(f"  [ERR]  {user['name']}: {e}")
        return None


def seed_profile_satellites(db, uid: int, user: dict) -> None:
    """Experience, education, projects, interests — best-effort if tables exist."""
    for exp in user.get("experience") or []:
        if not _table_exists(db, "user_experience"):
            break
        try:
            db.execute(
                """INSERT INTO user_experience
                   (user_id, title, company, location, start_date, end_date, is_current, description, employment_type)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    uid,
                    exp["title"],
                    exp["company"],
                    exp.get("location"),
                    exp["start_date"],
                    exp.get("end_date"),
                    exp.get("is_current", False),
                    exp.get("description", ""),
                    exp.get("employment_type", "Full-time"),
                ),
            )
        except Exception as e:
            print(f"    [WARN] experience: {e}")

    for edu in user.get("education") or []:
        if not _table_exists(db, "user_education"):
            break
        try:
            db.execute(
                """INSERT INTO user_education
                   (user_id, school, degree, field_of_study, start_year, end_year, grade, activities, description)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    uid,
                    edu["school"],
                    edu.get("degree"),
                    edu.get("field_of_study"),
                    edu.get("start_year"),
                    edu.get("end_year"),
                    edu.get("grade"),
                    edu.get("activities"),
                    edu.get("description", ""),
                ),
            )
        except Exception as e:
            print(f"    [WARN] education: {e}")

    for proj in user.get("projects") or []:
        if not _table_exists(db, "user_projects"):
            break
        try:
            tech = proj.get("technologies")
            if isinstance(tech, list):
                tech_json = json.dumps(tech)
            else:
                tech_json = tech if isinstance(tech, str) else "[]"
            db.execute(
                """INSERT INTO user_projects
                   (user_id, title, description, url, start_date, end_date, associated_with, technologies)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)""",
                (
                    uid,
                    proj["title"],
                    proj.get("description", ""),
                    proj.get("url"),
                    proj.get("start_date"),
                    proj.get("end_date"),
                    proj.get("associated_with"),
                    tech_json,
                ),
            )
        except Exception as e:
            print(f"    [WARN] project: {e}")

    for intr in user.get("interests") or []:
        if not _table_exists(db, "user_interests"):
            break
        try:
            db.execute(
                """INSERT INTO user_interests (user_id, interest_type, name, url)
                   VALUES (%s, %s, %s, %s)""",
                (uid, intr.get("type", "personal"), intr["name"], intr.get("url")),
            )
        except Exception as e:
            print(f"    [WARN] interest: {e}")


def seed_network(db, uid: int) -> None:
    try:
        db.execute(
            "INSERT INTO network (uid, num_connections) VALUES (%s, 0) ON CONFLICT DO NOTHING",
            (uid,),
        )
    except Exception as e:
        print(f"  [WARN] network for uid {uid}: {e}")


def build_augmented_posts(
    username: str,
    base_posts: list[dict],
    rng: random.Random,
    extra_text_min: int = 3,
    extra_text_max: int = 6,
    image_probability: float = 0.28,
) -> list[dict]:
    """Merge curated posts with random text-only (and some image) posts from pools."""
    pool = [p for p in TEXT_POST_POOL if p]
    rng.shuffle(pool)
    n_extra = rng.randint(extra_text_min, extra_text_max)
    extra: list[dict] = []
    for i in range(min(n_extra, len(pool))):
        text = pool[i]
        use_img = rng.random() < image_probability
        extra.append(
            {
                "text": text,
                "image": rng.choice(POST_MEDIA_URLS) if use_img else None,
            }
        )
    merged = list(base_posts) + extra
    rng.shuffle(merged)
    return merged


def seed_posts_for_user(
    db,
    uid: int,
    username: str,
    posts: list[dict],
    rng: random.Random,
) -> int:
    n = 0
    for p in posts:
        try:
            media_url, media_type = (None, None)
            if p.get("image"):
                media_url, media_type = p["image"]
            likes = rng.randint(5, 1800)
            comments = rng.randint(0, 210)
            days_ago = rng.randint(0, 120)
            hours_ago = rng.randint(0, 23)
            created = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            db.execute(
                """INSERT INTO post (uid, post_desc, media_url, media_type, likes, comments, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (uid, p["text"], media_url, media_type, likes, comments, created, created),
            )
            n += 1
        except Exception as e:
            print(f"  [WARN] post for @{username}: {e}")
    return n


def reset_network_counts(db, uid_map: dict[str, int]) -> None:
    for uid in uid_map.values():
        try:
            db.execute("UPDATE network SET num_connections = 0 WHERE uid = %s", (uid,))
        except Exception:
            pass


def seed_connections_dense(db, uid_map: dict[str, int], rng: random.Random) -> None:
    """Each user follows several others; rebuilds counts from scratch."""
    usernames = list(uid_map.keys())
    if len(usernames) < 2:
        return
    reset_network_counts(db, uid_map)
    for username, uid in uid_map.items():
        others = [u for u in usernames if u != username]
        k = min(rng.randint(5, min(12, len(others) + 4)), len(others))
        to_follow = rng.sample(others, k) if k else []
        for target in to_follow:
            target_uid = uid_map[target]
            try:
                db.execute(
                    """INSERT INTO connections (follower_uid, followed_uid)
                       VALUES (%s, %s) ON CONFLICT DO NOTHING""",
                    (uid, target_uid),
                )
                db.execute(
                    "UPDATE network SET num_connections = num_connections + 1 WHERE uid = %s",
                    (target_uid,),
                )
            except Exception:
                pass
        # occasional mutual
        if rng.random() < 0.35 and to_follow:
            back = rng.choice(to_follow)
            buid, tuid = uid_map[back], uid
            try:
                db.execute(
                    """INSERT INTO connections (follower_uid, followed_uid)
                       VALUES (%s, %s) ON CONFLICT DO NOTHING""",
                    (buid, tuid),
                )
                db.execute(
                    "UPDATE network SET num_connections = num_connections + 1 WHERE uid = %s",
                    (tuid,),
                )
            except Exception:
                pass


def assign_profile_images(users: list[dict], rng: random.Random) -> None:
    """Set https avatar + cover per user if missing."""
    covers = COVER_URLS[:]
    rng.shuffle(covers)
    for i, u in enumerate(users):
        if not u.get("profile_pic"):
            u["profile_pic"] = avatar_url(u["username"])
        if not u.get("cover_pic"):
            u["cover_pic"] = covers[i % len(covers)]


def run_full_seed(
    users: list[dict],
    posts_by_username: dict[str, list[dict]],
    *,
    hash_password_fn: Callable[[str], str],
    get_db_fn: Callable,
    seed: int | None = None,
    download_images: bool = True,
    augment_posts: bool = True,
    post_builder: Callable[[str, list[dict], random.Random], list[dict]] | None = None,
) -> None:
    """
    Seed all users, profile satellites, posts, and cross-user connections.
    """
    rng = random.Random(seed if seed is not None else int(time.time()) % 2**32)
    assign_profile_images(users, rng)

    db = get_db_fn()
    uid_map: dict[str, int] = {}

    print("\n── Users & profiles ───────────────────────────────────────────")
    for user in users:
        mirror_user_images(user, user["username"], download_images)
        result = seed_user(db, user, hash_password_fn)
        if not result:
            continue
        uid, _ = result
        uid_map[user["username"]] = uid
        seed_network(db, uid)
        seed_profile_satellites(db, uid, user)

    print("\n── Posts ──────────────────────────────────────────────────────")
    for user in users:
        uid = uid_map.get(user["username"])
        if uid is None:
            continue
        base = posts_by_username.get(user["username"], [])
        if post_builder:
            final_posts = post_builder(user["username"], base, rng)
        elif augment_posts:
            final_posts = build_augmented_posts(user["username"], base, rng)
        else:
            final_posts = base
        n = seed_posts_for_user(db, uid, user["username"], final_posts, rng)
        print(f"  [OK]   {n} posts for @{user['username']}")

    print("\n── Connections (all seeded users) ───────────────────────────")
    seed_connections_dense(db, uid_map, rng)
    print(f"  [OK]   Graph among {len(uid_map)} users")

    db.close()

    print("\n" + "=" * 65)
    print(f"  Done. {len(uid_map)} users in database (this run).")
    print("  Logins (passwords unchanged from seed data):")
    for u in users:
        if u["username"] in uid_map:
            print(f"    {u['email']:40}  {u['password']}")
    print("=" * 65)


def get_db_default():
    sys.path.insert(0, str(BACKEND_DIR))
    from config.database import get_connection_params, Database

    return Database(get_connection_params())
