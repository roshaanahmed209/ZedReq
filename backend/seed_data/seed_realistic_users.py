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
            "text": """Last Thursday looked ordinary until our latency graph for merchant onboarding started climbing — not a spike, a slow bleed across two regions.

On-call paged me while I was in a school pickup line. I handed the phone to my partner, drove home, and joined a bridge with two engineers I trust to disagree with me politely. The first theory was a bad deploy; git history said otherwise. The second theory was database — replication lag looked fine. The third was a feature flag that increased payload size on a path that had always been 'low risk.'

We split work: one person reproduced with recorded traffic, one traced the flag rollout timeline, I coordinated with risk so we didn't freeze payments longer than necessary. We rolled back the flag for 12% of traffic first, watched error budgets, then the rest.

What I keep thinking about isn't the rollback — it's that the engineer who shipped the flag had followed every checklist we wrote. The checklist didn't include 'measure body size percentiles on this endpoint under peak.' We're adding that now, plus a blameless review invite to the PM who asked for the experiment.

If you lead platform: your next incident might be 'by the book' and still wrong. Update the book.""",
            "image": None,
        },
        {
            "text": """A junior engineer pulled me aside after planning and asked a question I've heard a hundred times in shorter form: 'Should I go deep on Kubernetes or double down on SQL this year?'

I used to answer with frameworks and skill matrices. This time I asked what problem their squad will fight in Q3. They talked about slow queries in a reporting service and fear of touching Helm charts. We mapped two milestones: one month on SQL explain plans with a buddy, one spike on reading — not rewriting — our current charts.

Career advice isn't one-size-fits-all. The best learning plan I've seen is tied to a real constraint your team pays for in incidents or velocity. Everything else is procrastination with a LinkedIn certificate.

Happy to compare notes if you're mentoring someone early in platform work — what's worked for your folks?""",
            "image": POST_MEDIA_URLS[0],
        },
    ],
    "marcus_thompson_pm": [
        {
            "text": """We spent six weeks designing a 'manager override' for scheduling rules — the story was that store managers needed flexibility when the algorithm was too strict.

When we finally put paper prototypes in front of eight managers, the mood surprised me. They didn't want more power; they wanted fewer edge cases that made them look unfair to staff. One person said, quietly, 'If I override, someone posts about it on Facebook that night.'

We killed the override concept and reframed the roadmap around transparency: show why a shift was proposed, let staff swap within guardrails, and give managers an audit trail instead of a magic button. Engineering pushed back on scope — fair — so we cut a different feature that had lukewarm research.

The lesson I'm carrying: sometimes 'empowerment' in a PRD is actually liability in real life. Listen for the fear behind the feature request.

If you've ever killed something expensive after research, how did you communicate it upward without sounding like you wasted time?""",
            "image": None,
        },
        {
            "text": """Six months ago Legal flagged copy in our mobile onboarding for a state we were about to launch in. We had already built screens, animations, the whole sprint was 'done.'

The old me would have negotiated wording in Slack threads for weeks. This time I booked Legal, Design, and Compliance for a single working session with the actual strings in Figma comments. We resolved 80% of blockers live, documented the rest as a checklist for the next state rollout, and shipped two weeks later than hoped — but with zero emergency weekend rewrites.

Bring Legal early on words, not only on policy documents. Saves money, saves marriages, saves whatever patience your engineers have left.""",
            "image": POST_MEDIA_URLS[1],
        },
    ],
    "priya_sharma_ml": [
        {
            "text": """Our offline ranking model looked like a win: NDCG up, calibration pretty, stakeholders smiling in the review deck.

Then we shipped to a slice of live traffic and… almost nothing moved where it mattered — add-to-cart on long-tail categories. Two painful days later we realized we had been optimizing for users who already converted; the model barely touched cold visitors. Merchandising had been saying this in softer language for weeks; I wish I'd listened harder sooner.

We regrouped with a simple rule: every metric has a name and a person who loses sleep if it lies. We rebuilt the training slice with explicit cold-start buckets, added a human spot-check ritual before large experiments, and — this mattered — put a merchandising partner in the weekly model review, not just in the launch meeting.

I'm sharing this because the mistake wasn't math; it was storytelling with the wrong protagonist. If you work in applied ML: whose reality does your metric actually represent?

Drop a comment if you've caught a similar mismatch — I'd love to learn what signals you watch now.""",
            "image": None,
        },
        {
            "text": """Interviewing candidates for our team last month, I spent almost half of each loop on a single theme: 'Tell me about a time your model looked good offline and disappointed online — what did you check first?'

The best answers weren't textbook. They named specific leaks, delayed labels, inventory quirks, or UX changes that broke assumptions. The weakest answers jumped straight to architecture shopping.

It reminded me to prep candidates the way I'd want to be prepped: fundamentals plus war stories. If you're interviewing for applied roles, consider weighting diagnosis over buzzwords.""",
            "image": None,
        },
    ],
    "james_rodriguez_devops": [
        {
            "text": """We closed a sev-2 last night. The post-incident template asked for 'root cause.' I wrote three bullets and left the root cause field blank on purpose.

We had: a traffic shift from a marketing campaign nobody told ops about, a cache TTL change that was technically correct but untested under that shape of load, and on-call fatigue that slowed the first rollback decision. Any single label would have made someone the villain.

Instead we documented contributing factors, added a lightweight 'campaign calendar' integration for infra, and scheduled a dry-run of rollback steps with the team that owns the cache — not as punishment, as practice.

If your culture still demands one neat root cause: you're optimizing for slides, not learning. Five whys is a tool, not a religion.

Curious how other teams phrase this without sounding like philosophy class.""",
            "image": POST_MEDIA_URLS[2],
        },
        {
            "text": """August was the month I finally stopped hand-waving capacity. Finance asked for reserved instances; I brought utilization trends, risk of spot interruption on batch jobs, and a worst-case cost if Black Friday behaved like two years ago.

They approved less than I asked for — and the right amount. We revisited in October with real data instead of pride.

Capacity planning is a relationship between engineering credibility and finance trust. Charts help; honesty helps more.""",
            "image": None,
        },
    ],
    "aisha_okafor_design": [
        {
            "text": """We ran an accessibility audit on our clinic intake flow expecting a few color-contrast tweaks. Fourteen issues came back. Half were embarrassingly basic: labels not wired to inputs, error text that only changed color, focus traps in modals that broke on mobile.

I was defensive for about ten minutes — then I called our CS lead and asked for the last twenty tickets that mentioned 'couldn't finish form.' The pattern matched the audit.

We fixed the blockers in two sprints, measured support volume, and saw a real drop — not viral LinkedIn numbers, but enough that nurses stopped apologizing on the phone for 'the computer.'

Design quality isn't only what wins awards; it's what stops someone from feeling stupid while they're trying to care for patients.

If you're building health-adjacent products: fight for time on forms. They're where trust lives or dies.""",
            "image": None,
        },
        {
            "text": """Tomorrow I'm running a 45-minute Figma walkthrough for our customer success team — not 'design 101,' but how to find the source of truth for components so they stop screenshotting six-month-old screens in tickets.

I used to think enablement was extra. Now I see it as defect prevention. Every hour we spend aligning language between CS and Design saves three hours of triage.

If you've run similar sessions, what actually landed? I'm stealing good ideas.""",
            "image": POST_MEDIA_URLS[3],
        },
    ],
    "liam_walsh_backend": [
        {
            "text": """Our largest webhook partner changed retry intervals without a changelog entry. Subscriptions started stacking duplicate events at the edges; finance noticed before engineering did — not a great moment.

We hotfixed deduplication keys and backoff, then I did something I should have done a year ago: scheduled a quarterly sync with their integrations team, wrote SLA language into the contract draft for notification of behavioral changes, and built a dashboard that shows 'partner behavior drift' as a first-class alert.

Clever code saved the weekend; boring process might save the next quarter.

If you own integrations: when did you last read your partner's docs like a skeptic, not a believer?""",
            "image": None,
        },
        {
            "text": """Internal ops asked for a tool to replay failed payouts for review. Part of me wanted a microservice; the adult in the room used Django admin with tight permissions and audit logs.

Two weeks later they're exporting CSVs for compliance without opening tickets to my team. Not glamorous — effective.

Sometimes the right architecture is the one your org can operate when you're on holiday.""",
            "image": None,
        },
    ],
    "mei_zhang_ai": [
        {
            "text": """We shipped an assistive drafting feature for support reps — suggested replies based on ticket context. Offline evals looked strong; pilot NPS was fine.

Then I sat with four reps for two hours. Half of them said the suggestions made them slower because they had to mentally 'undo' confident-sounding wrong text before sending. A/B said they'd trust it more if we showed confidence and sources, even if that meant fewer suggestions.

We turned the feature off for a week — politically scary — and relaunched a simpler version: shorter snippets, explicit 'use / edit / ignore,' and a weekly feedback button that actually routes to me.

The takeaway I want to repeat: the metric isn't clicks; it's whether humans feel respected at work. Models serve people, not dashboards.

If you build copilots: when did you last watch someone use your product with their real queue, not a demo script?""",
            "image": None,
        },
        {
            "text": """Spent three afternoons this month labeling edge cases for eval sets — duplicate tickets, sarcasm, multilingual fragments. Nobody claps for that work in roadmap reviews.

Then we caught a regression before it hit 10% of traffic because the eval moved. I'll take the boring win.

If your team skips eval maintenance: you're not saving time; you're borrowing incidents.""",
            "image": POST_MEDIA_URLS[4],
        },
    ],
    "daniel_osei_frontend": [
        {
            "text": """We shipped keyboard navigation and visible focus states across our claims review table — work that sounded small until we realized partners had been tabbing into invisible traps for years.

A week later an email arrived from an insurance ops lead I'd never met. It wasn't long; it said thank you, named two people on their team with motor difficulties who could finally do reviews without a mouse.

I printed that email for myself — not for the wall of fame, as a reminder that accessibility tickets are revenue and dignity, not polish.

If you're debating whether to prioritize a11y this quarter: find one high-friction workflow and fix it end-to-end. The feedback might be quieter than a viral post, but it lands harder.""",
            "image": None,
        },
        {
            "text": """Working from Accra with CET overlap means my mornings are mine if I defend them. I stopped pretending I could do deep work while half of Europe wakes up and pings.

I blocked 8–10 local for implementation, moved standup later once, and told my manager honestly when a school morning blew the plan. The team adjusted — not perfectly, but enough that I stopped lying in Slack statuses.

Remote work isn't about being always on; it's about negotiating reality with humans who also have calendars.""",
            "image": None,
        },
    ],
    "emma_sullivan_sec": [
        {
            "text": """We ran threat modeling for checkout with developers, not at them. I brought a thin STRIDE outline; they brought nightmares — gift card stacking, race conditions on promo application, abuse of partial refunds.

Within an hour the whiteboard had scenarios our slide deck missed entirely. We prioritized two fixes for the next sprint, filed three backlog items with clear owners, and scheduled a retest after deployment.

Security as a gate gets eye rolls. Security as a shared imagination exercise gets fixes.

If you're in AppSec: try pizza, markers, and 'how would you steal your own feature?' before you open Burp.""",
            "image": POST_MEDIA_URLS[5],
        },
        {
            "text": """When I started, I thought triage speed meant typing fast. Now I know it means breathing once, opening the stack trace, and refusing to panic when the first line looks alien.

Half of findings are configuration ghosts; the other half need a calm human to trace data, not ego.

If you're new: your job isn't to know everything on day one. It's to document what you checked so the next person starts smarter.""",
            "image": None,
        },
    ],
    "arjun_mehta_fullstack": [
        {
            "text": """The encoding queue backed up at midnight — classic story. Marketing dropped a surprise content batch; our autoscaler hesitated; on-call woke up tired.

We could have thrown money at nodes. Instead we followed the runbook someone wrote last year: verify upstream ingest, check stuck jobs by codec, drain poison messages, scale workers only after the queue head looked healthy. By morning the backlog cleared without a second incident.

I don't know who wrote that runbook — if you're reading this, thank you. Documentation is love.

If you own pipelines: when someone saves you with a checklist, add one line to that checklist so the next fire is shorter.""",
            "image": None,
        },
        {
            "text": """Mentored a bootcamp grad this month who was drowning in 'learn Kafka, learn K8s, learn everything' anxiety.

We drew a coffee shop on the whiteboard — orders, queue, baristas, overflow line — and mapped it to our actual services. Their shoulders dropped. They asked better questions the next day.

Fundamentals wear fancy names in job posts. Teach the boring map first; the buzzwords attach faster afterward.""",
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
