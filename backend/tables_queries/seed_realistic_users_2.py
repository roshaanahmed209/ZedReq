"""
Seed 5 additional realistic users (different from seed_realistic_users.py).

- No big-brand employers: regional orgs, family businesses, niche B2B, public sector.
- LinkedIn-style posts; each run assigns a random number of posts per user.

Run from repo root or backend:
    python backend/tables_queries/seed_realistic_users_2.py
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = SCRIPT_DIR.parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent.resolve()

sys.path.insert(0, str(BACKEND_DIR))

try:
    from dotenv import load_dotenv

    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")
    else:
        load_dotenv()
except ImportError:
    pass

from config.database import Database, get_connection_params
from utils.auth import hash_password

# Images: office, warehouse, site work, clinic, generic professional (Unsplash)
POST_IMAGES = [
    ("https://images.unsplash.com/photo-1497366216548-37526070297c?w=900&q=80", "image"),
    ("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=900&q=80", "image"),
    ("https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=900&q=80", "image"),
    ("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=900&q=80", "image"),
    ("https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=900&q=80", "image"),
    ("https://images.unsplash.com/photo-1520607162513-77705c0f7d4a?w=900&q=80", "image"),
    ("https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&q=80", "image"),
    ("https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=900&q=80", "image"),
]

USERS = [
    {
        "username": "danielle_okonkwo_hr",
        "name": "Danielle Okonkwo",
        "email": "danielle.okonkwo@zedreq.dev",
        "password": "Danielle@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/women/12.jpg",
        "cover_pic": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&q=80",
        "short_desc": "Talent partner at Summit Regional Health (Toledo metro)",
        "about": (
            "HR business partner for nursing and allied health at a three-hospital system "
            "you've probably never heard of unless you live around northwest Ohio. "
            "I post about retention, shift scheduling headaches, and why 'culture fit' "
            "is a lazy phrase. Former case manager; switched to HR after burning out on paperwork. "
            "MPH from Ohio State, SHRM-CP."
        ),
        "skills": "Employee relations, scheduling systems, benefits admin, union coordination, Workday",
        "certificates": "SHRM-CP, Mental Health First Aid (adult)",
        "current_status": "Not hiring — full up on reqs until Q3",
        "location": "Perrysburg, OH",
        "company": "Summit Regional Health",
        "title": "HR Business Partner",
    },
    {
        "username": "ryan_mcelroy_supply",
        "name": "Ryan McElroy",
        "email": "ryan.mcelroy@zedreq.dev",
        "password": "Ryan@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/55.jpg",
        "cover_pic": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1200&q=80",
        "short_desc": "Buyer @ Great Lakes Cold Storage",
        "about": (
            "Procurement for a cold-chain warehouse group that moves dairy and produce "
            "between Michigan, Indiana, and Ontario. Lots of spreadsheets, forklift tours, "
            "and arguing about pallet standards. No glamour, but the trucks actually show up on time. "
            "Started as a warehouse lead; company paid for an APICS cert. "
            "Weekend hobby: fixing up an old fishing boat I definitely overpaid for."
        ),
        "skills": "Vendor negotiation, SAP MM, inventory control, refrigerated logistics, Excel",
        "certificates": "CPIM (in progress), Forklift trainer certification",
        "current_status": "Open to connecting with regional food & bev suppliers",
        "location": "Grand Rapids, MI",
        "company": "Great Lakes Cold Storage",
        "title": "Senior Buyer",
    },
    {
        "username": "nate_kim_pe",
        "name": "Nate Kim",
        "email": "nate.kim@zedreq.dev",
        "password": "Nate@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/67.jpg",
        "cover_pic": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1200&q=80",
        "short_desc": "Structural engineer | Kovacs & Patel, LLP",
        "about": (
            "Licensed PE in Wisconsin. Small firm (~35 people) doing schools, fire stations, "
            "and the occasional parking ramp retrofit. Most of my week is Revit, RISA, "
            "and explaining to owners why you can't delete that column. "
            "UW–Madison BSCE. I volunteer on Habitat site inspections a couple times a year."
        ),
        "skills": "Revit, RISA-3D, concrete design, wood framing, code review, field observation",
        "certificates": "PE (WI), SE exam — taking structural II this fall",
        "current_status": "Currently employed",
        "location": "Milwaukee, WI",
        "company": "Kovacs & Patel Structural Engineers, LLP",
        "title": "Project Engineer",
    },
    {
        "username": "vanessa_rios_mktg",
        "name": "Vanessa Ríos",
        "email": "vanessa.rios@zedreq.dev",
        "password": "Vanessa@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/women/89.jpg",
        "cover_pic": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=1200&q=80",
        "short_desc": "Marketing — Northline Packaging Solutions",
        "about": (
            "B2B marketing for corrugated and custom inserts — think boxes for medical device "
            "kits and industrial parts, not the pretty DTC stuff. Trade shows in Chicago and "
            "Cleveland, long sales cycles, lots of PDF spec sheets. "
            "First-gen college grad (UIC). I run our LinkedIn page badly on purpose so it sounds human."
        ),
        "skills": "HubSpot, trade show logistics, Salesforce campaigns, copywriting, print specs",
        "certificates": "Google Ads Search certified",
        "current_status": "Hiring a marketing coordinator — DM if you know someone detail-oriented",
        "location": "Elk Grove Village, IL",
        "company": "Northline Packaging Solutions",
        "title": "Marketing Manager",
    },
    {
        "username": "tony_gallagher_acct",
        "name": "Tony Gallagher",
        "email": "tony.gallagher@zedreq.dev",
        "password": "Tony@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/22.jpg",
        "cover_pic": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80",
        "short_desc": "Controller @ Martinez Brothers General Contractors",
        "about": (
            "Family commercial GC out of Joliet — schools, strip retail, small municipal jobs. "
            "I'm the guy who says no to the shiny new software every year and then implements it anyway. "
            "CPA, started in public (regional firm), escaped to industry before I forgot what sleep was. "
            "Three kids under ten; my 'side hustle' is youth soccer carpools."
        ),
        "skills": "Job costing, Sage 300, lien waivers, union payroll, month-end close, Excel",
        "certificates": "CPA (Illinois)",
        "current_status": "Currently employed",
        "location": "Joliet, IL",
        "company": "Martinez Brothers General Contractors",
        "title": "Controller",
    },
]

# Candidate posts per user; run() picks a random subset each time.
USER_POST_CANDIDATES: dict[str, list[dict]] = {
    "danielle_okonkwo_hr": [
        {
            "text": "If your interview process has seven rounds and a 'culture chat' that nobody can define, you're not hiring carefully — you're just slow.\n\nWe cut ours to four touchpoints last year and quality of hire went up. Candidates talk.",
            "image": None,
        },
        {
            "text": "Night shift nurses deserve the same professional development budget as days. Full stop.\n\nWe finally aligned stipends and the number of people signing up for CEUs on nights doubled. Wasn't magic — was respect.",
            "image": POST_IMAGES[3],
        },
        {
            "text": "Me explaining to a hiring manager why we can't list 'young and energetic' in the job posting:\n\n😐\n\nThem: 'But we need someone who can keep up'\n\nMe: 'Then write what the job actually requires.'",
            "image": None,
        },
        {
            "text": "Year-end open enrollment wrapped. I owe our benefits broker a coffee the size of my head.\n\nIf you're in Toledo area HR and want to swap notes on high-deductible uptake, my DMs are open.",
            "image": POST_IMAGES[6],
        },
        {
            "text": "Unpopular opinion: pizza in the break room is not a retention strategy. It's lunch.\n\nPay people fairly, fix the schedule, and listen when someone says they're drowning. The pizza can stay — just don't confuse it with culture.",
            "image": None,
        },
        {
            "text": "Shoutout to our EVS team — the hospital doesn't run without you and we don't say it enough.",
            "image": POST_IMAGES[4],
        },
        {
            "text": "Posted a role for a talent acquisition coordinator. Already got 200 applications in 48 hours.\n\nI'm reading every single one this weekend because that's the job. If you applied, thank you for your patience.",
            "image": None,
        },
        {
            "text": "Reminder (mostly to myself): you are allowed to log off after an employee relations case that drained you. The email will still be there Monday.",
            "image": POST_IMAGES[7],
        },
    ],
    "ryan_mcelroy_supply": [
        {
            "text": "Supplier missed a delivery window by 6 hours and threw off three production lines. Not angry — just tired.\n\nIf you sell into cold chain, communicate early when you're slipping. We can reroute. Silence costs everyone money.",
            "image": None,
        },
        {
            "text": "Spent my morning in a -10°F dock comparing pallet wrap specs. Glamorous career, I know.\n\nActually learned something: the 'cheaper' wrap was costing us more in rework. Sometimes the spreadsheet lies until you see the floor.",
            "image": POST_IMAGES[1],
        },
        {
            "text": "Anyone else drowning in year-end inventory counts or is that just me and my coffee machine?",
            "image": POST_IMAGES[5],
        },
        {
            "text": "Hired a temp buyer while we're backfilling a role. She's ex-Army logistics and already caught a duplicate PO nobody else noticed.\n\nSometimes the best hire isn't the one with the fanciest degree.",
            "image": None,
        },
        {
            "text": "Trade tip: if your vendor rep only calls when they want volume, get a new rep.\n\nGood partners show up when volumes are down too.",
            "image": None,
        },
        {
            "text": "Boat update: replaced the bilge pump. Still leaks a little. Still love it.",
            "image": POST_IMAGES[2],
        },
        {
            "text": "Driving back from Lansing with a trailer full of rejected cheese crates (long story). Midwest logistics is just vibes and DOT weigh stations.",
            "image": None,
        },
    ],
    "nate_kim_pe": [
        {
            "text": "Field visit today: contractor installed the wrong anchor embed depth on a brace frame. Caught it before pour.\n\nThis is why you show up in person sometimes instead of only redlining PDFs from your desk.",
            "image": POST_IMAGES[2],
        },
        {
            "text": "Studying for SE2 and my brain is mostly equations and guilt about not studying more.\n\nIf you took it recently — coffee on me in Walker's Point if you want to commiserate.",
            "image": None,
        },
        {
            "text": "Small firm perk: I get to see a project from schematic design through the ribbon cutting. Big firm friends tell me they miss that.",
            "image": POST_IMAGES[0],
        },
        {
            "text": "Owner asked if we could 'value engineer' out shear walls. I sent a one-paragraph email with a diagram and no jargon. Sometimes that's all it takes.",
            "image": None,
        },
        {
            "text": "Rain delay on site means I finally cleaned up my Revit template. Yes, I'm fun at parties.",
            "image": POST_IMAGES[7],
        },
        {
            "text": "Habitat build this Saturday — if you're local and free, we need bodies for sheathing. No PE license required 🙂",
            "image": POST_IMAGES[6],
        },
    ],
    "vanessa_rios_mktg": [
        {
            "text": "Our booth at Pack Expo was next to a robot arm demo and nobody cared about our sample boxes. So we leaned into it — handed out stress toys shaped like tiny cartons. Lines were longer than the robot.\n\nSometimes boring products need silly swag.",
            "image": POST_IMAGES[4],
        },
        {
            "text": "Wrote a case study that was honest about a delayed shipment. Sales was nervous. The prospect said it was the reason they trusted us.\n\nTransparency > polish.",
            "image": None,
        },
        {
            "text": "If your LinkedIn headline says 'storyteller' and you sell corrugated, I'm not mad — I'm just confused what story we're telling.\n\n(Mine says Marketing Manager. Boring wins.)",
            "image": None,
        },
        {
            "text": "Hiring a marketing coordinator. Must like spreadsheets, tolerate trade shows, and not roll eyes when I say 'dieline' for the 40th time.\n\nElk Grove Village / hybrid. Link in comments.",
            "image": POST_IMAGES[0],
        },
        {
            "text": "Cold email I got today: 'Revolutionize your packaging stack with AI.'\n\nBuddy, we need pallets that don't crush in humidity. Save the revolution for someone else's inbox.",
            "image": None,
        },
        {
            "text": "Printed spec wrong on a rush quote — caught it at 10pm because the client asked one clarifying question. Shoutout to clients who read the fine print. You saved both of us.",
            "image": POST_IMAGES[5],
        },
        {
            "text": "UIC night class gang — who's going to the alumni mixer next month?",
            "image": POST_IMAGES[6],
        },
    ],
    "tony_gallagher_acct": [
        {
            "text": "Month-end close on a short week because of a holiday. My closing checklist is taped to the monitor like a hostage note.\n\nWe'll get there. We always do.",
            "image": None,
        },
        {
            "text": "Project manager tried to expense a $400 'team building' dinner without a job code. Buddy. I like you. Use the code.",
            "image": None,
        },
        {
            "text": "Union fringe rates changed Jan 1. Payroll and I have been in the same conference room for two days. Send snacks.",
            "image": POST_IMAGES[1],
        },
        {
            "text": "CPA friends in construction — how are you handling the new lease standard on equipment with embedded service? DMs open. Not looking for theory; looking for what actually works on Sage.",
            "image": None,
        },
        {
            "text": "Took the kids to a job site Saturday (hard hats, the whole thing). Youngest asked why concrete takes so long to dry. I had no good answer. Parenting and accounting: both involve admitting what you don't know.",
            "image": POST_IMAGES[2],
        },
        {
            "text": "Auditors showed up prepared this year. I respect it. Still stressful. Still done.",
            "image": POST_IMAGES[7],
        },
        {
            "text": "If your job costing report doesn't match the field superintendent's notebook, trust the notebook first — then reconcile. Numbers lie when someone's handwriting doesn't.",
            "image": None,
        },
        {
            "text": "Bank finally approved a modest line increase. Means we can bid the school addition without losing sleep over bonding. Small wins.",
            "image": POST_IMAGES[0],
        },
    ],
}


def seed_user(db: Database, user: dict) -> tuple[int, int] | None:
    try:
        desc = db.execute_returning(
            """INSERT INTO description
               (short_desc, about, certificates, skills, current_status, profile_pic, cover_pic)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING desc_id""",
            (
                user["short_desc"],
                user["about"],
                user["certificates"],
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
                hash_password(user["password"]),
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


def seed_network(db: Database, uid: int) -> None:
    try:
        db.execute(
            "INSERT INTO network (uid, num_connections) VALUES (%s, 0) ON CONFLICT DO NOTHING",
            (uid,),
        )
    except Exception as e:
        print(f"  [WARN] network for uid {uid}: {e}")


def seed_posts(db: Database, uid: int, username: str, posts: list) -> None:
    for p in posts:
        try:
            media_url, media_type = (None, None)
            if p.get("image"):
                media_url, media_type = p["image"]

            likes = random.randint(8, 890)
            comments = random.randint(0, 62)

            days_ago = random.randint(0, 120)
            hours_ago = random.randint(0, 23)
            created = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

            db.execute(
                """INSERT INTO post (uid, post_desc, media_url, media_type, likes, comments, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (uid, p["text"], media_url, media_type, likes, comments, created, created),
            )
        except Exception as e:
            print(f"  [WARN] post for @{username}: {e}")


def seed_connections(db: Database, uid_map: dict[str, int]) -> None:
    usernames = list(uid_map.keys())
    for username, uid in uid_map.items():
        others = [u for u in usernames if u != username]
        if not others:
            continue
        k = min(random.randint(2, 4), len(others))
        to_follow = random.sample(others, k)

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


def pick_posts_for_user(username: str) -> list[dict]:
    pool = USER_POST_CANDIDATES.get(username, [])
    if not pool:
        return []
    n_min = 2
    n_max = min(len(pool), 7)
    k = random.randint(n_min, n_max)
    shuffled = pool[:]
    random.shuffle(shuffled)
    return shuffled[:k]


def run() -> None:
    random.seed()
    print("=" * 65)
    print("  ZedRec — Realistic User Seed (batch 2, 5 users)")
    print("=" * 65)

    params = get_connection_params()
    db = Database(params)

    uid_map: dict[str, int] = {}

    print("\n── Creating users & profiles ──────────────────────────────────")
    for user in USERS:
        result = seed_user(db, user)
        if result:
            uid, _ = result
            uid_map[user["username"]] = uid
            seed_network(db, uid)

    print("\n── Creating posts (random count per user) ─────────────────────")
    for user in USERS:
        uid = uid_map.get(user["username"])
        if uid is None:
            continue
        posts = pick_posts_for_user(user["username"])
        seed_posts(db, uid, user["username"], posts)
        print(f"  [OK]   {len(posts)} posts for @{user['username']}")

    print("\n── Creating connections ────────────────────────────────────────")
    seed_connections(db, uid_map)
    print(f"  [OK]   Connections among batch-2 users")

    db.close()

    print("\n" + "=" * 65)
    print(f"  Done! {len(uid_map)} users in this batch.")
    print()
    print("  Login credentials:")
    print("  ┌─────────────────────────────────┬─────────────────┐")
    print("  │ Email                           │ Password        │")
    print("  ├─────────────────────────────────┼─────────────────┤")
    for u in USERS:
        if u["username"] in uid_map:
            print(f"  │ {u['email']:<31} │ {u['password']:<15} │")
    print("  └─────────────────────────────────┴─────────────────┘")
    print("=" * 65)


if __name__ == "__main__":
    run()
