"""
Batch 3: five grounded professionals across different sectors.
Gender-matched profile photos, post images chosen to match post content.

Batch 3 only:
    python seed_data/seed_realistic_users_3.py

For full graph with batches 1 + 2 + 3:
    python seed_data/seed_realistic_run_all.py
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
    edu,
    get_db_default,
    intr,
    proj,
    run_full_seed,
    xp,
)
from utils.auth import hash_password

# ---------------------------------------------------------------------------
# Post media URLs — each URL is chosen to thematically match the post it's
# used in.  All are stable Unsplash photo permalinks (no keyword randomness).
# ---------------------------------------------------------------------------

# Organized by theme so we can reference them by name below
MEDIA = {
    # Healthcare / hospital
    "hospital_corridor":   "https://images.unsplash.com/photo-1504439468489-c8920d796a29?w=900&q=80",
    "nurse_station":       "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=900&q=80",
    "medical_chart":       "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=900&q=80",

    # Construction / job site
    "construction_site":   "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=900&q=80",
    "blueprint_desk":      "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=900&q=80",
    "concrete_pour":       "https://images.unsplash.com/photo-1565008576549-57569a49371d?w=900&q=80",

    # Finance / accounting / office
    "spreadsheet_coffee":  "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=900&q=80",
    "office_whiteboard":   "https://images.unsplash.com/photo-1497366216548-37526070297c?w=900&q=80",
    "desk_paperwork":      "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=900&q=80",

    # Warehouse / logistics / cold storage
    "warehouse_racks":     "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=900&q=80",
    "forklift_aisle":      "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=900&q=80",
    "loading_dock":        "https://images.unsplash.com/photo-1553413077-190dd305871c?w=900&q=80",

    # Engineering / structural
    "steel_frame":         "https://images.unsplash.com/photo-1565372195458-9de0b320ef04?w=900&q=80",
    "blueprint_roll":      "https://images.unsplash.com/photo-1503387837-b154d5074bd2?w=900&q=80",
    "building_exterior":   "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=900&q=80",

    # Marketing / trade show / packaging
    "trade_show_booth":    "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=900&q=80",
    "packaging_boxes":     "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=900&q=80",
    "laptop_analytics":    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900&q=80",

    # Legal / courtroom / law
    "law_books":           "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=900&q=80",
    "courthouse":          "https://images.unsplash.com/photo-1555421689-491a97ff2040?w=900&q=80",
    "contract_signing":    "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=900&q=80",

    # Education / classroom
    "classroom":           "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=900&q=80",
    "library_study":       "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=900&q=80",
    "whiteboard_lesson":   "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=900&q=80",

    # Community / outdoor / misc
    "coffee_meeting":      "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=900&q=80",
    "volunteering":        "https://images.unsplash.com/photo-1593113598332-cd288d649433?w=900&q=80",
    "city_street":         "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=900&q=80",
}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

USERS = [
    # ------------------------------------------------------------------
    # 1. FEMALE — Public school teacher turned instructional coach
    # ------------------------------------------------------------------
    {
        "username": "priya_mehta_edtech",
        "name": "Priya Mehta",
        "email": "priya.mehta@zedreq.dev",
        "password": "Priya@2024!",
        # profile_photo_url is gender-matched (female, South-Asian appearance)
        "profile_photo_url": "https://randomuser.me/api/portraits/women/44.jpg",
        "short_desc": "Instructional coach · K-12 literacy & tech integration",
        "about": (
            "Instructional coach for a mid-size suburban district outside Columbus. "
            "I work with classroom teachers on literacy strategies and edtech that doesn't "
            "collect dust after professional development day. Former 4th-grade teacher; "
            "moved into coaching after watching too many good tools get shelved for lack "
            "of follow-up support. M.Ed. from Ohio University. I post about what's actually "
            "working in schools — slowly."
        ),
        "skills": "Instructional design, reading intervention, Google Workspace for Education, classroom observation, coaching cycles",
        "certificates": "Reading Endorsement (Ohio), Google Certified Educator Level 2",
        "current_status": "Open to summer PD consulting",
        "location": "Westerville, OH",
        "city": "Westerville",
        "country": "United States",
        "company": "Olentangy Local School District",
        "title": "Instructional Coach",
        "industry": "Primary/Secondary Education",
        "experience": [
            xp(
                "Instructional Coach",
                "Olentangy Local School District",
                "Westerville, OH",
                "2020-08-01",
                None,
                True,
                "Coaching cycles for 18 teachers; literacy data review; edtech rollout support.",
            ),
            xp(
                "4th Grade Teacher",
                "Olentangy Local School District",
                "Westerville, OH",
                "2015-08-01",
                "2020-06-30",
                False,
                "Reading and math; student growth data for IEP collaboration.",
            ),
            xp(
                "Reading Interventionist",
                "Columbus City Schools",
                "Columbus, OH",
                "2012-08-01",
                "2015-06-30",
                False,
                "Small-group Tier 2 and 3 reading interventions, K-3.",
            ),
        ],
        "education": [
            edu("Ohio University", "M.Ed.", "Curriculum & Instruction", 2013, 2016),
            edu("Ohio State University", "B.S.", "Early Childhood Education", 2008, 2012),
        ],
        "projects": [
            proj(
                "Coaching cycle tracker",
                "Simple shared doc system for observation → debrief → goal → follow-up. "
                "Replaced the email chaos we had before.",
                None,
                ["Google Sheets", "Google Docs"],
            ),
        ],
        "interests": [
            intr("Children's book author (aspiring — one drawer full of drafts)"),
            intr("Weekend hiking with terrible trail snacks"),
            intr("School garden committee", "volunteer"),
        ],
    },

    # ------------------------------------------------------------------
    # 2. MALE — Municipal water utility engineer
    # ------------------------------------------------------------------
    {
        "username": "marcus_bell_utilities",
        "name": "Marcus Bell",
        "email": "marcus.bell@zedreq.dev",
        "password": "Marcus@2024!",
        # profile_photo_url — male, mid-30s Black professional
        "profile_photo_url": "https://randomuser.me/api/portraits/men/32.jpg",
        "short_desc": "Civil/environmental engineer · municipal water systems",
        "about": (
            "Project engineer for a mid-sized city water utility in the Midwest. "
            "Water main rehab, lead service line replacement, SCADA upgrades. "
            "PE in Indiana; grew up in Gary. I post when something fails — the polite "
            "infrastructure version of a postmortem. Most days I'm reading soils reports "
            "and arguing about pipe specifications with contractors who've been at this longer than me."
        ),
        "skills": "Water distribution design, EPANET modeling, AutoCAD Civil 3D, SCADA basics, lead service line assessment",
        "certificates": "PE (Indiana), 40-Hour HAZWOPER",
        "current_status": "Not looking; too many active projects",
        "location": "Indianapolis, IN",
        "city": "Indianapolis",
        "country": "United States",
        "company": "Indianapolis Department of Public Utilities",
        "title": "Project Engineer II",
        "industry": "Water & Utilities",
        "experience": [
            xp(
                "Project Engineer II",
                "Indianapolis Department of Public Utilities",
                "Indianapolis, IN",
                "2020-03-01",
                None,
                True,
                "Lead service line inventory and replacement program; main break response coordination.",
            ),
            xp(
                "Project Engineer I",
                "Indianapolis Department of Public Utilities",
                "Indianapolis, IN",
                "2017-06-01",
                "2020-02-28",
                False,
                "Design of water main extensions, hydrant relocations, meter pit installations.",
            ),
            xp(
                "Engineering Intern",
                "Arcadis US",
                "Indianapolis, IN",
                "2016-05-01",
                "2016-08-31",
                False,
                "Stormwater modeling and drainage plan review.",
            ),
        ],
        "education": [
            edu("Purdue University", "B.S.", "Civil Engineering", 2013, 2017),
        ],
        "projects": [
            proj(
                "Lead service line inventory tool",
                "Excel + GIS workflow that consolidated four legacy data sources into "
                "one auditable inventory. Used for EPA reporting.",
                None,
                ["AutoCAD Civil 3D", "ArcGIS", "Excel"],
            ),
        ],
        "interests": [
            intr("Gary Southshore RailCats fan (obligatory)"),
            intr("Home brewing — water chemistry obsession is occupational"),
            intr("Volunteer fire department", "volunteer"),
        ],
    },

    # ------------------------------------------------------------------
    # 3. FEMALE — Immigration paralegal at a small firm
    # ------------------------------------------------------------------
    {
        "username": "sofia_reyes_legal",
        "name": "Sofía Reyes",
        "email": "sofia.reyes@zedreq.dev",
        "password": "Sofia@2024!",
        # profile_photo_url — female, Latina, late 20s
        "profile_photo_url": "https://randomuser.me/api/portraits/women/26.jpg",
        "short_desc": "Immigration paralegal · family & employment-based petitions",
        "about": (
            "Paralegal at a 6-attorney immigration boutique in San Antonio. "
            "I prepare I-130s, I-485s, PERM documentation, and RFE responses. "
            "First-gen college grad (UTSA). My mom's naturalization case is what got me here. "
            "I post about practical things: what an RFE actually means, why translation errors "
            "tank cases, what to expect at a biometrics appointment. Not legal advice. Just clarity "
            "for people who are scared and Googling at 11 PM."
        ),
        "skills": "Immigration case management (INSZoom), I-130/I-485 preparation, PERM documentation, RFE drafting support, client communication in Spanish",
        "certificates": "NALA Paralegal Certificate (in progress), Notary Public (Texas)",
        "current_status": "Employed — growing caseload",
        "location": "San Antonio, TX",
        "city": "San Antonio",
        "country": "United States",
        "company": "Vega & Associates Immigration Law",
        "title": "Senior Paralegal",
        "industry": "Law Practice",
        "experience": [
            xp(
                "Senior Paralegal",
                "Vega & Associates Immigration Law",
                "San Antonio, TX",
                "2021-02-01",
                None,
                True,
                "Manage active caseload of 90+ family and employment-based petitions; RFE response coordination.",
            ),
            xp(
                "Paralegal",
                "Vega & Associates Immigration Law",
                "San Antonio, TX",
                "2018-09-01",
                "2021-01-31",
                False,
                "File prep, client intake, court filing deadlines, USCIS correspondence.",
            ),
            xp(
                "Legal Assistant",
                "Garza Family Law",
                "San Antonio, TX",
                "2017-05-01",
                "2018-08-31",
                False,
                "Scheduling, document scanning, basic pleadings support.",
            ),
        ],
        "education": [
            edu("University of Texas at San Antonio", "B.A.", "Political Science", 2013, 2017),
        ],
        "projects": [
            proj(
                "RFE response templates",
                "Internal library of 14 annotated RFE response frameworks — cut attorney "
                "drafting time by about a third on common issues.",
                None,
                ["INSZoom", "Word"],
            ),
        ],
        "interests": [
            intr("RAICES Texas fundraisers", "volunteer"),
            intr("True crime en español — podcast recs welcome"),
            intr("Homemade tamales (family recipe, not negotiable)"),
        ],
    },

    # ------------------------------------------------------------------
    # 4. MALE — Regional bank commercial loan officer
    # ------------------------------------------------------------------
    {
        "username": "brett_holloway_banking",
        "name": "Brett Holloway",
        "email": "brett.holloway@zedreq.dev",
        "password": "Brett@2024!",
        # profile_photo_url — male, white, 40s
        "profile_photo_url": "https://randomuser.me/api/portraits/men/51.jpg",
        "short_desc": "Commercial loan officer · Midwest community bank",
        "about": (
            "Commercial lender at a community bank covering eastern Iowa and western Illinois. "
            "Ag lines, equipment, small business real estate. "
            "I've been doing this since before smartphones had GPS — which means I've driven "
            "down a lot of wrong gravel roads to look at collateral. "
            "Finance degree from Iowa State. Three kids, one tractor I have no business owning."
        ),
        "skills": "Commercial credit underwriting, farm operating lines, SBA 7(a) basics, financial statement analysis, relationship management",
        "certificates": "Graduate School of Banking (Wisconsin), SBA Lender Training",
        "current_status": "Not looking — happy where I am",
        "location": "Davenport, IA",
        "city": "Davenport",
        "country": "United States",
        "company": "Heartland Community Bank",
        "title": "VP, Commercial Lending",
        "industry": "Banking",
        "experience": [
            xp(
                "VP, Commercial Lending",
                "Heartland Community Bank",
                "Davenport, IA",
                "2016-04-01",
                None,
                True,
                "Portfolio of ~$48M; ag, equipment, small commercial RE. Credit committee presenter.",
            ),
            xp(
                "Commercial Loan Officer",
                "Heartland Community Bank",
                "Davenport, IA",
                "2010-07-01",
                "2016-03-31",
                False,
                "New business development, loan origination, annual reviews.",
            ),
            xp(
                "Credit Analyst",
                "Quad Cities Bank & Trust",
                "Rock Island, IL",
                "2006-06-01",
                "2010-06-30",
                False,
                "Spreading financials, covenant monitoring, participations.",
            ),
        ],
        "education": [
            edu("Iowa State University", "B.S.", "Finance", 2002, 2006),
        ],
        "projects": [
            proj(
                "Annual review workflow streamline",
                "Moved ag annual reviews from paper packets to a shared drive checklist. "
                "Cut processing time from three weeks to ten days.",
                None,
                ["Excel", "SharePoint"],
            ),
        ],
        "interests": [
            intr("Pheasant hunting — mediocre shot, excellent excuse to be outside"),
            intr("Iowa State football — years of experience managing disappointment"),
            intr("4-H volunteer judge, livestock projects", "volunteer"),
        ],
    },

    # ------------------------------------------------------------------
    # 5. FEMALE — Environmental health & safety coordinator, manufacturing
    # ------------------------------------------------------------------
    {
        "username": "amber_novak_ehs",
        "name": "Amber Novak",
        "email": "amber.novak@zedreq.dev",
        "password": "Amber@2024!",
        # profile_photo_url — female, white, 30s
        "profile_photo_url": "https://randomuser.me/api/portraits/women/68.jpg",
        "short_desc": "EHS coordinator · plastics & injection molding",
        "about": (
            "Environmental health & safety coordinator at an injection molding plant in the Lehigh Valley. "
            "OSHA compliance, incident investigations, chemical inventory, annual training calendar. "
            "Started as a quality tech; got pulled into EHS after a near-miss that nobody wanted to document "
            "properly. I wanted it documented properly. That's basically the job summary. "
            "CSP candidate; Penn State B.S. in Safety Science."
        ),
        "skills": "OSHA 300 log, incident investigation, SDS management, lock-out/tag-out audits, industrial hygiene sampling, JSA facilitation",
        "certificates": "OSHA 30-Hour General Industry, ASP (passed; CSP exam pending)",
        "current_status": "Open to connecting with EHS folks in manufacturing",
        "location": "Allentown, PA",
        "city": "Allentown",
        "country": "United States",
        "company": "Keystone Precision Molding",
        "title": "EHS Coordinator",
        "industry": "Plastics Manufacturing",
        "experience": [
            xp(
                "EHS Coordinator",
                "Keystone Precision Molding",
                "Allentown, PA",
                "2019-05-01",
                None,
                True,
                "Single-site EHS program; zero recordable injuries in 2022. Managed PA DEP air permit renewal.",
            ),
            xp(
                "EHS Assistant",
                "Keystone Precision Molding",
                "Allentown, PA",
                "2017-01-01",
                "2019-04-30",
                False,
                "Training scheduling, SDS library, PPE purchasing.",
            ),
            xp(
                "Quality Technician",
                "Keystone Precision Molding",
                "Allentown, PA",
                "2015-06-01",
                "2016-12-31",
                False,
                "First-article inspections, CMM operation, customer corrective actions.",
            ),
        ],
        "education": [
            edu("Pennsylvania State University", "B.S.", "Safety Sciences", 2011, 2015),
        ],
        "projects": [
            proj(
                "Near-miss reporting culture rebuild",
                "After a mold-change incident, redesigned the near-miss form to a "
                "5-question anonymous card. Submissions went from 2/year to ~30/year.",
                None,
                [],
            ),
        ],
        "interests": [
            intr("Trail running — slowest person in every 5K, happiest finisher"),
            intr("ASSE student chapter mentor", "volunteer"),
            intr("Fermenting things (kombucha, sauerkraut, occasional disaster)"),
        ],
    },
]


# ---------------------------------------------------------------------------
# Posts — images are chosen to match the content of the specific post
# ---------------------------------------------------------------------------

USER_POST_CANDIDATES: dict[str, list[dict]] = {
    # ----------------------------------------------------------------
    # Priya Mehta — instructional coach / K-12 education
    # ----------------------------------------------------------------
    "priya_mehta_edtech": [
        {
            "text": (
                "Three years into coaching and the hardest thing I do is still the debrief after "
                "a hard observation.\n\n"
                "Not the feedback itself — I've gotten better at that. The hard part is the "
                "five minutes before I walk into the room, when I have to decide whether I'm "
                "going to lead with what I saw or with a question. Nine times out of ten, the "
                "question surfaces something the data couldn't.\n\n"
                "Last week a teacher I've worked with for two years told me a lesson I thought "
                "flopped was intentionally messy — she wanted students to struggle before the "
                "anchor chart went up. She was right. My script would have missed it.\n\n"
                "Coaching tip I keep relearning: your observation notes are a hypothesis, not a verdict."
            ),
            "image": MEDIA["classroom"],
        },
        {
            "text": (
                "Every August our district rolls out something new. Every August teachers nod politely "
                "and wait to see if it'll still exist in February.\n\n"
                "That's not cynicism — that's pattern recognition. Good teachers are scientists about "
                "their own time.\n\n"
                "My job is to be the person who shows up in February still talking about it. "
                "Not because admin told me to — because I actually followed up, helped troubleshoot "
                "the parts that broke, and admitted when something wasn't worth the effort.\n\n"
                "Trust in PD isn't built in August. It's built by March."
            ),
            "image": MEDIA["whiteboard_lesson"],
        },
        {
            "text": (
                "The reading intervention group I visit on Thursdays has six kids. "
                "Three of them came in reading below grade level in September.\n\n"
                "One of those three — a kid who flatly refused to read aloud in September — "
                "read a paragraph to the whole group last week. Unprompted.\n\n"
                "I don't post outcomes often because they're never as simple as the headline. "
                "But I'll post this one. Decodable texts, consistent small group, "
                "one teacher who never once made him feel bad for not knowing. "
                "That's the whole intervention.\n\n"
                "Shoutout to every reading specialist doing invisible heroic work on a Thursday morning."
            ),
            "image": MEDIA["library_study"],
        },
        {
            "text": (
                "Hot take: Google Classroom is not an instructional tool. "
                "It's a folder with a grade book attached.\n\n"
                "That's fine — folders matter. But I've sat through too many PD sessions "
                "where turning in a PDF digitally got called 'blended learning.'\n\n"
                "If students are doing the same low-engagement task on a screen instead of paper, "
                "you've added a battery charge requirement, not a pedagogy upgrade.\n\n"
                "Edtech earns its place when it changes what's possible — "
                "differentiation, immediate feedback, student voice, real audience. "
                "Otherwise it's just expensive laminating."
            ),
            "image": None,
        },
        {
            "text": (
                "We're into standardized testing season, which means I am fielding a lot of "
                "'what does this score actually mean' from parents and, honestly, from teachers too.\n\n"
                "A percentile score tells you where a student stands relative to a norm group "
                "on one day. It does not tell you what they know, what they'll learn next, "
                "or whether their teacher is effective.\n\n"
                "I spend a chunk of my coaching hours helping teachers use classroom-based data "
                "that they collected, that reflects what they actually taught. "
                "That data changes instruction. The April score changes anxiety levels.\n\n"
                "Both matter. But they answer different questions."
            ),
            "image": MEDIA["coffee_meeting"],
        },
    ],

    # ----------------------------------------------------------------
    # Marcus Bell — water utility civil engineer
    # ----------------------------------------------------------------
    "marcus_bell_utilities": [
        {
            "text": (
                "We had a 12-inch water main break at 2 AM on a Tuesday. "
                "By 6 AM we had restored service to 340 addresses.\n\n"
                "Nobody wrote a news story. Nobody should have to — that's what 'it's working' looks like.\n\n"
                "What I want people to understand about public utilities: "
                "the quietest days are the days the most people showed up. "
                "Operators checking chlorine residuals. Maintenance crew on the leak detection van. "
                "The engineer who pushed for the valve spacing that let us isolate four blocks "
                "instead of twelve.\n\n"
                "Infrastructure is invisible until it isn't. "
                "The goal is to keep it boring."
            ),
            "image": MEDIA["city_street"],
        },
        {
            "text": (
                "Lead service line replacement update: we've completed 1,847 replacements "
                "since the federal mandate moved the deadline.\n\n"
                "What I didn't expect: the conversations on doorsteps. "
                "Half the residents think we're there to check their water bill. "
                "Half assume we're digging because something is already wrong.\n\n"
                "We started sending a one-page explanation two weeks before crew arrival. "
                "Door-answer rate went up; angry calls went down. "
                "Public works communication is as real as the pipe specification.\n\n"
                "If you're running an LSL program and skipping the community piece, "
                "you're skipping half the project."
            ),
            "image": MEDIA["concrete_pour"],
        },
        {
            "text": (
                "Someone asked me last week whether I'd considered going private sector "
                "for better pay.\n\n"
                "Probably yes on the pay. But I grew up in Gary, Indiana, "
                "where water infrastructure is not an abstraction. "
                "I know exactly who my work serves — I drive through their neighborhoods "
                "to check on our main replacement crews.\n\n"
                "Public engineering isn't for everyone. The procurement timelines alone "
                "will age you. But if you need the outcome to feel concrete, "
                "try improving a city's lead exposure numbers."
            ),
            "image": MEDIA["blueprint_desk"],
        },
        {
            "text": (
                "Quick thing nobody tells you about EPANET modeling:\n\n"
                "The model is only as good as the field data, "
                "and the field data is only as good as whoever last updated the GIS layer, "
                "and that layer was last touched in 2019 by someone who no longer works here.\n\n"
                "Every hydraulic model I've inherited has at least one pipe segment "
                "with a diameter that doesn't match what's in the ground. "
                "Usually discovered during a main break. Always during a main break.\n\n"
                "Lesson: budget time to validate your model with actual field checks "
                "before you trust it for a capital project."
            ),
            "image": None,
        },
        {
            "text": (
                "Volunteering with the fire department has made me a better utility engineer.\n\n"
                "Not because of the emergencies — because of the pre-plans. "
                "Before every shift, the crew walks through hydrant locations, "
                "flow rates, secondary supply options. They don't assume the system works. "
                "They verify it and plan for when it doesn't.\n\n"
                "I brought that habit back to my main rehab scheduling. "
                "We now map which hydrants are out of service during any repair window "
                "and notify fire dispatch before the first shovel goes in.\n\n"
                "Cross-functional communication is unglamorous. It's also how cities don't burn."
            ),
            "image": MEDIA["blueprint_roll"],
        },
    ],

    # ----------------------------------------------------------------
    # Sofía Reyes — immigration paralegal
    # ----------------------------------------------------------------
    "sofia_reyes_legal": [
        {
            "text": (
                "An RFE is not a denial. I say this to at least two clients a week.\n\n"
                "A Request for Evidence means USCIS wants more information before they decide. "
                "It's stressful — I know it's stressful — but it is a solvable problem if "
                "you respond on time with the right documentation.\n\n"
                "What tanks RFE responses: vague cover letters, missing translations, "
                "evidence that doesn't directly address the specific issue raised, "
                "and waiting until day 85 of a 90-day window.\n\n"
                "If you get an RFE: call your attorney or paralegal immediately. "
                "Read the request carefully. Make a checklist. "
                "The government gave you a roadmap. Follow it.\n\n"
                "(Not legal advice. General information only.)"
            ),
            "image": MEDIA["law_books"],
        },
        {
            "text": (
                "The biometrics appointment scares people more than it should "
                "and the interview scares people less than it does.\n\n"
                "Biometrics: you go in, they take your fingerprints and photo, you leave. "
                "Thirty minutes. Bring your appointment notice and ID. That's it.\n\n"
                "The interview is where preparation matters. You need to know your petition, "
                "know your documents, and be consistent with what you submitted. "
                "Inconsistencies — even innocent ones — create problems.\n\n"
                "We prep every client the week before. "
                "Not because the questions are traps; because knowing what to expect "
                "is how you walk in calmly instead of frozen."
            ),
            "image": MEDIA["courthouse"],
        },
        {
            "text": (
                "I've been doing this for six years. "
                "The cases that keep me up at night aren't the complicated ones — "
                "they're the ones where a translation error or a checkbox mistake "
                "from years before we got involved created a problem we now have to untangle.\n\n"
                "If you're going to file immigration paperwork on your own: "
                "use an accredited representative or attorney. "
                "If the cost is the barrier, legal aid organizations exist. "
                "I will find you one.\n\n"
                "A $50 online filing service cannot write you a brief "
                "if USCIS questions your case. A paralegal can help prepare the response. "
                "A notario who is not an attorney cannot legally represent you. Please know the difference."
            ),
            "image": None,
        },
        {
            "text": (
                "My mom's naturalization ceremony was in a federal courthouse "
                "with about 80 other people from 30-something countries.\n\n"
                "The clerk called each country of origin alphabetically. "
                "When he called Colombia, she stood up and said 'here' like she was in class.\n\n"
                "I work on these cases every day and that ceremony still got me. "
                "Paperwork is how you get there. "
                "That's why I care about the paperwork."
            ),
            "image": MEDIA["contract_signing"],
        },
        {
            "text": (
                "Hiring a paralegal who speaks the client's language is not a nice-to-have "
                "in immigration law. It's a risk management decision.\n\n"
                "Errors in client intake — dates, relationships, entry history — "
                "often happen not because clients are careless but because "
                "the intake form is in English and the explanation of what's being asked "
                "is also in English, which the client speaks partially or under stress.\n\n"
                "We added Spanish intake forms in 2021. "
                "Our intake correction rate dropped. "
                "Our attorney time on clarifications dropped. "
                "Clients showed up to consultations with the right documents more often.\n\n"
                "Language access is process improvement. Firms who don't see that are leaving errors on the table."
            ),
            "image": MEDIA["office_whiteboard"],
        },
    ],

    # ----------------------------------------------------------------
    # Brett Holloway — community bank commercial lender
    # ----------------------------------------------------------------
    "brett_holloway_banking": [
        {
            "text": (
                "I drove 40 minutes down a county road to look at collateral last Tuesday. "
                "Grain bins, a machine shed, and about 600 acres of well-drained corn ground.\n\n"
                "Finance people ask why community bankers make site visits "
                "when you can pull an appraisal.\n\n"
                "Because an appraisal won't tell you the landlord is retiring and might sell, "
                "or that the pivot in the south field has needed a gear since April, "
                "or that the guy you're lending to has his neighbor's kids helping at harvest "
                "because the operation is actually healthy enough to share.\n\n"
                "Context lives on the ground. "
                "The spread sheet confirms what the visit already told you."
            ),
            "image": MEDIA["spreadsheet_coffee"],
        },
        {
            "text": (
                "Community banking is relationship lending, which means "
                "you sometimes lend to people whose financials you could decline "
                "and choose not to — and sometimes you decline people you genuinely like.\n\n"
                "The second one is harder. "
                "I've had to tell good farmers with bad timing that we can't structure it this year. "
                "Every time I try to give them something useful from the conversation: "
                "what the coverage ratio looks like now, what would need to change, "
                "who else might be a fit.\n\n"
                "A decline with a roadmap is a better product than a decline with a form letter. "
                "Most people come back when things change — if you treated them right."
            ),
            "image": MEDIA["desk_paperwork"],
        },
        {
            "text": (
                "The ag operating line renewals are hitting right now. "
                "Input costs are still elevated. "
                "Some operations that looked fine two years ago are tighter than they'd like.\n\n"
                "I'm not panicking because I know these customers and I know their land. "
                "But I am having a lot of honest conversations about working capital cushions "
                "and what the rental rate market looks like for next year.\n\n"
                "If you're a farmer dealing with a lender who went silent on you: "
                "ask the direct question. 'Where do I stand?' is a reasonable thing to say. "
                "A lender who can't answer that clearly isn't doing their job."
            ),
            "image": None,
        },
        {
            "text": (
                "Attended the Iowa State Bankers Association conference this week. "
                "Three sessions on AI in underwriting, one session on community reinvestment.\n\n"
                "I think we've got the ratio slightly backwards.\n\n"
                "The algorithm is not why a third-generation farmer trusts you with a line of credit. "
                "The algorithm didn't come to the funeral. "
                "The algorithm didn't help restructure when the 2012 drought hit.\n\n"
                "Use the tools. "
                "Don't outsource the relationship."
            ),
            "image": MEDIA["coffee_meeting"],
        },
        {
            "text": (
                "Judged the livestock showmanship at the county fair on Saturday as a 4-H volunteer.\n\n"
                "Eleven-year-old walked a market steer twice her size around the ring "
                "like she'd been doing it for years. Turns out she had — it was her third year.\n\n"
                "I lend to agricultural operations. "
                "The best insight into whether an operation has a future is whether "
                "the next generation is paying attention.\n\n"
                "She was paying very close attention. Good sign."
            ),
            "image": MEDIA["city_street"],
        },
    ],

    # ----------------------------------------------------------------
    # Amber Novak — EHS coordinator, plastics manufacturing
    # ----------------------------------------------------------------
    "amber_novak_ehs": [
        {
            "text": (
                "Near-miss reports are a gift. "
                "Most companies treat them like an admission of guilt.\n\n"
                "When I took this role, we had logged 2 near-misses in the previous calendar year. "
                "Not because the plant was safe — because nobody trusted that reporting "
                "wouldn't come back on them.\n\n"
                "We redesigned the form: anonymous, five questions, drop box by the timeclock. "
                "Year one: 14 reports. Year two: 31. "
                "Did the plant get more dangerous? No. "
                "It got more honest.\n\n"
                "If your near-miss rate is suspiciously low, "
                "ask whether your reporting culture is safe — not whether your plant is."
            ),
            "image": MEDIA["warehouse_racks"],
        },
        {
            "text": (
                "OSHA 300 log season is not my favorite time of year.\n\n"
                "Not because of the recording — that I can do in my sleep at this point. "
                "It's the conversations before posting where a supervisor tries to make the "
                "case that a recordable is actually first aid if you look at it sideways.\n\n"
                "I don't look at it sideways. I look at the OSHA definitions.\n\n"
                "If you're in EHS and feeling pressure to misclassify: "
                "document the conversation. "
                "The record you're being asked to minimize will outlast the pressure."
            ),
            "image": MEDIA["desk_paperwork"],
        },
        {
            "text": (
                "Did a LOTO audit this week. Found three energy control procedures "
                "that hadn't been reviewed since the machine was installed in 2018.\n\n"
                "The procedures weren't wrong — the equipment hadn't changed much. "
                "But two of the machines had a secondary hydraulic circuit added in 2021 "
                "that nobody updated the ECP for.\n\n"
                "That is the audit finding that doesn't look like much on paper "
                "and is how people get seriously hurt.\n\n"
                "If your LOTO procedures haven't been reviewed since 'whenever we bought the machine,' "
                "that's not a schedule, that's a gap."
            ),
            "image": MEDIA["forklift_aisle"],
        },
        {
            "text": (
                "I passed the ASP exam last fall and I'm sitting for the CSP this spring.\n\n"
                "I want to say something to anyone in EHS who is earlier in their career and "
                "looking at the certification path and thinking it seems like a lot:\n\n"
                "It is a lot. The body of knowledge is wide. "
                "I studied in 30-minute windows at 5:30 AM because that was the window I had.\n\n"
                "But the process of studying for the exam made me better at the job "
                "before I ever sat for the test. "
                "The industrial hygiene section alone changed how I was doing air sampling.\n\n"
                "Worth it. Grind is real. Worth it."
            ),
            "image": None,
        },
        {
            "text": (
                "The SDS library used to be a binder on a shelf in the corner of the maintenance room.\n\n"
                "I am not exaggerating. One binder. "
                "The plant runs about 60 chemicals at any given time.\n\n"
                "We migrated to a digital system two years ago. "
                "Took six weeks to cross-reference every chemical on the floor "
                "with a current SDS, get them uploaded, and train shift leads on how to pull them.\n\n"
                "Last month a new material came in without a datasheet. "
                "The receiving team flagged it immediately and sent the lot back. "
                "Six weeks of setup paid for itself in one shift.\n\n"
                "EHS infrastructure is invisible until it works. "
                "That's what success looks like."
            ),
            "image": MEDIA["loading_dock"],
        },
    ],
}


# ---------------------------------------------------------------------------
# Post selector
# ---------------------------------------------------------------------------

def pick_posts_for_user(username: str, rng: random.Random) -> list[dict]:
    pool = USER_POST_CANDIDATES.get(username, [])
    if not pool:
        return []
    n_max = min(len(pool), 4)
    n_min = min(2, n_max)
    k = rng.randint(n_min, n_max)
    shuffled = pool[:]
    rng.shuffle(shuffled)
    return shuffled[:k]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed batch 3 realistic users only")
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    master_seed = args.seed if args.seed is not None else random.randrange(2**31)
    rng = random.Random(master_seed)
    posts = {u["username"]: pick_posts_for_user(u["username"], rng) for u in USERS}

    print("=" * 65)
    print("  ZedReq — realistic seed (batch 3 only)")
    print("  Tip: use seed_data/seed_realistic_run_all.py for all batches + full graph")
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