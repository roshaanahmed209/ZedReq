"""
Seed 10 Realistic Users for ZedRec
Real-looking LinkedIn-style professionals with posts, profiles, and connections.

Run from the backend/ directory on Render shell:
    python tables_queries/seed_realistic_users.py

Or from anywhere:
    python /path/to/backend/tables_queries/seed_realistic_users.py
"""

import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# ── Path setup (works from any directory) ─────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent.resolve()          # tables_queries/
BACKEND_DIR  = SCRIPT_DIR.parent.resolve()              # backend/
PROJECT_ROOT = BACKEND_DIR.parent.resolve()             # project root

sys.path.insert(0, str(BACKEND_DIR))

# Load .env from project root if it exists
try:
    from dotenv import load_dotenv
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")
    else:
        load_dotenv()
except ImportError:
    pass  # dotenv not required if DATABASE_URL is already set

# ── Imports ───────────────────────────────────────────────────────────────────
from config.database import get_connection_params, Database
from utils.auth import hash_password

# ══════════════════════════════════════════════════════════════════════════════
#  USER DATA  — 10 realistic professionals
# ══════════════════════════════════════════════════════════════════════════════

USERS = [
    {
        "username":   "sarah_chen_dev",
        "name":       "Sarah Chen",
        "email":      "sarah.chen@zedreq.dev",
        "password":   "Sarah@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/women/44.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&q=80",
        "short_desc":  "Senior Software Engineer at Meta",
        "about": (
            "Senior Software Engineer at Meta with 7+ years of experience building "
            "large-scale distributed systems. Led the team that migrated Facebook Marketplace "
            "to a microservices architecture, reducing latency by 40%. "
            "Passionate about developer experience, open-source, and mentoring early-career engineers. "
            "Speaker at React Conf 2023. CS graduate from Stanford."
        ),
        "skills":     "React, TypeScript, Python, GraphQL, Distributed Systems, Kubernetes",
        "certificates": "AWS Solutions Architect Professional, Meta Engineering Excellence Award 2022",
        "current_status": "Open to speaking opportunities",
        "location":   "San Francisco, CA",
        "company":    "Meta",
        "title":      "Senior Software Engineer",
    },
    {
        "username":   "marcus_thompson_pm",
        "name":       "Marcus Thompson",
        "email":      "marcus.thompson@zedreq.dev",
        "password":   "Marcus@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/32.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80",
        "short_desc":  "Product Manager at Google",
        "about": (
            "Product Manager at Google working on Search infrastructure. "
            "Previously at Airbnb and two YC-backed startups. "
            "I obsess over user research, ruthless prioritization, and shipping things that matter. "
            "Built products used by 200M+ users. MBA from Wharton, BSCS from MIT. "
            "Angel investor in 6 early-stage startups."
        ),
        "skills":     "Product Strategy, User Research, A/B Testing, SQL, JIRA, Roadmapping",
        "certificates": "Certified Scrum Product Owner (CSPO), Google PM Leadership Award 2023",
        "current_status": "Currently employed",
        "location":   "Mountain View, CA",
        "company":    "Google",
        "title":      "Senior Product Manager",
    },
    {
        "username":   "priya_sharma_ml",
        "name":       "Priya Sharma",
        "email":      "priya.sharma@zedreq.dev",
        "password":   "Priya@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/women/58.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80",
        "short_desc":  "ML Engineer at Microsoft Research",
        "about": (
            "Machine Learning Engineer at Microsoft Research, specializing in NLP and LLMs. "
            "Co-authored 3 papers at NeurIPS and ICML on efficient transformer architectures. "
            "Led fine-tuning efforts for Copilot's code completion model. "
            "Previously a research intern at DeepMind. IIT Bombay (B.Tech) → CMU (M.S. ML)."
        ),
        "skills":     "Python, PyTorch, TensorFlow, Transformers, CUDA, MLflow, Azure ML",
        "certificates": "Microsoft Azure AI Engineer, NeurIPS 2023 Outstanding Paper Honorable Mention",
        "current_status": "Open to collaboration on research",
        "location":   "Redmond, WA",
        "company":    "Microsoft Research",
        "title":      "ML Engineer II",
    },
    {
        "username":   "james_rodriguez_devops",
        "name":       "James Rodriguez",
        "email":      "james.rodriguez@zedreq.dev",
        "password":   "James@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/76.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
        "short_desc":  "Staff DevOps Engineer at Amazon",
        "about": (
            "Staff DevOps / Platform Engineer at Amazon (AWS). "
            "I build the infrastructure that runs Amazon's checkout pipeline — 99.999% uptime, "
            "processing $500M+ transactions daily. "
            "Kubernetes, Terraform, and chaos engineering nerd. "
            "Gave the keynote at KubeCon NA 2023 on cost-optimized multi-region deployments. "
            "Former US Army IT Specialist. Self-taught engineer."
        ),
        "skills":     "Kubernetes, Terraform, AWS, Golang, Prometheus, Grafana, Ansible, CI/CD",
        "certificates": "CKA, CKS, AWS DevOps Engineer Professional, HashiCorp Terraform Associate",
        "current_status": "Currently employed",
        "location":   "Seattle, WA",
        "company":    "Amazon",
        "title":      "Staff DevOps Engineer",
    },
    {
        "username":   "aisha_okafor_design",
        "name":       "Aisha Okafor",
        "email":      "aisha.okafor@zedreq.dev",
        "password":   "Aisha@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/women/21.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=1200&q=80",
        "short_desc":  "Senior UX Designer at Airbnb",
        "about": (
            "Senior UX Designer at Airbnb focused on host onboarding and trust & safety flows. "
            "Design systems contributor — built Airbnb's new icon library used across 12 product teams. "
            "I believe great design is invisible. "
            "Previously at Figma (yes, I designed tools at Figma). "
            "Grew up in Lagos, studied Fine Arts at Yale, then stumbled into tech."
        ),
        "skills":     "Figma, Prototyping, User Research, Design Systems, Accessibility, Motion Design",
        "certificates": "Google UX Design Certificate, Interaction Design Foundation UX Master",
        "current_status": "Open to freelance projects",
        "location":   "San Francisco, CA",
        "company":    "Airbnb",
        "title":      "Senior UX Designer",
    },
    {
        "username":   "liam_walsh_backend",
        "name":       "Liam Walsh",
        "email":      "liam.walsh@zedreq.dev",
        "password":   "Liam@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/43.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&q=80",
        "short_desc":  "Backend Engineer at Stripe",
        "about": (
            "Backend Engineer at Stripe, working on the Payment Intents API and fraud detection pipeline. "
            "Fanatic about correctness, idempotency, and making distributed systems actually work. "
            "Wrote the internal RFC that reduced Stripe's webhook retry storm by 70%. "
            "Open-source contributor: psycopg3, SQLAlchemy. "
            "Trinity College Dublin (Computer Science). Based in Dublin, working remotely from Cork."
        ),
        "skills":     "Python, Go, PostgreSQL, Redis, Kafka, gRPC, Event-Driven Architecture",
        "certificates": "PostgreSQL Professional, AWS Certified Developer",
        "current_status": "Currently employed",
        "location":   "Cork, Ireland",
        "company":    "Stripe",
        "title":      "Software Engineer L4",
    },
    {
        "username":   "mei_zhang_ai",
        "name":       "Mei Zhang",
        "email":      "mei.zhang@zedreq.dev",
        "password":   "Mei@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/women/66.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&q=80",
        "short_desc":  "AI Research Engineer at OpenAI",
        "about": (
            "AI Research Engineer at OpenAI on the alignment team. "
            "Working on scalable oversight and interpretability for frontier models. "
            "PhD candidate (leave of absence) at Berkeley AI Research (BAIR). "
            "First-author on a paper about reward model elicitation — 800+ citations. "
            "I write about AI safety on Substack: 'Alignment Notes' — 12k subscribers."
        ),
        "skills":     "Python, JAX, PyTorch, RLHF, Constitutional AI, Mechanistic Interpretability",
        "certificates": "ICLR 2023 Outstanding Paper Award, NSF Graduate Research Fellowship",
        "current_status": "Open to speaking at AI safety conferences",
        "location":   "San Francisco, CA",
        "company":    "OpenAI",
        "title":      "AI Research Engineer",
    },
    {
        "username":   "daniel_osei_frontend",
        "name":       "Daniel Osei",
        "email":      "daniel.osei@zedreq.dev",
        "password":   "Daniel@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/88.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&q=80",
        "short_desc":  "Frontend Engineer at Shopify",
        "about": (
            "Frontend Engineer at Shopify building the merchant dashboard and checkout experience. "
            "Obsessed with web performance — helped push Shopify's Lighthouse score from 61 to 94. "
            "Creator of 'react-micro-animate' (3.2k GitHub stars). "
            "Accessibility advocate: every component I ship meets WCAG 2.1 AA. "
            "From Accra, Ghana. Remote-first since 2019. "
            "I stream coding on Twitch every Thursday."
        ),
        "skills":     "React, Next.js, TypeScript, Web Performance, Accessibility, Storybook, Remix",
        "certificates": "Meta Frontend Developer, W3C Web Accessibility Specialist",
        "current_status": "Open to consulting",
        "location":   "Accra, Ghana (Remote)",
        "company":    "Shopify",
        "title":      "Senior Frontend Engineer",
    },
    {
        "username":   "emma_sullivan_sec",
        "name":       "Emma Sullivan",
        "email":      "emma.sullivan@zedreq.dev",
        "password":   "Emma@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/women/33.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200&q=80",
        "short_desc":  "Security Engineer at Cloudflare",
        "about": (
            "Security Engineer at Cloudflare on the Zero Trust team. "
            "I find bugs in things that are supposed to be unbreakable. "
            "CVEs: 7. Bug bounty earnings: not disclosing 😄. "
            "Previously: red team at Google, CTF player (0ctf top 10 worldwide). "
            "Speaker at DEF CON 31: 'Breaking mTLS at Scale'. "
            "University of Edinburgh, MSc Information Security."
        ),
        "skills":     "Penetration Testing, Rust, Python, TLS/PKI, Zero Trust, Threat Modeling, Burp Suite",
        "certificates": "OSCP, CISSP, GREM, CEH",
        "current_status": "Currently employed",
        "location":   "London, UK",
        "company":    "Cloudflare",
        "title":      "Senior Security Engineer",
    },
    {
        "username":   "arjun_mehta_fullstack",
        "name":       "Arjun Mehta",
        "email":      "arjun.mehta@zedreq.dev",
        "password":   "Arjun@2024!",
        "profile_pic": "https://randomuser.me/api/portraits/men/54.jpg",
        "cover_pic":   "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200&q=80",
        "short_desc":  "Full Stack Engineer at Netflix",
        "about": (
            "Full Stack Engineer at Netflix on the Content Delivery team — yes, I help make "
            "sure your Netflix doesn't buffer. "
            "Built the adaptive bitrate experimentation framework used in 16 A/B tests. "
            "Side project: 'DevPulse' — a real-time engineering metrics dashboard, "
            "20k monthly active users. "
            "IIT Delhi → 2 years at a Bangalore startup → Netflix. "
            "Mentor at GirlScript Foundation."
        ),
        "skills":     "React, Node.js, Java, Spring Boot, Cassandra, Kafka, AWS, System Design",
        "certificates": "AWS Solutions Architect, Oracle Java Certified Professional",
        "current_status": "Open to mentorship requests",
        "location":   "Los Gatos, CA",
        "company":    "Netflix",
        "title":      "Senior Software Engineer",
    },
]

# ══════════════════════════════════════════════════════════════════════════════
#  POSTS  — Realistic LinkedIn-style content, some with images
# ══════════════════════════════════════════════════════════════════════════════

# Post image pool — tech/professional Unsplash photos
POST_IMAGES = [
    ("https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=900&q=80", "image"),   # code on monitor
    ("https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=900&q=80", "image"),   # hackathon
    ("https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=900&q=80", "image"),   # team around laptop
    ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900&q=80", "image"),      # dashboard analytics
    ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=900&q=80", "image"),   # matrix/code
    ("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=900&q=80", "image"),   # whiteboard planning
    ("https://images.unsplash.com/photo-1523289333742-be1143f6b766?w=900&q=80", "image"),   # award/trophy
    ("https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=900&q=80", "image"),   # home office
    ("https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=900&q=80", "image"),   # laptop coffee
    ("https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=900&q=80", "image"),   # conference stage
    ("https://images.unsplash.com/photo-1516321497487-e288fb19713f?w=900&q=80", "image"),   # video call meeting
    ("https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=900&q=80", "image"),   # robot/AI
]

# Each user has their own set of posts (username → list of post dicts)
USER_POSTS = {
    "sarah_chen_dev": [
        {
            "text": "Just wrapped up migrating Facebook Marketplace's recommendation engine to a new GraphQL federated schema. 3 months of work, 47 PRs, 0 production incidents. 🎉\n\nKey lesson: treat your schema as a product. Version it, document it, and never break clients without a deprecation period.\n\nThread on what we learned 👇",
            "image": POST_IMAGES[0],
        },
        {
            "text": "Hot take: the most underrated skill for senior engineers isn't technical — it's knowing when NOT to build something.\n\nI've seen teams spend 6 months building an internal tool that a $49/month SaaS already solved. The best engineers I work with spend as much time saying 'no' as writing code.",
            "image": None,
        },
        {
            "text": "Spoke at React Conf today about compound components and the Context API patterns we use at scale. Terrifying and exhilarating at the same time.\n\nSlides are up at the link below. The Q&A ran 20 minutes over — turns out everyone has opinions about render props 😂",
            "image": POST_IMAGES[9],
        },
        {
            "text": "Mentorship update: the 4 engineers I've been mentoring through the last 6 months all received their promotion packets this cycle.\n\nProud doesn't begin to cover it. If you're a senior/staff engineer and you're not mentoring — you're leaving the most impactful work on the table.",
            "image": None,
        },
        {
            "text": "TypeScript 5.3 dropped and I've been playing with the new `import attributes` syntax all morning instead of reviewing PRs. Worth it.\n\nFavorite new feature: `satisfies` operator composing with `as const`. Finally.",
            "image": POST_IMAGES[4],
        },
    ],
    "marcus_thompson_pm": [
        {
            "text": "The best product decision I made this year wasn't building something new — it was deleting a feature.\n\nWe removed a 'power user' filter that only 0.3% of Search users touched, but was responsible for 12% of our bug reports. Metrics improved across the board. Sometimes less really is more.",
            "image": None,
        },
        {
            "text": "Just finished a 3-week sprint of user interviews (47 sessions across 6 countries). The most consistent finding: users don't want more features. They want the existing ones to work faster and more reliably.\n\nSpeed is a feature. Reliability is a feature. Never forget it.",
            "image": POST_IMAGES[2],
        },
        {
            "text": "Framework I use for every product decision:\n\n1. What user problem are we solving?\n2. How do we know this is real? (data + interviews)\n3. What's the simplest version we can ship?\n4. How will we know it worked?\n\nIf you can't answer all 4 in 2 minutes, you're not ready to build.",
            "image": None,
        },
        {
            "text": "Exciting news — our team's work on Search latency shipped to 100% of users yesterday. P99 dropped by 180ms globally.\n\nThat's 180ms × 8.5 billion queries per day. The math on user time saved is genuinely staggering.",
            "image": POST_IMAGES[3],
        },
    ],
    "priya_sharma_ml": [
        {
            "text": "Our paper 'Efficient Token Merging for Long-Context Transformers' was accepted at NeurIPS 2024! 🎊\n\nTL;DR: we can reduce inference cost by 38% on sequences >8k tokens with <0.5% accuracy degradation on standard benchmarks. Preprint on arXiv tonight.",
            "image": POST_IMAGES[5],
        },
        {
            "text": "Controversial opinion in ML: most teams don't need a bigger model. They need better data.\n\nI've seen a 7B model fine-tuned on 50k high-quality examples outperform GPT-4 on domain-specific tasks. Garbage in, garbage out — no matter how many parameters you have.",
            "image": None,
        },
        {
            "text": "Spent the weekend doing a deep dive into Mamba and State Space Models. The attention-free architecture is genuinely interesting for certain sequence tasks.\n\nNot convinced it kills transformers anytime soon, but for streaming inference on edge devices? Worth watching closely.",
            "image": POST_IMAGES[11],
        },
        {
            "text": "3 things I wish someone told me before starting my ML career:\n\n• You'll spend 80% of your time on data, not models\n• Baseline models are usually better than you think\n• Reproducibility isn't optional — it IS the work\n\nWhat would you add?",
            "image": None,
        },
        {
            "text": "Just hit 100 citations on my first-ever paper — the one I almost didn't submit because I thought it wasn't good enough.\n\nImposter syndrome is a liar. Submit the paper.",
            "image": POST_IMAGES[6],
        },
        {
            "text": "Running evaluations on our latest Copilot code completion model. The improvement in Python docstring generation is remarkable — it's reading context from 3 files away now.\n\nCan't share numbers yet, but ship date is getting close 👀",
            "image": POST_IMAGES[0],
        },
    ],
    "james_rodriguez_devops": [
        {
            "text": "Kubernetes war story: last Tuesday our checkout pipeline had a 4-minute partial outage. Root cause? A memory limit set in 2019 that nobody questioned.\n\nFix took 2 minutes. Post-mortem took 3 hours. That's the job.\n\nAlways question 'that's just how it's always been configured.'",
            "image": None,
        },
        {
            "text": "KubeCon keynote is done ✅\n\nTalked about how we run 47,000 pods across 6 regions with a 3-person on-call rotation. The secret isn't heroics — it's aggressive automation and a culture where no manual step is acceptable twice.",
            "image": POST_IMAGES[9],
        },
        {
            "text": "Terraform tip that saved us $2.1M/year:\n\nWe added a `cost_estimation` step to every PR pipeline that shows the projected monthly cost delta before merge. Engineers naturally started asking 'do we really need this?' way more often.\n\nMake the cost visible.",
            "image": POST_IMAGES[7],
        },
        {
            "text": "New blog post: 'Why We Moved From Helm to ArgoCD (And Why We Kind Of Regret It)'\n\nSpoiler: both tools are fine. The problem was our deployment mental model, not the tool. Link in comments.",
            "image": None,
        },
        {
            "text": "Today I helped a junior engineer debug their first production incident. Watching them go from panic to methodical investigation to fix in 45 minutes was the best part of my week.\n\nRemember what it felt like when someone patient walked you through your first fire. Be that person.",
            "image": POST_IMAGES[2],
        },
    ],
    "aisha_okafor_design": [
        {
            "text": "Redesigned Airbnb's host onboarding flow. New design tested 27% better on task completion and reduced support tickets by 31%.\n\nThe biggest change? We removed 6 screens. Not added — removed. The best UX is the one that gets out of the way.",
            "image": POST_IMAGES[5],
        },
        {
            "text": "Hot take from a designer: the Figma vs Sketch debate is completely irrelevant. Master the fundamentals — hierarchy, contrast, spacing, flow — and you can use any tool.\n\nI see juniors obsessing over tools instead of sharpening their eye. The eye is the skill.",
            "image": None,
        },
        {
            "text": "Just released our new icon library to the Airbnb design system. 340 icons, each hand-crafted with pixel-perfect 24px and 16px variants.\n\nThe part nobody sees: 6 months of debating stroke width, corner radius, and optical balance. Design is mostly invisible arguments.",
            "image": POST_IMAGES[3],
        },
        {
            "text": "Accessibility isn't a feature — it's a quality bar.\n\nWe ran our new host dashboard through a screen reader for the first time with a blind host in the room. It was humbling. Every designer should do this once a quarter, minimum.",
            "image": POST_IMAGES[8],
        },
        {
            "text": "Before Figma, I designed tools at Figma. People ask what that was like.\n\nAnswer: same as any other product role, except every designer you show your work to immediately files 6 bugs. Most useful feedback of my career.",
            "image": None,
        },
        {
            "text": "Portfolio refresh is live. 5 case studies, including the Airbnb Trust & Safety redesign that I'm most proud of.\n\nFeedback welcome — especially from non-designers. You're actually my target audience.",
            "image": POST_IMAGES[1],
        },
        {
            "text": "Mentoring a design student from Lagos today (shoutout to ADPList). She showed me work that reminded me why I do this.\n\nPlease mentor. It costs you an hour. It can change someone's trajectory entirely.",
            "image": None,
        },
    ],
    "liam_walsh_backend": [
        {
            "text": "Database hot take: most 'scaling problems' I've seen are actually 'missing index problems' or 'N+1 query problems.' Before you add Redis, run EXPLAIN ANALYZE.\n\nI've fixed 4 'we need to rewrite everything' crises this year with a single CREATE INDEX statement.",
            "image": None,
        },
        {
            "text": "Open-sourced the webhook idempotency library we built internally at Stripe. It's not glamorous, but idempotent distributed operations are genuinely hard to get right and I want fewer engineers reinventing this wheel.\n\nGitHub link in comments. PRs welcome.",
            "image": POST_IMAGES[0],
        },
        {
            "text": "Published an RFC to the Python core list: improving psycopg3's async connection pool behaviour under backpressure. \n\nGetting feedback from the core maintainers is equal parts exciting and terrifying.",
            "image": None,
        },
        {
            "text": "The phrase 'eventual consistency' has destroyed more systems than it has saved.\n\nEvery time someone reaches for it, ask: 'what is the worst-case divergence window and can our users tolerate it?' If you can't answer that, you don't actually want eventual consistency — you want to avoid thinking about it.",
            "image": POST_IMAGES[4],
        },
    ],
    "mei_zhang_ai": [
        {
            "text": "New post on Alignment Notes: 'Why Scalable Oversight Is Harder Than It Looks (But Worth Doing)'\n\nTL;DR: having humans supervise AI outputs only works if humans can evaluate those outputs. At frontier capability, they often can't. That's the crux.\n\nLink in bio. Would love researcher feedback.",
            "image": POST_IMAGES[11],
        },
        {
            "text": "Just had a 2-hour argument with a colleague about whether RLHF reward hacking is a solvable problem or a fundamental limit.\n\nWe didn't resolve it. That's fine. The best alignment meetings end with sharper questions, not comfortable answers.",
            "image": None,
        },
        {
            "text": "Preprint drop: 'Eliciting Latent Knowledge from Reward Models via Activation Steering'\n\nWe can extract implicit value judgments from reward models that never surface in their outputs. The implications for interpretability (and for misuse) are both significant.\n\nPlease read critically.",
            "image": POST_IMAGES[5],
        },
        {
            "text": "Taking a week off Twitter/X. The AI discourse is exhausting — everyone is either certain it will kill us or certain it won't. Reality is more uncertain and more interesting than either camp admits.\n\nBack to lab. Graphs don't doompost.",
            "image": None,
        },
        {
            "text": "Berkeley AI Research had their annual open house this week. The density of brilliant people in one building is still surreal to me.\n\nMy honest hot take on academic vs industry research in 2024: the compute gap is now wide enough that it's changing what questions academia can even ask.",
            "image": POST_IMAGES[2],
        },
    ],
    "daniel_osei_frontend": [
        {
            "text": "Pushed Shopify's merchant dashboard Lighthouse score from 61 → 94 over 8 months.\n\nThe 3 highest-impact changes:\n1. Replaced 4 icon libraries with a single tree-shakeable one\n2. Deferred all non-critical analytics scripts\n3. Added proper content-visibility to long lists\n\nNo framework rewrite needed.",
            "image": POST_IMAGES[3],
        },
        {
            "text": "react-micro-animate just hit 3,000 GitHub stars 🌟\n\nStarted it as a weekend project because I was frustrated with Framer Motion's bundle size for simple use cases. Still maintained entirely by me. Open to co-maintainers — DM me.",
            "image": POST_IMAGES[6],
        },
        {
            "text": "Accessibility audit today: 'add an aria-label to this button.'\n\nMe: yes, and also this colour contrast ratio is 2.8:1 and the focus ring disappears in Safari and this modal traps keyboard focus and this error message is only indicated by colour.\n\nAccessibility is always more than one label.",
            "image": None,
        },
        {
            "text": "Streamed for 3 hours last Thursday building a custom Shopify app from scratch. 847 concurrent viewers. Chat was full of questions I genuinely had to think about.\n\nLive coding is the most honest way to show your actual thought process. Highly recommend trying it.",
            "image": POST_IMAGES[10],
        },
        {
            "text": "Remote work from Accra update, year 5:\n\nThe infrastructure is better than people assume. The community is thriving. The time zone calls with CA are hard.\n\nBest decision of my career. Would not go back to an office even if you doubled my salary.",
            "image": POST_IMAGES[7],
        },
        {
            "text": "Next.js 15 and the new compiler are genuinely impressive. Cold start on our 300-route app went from 14s to 3s.\n\nBut I remain a Remix believer for data-heavy apps. The loader/action pattern is still the most honest mental model for web data fetching I've encountered.",
            "image": None,
        },
    ],
    "emma_sullivan_sec": [
        {
            "text": "DEF CON talk is up on YouTube: 'Breaking mTLS at Scale — A Case Study in Assumptions'\n\nSpoiler: the vulnerability wasn't in TLS. It was in the engineers' belief that 'we use mTLS' meant 'we are secure.' Certificate pinning misconfigured in 3 different places.\n\nWatch. Share. Don't make these mistakes.",
            "image": POST_IMAGES[9],
        },
        {
            "text": "Just filed CVE number 7. 9 months of responsible disclosure with the vendor. Patched. Now public.\n\nI won't name the company (patch first, names later). But the class of vulnerability — trusting client-supplied tokens in a JWT header without re-validating claims — is shockingly common.",
            "image": None,
        },
        {
            "text": "Zero Trust isn't a product you buy. It's an architectural principle you earn.\n\nI've done security reviews for 30+ companies now. The ones with the best security posture don't necessarily have the best tools. They have the best threat models and the most honest conversations about trust boundaries.",
            "image": POST_IMAGES[4],
        },
        {
            "text": "CTF recap: 0ctf 2024. We finished 8th globally (team of 3). \n\nThe web challenge that broke me took 9 hours and involved a deserialization gadget chain through 4 frameworks. When we finally popped the shell at 2am, the three of us literally screamed.\n\nThis is why I do security.",
            "image": None,
        },
        {
            "text": "If you're learning security in 2024:\n\n1. Stop buying courses, start playing CTFs (PicoCTF → HackTheBox → CTFtime)\n2. Read actual CVE write-ups, not just headlines\n3. Build things and then attack them\n4. The OSCP is worth it but it's a floor, not a ceiling\n\nDMs open for advice.",
            "image": POST_IMAGES[8],
        },
    ],
    "arjun_mehta_fullstack": [
        {
            "text": "DevPulse just hit 20,000 monthly active users. Started it in a weekend 18 months ago because I was annoyed that our DORA metrics were buried in 4 different dashboards.\n\nBuilt with Next.js + Kafka + Postgres. Still running on a $40/month VPS.\n\nSometimes the boring stack wins.",
            "image": POST_IMAGES[3],
        },
        {
            "text": "A/B test result we shipped this week: our new adaptive bitrate algorithm reduced rebuffering events by 22% on mobile networks in India and Southeast Asia.\n\nThose are real people who didn't have their shows pause. That's the job.",
            "image": POST_IMAGES[5],
        },
        {
            "text": "System design interview tip that nobody says out loud:\n\nThe interviewer doesn't expect you to know the 'right' answer. They want to see how you reason under constraints.\n\nSay 'I'm going to start simple and add complexity as we identify bottlenecks.' Then actually do that.",
            "image": None,
        },
        {
            "text": "I mentor 6 engineers through GirlScript Foundation. One of them just got an offer from a FAANG company today.\n\nShe emailed me before she told her family. I'm still emotional about it.",
            "image": POST_IMAGES[6],
        },
        {
            "text": "Hot take: Cassandra is a terrible choice for most applications. Fantastic for a narrow set of write-heavy, partition-tolerant use cases.\n\nWe use it at Netflix because our use case fits perfectly. For 95% of the startups I see choosing it: just use Postgres.",
            "image": None,
        },
        {
            "text": "IIT Delhi → 2-year startup → Netflix journey taught me:\n\nThe startup years were harder and paid less. They were also where I learned the most.\n\nIf you're early career and you get a startup offer alongside a big-tech offer, the right choice depends entirely on the startup. Do your due diligence on the people, not just the valuation.",
            "image": POST_IMAGES[8],
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  SEED FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def seed_user(db: Database, user: dict) -> tuple[int, int] | None:
    """Insert description + user. Returns (uid, desc_id) or None on failure."""
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
            # User already exists — fetch uid
            existing = db.fetch_one(
                "SELECT uid FROM users WHERE username = %s", (user["username"],)
            )
            if existing:
                uid = existing["uid"]
                print(f"  [SKIP] User already exists: {user['username']} (uid {uid})")
                return uid, desc_id
            return None

        uid = result["uid"]
        # Link description back to user (description.proj_id not needed here)
        print(f"  [OK]   Created {user['name']} (@{user['username']}) → uid {uid}")
        return uid, desc_id

    except Exception as e:
        print(f"  [ERR]  {user['name']}: {e}")
        return None


def seed_network(db: Database, uid: int):
    """Create network row for user."""
    try:
        db.execute(
            "INSERT INTO network (uid, num_connections) VALUES (%s, 0) ON CONFLICT DO NOTHING",
            (uid,),
        )
    except Exception as e:
        print(f"  [WARN] network for uid {uid}: {e}")


def seed_posts(db: Database, uid: int, username: str, posts: list):
    """Insert posts for a user."""
    for p in posts:
        try:
            media_url, media_type = (None, None)
            if p.get("image"):
                media_url, media_type = p["image"]

            # Randomise engagement counts to look realistic
            likes    = random.randint(12, 3400)
            comments = random.randint(2, 340)

            # Random timestamp in the last 90 days
            days_ago = random.randint(0, 90)
            hours_ago = random.randint(0, 23)
            created = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

            db.execute(
                """INSERT INTO post (uid, post_desc, media_url, media_type, likes, comments, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (uid, p["text"], media_url, media_type, likes, comments, created, created),
            )
        except Exception as e:
            print(f"  [WARN] post for @{username}: {e}")


def seed_connections(db: Database, uid_map: dict):
    """Create realistic follow/connection relationships between users."""
    usernames = list(uid_map.keys())

    for username, uid in uid_map.items():
        # Each user connects with 4–8 others
        others = [u for u in usernames if u != username]
        to_follow = random.sample(others, min(random.randint(4, 8), len(others)))

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


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def run():
    print("=" * 65)
    print("  ZedRec — Realistic User Seed Script")
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

    print(f"\n── Creating posts ──────────────────────────────────────────────")
    for user in USERS:
        uid = uid_map.get(user["username"])
        if uid is None:
            continue
        posts = USER_POSTS.get(user["username"], [])
        seed_posts(db, uid, user["username"], posts)
        print(f"  [OK]   {len(posts)} posts for @{user['username']}")

    print(f"\n── Creating connections ────────────────────────────────────────")
    seed_connections(db, uid_map)
    print(f"  [OK]   Connections seeded for {len(uid_map)} users")

    db.close()

    print("\n" + "=" * 65)
    print(f"  Done! {len(uid_map)} users seeded.")
    print()
    print("  Login credentials (all users):")
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
