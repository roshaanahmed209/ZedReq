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
            "text": """If your interview process has seven rounds and a "culture chat" that nobody can define, you're not hiring carefully — you're just slow.

Last year our TA lead and I mapped every touchpoint candidates actually experienced. Three steps were legacy from when we copied a tech-company playbook we don't need. Two steps duplicated the same competency screen. We cut to four intentional conversations: recruiter screen, hiring manager depth, peer panel with a real work sample, and a final values conversation with clear rubrics.

Candidates started finishing in under two weeks instead of six. Quality of hire didn't tank — our hiring manager satisfaction scores went up because they weren't fatigued before day one.

What I'd do differently if I started again: involve nursing directors earlier so clinical credibility shows up in the first message, not the third.

If you're in HR in healthcare: how many steps exist because of fear, not evidence?""",
            "image": None,
        },
        {
            "text": """Night shift nurses deserve the same professional development budget as days. Full stop.

For years our CEU stipend was effectively a day-shift perk — classes were scheduled when nights were sleeping. We piloted asynchronous modules plus two paid on-shift education hours per month. Uptake on nights doubled in a quarter. Retention conversations got easier because people stopped feeling like second-class citizens on their own units.

The pushback I expected from finance was real; we showed reduced OT from coverage gaps tied to burnout. Not perfect science, but enough to extend the pilot.

Equity isn't a poster; it's whether someone can access growth without quitting their life.""",
            "image": PM[3],
        },
        {
            "text": """True story from last Tuesday: a hiring manager wanted the phrase "young and energetic" in a posting for a patient transport role.

I walked through the legal risk, then asked what problem they were solving — turns out they needed someone who could lift safely and pass a physical. We rewrote the posting around OSHA-aligned requirements and shift stamina. They got a stronger slate, including two candidates over 50 who crushed the work sample.

My takeaway: push back with a question, not a lecture. People usually have a legitimate worry hiding behind lazy language.""",
            "image": None,
        },
        {
            "text": """Open enrollment closed Friday. I owe our benefits broker something caffeinated the size of my head.

This year we added office hours in the cafeteria with translators for two languages our night staff actually speaks. Enrollment errors dropped; calls to my team dropped. Small change, loud relief.

If you're in Toledo-area HR and want to compare notes on HDHP uptake or communication tactics, DM me — always learning.""",
            "image": PM[5],
        },
        {
            "text": """Unpopular opinion: pizza in the break room is not a retention strategy. It's lunch.

Last month a nurse told me she was drowning on back-to-back twelves while we celebrated "culture week" with snacks. I didn't fix her schedule in one conversation — but I did escalate staffing ratios with data from our own overtime logs. Pizza stayed; we also moved two float positions.

Listen for the sentence under the thank-you. That's usually the real work.""",
            "image": None,
        },
    ],
    "ryan_mcelroy_supply": [
        {
            "text": """A supplier missed a delivery window by six hours and threw off three production lines. I wasn't angry — I was tired in that specific way that makes you calm.

I called the account manager instead of firing off email. Turns out their dock had a refrigeration alarm failure; they were embarrassed and already rerouting. We split the cost of an expedited lane for one pallet and documented a new escalation path for temperature-sensitive delays.

Silence would have cost us more than the lane. If you sell into cold chain: tell your buyers early when you're slipping. We can often reroute — we can't read minds.""",
            "image": None,
        },
        {
            "text": """I spent yesterday morning in a -10°F dock comparing pallet wrap specs. Glamorous career, I know.

Finance pushed the cheaper roll. Operations showed me rescan data — more tears, more rework, more temp labor. We ran a two-week A/B on one lane. The "expensive" wrap saved money once you counted labor and shrink.

Spreadsheets lie until you watch the floor. I should have done the walk sooner.""",
            "image": PM[1],
        },
        {
            "text": """We brought in a temp buyer while backfilling a permanent role. She's ex-Army logistics — first week she caught a duplicate PO that three of us had stared at.

Sometimes the best hire isn't the fanciest degree; it's someone trained to check assumptions when everyone else is rushing.

If you're hiring in supply chain: look for systems thinking and nerves of steel, not just category keywords.""",
            "image": None,
        },
        {
            "text": """Boat update: replaced the bilge pump. Still leaks a little when I'm dramatic about it. Still love it.

Why post this on LinkedIn? Because careers aren't linear glamour — they're maintenance, patience, and fixing what you can on a Sunday before Monday's inventory count.

Also: if you know a good marine electrician near Grand Rapids, my inbox is open.""",
            "image": PM[3],
        },
        {
            "text": """Drove back from Lansing with a trailer of rejected cheese crates — long story involving specs, humidity, and a label font nobody agreed on.

Midwest logistics is part DOT weigh stations, part group chat apologies, part showing up the next day anyway.

What I handled differently this time: I called the customer before they saw the truck turn around. Trust recovered faster than the last incident when we hid behind email.""",
            "image": None,
        },
    ],
    "nate_kim_pe": [
        {
            "text": """Field visit yesterday: contractor had installed the wrong anchor embed depth on a brace frame. Caught it before pour — not because I'm a genius, because someone on site texted a photo when it felt "off."

I used to live in PDFs. Now I start with eyes on steel. The code is non-negotiable; the conversation with trades goes better when you show up before concrete is expensive.

If you're early in structural: learn to listen to supers. They know the lie of the land better than your laptop.""",
            "image": PM[2],
        },
        {
            "text": """Studying for SE2. My brain is equations, guilt, and more guilt.

What helps: study groups that admit confusion, not performance. I'm buying coffee in Walker's Point for anyone who took structural II recently and wants to commiserate — no resume swap required.

Exams measure persistence as much as intelligence. Still nerve-wracking.""",
            "image": None,
        },
        {
            "text": """Small firm perk: I see projects from schematic design to ribbon cutting. Big-firm friends say they miss that end-to-end ownership.

Tradeoff is longer hours and wearing more hats. Win is walking past a fire station with my kids and saying "I helped hold that roof up."

If you're choosing firm size: ask what feedback loop you need to feel sane.""",
            "image": PM[0],
        },
        {
            "text": """Owner asked if we could "value engineer" out shear walls. I sent one email: short paragraph, simple diagram, code reference, and two options that actually saved money without deleting lateral resistance.

Sometimes panic wants paragraphs of jargon. Clarity is faster — and safer.""",
            "image": None,
        },
        {
            "text": """Habitat build this Saturday — need bodies for sheathing. No PE license required; just gloves and willingness to take direction.

I show up because structures should serve people, not only balance sheets. Also: hammering is cheaper therapy than my gym membership.""",
            "image": PM[5],
        },
    ],
    "vanessa_rios_mktg": [
        {
            "text": """Pack Expo: our booth sat next to a flashy robot arm demo. Nobody cared about our corrugated samples for the first hour.

We leaned in — handed out stress toys shaped like tiny cartons, ran a "guess the burst strength" game with a cheap tester, and suddenly people stayed long enough to hear what we actually sell.

Sometimes boring products need silly doors to open serious conversations.

Marketing lesson: attention first, spec sheet second.""",
            "image": PM[4],
        },
        {
            "text": """I wrote a case study that admitted a delayed shipment — sales was terrified.

The prospect later told our rep that honesty was why they trusted us. Transparency beat polish.

We're not perfect at logistics; we're rigorous about communication. That's the story worth telling.""",
            "image": None,
        },
        {
            "text": """Hiring a marketing coordinator: spreadsheets, trade shows, tolerance for the word "dieline," sense of humor required. Elk Grove Village / hybrid.

I'll read every application myself for the first pass — not because I'm a hero, because I want someone who reads emails from customers the way I'd want mine read.

DM if you want the JD; please share with detail-oriented humans in your network.""",
            "image": PM[0],
        },
        {
            "text": """Cold email of the week: "Revolutionize your packaging stack with AI."

Buddy, we need pallets that don't crush in humidity during a July unload. Save the revolution for someone else's inbox.

If you sell to industrial buyers: lead with a problem we actually have on the dock, not a keynote slide.""",
            "image": None,
        },
        {
            "text": """I misprinted a spec on a rush quote — caught it at 10pm because the client asked one clarifying question instead of assuming.

Shoutout to buyers who read fine print. You saved both of us a very expensive Monday.

I'm adding a peer review step for anything under 24-hour turnaround. Pride isn't worth scrap.""",
            "image": PM[2],
        },
    ],
    "tony_gallagher_acct": [
        {
            "text": """Month-end close on a short week thanks to a holiday. My checklist is taped to the monitor like a hostage note.

We'll get there — we always do — because the field supers need payroll funded and subs need lien waivers clean.

If you're in accounting: solidarity. If you're not: thank your controller quietly; they're holding chaos in Excel.""",
            "image": None,
        },
        {
            "text": """PM tried to expense a $400 team dinner without a job code. I like the guy — which is why I walked to his desk instead of rejecting it anonymously.

Ten minutes later we had the right code and a saved template for next time. Relationship intact, audit trail intact.

Policy without conversation breeds resentment. Conversation without policy breeds chaos. Do both.""",
            "image": None,
        },
        {
            "text": """Union fringe rates changed January 1. Payroll and I lived in the same conference room for two days. Send snacks next time; we ran out of pretzels.

Construction accounting isn't glamorous — it's translation between agreements, job costing, and reality on site.

CPA friends in GC work: how are you handling embedded service leases on equipment? I want war stories, not theory.""",
            "image": PM[1],
        },
        {
            "text": """Took the kids to a job site Saturday — hard hats, the whole thing. Youngest asked why concrete takes so long to dry.

I had no good answer that fits in a car ride. Parenting and accounting: both involve admitting what you don't know, then looking it up together.

Also: safety briefing with children is excellent audience training.""",
            "image": PM[3],
        },
        {
            "text": """Bank approved a modest line increase — not flashy, but it means we can bid the school addition without losing sleep over bonding capacity.

Small win on paper; huge relief in Monday estimating meetings.

Grateful for lenders who understand family contractors aren't spreadsheets with legs.""",
            "image": PM[0],
        },
    ],
}


def pick_posts_for_user(username: str, rng: random.Random) -> list[dict]:
    pool = USER_POST_CANDIDATES.get(username, [])
    if not pool:
        return []
    # Fewer posts per user — each candidate is long-form (LinkedIn-style narrative).
    n_max = min(len(pool), 4)
    n_min = min(2, n_max)
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
