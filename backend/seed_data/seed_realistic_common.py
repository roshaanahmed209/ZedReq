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

# Long-form LinkedIn-style narratives (original copy): situation → tension → what we did → outcome / lesson.
# Augmentation adds fewer of these per user because each post is lengthy.
TEXT_POST_POOL: list[str] = [
    """Two Tuesdays ago, our checkout API started returning intermittent 503s during lunch rush. Nothing had shipped that morning — or so we thought.

I pulled three of us into a war room: on-call, the engineer who last touched caching, and a product partner so we didn't optimize for the wrong thing. For the first hour we chased ghosts: one dashboard said CPU was fine, another hinted at connection pool exhaustion. We stopped guessing and reproduced traffic in staging with the same feature flags as prod.

What actually happened: a background job had started holding DB connections longer after a config tweak the night before. Under combined load, the API tier starved. We rolled back the config, added a guardrail alert on pool wait time, and wrote a two-page incident note the same day.

What I'm proud of isn't the fix — it's that nobody threw blame across teams. We named the gap in our change process and added a 24h soak checklist for pool-related settings.

If you're running a similar stack: watch connection wait metrics as closely as you watch CPU. The failure mode hides until it's expensive.""",
    """I used to think the best 1:1s were the ones where my report walked away inspired. I've changed my mind.

Last month one of my engineers seemed off — quieter in standup, slower on reviews. I almost sent a generic 'how can I help' message. Instead I blocked 45 minutes, turned my camera on, and asked one specific question: 'What's eating the most mental energy right now?'

They talked about a parent in hospital and unrealistic deadlines on a side project with another team. We didn't solve everything in one conversation. We did agree on three concrete changes: I escalated the cross-team pressure, we shifted one deadline, and they took a day of PTO without guilt.

The lesson for me: inspiration is cheap; clarity and follow-through are respect. If you're a manager, try swapping one motivational speech for one boring, specific problem you remove from someone's plate.""",
    """I interviewed for a senior role last quarter and walked out genuinely surprised — not by the algorithms, but by how much time we spent on how I'd debug a model that looked good offline and failed in production.

The panel asked about leakage, delayed labels, and how I'd communicate uncertainty to non-technical stakeholders. I had prepared LeetCode; I should have prepared stories.

Here's what I changed in how I prep now:
• I keep a one-pager of three real projects: goal, metric, what broke, what I learned.
• I practice explaining trade-offs in plain English — latency vs accuracy, cost vs coverage.
• I ask interviewers how they measure 'success' for the role in the first 90 days.

Offers aren't guaranteed, but my last two conversations felt more mutual and less like a test. If you're job searching, consider spending as much time on narrative as on flashcards.""",
    """We almost shipped a 'smart default' that would have auto-selected shipping options for small business customers. The model looked great in notebooks.

Then we sat with five merchants for ninety minutes. Three of them said the same thing in different words: 'If you choose for me and it's wrong, my customer blames me — not your algorithm.' We killed the auto-select and shipped transparent recommendations with one-click apply instead. Conversion dipped slightly in the experiment, but support tickets and churn risk dropped more than we expected.

I'm sharing this because it's easy to fall in love with automation scores. Sometimes the right product is slower, more visible, and more human. Our PM wrote that sentence on the wall of our team room; I think it belongs in more roadmaps.""",
    """Friday at 4:58 p.m., finance emailed: 'Can we get a cut of revenue by SKU for the board deck Monday?' The honest answer was no — not without risking a fragile legacy report job.

Instead of saying no outright, I called the requester, repeated back what decision the numbers would drive, and proposed a narrower slice we could certify by Sunday. We agreed on three KPIs, not fifteen. I paired with an analyst, documented assumptions in the sheet, and sent a short note about what we didn't include and why.

The board got what they needed. The team didn't burn the weekend. The relationship with finance is warmer because we negotiated scope instead of hiding behind process.

If you work with data: clarity on the decision beats completeness of the spreadsheet.""",
    """I used to dread giving corrective feedback. I'd soften it until it meant nothing, or delay it until I was frustrated — then it came out sharp.

A coach had me try a stupidly simple format: observation (fact), impact (on team or customer), request (one behavior), support (what I'll do). I practiced on paper until it felt robotic, then used it in a real conversation about missed code review turnaround.

The other person pushed back at first. We stayed on the facts. By the end they said, 'I didn't realize it blocked release that way.' Two weeks later their stats improved without me nagging.

I'm not claiming one script fixes culture. I am saying structure reduced my anxiety and made the conversation fairer. If feedback is hard for you too, consider stealing a template before improvising every time.""",
    """Our design system had beautiful components and almost nobody used them. Designers said engineering variants were outdated; engineers said Figma didn't match states in production.

We didn't launch a big task force. We picked one flow — password reset — and rebuilt it end-to-end using only system pieces, with one designer and one engineer full-time for two weeks. We screenshotted before/after, measured time-to-implement for the next three features, and presented those numbers internally.

Adoption didn't hit 100% overnight. But teams started opening tickets to align tokens instead of inventing new grays. Small proof beat a big mandate.

If your design ops effort feels stuck, shrink the scope until you can show a win on a single journey.""",
    """I spent six months feeling like a fraud after switching from backend to a more ML-adjacent role. Everyone seemed to speak in paper titles and framework names I hadn't read.

What helped wasn't more courses — it was admitting 'I don't follow' in meetings until I did. I found two peers who traded lunch for whiteboard sessions. I kept a running doc of terms I looked up so I didn't ask the same question twice.

Last week I presented an eval plan to leadership without shaking. The content wasn't magic; the confidence came from repetition and honest questions.

If you're pivoting careers: the gap feels huge from the inside. From the outside, people mostly want reliability and curiosity. Give yourself permission to be a beginner in public.""",
    """We had a classic standoff: Security wanted stricter SSO for internal tools; a product squad argued it would slow experiments with contractors.

Instead of escalating to executives immediately, we ran a joint threat modeling lunch — pizza, whiteboard, no slides. The app owner explained real workflows; we mapped where data actually lived. Turns out the risk wasn't contractors logging in — it was shared service accounts nobody rotated.

We fixed the accounts, scoped MFA to the sensitive paths only, and shipped in two sprints instead of six months of debate.

Takeaway: align on the asset and the adversary before you argue about the tool. Saves a lot of politics.""",
    """I volunteer as a mock interviewer at a local bootcamp twice a year. This year one candidate froze on a simple SQL question — then, when I switched to 'tell me about a hard bug,' they lit up and explained a distributed tracing issue beautifully.

Afterward I told them the truth: some interview loops overweight trivia; others weight problem-solving. They should ask recruiters which style to expect and prep both stories and syntax.

It reminded me how arbitrary gates feel from the outside. If you hire: be explicit about what you're testing. If you interview: ask what 'good' looks like for that company. Everyone saves time.""",
    """Remote work + two kids means my 'deep work' used to happen at 10 p.m. I was proud of it until my spouse pointed out I was cranky all weekend.

I tried something mundane: I blocked 7:30–9:00 a.m. three days a week as 'no meetings unless on fire,' moved standup later once, and told my manager honestly that afternoons are fragmented. Not everyone has that flexibility — I get that. In my case, protecting one predictable window did more for output than any productivity app.

If you're burning the candle at both ends: audit your calendar for one defensible block and defend it for a month. Measure mood and throughput before optimizing further.""",
    """Our customer success team forwarded an angry email chain about a 'bug' that was actually misunderstood pricing on the invoice PDF. Engineering could have dismissed it.

We didn't. CS, a PM, and I joined one call with the customer. We listened for twenty minutes, repeated their concern, showed them exactly where the line item came from, and fixed the wording on the PDF the same week. No code defect — but a real trust defect.

Support tickets on that topic dropped to near zero. Sales said renewals got easier.

Lesson: not every ticket needs a Jira epic. Sometimes it needs empathy and clearer language. Product quality includes the words next to the numbers.""",
    """I used to think networking meant conferences and LinkedIn DMs to strangers. Last year a project went sideways and I needed a second opinion fast. I messaged three former coworkers I hadn't spoken to in years — honestly, expecting silence.

Two replied within a day. One introduced me to someone who had solved the same compliance wrinkle. The problem unraveled over coffee chats, not pitches.

I learned maintenance matters: a short note when someone changes jobs, a congrats on a launch, nothing transactional. The 'network' isn't a Rolodex — it's people who remember you as decent when you aren't asking for anything.

If you're early career: invest in a few real relationships, not a thousand shallow connections.""",
    """We debated for three sprints whether to rebuild an internal admin tool or patch it. The discussion was exhausting — everyone had opinions, nobody had shared data.

We time-boxed one week to instrument actual usage: who logged in, which actions fired, how often support filed tickets. The data was boring and decisive: three power users, high pain on one workflow. We rebuilt that slice only.

Six weeks later those users sent a thank-you note. Leadership asked why we hadn't done it sooner. The honest answer: we were arguing from anecdotes.

If you're stuck on build vs buy vs patch: buy yourself clarity with lightweight analytics before you buy software.""",
    """I bombed a presentation to executives — rushed, too many slides, lost the thread when someone asked a sharp question. I wanted to disappear.

My manager's feedback afterward was specific: 'You tried to prove you worked hard instead of proving we should fund the next step.' She made me rewrite the deck to five slides: problem, options, recommendation, risk, ask. We rehearsed with her interrupting me on purpose.

The redo wasn't glamorous, but the project got funded.

If you present to leadership: they usually want a decision frame, not your entire journey. Save the journey for the appendix or the blog post.""",
    """On-call woke me at 2 a.m. — payment webhooks backing up. My instinct was to scale workers immediately. A teammate said, 'Prove it's compute first.'

We traced the bottleneck to a third-party sandbox that had started rate-limiting us after an unannounced change. We added backoff, contacted the vendor, and temporarily split traffic. Scaling would have masked the issue and cost money.

I'm grateful for the teammate who slowed me down. Speed of reaction matters; correctness of diagnosis matters more.

If you're building runbooks: include a 'what would prove us wrong' step before the 'scale up' step.""",
    """I used to say yes to every mentorship request because it felt rude to decline. I ended up half-present on calls and resentful.

Now I keep two slots a month, same time, same format: 30 minutes, one agenda item they send in advance, and I follow up with one resource. If someone needs more, I point them to communities and cohort programs.

Quality of attention went up; guilt went down. A few mentees told me the structure helped them prepare better too.

Boundaries aren't rejection — they're how you show up fully when you say yes.""",
    """Our 'diversity initiative' used to mean one slide in onboarding. Then an engineer spoke up in retro: 'We celebrate hiring but not retention — and I'm tired.'

That comment started a smaller, messier program: mentorship pairings with opt-in, anonymous pulse checks every quarter, and managers trained on promotion packet bias. We're not done; attrition improved modestly but honestly.

I'm posting because the catalyst wasn't a corporate strategy deck — it was someone brave in a retro. If you lead teams: make space for uncomfortable truths in low-stakes forums before they become exit interviews.""",
    """I spent a weekend building a side automation that 'saves hours.' It broke on Monday because I skipped input validation and didn't log errors.

I fixed it, added tests, and laughed at myself — I preach the same things at work. Side projects are fun precisely because they're risky; production habits still apply if you hate redoing work.

Humble reminder to myself and anyone shipping fast: the boring parts exist because someone learned the hard way.""",
    """A junior asked why we don't use the newest JS framework everyone tweets about. The senior answer was honest: 'Our customers need stability more than our repo needs novelty. We upgrade on purpose, not on hype.'

We then carved half a day every month for a 'spike budget' — try new tools on non-critical paths. People felt heard; the core stack stayed sane.

Balance isn't ignoring innovation; it's scheduling it so it doesn't derail commitments. Might be worth trying if your team argues about tech churn.""",
    """I almost declined a speaking slot at a local meetup — imposter syndrome, slides not perfect. A friend said, 'Share one real failure; you'll help someone more than ten best practices.'

I talked about a rollback I caused and what we changed in CI. Three people came up afterward with similar stories. One became a coworker a year later.

Visibility compounds in ways you can't spreadsheet. If you're on the fence about a small stage: take it, tell the truth, be kind to yourself after.""",
    """We inherited a 'temporary' cron job that became permanent for four years. Nobody wanted to own it because the original author had left.

Finally we scheduled a 'debt funeral' sprint item: document, add monitoring, or delete. The team voted delete after discovering downstream consumers had migrated. We turned it off with a feature flag and watched metrics for 48 hours.

The emotional weight of mystery jobs is real. Naming them and time-boxing decisions beats pretending they're fine.

If you have a mysterious script: give it an owner or a sunset date this quarter.""",
    """Customer called us incompetent in a public thread. My gut said respond with facts and screenshots.

Our head of CS asked for one hour delay. She drafted a reply that started with an apology for their experience, summarized what we knew, and promised a named owner and timeline — no defensiveness. The thread de-escalated; the customer edited their comment.

I learned tone travels faster than truth online. Facts still matter — they came in comment two — but leading with humanity isn't weakness.

If you own comms during incidents: draft angry, send calm.""",
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
    extra_text_min: int = 1,
    extra_text_max: int = 3,
    image_probability: float = 0.12,
) -> list[dict]:
    """Merge curated posts with random long-form narratives from TEXT_POST_POOL (fewer per user — each is lengthy)."""
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
