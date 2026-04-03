"""
Batch 2: five additional grounded professionals (regional / non-tech-glamour roles).
Full profiles + LinkedIn-style posts. For cross-batch connections run:

    python seed_data/seed_realistic_run_all.py

Batch 2 only:
    python seed_data/seed_realistic_users_2.py
"""

from __future__ import annotations

import argparse
import random
import sys
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

from seed_data.seed_realistic_common import (
    POST_MEDIA_URLS,
    edu,
    get_db_default,
    intr,
    proj,
    run_full_seed,
    xp,
)
from utils.auth import hash_password

PM = POST_MEDIA_URLS

USERS = [
    {
        "username": "danielle_okonkwo_hr",
        "name": "Danielle Okonkwo",
        "email": "danielle.okonkwo@zedreq.dev",
        "password": "Danielle@2024!",
        "short_desc": "HR business partner · regional health system",
        "about": (
            "HR business partner for nursing and allied health at a three-hospital system "
            "around northwest Ohio. I post about retention, scheduling, and why vague job ads backfire. "
            "Former case manager; switched to HR after burning out on paperwork. MPH from Ohio State, SHRM-CP."
        ),
        "skills": "Employee relations, scheduling systems, benefits admin, union coordination, Workday",
        "certificates": "SHRM-CP, Mental Health First Aid (adult)",
        "current_status": "Not hiring for my team until Q3 — still happy to connect",
        "location": "Perrysburg, OH",
        "city": "Perrysburg",
        "country": "United States",
        "company": "Summit Regional Health",
        "title": "HR Business Partner",
        "industry": "Hospital & Health Care",
        "experience": [
            xp(
                "HR Business Partner",
                "Summit Regional Health",
                "Perrysburg, OH",
                "2019-03-01",
                None,
                True,
                "Partner to nursing directors; ER and med-surg units. ER staffing and union grievance prep.",
            ),
            xp(
                "HR Generalist",
                "Summit Regional Health",
                "Toledo, OH",
                "2016-01-01",
                "2019-02-28",
                False,
                "Onboarding, benefits questions, leave tracking.",
            ),
            xp(
                "Case Manager",
                "Wood County Social Services",
                "Bowling Green, OH",
                "2013-08-01",
                "2015-12-31",
                False,
                "Medicaid eligibility and care coordination.",
            ),
        ],
        "education": [
            edu("Ohio State University", "M.P.H.", "Health Policy", 2011, 2013),
            edu("University of Toledo", "B.S.", "Social Work", 2007, 2011),
        ],
        "projects": [
            proj(
                "Night-shift CEU pilot",
                "Piloted equal stipends for night-shift CEUs; expanded system-wide after one year.",
                None,
                [],
            ),
        ],
        "interests": [
            intr("Church choir", "volunteer"),
            intr("Half-marathons"),
            intr("Meal-prep Sundays"),
        ],
    },
    {
        "username": "ryan_mcelroy_supply",
        "name": "Ryan McElroy",
        "email": "ryan.mcelroy@zedreq.dev",
        "password": "Ryan@2024!",
        "short_desc": "Senior buyer · cold-chain logistics",
        "about": (
            "Procurement for a cold-chain warehouse group moving dairy and produce across Michigan, Indiana, and Ontario. "
            "Spreadsheets, forklift tours, pallet standards. Started as a warehouse lead; company sponsored APICS coursework."
        ),
        "skills": "Vendor negotiation, SAP MM, inventory control, refrigerated logistics, Excel",
        "certificates": "CPIM (in progress), Forklift trainer certification",
        "current_status": "Open to connecting with regional food & bev suppliers",
        "location": "Grand Rapids, MI",
        "city": "Grand Rapids",
        "country": "United States",
        "company": "Great Lakes Cold Storage",
        "title": "Senior Buyer",
        "industry": "Logistics & Supply Chain",
        "experience": [
            xp(
                "Senior Buyer",
                "Great Lakes Cold Storage",
                "Grand Rapids, MI",
                "2020-06-01",
                None,
                True,
                "Proteins and dairy categories; vendor scorecards and cost-down projects.",
            ),
            xp(
                "Buyer",
                "Great Lakes Cold Storage",
                "Grand Rapids, MI",
                "2017-02-01",
                "2020-05-31",
                False,
                "PO execution, receiving disputes, seasonal volume spikes.",
            ),
            xp(
                "Warehouse Lead",
                "Great Lakes Cold Storage",
                "Grand Rapids, MI",
                "2012-05-01",
                "2017-01-31",
                False,
                "Receiving crew, cycle counts, 3PL coordination.",
            ),
        ],
        "education": [
            edu("Grand Valley State University", "B.B.A.", "Supply Chain Management", 2008, 2012),
        ],
        "projects": [
            proj(
                "Vendor scorecard v2",
                "Simple monthly dashboard shared with ops — fewer surprise stockouts.",
                None,
                ["Excel", "Power BI"],
            ),
        ],
        "interests": [intr("Fishing — questionable boat"), intr("Youth hockey parent"), intr("Detroit sports")],
    },
    {
        "username": "nate_kim_pe",
        "name": "Nate Kim",
        "email": "nate.kim@zedreq.dev",
        "password": "Nate@2024!",
        "short_desc": "Structural engineer · schools & public work",
        "about": (
            "Licensed PE in Wisconsin. Small firm (~35) doing schools, fire stations, parking ramps. "
            "Revit, RISA, field visits. UW–Madison BSCE. Habitat site volunteer a few weekends a year."
        ),
        "skills": "Revit, RISA-3D, concrete design, wood framing, code review, field observation",
        "certificates": "PE (Wisconsin)",
        "current_status": "Studying for SE — grumpy but determined",
        "location": "Milwaukee, WI",
        "city": "Milwaukee",
        "country": "United States",
        "company": "Kovacs & Patel Structural Engineers, LLP",
        "title": "Project Engineer",
        "industry": "Civil Engineering",
        "experience": [
            xp(
                "Project Engineer",
                "Kovacs & Patel Structural Engineers, LLP",
                "Milwaukee, WI",
                "2018-01-01",
                None,
                True,
                "K-12 additions, CMU gymnasiums, occasional parking structure retrofits.",
            ),
            xp(
                "EIT / Designer",
                "Kovacs & Patel Structural Engineers, LLP",
                "Milwaukee, WI",
                "2016-06-01",
                "2017-12-31",
                False,
                "Detailing, calc packages, submittal review.",
            ),
        ],
        "education": [edu("University of Wisconsin–Madison", "B.S.", "Civil Engineering", 2012, 2016)],
        "projects": [
            proj(
                "Revit family library cleanup",
                "Internal cleanup that actually made juniors faster — rare win.",
                None,
                ["Revit"],
            ),
        ],
        "interests": [intr("Habitat for Humanity builds", "volunteer"), intr("Brewery patios"), intr("Badgers football")],
    },
    {
        "username": "vanessa_rios_mktg",
        "name": "Vanessa Ríos",
        "email": "vanessa.rios@zedreq.dev",
        "password": "Vanessa@2024!",
        "short_desc": "B2B marketing · packaging & corrugated",
        "about": (
            "Marketing for corrugated and custom inserts — medical device kits, industrial parts, not flashy DTC. "
            "Trade shows in Chicago and Cleveland. First-gen college (UIC). I run our LinkedIn like a human, not a brochure."
        ),
        "skills": "HubSpot, trade show logistics, Salesforce campaigns, copywriting, print specs",
        "certificates": "Google Ads Search certified",
        "current_status": "Hiring a marketing coordinator — DM for the JD",
        "location": "Elk Grove Village, IL",
        "city": "Elk Grove Village",
        "country": "United States",
        "company": "Northline Packaging Solutions",
        "title": "Marketing Manager",
        "industry": "Packaging & Containers",
        "experience": [
            xp(
                "Marketing Manager",
                "Northline Packaging Solutions",
                "Elk Grove Village, IL",
                "2019-08-01",
                None,
                True,
                "Demand gen, website refresh, partner co-marketing.",
            ),
            xp(
                "Marketing Coordinator",
                "Northline Packaging Solutions",
                "Elk Grove Village, IL",
                "2016-03-01",
                "2019-07-31",
                False,
                "Email campaigns, show booth logistics, brochure updates.",
            ),
            xp(
                "Sales Support Specialist",
                "Midwest Industrial Supply",
                "Chicago, IL",
                "2014-07-01",
                "2016-02-29",
                False,
                "Quotes, sample shipments, CRM cleanup.",
            ),
        ],
        "education": [edu("University of Illinois Chicago", "B.A.", "Communication", 2010, 2014)],
        "projects": [
            proj(
                "Honest case study series",
                "Three write-ups that mention delays — sales actually uses them.",
                None,
                [],
            ),
        ],
        "interests": [intr("UIC alumni events"), intr("True crime podcasts"), intr("Neighborhood farmers market")],
    },
    {
        "username": "tony_gallagher_acct",
        "name": "Tony Gallagher",
        "email": "tony.gallagher@zedreq.dev",
        "password": "Tony@2024!",
        "short_desc": "Controller · family commercial GC",
        "about": (
            "Controller for a family commercial GC in Joliet — schools, strip retail, small municipal jobs. "
            "CPA; started in public at a regional firm. Three kids; youth soccer eats our weekends."
        ),
        "skills": "Job costing, Sage 300, lien waivers, union payroll, month-end close, Excel",
        "certificates": "CPA (Illinois)",
        "current_status": "Currently employed",
        "location": "Joliet, IL",
        "city": "Joliet",
        "country": "United States",
        "company": "Martinez Brothers General Contractors",
        "title": "Controller",
        "industry": "Construction",
        "experience": [
            xp(
                "Controller",
                "Martinez Brothers General Contractors",
                "Joliet, IL",
                "2017-01-01",
                None,
                True,
                "Financial statements, job WIP, banking, audit liaison.",
            ),
            xp(
                "Assistant Controller",
                "Martinez Brothers General Contractors",
                "Joliet, IL",
                "2014-05-01",
                "2016-12-31",
                False,
                "AP/AR oversight, payroll tie-outs.",
            ),
            xp(
                "Staff Accountant",
                "Briggs & Lowell CPAs",
                "Naperville, IL",
                "2011-09-01",
                "2014-04-30",
                False,
                "Audit and tax for construction and nonprofit clients.",
            ),
        ],
        "education": [edu("Northern Illinois University", "B.S.", "Accounting", 2007, 2011)],
        "projects": [
            proj(
                "Subcontractor onboarding checklist",
                "One-pager that cut back-and-forth on COI and waivers.",
                None,
                [],
            ),
        ],
        "interests": [intr("Youth soccer coach", "volunteer"), intr("Smoking brisket"), intr("Irish folk sessions")],
    },
]


USER_POST_CANDIDATES: dict[str, list[dict]] = {
    "danielle_okonkwo_hr": [
        {
            "text": "If your interview process has seven rounds and a 'culture chat' that nobody can define, you're not hiring carefully — you're just slow.\n\nWe cut ours to four touchpoints last year and quality of hire went up. Candidates talk.",
            "image": None,
        },
        {
            "text": "Night shift nurses deserve the same professional development budget as days. Full stop.\n\nWe finally aligned stipends and the number of people signing up for CEUs on nights doubled. Wasn't magic — was respect.",
            "image": PM[3],
        },
        {
            "text": "Me explaining to a hiring manager why we can't list 'young and energetic' in the job posting:\n\nThem: 'But we need someone who can keep up'\n\nMe: 'Then write what the job actually requires.'",
            "image": None,
        },
        {
            "text": "Year-end open enrollment wrapped. I owe our benefits broker a coffee the size of my head.\n\nIf you're in Toledo area HR and want to swap notes on high-deductible uptake, my DMs are open.",
            "image": PM[5],
        },
        {
            "text": "Unpopular opinion: pizza in the break room is not a retention strategy. It's lunch.\n\nPay people fairly, fix the schedule, and listen when someone says they're drowning.",
            "image": None,
        },
        {
            "text": "Shoutout to our EVS team — the hospital doesn't run without you and we don't say it enough.",
            "image": PM[4],
        },
        {
            "text": "Posted a role for a talent acquisition coordinator. Already got 200 applications in 48 hours.\n\nI'm reading every single one this weekend because that's the job.",
            "image": None,
        },
        {
            "text": "Reminder (mostly to myself): you are allowed to log off after an employee relations case that drained you. The email will still be there Monday.",
            "image": PM[0],
        },
    ],
    "ryan_mcelroy_supply": [
        {
            "text": "Supplier missed a delivery window by 6 hours and threw off three production lines. Not angry — just tired.\n\nIf you sell into cold chain, communicate early when you're slipping. We can reroute. Silence costs everyone money.",
            "image": None,
        },
        {
            "text": "Spent my morning in a -10°F dock comparing pallet wrap specs. Glamorous career, I know.\n\nActually learned something: the 'cheaper' wrap was costing us more in rework.",
            "image": PM[1],
        },
        {
            "text": "Anyone else drowning in year-end inventory counts or is that just me and my coffee machine?",
            "image": PM[2],
        },
        {
            "text": "Hired a temp buyer while we're backfilling a role. She's ex-Army logistics and already caught a duplicate PO nobody else noticed.",
            "image": None,
        },
        {
            "text": "Trade tip: if your vendor rep only calls when they want volume, get a new rep.\n\nGood partners show up when volumes are down too.",
            "image": None,
        },
        {
            "text": "Boat update: replaced the bilge pump. Still leaks a little. Still love it.",
            "image": PM[3],
        },
        {
            "text": "Driving back from Lansing with a trailer full of rejected cheese crates (long story). Midwest logistics is just vibes and DOT weigh stations.",
            "image": None,
        },
    ],
    "nate_kim_pe": [
        {
            "text": "Field visit today: contractor installed the wrong anchor embed depth on a brace frame. Caught it before pour.\n\nThis is why you show up in person sometimes instead of only redlining PDFs from your desk.",
            "image": PM[2],
        },
        {
            "text": "Studying for SE2 and my brain is mostly equations and guilt about not studying more.\n\nIf you took it recently — coffee on me in Walker's Point if you want to commiserate.",
            "image": None,
        },
        {
            "text": "Small firm perk: I get to see a project from schematic design through the ribbon cutting. Big firm friends tell me they miss that.",
            "image": PM[0],
        },
        {
            "text": "Owner asked if we could 'value engineer' out shear walls. I sent a one-paragraph email with a diagram and no jargon. Sometimes that's all it takes.",
            "image": None,
        },
        {
            "text": "Rain delay on site means I finally cleaned up my Revit template. Yes, I'm fun at parties.",
            "image": PM[4],
        },
        {
            "text": "Habitat build this Saturday — if you're local and free, we need bodies for sheathing. No PE license required 🙂",
            "image": PM[5],
        },
    ],
    "vanessa_rios_mktg": [
        {
            "text": "Our booth at Pack Expo was next to a robot arm demo and nobody cared about our sample boxes. So we leaned into it — handed out stress toys shaped like tiny cartons.\n\nSometimes boring products need silly swag.",
            "image": PM[4],
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
            "text": "Hiring a marketing coordinator. Must like spreadsheets, tolerate trade shows, and not roll eyes when I say 'dieline' for the 40th time.\n\nElk Grove Village / hybrid.",
            "image": PM[0],
        },
        {
            "text": "Cold email I got today: 'Revolutionize your packaging stack with AI.'\n\nBuddy, we need pallets that don't crush in humidity. Save the revolution for someone else's inbox.",
            "image": None,
        },
        {
            "text": "Printed spec wrong on a rush quote — caught it at 10pm because the client asked one clarifying question. Shoutout to clients who read the fine print.",
            "image": PM[2],
        },
        {
            "text": "UIC night class gang — who's going to the alumni mixer next month?",
            "image": PM[5],
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
            "image": PM[1],
        },
        {
            "text": "CPA friends in construction — how are you handling the new lease standard on equipment with embedded service? DMs open. Not looking for theory; looking for what actually works on Sage.",
            "image": None,
        },
        {
            "text": "Took the kids to a job site Saturday (hard hats, the whole thing). Youngest asked why concrete takes so long to dry. I had no good answer.",
            "image": PM[3],
        },
        {
            "text": "Auditors showed up prepared this year. I respect it. Still stressful. Still done.",
            "image": PM[4],
        },
        {
            "text": "If your job costing report doesn't match the field superintendent's notebook, trust the notebook first — then reconcile.",
            "image": None,
        },
        {
            "text": "Bank finally approved a modest line increase. Means we can bid the school addition without losing sleep over bonding. Small wins.",
            "image": PM[0],
        },
    ],
}


def pick_posts_for_user(username: str, rng: random.Random) -> list[dict]:
    pool = USER_POST_CANDIDATES.get(username, [])
    if not pool:
        return []
    n_max = min(len(pool), 7)
    n_min = min(3, n_max)
    k = rng.randint(n_min, n_max)
    shuffled = pool[:]
    rng.shuffle(shuffled)
    return shuffled[:k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed batch 2 realistic users only")
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    master_seed = args.seed if args.seed is not None else random.randrange(2**31)
    rng = random.Random(master_seed)
    posts = {u["username"]: pick_posts_for_user(u["username"], rng) for u in USERS}

    print("=" * 65)
    print("  ZedReq — realistic seed (batch 2 only)")
    print("  Tip: use seed_data/seed_realistic_run_all.py for batch 1 + 2 + full graph")
    print("=" * 65)

    run_full_seed(
        USERS,
        posts,
        hash_password_fn=hash_password,
        get_db_fn=get_db_default,
        seed=master_seed,
        download_images=not args.no_download,
        augment_posts=True,
    )


if __name__ == "__main__":
    main()
