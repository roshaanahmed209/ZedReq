"""
Batch 1: ten professional personas with full profiles (experience, education, projects, interests),
LinkedIn-style posts, and connections among seeded users.

Prefer the combined runner so batch 1 + 2 connect to each other:
    python seed_data/seed_realistic_run_all.py

This file alone (batch 1 only):
    python seed_data/seed_realistic_users.py
"""

from __future__ import annotations

import argparse
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

from seed_data.seed_realistic_common import POST_MEDIA_URLS, edu, get_db_default, intr, proj, run_full_seed, xp

from utils.auth import hash_password

# Profile pics / covers left blank → stable https URLs assigned in run_full_seed


USERS = [
    {
        "username": "sarah_chen_dev",
        "name": "Sarah Chen",
        "email": "sarah.chen@zedreq.dev",
        "password": "Sarah@2024!",
        "short_desc": "Engineering lead · product infra",
        "about": (
            "I lead a small platform team at a mid-size fintech (about 400 engineers company-wide). "
            "Most days: API design, on-call hygiene, and helping teams ship without painting themselves into corners. "
            "Before this I spent four years at an agency — learned to estimate, communicate, and say no. "
            "Bay Area native; I take long walks when specs get fuzzy."
        ),
        "skills": "TypeScript, React, Node.js, PostgreSQL, system design, mentoring, technical writing",
        "certificates": "AWS Solutions Architect – Associate",
        "current_status": "Not looking — happy where I am",
        "location": "Oakland, CA",
        "city": "Oakland",
        "country": "United States",
        "company": "Northbridge Payments",
        "title": "Staff Software Engineer",
        "industry": "Financial Services",
        "experience": [
            xp(
                "Staff Software Engineer",
                "Northbridge Payments",
                "Oakland, CA",
                "2021-02-01",
                None,
                True,
                "Owns internal tooling for service deployment and feature flags. Reduced incident MTTR by focusing on runbooks and dashboards.",
            ),
            xp(
                "Senior Software Engineer",
                "Northbridge Payments",
                "Oakland, CA",
                "2018-06-01",
                "2021-01-31",
                False,
                "Frontend and API work for merchant onboarding; helped migrate a legacy Angular app to React.",
            ),
            xp(
                "Software Engineer",
                "Brightline Digital",
                "San Francisco, CA",
                "2015-09-01",
                "2018-05-31",
                False,
                "Client projects — React, Rails, content sites. Learned to ship under fixed bids.",
            ),
        ],
        "education": [
            edu("UC Berkeley", "B.A.", "Computer Science", 2011, 2015),
            edu("Coursera", "Certificate", "Machine Learning", 2019, 2019, description="Andrew Ng course — baseline for ML discussions with data team"),
        ],
        "projects": [
            proj(
                "Team RFC templates",
                "Open-sourced internal templates for lightweight RFCs; ~400 stars on GitHub.",
                "https://github.com",
                ["Markdown"],
            ),
        ],
        "interests": [intr("Trail running"), intr("Single-origin coffee"), intr("Public transit", "cause")],
    },
    {
        "username": "marcus_thompson_pm",
        "name": "Marcus Thompson",
        "email": "marcus.thompson@zedreq.dev",
        "password": "Marcus@2024!",
        "short_desc": "Product manager · B2B SaaS",
        "about": (
            "PM for a workforce scheduling product used by hospitals and retail chains in the US and Canada. "
            "I care about discovery, pricing experiments, and not shipping features nobody asked for. "
            "Ex-consultant (two years) — left when I realized I wanted to own outcomes, not slides. "
            "Based in Chicago; two kids under six."
        ),
        "skills": "Product discovery, SQL, Amplitude, Figma, stakeholder management, writing",
        "certificates": "Scrum Product Owner (PSPO I)",
        "current_status": "Open to advisory conversations only",
        "location": "Chicago, IL",
        "city": "Chicago",
        "country": "United States",
        "company": "ShiftWell Software",
        "title": "Principal Product Manager",
        "industry": "Computer Software",
        "experience": [
            xp(
                "Principal Product Manager",
                "ShiftWell Software",
                "Chicago, IL",
                "2019-04-01",
                None,
                True,
                "0→1 mobile app for shift swaps; now focused on enterprise rollout and integrations.",
            ),
            xp(
                "Product Manager",
                "ShiftWell Software",
                "Chicago, IL",
                "2016-01-01",
                "2019-03-31",
                False,
                "Growth experiments, onboarding funnel, first paid pilots.",
            ),
            xp(
                "Associate",
                "Helix Strategy Group",
                "Chicago, IL",
                "2014-08-01",
                "2015-12-31",
                False,
                "Market sizing and due diligence for PE clients.",
            ),
        ],
        "education": [
            edu("Northwestern University", "M.B.A.", "Marketing & Strategy", 2012, 2014),
            edu("University of Illinois", "B.S.", "Industrial Engineering", 2008, 2012),
        ],
        "projects": [
            proj(
                "Scheduling ROI calculator",
                "Internal spreadsheet-turned-web-tool for sales; adopted by CS team.",
                None,
                ["Sheets", "Retool"],
            ),
        ],
        "interests": [intr("Youth basketball coach", "volunteer"), intr("Jazz"), intr("Deep dish pizza", "personal")],
    },
    {
        "username": "priya_sharma_ml",
        "name": "Priya Sharma",
        "email": "priya.sharma@zedreq.dev",
        "password": "Priya@2024!",
        "short_desc": "Applied scientist · recommendations",
        "about": (
            "I work on ranking and relevance for a regional e-commerce marketplace (think furniture + home goods). "
            "Not FAANG — we move slower but I touch the full stack from offline jobs to online serving. "
            "From Pune; moved to Toronto in 2018. I write short technical notes for my team, not viral threads."
        ),
        "skills": "Python, PyTorch, SQL, Spark, A/B testing, data pipelines",
        "certificates": "Deep Learning Specialization (Coursera)",
        "current_status": "Open to speaking at local meetups",
        "location": "Toronto, ON",
        "city": "Toronto",
        "country": "Canada",
        "company": "Homestead Marketplaces Inc.",
        "title": "Senior Applied Scientist",
        "industry": "Internet",
        "experience": [
            xp(
                "Senior Applied Scientist",
                "Homestead Marketplaces Inc.",
                "Toronto, ON",
                "2020-03-01",
                None,
                True,
                "Search ranking, cold-start recommendations, monitoring for model drift.",
            ),
            xp(
                "Data Scientist",
                "Homestead Marketplaces Inc.",
                "Toronto, ON",
                "2018-05-01",
                "2020-02-29",
                False,
                "Attribution modeling, cohort analysis, first ML prototypes.",
            ),
            xp(
                "Analyst",
                "Retail Analytics Co.",
                "Pune, India",
                "2016-07-01",
                "2018-03-31",
                False,
                "SQL reporting for FMCG clients.",
            ),
        ],
        "education": [
            edu("University of Toronto", "M.Sc.", "Applied Computing", 2016, 2018),
            edu("University of Pune", "B.E.", "Information Technology", 2012, 2016),
        ],
        "projects": [
            proj(
                "Notebook: practical recsys eval",
                "Internal wiki series on offline metrics we actually trust.",
                None,
                ["Python"],
            ),
        ],
        "interests": [intr("Hiking in Ontario parks"), intr("Malayalam cinema"), intr("Mentoring newcomers", "volunteer")],
    },
    {
        "username": "james_rodriguez_devops",
        "name": "James Rodriguez",
        "email": "james.rodriguez@zedreq.dev",
        "password": "James@2024!",
        "short_desc": "Platform engineer · reliability",
        "about": (
            "Kubernetes, Terraform, and the boring parts that keep payments flowing. "
            "I work for a logistics company you've seen on the side of trucks — internal platforms, not consumer apps. "
            "Veteran; transitioned through a coding bootcamp and a lot of self-study. I value clear handoffs and honest postmortems."
        ),
        "skills": "Kubernetes, Terraform, AWS, Go, Bash, Prometheus, Grafana",
        "certificates": "CKA, AWS SysOps Associate",
        "current_status": "Currently employed",
        "location": "Dallas, TX",
        "city": "Dallas",
        "country": "United States",
        "company": "Continental Freight Systems",
        "title": "Senior Platform Engineer",
        "industry": "Transportation / Trucking",
        "experience": [
            xp(
                "Senior Platform Engineer",
                "Continental Freight Systems",
                "Dallas, TX",
                "2021-01-01",
                None,
                True,
                "EKS clusters, GitOps, cost dashboards for compute.",
            ),
            xp(
                "DevOps Engineer",
                "MedDevice Cloud",
                "Austin, TX",
                "2018-04-01",
                "2020-12-31",
                False,
                "CI/CD for regulated environments; lots of change tickets.",
            ),
            xp(
                "IT Specialist",
                "US Army",
                "Various",
                "2012-01-01",
                "2016-12-31",
                False,
                "Networking, help desk escalation, security compliance tasks.",
            ),
        ],
        "education": [
            edu("Southern New Hampshire University", "B.S.", "Information Technology", 2017, 2020),
        ],
        "projects": [
            proj(
                "Homelab GitOps",
                "Personal cluster for experimenting with Argo CD and sealed secrets.",
                None,
                ["Kubernetes", "Terraform"],
            ),
        ],
        "interests": [intr("Barbecue"), intr("Veteran peer mentoring", "volunteer"), intr("Fishing")],
    },
    {
        "username": "aisha_okafor_design",
        "name": "Aisha Okafor",
        "email": "aisha.okafor@zedreq.dev",
        "password": "Aisha@2024!",
        "short_desc": "Product designer · design systems",
        "about": (
            "Designer at a health-tech startup building tools for small clinic workflows — scheduling, billing, patient comms. "
            "Before that: in-house at a university press (yes, books). I care about typography, accessible forms, and designers who read contracts."
        ),
        "skills": "Figma, research, prototyping, WCAG, design systems, workshop facilitation",
        "certificates": "NN/g UX Certification",
        "current_status": "Select freelance (referral only)",
        "location": "Philadelphia, PA",
        "city": "Philadelphia",
        "country": "United States",
        "company": "ClinicFlow Health",
        "title": "Lead Product Designer",
        "industry": "Hospital & Health Care",
        "experience": [
            xp(
                "Lead Product Designer",
                "ClinicFlow Health",
                "Philadelphia, PA",
                "2020-09-01",
                None,
                True,
                "Design system, component library with eng, research with office managers.",
            ),
            xp(
                "Product Designer",
                "ClinicFlow Health",
                "Philadelphia, PA",
                "2018-01-01",
                "2020-08-31",
                False,
                "End-to-end flows for billing and reminders.",
            ),
            xp(
                "Designer",
                "Temple University Press",
                "Philadelphia, PA",
                "2015-06-01",
                "2017-12-31",
                False,
                "Book covers, marketing collateral, web maintenance.",
            ),
        ],
        "education": [
            edu("Tyler School of Art, Temple University", "B.F.A.", "Graphic Design", 2011, 2015),
        ],
        "projects": [
            proj(
                "Accessible form patterns",
                "Blog series + Figma kit shared with local UX meetup.",
                None,
                [],
            ),
        ],
        "interests": [intr("Letterpress printing"), intr("City planning", "cause"), intr("Cooking West African recipes")],
    },
    {
        "username": "liam_walsh_backend",
        "name": "Liam Walsh",
        "email": "liam.walsh@zedreq.dev",
        "password": "Liam@2024!",
        "short_desc": "Backend engineer · payments-ish",
        "about": (
            "Python and Postgres for an Irish subscription-box company (meal kits + add-ons). "
            "Remote from Cork. I like idempotent webhooks, clear error messages, and PRs that explain the 'why'. "
            "Previously built internal tools at a bank — slower releases, good lessons in compliance."
        ),
        "skills": "Python, Django, PostgreSQL, Redis, Celery, Docker",
        "certificates": "",
        "current_status": "Currently employed",
        "location": "Cork, Ireland",
        "city": "Cork",
        "country": "Ireland",
        "company": "HarborBox Meals",
        "title": "Senior Backend Engineer",
        "industry": "Food & Beverages",
        "experience": [
            xp(
                "Senior Backend Engineer",
                "HarborBox Meals",
                "Cork, Ireland",
                "2021-05-01",
                None,
                True,
                "Billing integrations, subscription lifecycle, partner APIs.",
            ),
            xp(
                "Backend Engineer",
                "HarborBox Meals",
                "Cork, Ireland",
                "2019-02-01",
                "2021-04-30",
                False,
                "Inventory sync, warehouse integrations.",
            ),
            xp(
                "Software Developer",
                "First Provincial Bank",
                "Dublin, Ireland",
                "2016-09-01",
                "2019-01-31",
                False,
                "Internal reporting tools and batch jobs.",
            ),
        ],
        "education": [
            edu("University College Cork", "B.Sc.", "Computer Science", 2012, 2016),
        ],
        "projects": [
            proj(
                "webhook retry library",
                "Small OSS helper for exponential backoff + dead-letter patterns.",
                "https://github.com",
                ["Python"],
            ),
        ],
        "interests": [intr("Rugby club supporter"), intr("Sea swimming"), intr("Guitar")],
    },
    {
        "username": "mei_zhang_ai",
        "name": "Mei Zhang",
        "email": "mei.zhang@zedreq.dev",
        "password": "Mei@2024!",
        "short_desc": "ML engineer · NLP for support tools",
        "about": (
            "I fine-tune and evaluate language models for customer-support assist (suggestions, not auto-send). "
            "Company: B2B helpdesk SaaS, ~200 people. I collaborate daily with support leads — the model is useless if reps won't trust it. "
            "Vancouver. I avoid hype posts; I prefer writing internal postmortems when evals regress."
        ),
        "skills": "Python, PyTorch, Hugging Face, evaluation design, prompt tooling, SQL",
        "certificates": "",
        "current_status": "Not looking",
        "location": "Vancouver, BC",
        "city": "Vancouver",
        "country": "Canada",
        "company": "Deskline",
        "title": "Machine Learning Engineer",
        "industry": "Computer Software",
        "experience": [
            xp(
                "Machine Learning Engineer",
                "Deskline",
                "Vancouver, BC",
                "2022-01-01",
                None,
                True,
                "Assistive drafting for tickets, safety filters, human-in-the-loop review tooling.",
            ),
            xp(
                "Software Engineer",
                "Deskline",
                "Vancouver, BC",
                "2019-06-01",
                "2021-12-31",
                False,
                "Search and routing features for ticket queues.",
            ),
        ],
        "education": [
            edu("University of British Columbia", "M.Sc.", "Computer Science", 2017, 2019),
            edu("Simon Fraser University", "B.Sc.", "Computing Science", 2013, 2017),
        ],
        "projects": [
            proj(
                "Eval notebook templates",
                "Standardized notebooks for regression testing on support datasets.",
                None,
                ["Python", "Jupyter"],
            ),
        ],
        "interests": [intr("Hiking BC"), intr("Speculative fiction"), intr("Women in ML meetups", "volunteer")],
    },
    {
        "username": "daniel_osei_frontend",
        "name": "Daniel Osei",
        "email": "daniel.osei@zedreq.dev",
        "password": "Daniel@2024!",
        "short_desc": "Frontend engineer · remote from Accra",
        "about": (
            "I build admin dashboards for a European travel insurance API company — React, TypeScript, lots of forms and tables. "
            "Fully remote; overlap hours with CET. Before this, freelanced for local NGOs on WordPress and small React apps. "
            "I care about performance on slow networks and keyboard accessibility."
        ),
        "skills": "React, TypeScript, Vite, TanStack Query, testing-library, Storybook",
        "certificates": "Meta Front-End Developer Certificate",
        "current_status": "Open to part-time mentoring",
        "location": "Accra, Ghana",
        "city": "Accra",
        "country": "Ghana",
        "company": "SafeTrip Europe API",
        "title": "Senior Frontend Engineer",
        "industry": "Insurance",
        "experience": [
            xp(
                "Senior Frontend Engineer",
                "SafeTrip Europe API",
                "Remote",
                "2021-03-01",
                None,
                True,
                "Partner portal, claims review UI, design-system adoption.",
            ),
            xp(
                "Frontend Developer",
                "SafeTrip Europe API",
                "Remote",
                "2019-01-01",
                "2021-02-28",
                False,
                "Greenfield React app replacing legacy jQuery screens.",
            ),
            xp(
                "Freelance Web Developer",
                "Self-employed",
                "Accra, Ghana",
                "2017-06-01",
                "2018-12-31",
                False,
                "Sites for NGOs and a local restaurant group.",
            ),
        ],
        "education": [
            edu("Ashesi University", "B.A.", "Computer Science", 2013, 2017),
        ],
        "projects": [
            proj(
                "a11y checklist extension",
                "Browser extension prototype for internal QA (never shipped publicly).",
                None,
                ["TypeScript"],
            ),
        ],
        "interests": [intr("Afrobeats production"), intr("Youth coding workshops", "volunteer"), intr("Premier League")],
    },
    {
        "username": "emma_sullivan_sec",
        "name": "Emma Sullivan",
        "email": "emma.sullivan@zedreq.dev",
        "password": "Emma@2024!",
        "short_desc": "Security engineer · appsec",
        "about": (
            "Application security for a national grocery retailer's e-commerce stack. "
            "Lots of scanning, threat modeling with squads, and helping developers fix things without shame. "
            "Based in Manchester. OSCP holder; I still get nervous before every engagement."
        ),
        "skills": "AppSec, Burp, secure SDLC, Python, cloud IAM basics, threat modeling",
        "certificates": "OSCP, CompTIA Security+",
        "current_status": "Currently employed",
        "location": "Manchester, UK",
        "city": "Manchester",
        "country": "United Kingdom",
        "company": "FreshBasket Retail Group",
        "title": "Senior Application Security Engineer",
        "industry": "Retail",
        "experience": [
            xp(
                "Senior Application Security Engineer",
                "FreshBasket Retail Group",
                "Manchester, UK",
                "2020-11-01",
                None,
                True,
                "SSDLC gates, pentest coordination, secure coding training.",
            ),
            xp(
                "Security Engineer",
                "FreshBasket Retail Group",
                "Manchester, UK",
                "2018-04-01",
                "2020-10-31",
                False,
                "Vulnerability management, SIEM tuning with SOC.",
            ),
            xp(
                "IT Security Analyst",
                "Regional Bank PLC",
                "Leeds, UK",
                "2016-09-01",
                "2018-03-31",
                False,
                "Access reviews, phishing simulations, policy updates.",
            ),
        ],
        "education": [
            edu("University of Manchester", "M.Sc.", "Advanced Computer Science", 2015, 2016),
            edu("University of Leeds", "B.Sc.", "Computer Science", 2012, 2015),
        ],
        "projects": [
            proj(
                "Secure coding lunch talks",
                "Internal series — 30 min, pizza funded, no recording pressure.",
                None,
                [],
            ),
        ],
        "interests": [intr("Parkrun"), intr("Board games"), intr("STEM school visits", "volunteer")],
    },
    {
        "username": "arjun_mehta_fullstack",
        "name": "Arjun Mehta",
        "email": "arjun.mehta@zedreq.dev",
        "password": "Arjun@2024!",
        "short_desc": "Full-stack engineer · streaming infra",
        "about": (
            "I work on internal tooling for video encoding pipelines — not the glamorous consumer app, but the jobs that "
            "transcode and QC content before it hits apps. Company is mid-market streaming tech. "
            "Bangalore → moved to Austin in 2021. I like boring tech that scales: queues, workers, observability."
        ),
        "skills": "Java, Spring Boot, React, Kafka, PostgreSQL, AWS",
        "certificates": "AWS Developer Associate",
        "current_status": "Currently employed",
        "location": "Austin, TX",
        "city": "Austin",
        "country": "United States",
        "company": "StreamFoundry",
        "title": "Senior Software Engineer",
        "industry": "Entertainment",
        "experience": [
            xp(
                "Senior Software Engineer",
                "StreamFoundry",
                "Austin, TX",
                "2021-08-01",
                None,
                True,
                "Workflow orchestration for transcoding, admin APIs, on-call for pipeline incidents.",
            ),
            xp(
                "Software Engineer",
                "StreamFoundry",
                "Austin, TX",
                "2019-01-01",
                "2021-07-31",
                False,
                "Microservices for metadata extraction.",
            ),
            xp(
                "Software Engineer",
                "Bangalore SaaS Studio",
                "Bangalore, India",
                "2016-07-01",
                "2018-12-31",
                False,
                "CRUD apps, first exposure to Kafka and Docker.",
            ),
        ],
        "education": [
            edu("University of Texas at Austin", "M.S.", "Computer Science", 2019, 2021),
            edu("BITS Pilani", "B.E.", "Computer Science", 2012, 2016),
        ],
        "projects": [
            proj(
                "encoding cost simulator",
                "Spreadsheet + small CLI the team uses for rough job cost estimates.",
                None,
                ["Python"],
            ),
        ],
        "interests": [intr("Cricket league"), intr("BBQ"), intr("Mentoring international students", "volunteer")],
    },
]


USER_POSTS = {
    "sarah_chen_dev": [
        {
            "text": (
                "Yesterday our on-call rotation caught a deploy that doubled latency on one shard — not a hero moment, "
                "just someone who read the dashboard and rolled back within minutes. That's the culture I'm trying to protect."
            ),
            "image": None,
        },
        {
            "text": (
                "Junior on the team asked whether they should 'learn Kubernetes' or 'get better at SQL.' "
                "I said: pick the problem your team is actually fighting next quarter. Generic career ladders mislead people."
            ),
            "image": POST_MEDIA_URLS[0],
        },
    ],
    "marcus_thompson_pm": [
        {
            "text": (
                "We almost built a 'manager override' for the scheduling rules. User research showed managers hated the idea — "
                "they wanted fewer exceptions, not more power. Back to the drawing board, and honestly relieved."
            ),
            "image": None,
        },
        {
            "text": "Tip for PMs in regulated spaces: bring Legal in early on copy, not just on policy. Saves weeks.",
            "image": POST_MEDIA_URLS[1],
        },
    ],
    "priya_sharma_ml": [
        {
            "text": (
                "Our offline metric looked great; online, click-through barely moved. Turns out we were optimizing for the wrong slice. "
                "Humbling week — but the partnership with merchandising is stronger now."
            ),
            "image": None,
        },
        {
            "text": "If you're training ranking models, spend time on position bias before you tune architecture. Boring advice, still true.",
            "image": None,
        },
    ],
    "james_rodriguez_devops": [
        {
            "text": (
                "Post-incident: we didn't have a single root cause — we had three contributing factors and one lucky break. "
                "Anyone selling 'five whys to perfection' hasn't run ops at scale."
            ),
            "image": POST_MEDIA_URLS[2],
        },
        {
            "text": "Shoutout to finance for approving the reserved instances we asked for in August. Capacity planning is a team sport.",
            "image": None,
        },
    ],
    "aisha_okafor_design": [
        {
            "text": (
                "Accessibility audit on our patient intake form: 14 issues, half were label/input mismatches. "
                "Fixing them reduced support calls from clinics. Design details are business details."
            ),
            "image": None,
        },
        {
            "text": "Running a 45-min Figma session for customer success tomorrow — they asked to learn components. Excited.",
            "image": POST_MEDIA_URLS[3],
        },
    ],
    "liam_walsh_backend": [
        {
            "text": (
                "Webhook partner changed their retry policy without telling us. We handled it, but I'm drafting a clearer SLA section "
                "for the next contract. Communication beats clever code."
            ),
            "image": None,
        },
        {
            "text": "Django admin saved us again for an internal ops task. Sometimes the boring tool is the right tool.",
            "image": None,
        },
    ],
    "mei_zhang_ai": [
        {
            "text": (
                "We turned off a 'helpful' suggestion model after reps said it added cognitive load. Metrics aren't the whole story — "
                "listen to the people on the phone."
            ),
            "image": None,
        },
        {
            "text": "Writing eval sets is unglamorous work. If your team skips it, you'll pay in production weirdness.",
            "image": POST_MEDIA_URLS[4],
        },
    ],
    "daniel_osei_frontend": [
        {
            "text": (
                "Shipped keyboard navigation fixes for our claims table — one insurance partner actually sent a thank-you email. "
                "Rare and motivating."
            ),
            "image": None,
        },
        {
            "text": "Working from Accra with CET overlap means my mornings are quiet. I've learned to protect deep work then.",
            "image": None,
        },
    ],
    "emma_sullivan_sec": [
        {
            "text": (
                "Ran a threat modeling session with the checkout squad — developers brought better abuse cases than the slide deck. "
                "Security works when it's a conversation, not a gate."
            ),
            "image": POST_MEDIA_URLS[5],
        },
        {
            "text": "If you're new to AppSec: learn to read stack traces calmly. Half of triage is patience.",
            "image": None,
        },
    ],
    "arjun_mehta_fullstack": [
        {
            "text": (
                "Encoding queue backlog last night — not glamorous, but we added a temporary worker fleet and cleared it by morning. "
                "Thanks to whoever documented the runbook last year."
            ),
            "image": None,
        },
        {
            "text": "Mentoring note: explaining distributed systems with a coffee shop analogy still works in 2026.",
            "image": None,
        },
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed batch 1 realistic users only")
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    print("=" * 65)
    print("  ZedReq — realistic seed (batch 1 only)")
    print("  Tip: use seed_data/seed_realistic_run_all.py for batch 1 + 2 + full graph")
    print("=" * 65)

    run_full_seed(
        USERS,
        USER_POSTS,
        hash_password_fn=hash_password,
        get_db_fn=get_db_default,
        seed=args.seed,
        download_images=not args.no_download,
        augment_posts=True,
    )


if __name__ == "__main__":
    main()
