"""
Generate comprehensive data for all existing users (except admin@roshaan.com)
This script populates all user-related tables with realistic sample data.
"""

import os
import sys
import random
import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_connection_params, Database

# Sample data pools
COMPANIES = [
    "TechCorp", "InnovateLabs", "CloudSystems", "DataFlow Inc", "CodeCraft",
    "Digital Solutions", "WebWorks", "AppDev Co", "Software Plus", "TechNova",
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Uber", "Airbnb"
]

JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
    "Frontend Developer", "Backend Developer", "DevOps Engineer", "Data Scientist",
    "Product Manager", "UI/UX Designer", "QA Engineer", "Security Engineer",
    "Cloud Architect", "Mobile Developer", "Machine Learning Engineer"
]

SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Vue.js", "Angular",
    "Java", "C++", "Go", "Rust", "SQL", "MongoDB", "PostgreSQL", "Redis",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Git",
    "REST API", "GraphQL", "Microservices", "CI/CD", "Agile", "Scrum"
]

SCHOOLS = [
    "MIT", "Stanford University", "Harvard University", "UC Berkeley",
    "Carnegie Mellon", "University of Washington", "Georgia Tech",
    "University of Texas", "NYU", "Columbia University", "Princeton",
    "Caltech", "Cornell University", "University of Michigan"
]

DEGREES = [
    "Bachelor of Science in Computer Science",
    "Master of Science in Computer Science",
    "Bachelor of Engineering",
    "Master of Engineering",
    "PhD in Computer Science",
    "Bachelor of Science in Software Engineering"
]

FIELDS_OF_STUDY = [
    "Computer Science", "Software Engineering", "Data Science",
    "Information Systems", "Computer Engineering", "Cybersecurity"
]

POST_DESCRIPTIONS = [
    "Just finished building a new feature! Excited to see how users respond.",
    "Learning new technologies is always exciting. Currently diving into {skill}.",
    "Great day at work today! Collaborated with an amazing team on {project}.",
    "Sharing some insights from my recent project. Hope it helps others!",
    "Just completed a certification in {skill}. The learning never stops!",
    "Working on an interesting problem today. Love the challenge!",
    "Attended an amazing tech conference. So many great ideas!",
    "Started a new side project. Can't wait to share it with everyone!",
    "Code review tip: Always think about maintainability and readability.",
    "The best code is code that others can understand and extend easily.",
    "Just deployed a new feature to production. Feeling accomplished!",
    "Collaboration is key in software development. Great team today!",
    "Always learning something new. Today it's {skill}.",
    "Sharing knowledge is one of the best ways to learn.",
    "Building something awesome with {skill}. Stay tuned!"
]

PROJECT_TITLES = [
    "E-Commerce Platform", "Social Media Dashboard", "Task Management App",
    "Weather Forecast App", "Recipe Sharing Platform", "Fitness Tracker",
    "Budget Management Tool", "Learning Management System", "Chat Application",
    "Blog Platform", "Portfolio Website", "Analytics Dashboard"
]

TECHNOLOGIES = [
    ["React", "Node.js", "MongoDB"],
    ["Vue.js", "Python", "PostgreSQL"],
    ["Angular", "Java", "MySQL"],
    ["React", "TypeScript", "Firebase"],
    ["Next.js", "Node.js", "Prisma"],
    ["Flutter", "Dart", "Firebase"],
    ["React Native", "Node.js", "MongoDB"]
]

INTEREST_TYPES = ["company", "group", "influencer", "school"]
INTEREST_NAMES = {
    "company": ["Google", "Microsoft", "Apple", "Meta", "Amazon", "Netflix"],
    "group": ["React Developers", "Python Community", "DevOps Engineers", "Data Scientists"],
    "influencer": ["Tech Influencer 1", "Code Master", "Dev Guru", "Tech Leader"],
    "school": ["MIT", "Stanford", "Harvard", "UC Berkeley"]
}

RECOMMENDATION_TEXTS = [
    "{name} is an exceptional {role} with strong technical skills and great teamwork.",
    "I had the pleasure of working with {name}. Highly recommend for any {role} position.",
    "{name} demonstrates excellent problem-solving abilities and technical expertise.",
    "Outstanding {role} with a passion for learning and innovation.",
    "{name} is a dedicated professional who consistently delivers high-quality work.",
    "I highly recommend {name} for their expertise in {skill} and collaborative spirit.",
    "{name} is a talented {role} with a strong work ethic and technical depth."
]

RELATIONSHIPS = [
    "Former Colleague", "Manager", "Team Lead", "Mentor", "Peer",
    "Project Partner", "Client", "Supervisor", "Classmate"
]

JOB_DESCRIPTIONS = [
    "We are looking for a talented {title} to join our team. You will work on exciting projects using {skills}.",
    "Join us as a {title} and help build innovative solutions. Experience with {skills} required.",
    "Seeking an experienced {title} to develop and maintain our platform. Must know {skills}.",
    "Opportunity for a {title} to work on cutting-edge technology. Skills in {skills} preferred.",
    "We need a {title} to help scale our infrastructure. Knowledge of {skills} is essential."
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
    "Boston, MA", "Los Angeles, CA", "Chicago, IL", "Denver, CO",
    "Remote", "Hybrid", "London, UK", "Toronto, Canada"
]

JOB_TYPES = ["full-time", "part-time", "contract", "internship"]
EXPERIENCE_LEVELS = ["entry-level", "mid-level", "senior", "executive"]


def get_db() -> Database:
    """Get database connection"""
    params = get_connection_params()
    return Database(params)


def get_all_users_except_admin(db: Database) -> List[Dict[str, Any]]:
    """Get all users except admin@roshaan.com"""
    users = db.fetch_all(
        "SELECT uid, username, name, user_email FROM users WHERE user_email != %s",
        ("admin@roshaan.com",)
    )
    return users


def get_existing_courses(db: Database) -> List[Dict[str, Any]]:
    """Get all existing courses"""
    return db.fetch_all("SELECT id, title FROM lms_courses WHERE is_active = TRUE")


def get_existing_domains(db: Database) -> List[Dict[str, Any]]:
    """Get all existing domains"""
    return db.fetch_all("SELECT id, name FROM lms_domains")


def get_existing_sections(db: Database) -> List[Dict[str, Any]]:
    """Get all existing course sections"""
    return db.fetch_all("SELECT id, course_id FROM lms_course_sections")


def get_existing_questions(db: Database) -> List[Dict[str, Any]]:
    """Get all existing questions"""
    return db.fetch_all("SELECT id, course_id FROM lms_questions")


def get_existing_job_postings(db: Database) -> List[Dict[str, Any]]:
    """Get all existing job postings"""
    return db.fetch_all("SELECT job_id FROM job_postings WHERE status = 'active'")


def generate_descriptions(db: Database, user_ids: List[int]) -> Dict[int, int]:
    """Generate description records for users"""
    print("\n[1/20] Generating descriptions...")
    desc_map = {}
    count = 0
    
    for user_id in user_ids:
        # Check if user already has a description_id
        user = db.fetch_one("SELECT description_id FROM users WHERE uid = %s", (user_id,))
        if user and user.get('description_id'):
            desc_map[user_id] = user['description_id']
            continue
        
        short_desc = random.choice(JOB_TITLES)
        about = f"Experienced {short_desc} with a passion for building innovative solutions. " \
                f"Skilled in {', '.join(random.sample(SKILLS, 5))}."
        certs = ", ".join(random.sample(["AWS Certified", "Google Cloud Professional", 
                                         "Microsoft Azure", "Kubernetes Certified"], 2))
        skills = ", ".join(random.sample(SKILLS, random.randint(5, 10)))
        status = random.choice(["Available for work", "Open to opportunities", 
                               "Currently employed", "Freelancing"])
        
        try:
            result = db.execute_returning(
                '''INSERT INTO description (short_desc, about, certificates, skills, current_status)
                   VALUES (%s, %s, %s, %s, %s)
                   RETURNING desc_id''',
                (short_desc, about, certs, skills, status)
            )
            if result:
                desc_id = result['desc_id']
                desc_map[user_id] = desc_id
                # Update user with description_id
                db.execute(
                    "UPDATE users SET description_id = %s WHERE uid = %s",
                    (desc_id, user_id)
                )
                count += 1
        except Exception as e:
            print(f"  Error creating description for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} descriptions")
    return desc_map


def generate_posts(db: Database, user_ids: List[int]) -> None:
    """Generate posts for users"""
    print("\n[2/20] Generating posts...")
    count = 0
    
    for user_id in user_ids:
        num_posts = random.randint(3, 10)
        for _ in range(num_posts):
            post_desc = random.choice(POST_DESCRIPTIONS).format(
                skill=random.choice(SKILLS),
                project=random.choice(PROJECT_TITLES)
            )
            likes = random.randint(0, 50)
            comments = random.randint(0, 20)
            
            # Random chance of having media
            has_media = random.random() < 0.3
            media_url = f"https://example.com/media/{random.randint(1000, 9999)}.jpg" if has_media else None
            media_type = random.choice(["image", "video"]) if has_media else None
            
            try:
                # First insert to get post_id
                result = db.execute_returning(
                    '''INSERT INTO post (uid, post_desc, likes, comments, media_url, media_type, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       RETURNING post_id''',
                    (user_id, post_desc, likes, comments, media_url, media_type,
                     datetime.now() - timedelta(days=random.randint(0, 90)))
                )
                if result:
                    post_id = result['post_id']
                    # Update with post_link
                    post_link = f"/post/{post_id}"
                    db.execute(
                        "UPDATE post SET post_link = %s WHERE post_id = %s",
                        (post_link, post_id)
                    )
                    count += 1
            except Exception as e:
                print(f"  Error creating post for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} posts")


def generate_likes(db: Database, user_ids: List[int]) -> None:
    """Generate likes on posts"""
    print("\n[3/20] Generating likes...")
    count = 0
    
    # Get all posts
    posts = db.fetch_all("SELECT post_id FROM post WHERE is_deleted = FALSE")
    
    for post in posts:
        # Random users like this post
        likers = random.sample(user_ids, random.randint(0, min(10, len(user_ids))))
        for user_id in likers:
            try:
                db.execute(
                    '''INSERT INTO likes (post_id, uid, created_at)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (post_id, uid) DO NOTHING''',
                    (post['post_id'], user_id, datetime.now() - timedelta(days=random.randint(0, 30)))
                )
                count += 1
            except Exception as e:
                pass  # Ignore conflicts
    
    print(f"  ✓ Generated {count} likes")


def generate_connections(db: Database, user_ids: List[int]) -> None:
    """Generate connections between users"""
    print("\n[4/20] Generating connections...")
    count = 0
    
    for user_id in user_ids:
        # Each user connects with 5-15 other users
        num_connections = random.randint(5, min(15, len(user_ids) - 1))
        connected_users = random.sample([uid for uid in user_ids if uid != user_id], num_connections)
        
        for connected_id in connected_users:
            try:
                # Create bidirectional connection
                db.execute(
                    '''INSERT INTO connections (follower_uid, followed_uid, connected_at)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (follower_uid, followed_uid) DO NOTHING''',
                    (user_id, connected_id, datetime.now() - timedelta(days=random.randint(0, 180)))
                )
                count += 1
            except Exception as e:
                pass  # Ignore conflicts
    
    print(f"  ✓ Generated {count} connections")


def generate_network(db: Database, user_ids: List[int]) -> None:
    """Generate network records"""
    print("\n[5/20] Generating network records...")
    count = 0
    
    for user_id in user_ids:
        # Get connection count
        result = db.fetch_one(
            "SELECT COUNT(*) as count FROM connections WHERE follower_uid = %s",
            (user_id,)
        )
        num_connections = result['count'] if result else 0
        
        try:
            db.execute(
                '''INSERT INTO network (uid, num_connections, created_at, updated_at)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (uid) DO UPDATE SET num_connections = %s, updated_at = %s''',
                (user_id, num_connections, datetime.now(), datetime.now(), num_connections, datetime.now())
            )
            count += 1
        except Exception as e:
            print(f"  Error creating network for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} network records")


def generate_connection_requests(db: Database, user_ids: List[int]) -> None:
    """Generate connection requests"""
    print("\n[6/20] Generating connection requests...")
    count = 0
    
    for user_id in user_ids:
        # Each user sends 2-5 connection requests
        num_requests = random.randint(2, 5)
        potential_receivers = [uid for uid in user_ids if uid != user_id]
        receivers = random.sample(potential_receivers, min(num_requests, len(potential_receivers)))
        
        for receiver_id in receivers:
            # Check if connection already exists
            existing = db.fetch_one(
                "SELECT 1 FROM connections WHERE follower_uid = %s AND followed_uid = %s",
                (user_id, receiver_id)
            )
            if existing:
                continue
            
            status = random.choice(["pending", "accepted", "rejected"])
            message = random.choice([
                "Hi! I'd like to connect with you.",
                "Would love to connect and network!",
                "Let's connect and share ideas!",
                None
            ])
            
            try:
                db.execute(
                    '''INSERT INTO connection_requests (sender_id, receiver_id, status, message, created_at)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (sender_id, receiver_id) DO NOTHING''',
                    (user_id, receiver_id, status, message, datetime.now() - timedelta(days=random.randint(0, 30)))
                )
                count += 1
            except Exception as e:
                pass  # Ignore conflicts
    
    print(f"  ✓ Generated {count} connection requests")


def generate_notifications(db: Database, user_ids: List[int]) -> None:
    """Generate notifications"""
    print("\n[7/20] Generating notifications...")
    count = 0
    
    notification_types = [
        ("connection_request", "New Connection Request", "You have a new connection request"),
        ("connection_accepted", "Connection Accepted", "Your connection request was accepted"),
        ("post_like", "New Like", "Someone liked your post"),
        ("post_comment", "New Comment", "Someone commented on your post"),
        ("job_application", "Application Update", "Your job application status has been updated"),
    ]
    
    for user_id in user_ids:
        num_notifications = random.randint(5, 20)
        for _ in range(num_notifications):
            notif_type, title, message = random.choice(notification_types)
            related_user_id = random.choice([uid for uid in user_ids if uid != user_id]) if random.random() < 0.7 else None
            
            try:
                db.execute(
                    '''INSERT INTO notifications (user_id, type, title, message, related_user_id, is_read, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                    (user_id, notif_type, title, message, related_user_id, random.random() < 0.3,
                     datetime.now() - timedelta(days=random.randint(0, 60)))
                )
                count += 1
            except Exception as e:
                print(f"  Error creating notification: {e}")
    
    print(f"  ✓ Generated {count} notifications")


def generate_payments(db: Database, user_ids: List[int]) -> None:
    """Generate payment records"""
    print("\n[8/20] Generating payment records...")
    count = 0
    
    for user_id in user_ids:
        # Only some users have payment records
        if random.random() < 0.3:
            # Check if payment already exists
            existing = db.fetch_one("SELECT pay_id FROM payment WHERE uid = %s", (user_id,))
            if existing:
                continue
            
            subscription_status = random.choice(["active", "inactive", "cancelled", "trial"])
            subscription_plan = random.choice(["basic", "premium", "enterprise"]) if subscription_status == "active" else None
            
            try:
                db.execute(
                    '''INSERT INTO payment (uid, subscription_status, subscription_plan, subscription_start, created_at)
                       VALUES (%s, %s, %s, %s, %s)''',
                    (user_id, subscription_status, subscription_plan,
                     datetime.now() - timedelta(days=random.randint(0, 365)) if subscription_status == "active" else None,
                     datetime.now() - timedelta(days=random.randint(0, 365)))
                )
                count += 1
            except Exception as e:
                print(f"  Error creating payment for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} payment records")


def generate_user_experience(db: Database, user_ids: List[int]) -> None:
    """Generate user experience records"""
    print("\n[9/20] Generating user experience records...")
    count = 0
    
    for user_id in user_ids:
        num_experiences = random.randint(1, 4)
        for i in range(num_experiences):
            title = random.choice(JOB_TITLES)
            company = random.choice(COMPANIES)
            location = random.choice(LOCATIONS)
            
            # Calculate dates
            end_date_offset = random.randint(365, 2000) if i < num_experiences - 1 else None
            start_date = date.today() - timedelta(days=random.randint(500, 2000))
            end_date = start_date + timedelta(days=end_date_offset) if end_date_offset else None
            is_current = (end_date is None)
            
            description = f"Worked as {title} at {company}. Responsible for {random.choice(['developing', 'maintaining', 'designing', 'managing'])} {random.choice(['web applications', 'mobile apps', 'APIs', 'databases', 'cloud infrastructure'])}."
            employment_type = random.choice(["full-time", "part-time", "contract", "internship"])
            
            try:
                db.execute(
                    '''INSERT INTO user_experience (user_id, title, company, location, start_date, end_date, is_current, description, employment_type)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (user_id, title, company, location, start_date, end_date, is_current, description, employment_type)
                )
                count += 1
            except Exception as e:
                print(f"  Error creating experience for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} experience records")


def generate_user_education(db: Database, user_ids: List[int]) -> None:
    """Generate user education records"""
    print("\n[10/20] Generating user education records...")
    count = 0
    
    for user_id in user_ids:
        num_educations = random.randint(1, 3)
        for _ in range(num_educations):
            school = random.choice(SCHOOLS)
            degree = random.choice(DEGREES)
            field_of_study = random.choice(FIELDS_OF_STUDY)
            start_year = random.randint(2010, 2020)
            end_year = start_year + random.randint(3, 5)
            grade = random.choice(["3.5", "3.7", "3.8", "3.9", "4.0", "A", "B+", "A-"])
            activities = random.choice([
                "Student Council", "Coding Club", "Hackathon Organizer",
                "Research Assistant", "Teaching Assistant", None
            ])
            description = f"Studied {field_of_study} at {school}. Focused on {random.choice(['software engineering', 'data science', 'machine learning', 'web development'])}."
            
            try:
                db.execute(
                    '''INSERT INTO user_education (user_id, school, degree, field_of_study, start_year, end_year, grade, activities, description)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (user_id, school, degree, field_of_study, start_year, end_year, grade, activities, description)
                )
                count += 1
            except Exception as e:
                print(f"  Error creating education for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} education records")


def generate_user_projects(db: Database, user_ids: List[int]) -> None:
    """Generate user project records"""
    print("\n[11/20] Generating user project records...")
    count = 0
    
    for user_id in user_ids:
        num_projects = random.randint(2, 6)
        for _ in range(num_projects):
            title = random.choice(PROJECT_TITLES)
            description = f"A {title.lower()} built with modern technologies. Features include {random.choice(['user authentication', 'real-time updates', 'data visualization', 'responsive design'])}."
            url = f"https://github.com/user/{title.lower().replace(' ', '-')}" if random.random() < 0.7 else None
            start_date = date.today() - timedelta(days=random.randint(100, 500))
            end_date = start_date + timedelta(days=random.randint(30, 180)) if random.random() < 0.7 else None
            associated_with = random.choice(COMPANIES) if random.random() < 0.5 else None
            technologies = random.choice(TECHNOLOGIES)
            
            try:
                db.execute(
                    '''INSERT INTO user_projects (user_id, title, description, url, start_date, end_date, associated_with, technologies)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (user_id, title, description, url, start_date, end_date, associated_with, json.dumps(technologies))
                )
                count += 1
            except Exception as e:
                print(f"  Error creating project for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} project records")


def generate_user_recommendations(db: Database, user_ids: List[int]) -> None:
    """Generate user recommendation records"""
    print("\n[12/20] Generating user recommendation records...")
    count = 0
    
    for user_id in user_ids:
        # Each user gets 1-3 recommendations
        num_recommendations = random.randint(1, 3)
        recommenders = random.sample([uid for uid in user_ids if uid != user_id], 
                                     min(num_recommendations, len(user_ids) - 1))
        
        user = db.fetch_one("SELECT name FROM users WHERE uid = %s", (user_id,))
        user_name = user['name'] if user else "User"
        
        for recommender_id in recommenders:
            recommender = db.fetch_one("SELECT name FROM users WHERE uid = %s", (recommender_id,))
            recommender_name = recommender['name'] if recommender else "Colleague"
            
            relationship = random.choice(RELATIONSHIPS)
            role = random.choice(JOB_TITLES)
            skill = random.choice(SKILLS)
            recommendation_text = random.choice(RECOMMENDATION_TEXTS).format(
                name=user_name, role=role, skill=skill
            )
            
            try:
                db.execute(
                    '''INSERT INTO user_recommendations (user_id, recommender_id, relationship, recommendation_text, is_visible)
                       VALUES (%s, %s, %s, %s, %s)''',
                    (user_id, recommender_id, relationship, recommendation_text, True)
                )
                count += 1
            except Exception as e:
                print(f"  Error creating recommendation: {e}")
    
    print(f"  ✓ Generated {count} recommendation records")


def generate_user_interests(db: Database, user_ids: List[int]) -> None:
    """Generate user interest records"""
    print("\n[13/20] Generating user interest records...")
    count = 0
    
    for user_id in user_ids:
        num_interests = random.randint(3, 8)
        for _ in range(num_interests):
            interest_type = random.choice(INTEREST_TYPES)
            name = random.choice(INTEREST_NAMES[interest_type])
            url = f"https://example.com/{interest_type}/{name.lower().replace(' ', '-')}" if random.random() < 0.5 else None
            
            try:
                db.execute(
                    '''INSERT INTO user_interests (user_id, interest_type, name, url)
                       VALUES (%s, %s, %s, %s)''',
                    (user_id, interest_type, name, url)
                )
                count += 1
            except Exception as e:
                print(f"  Error creating interest: {e}")
    
    print(f"  ✓ Generated {count} interest records")


def generate_profile_analytics(db: Database, user_ids: List[int]) -> None:
    """Generate profile analytics records"""
    print("\n[14/20] Generating profile analytics records...")
    count = 0
    
    for user_id in user_ids:
        num_views = random.randint(5, 30)
        for _ in range(num_views):
            viewer_id = random.choice([uid for uid in user_ids if uid != user_id]) if random.random() < 0.8 else None
            view_type = random.choice(["profile_view", "search_appearance"])
            source = random.choice(["search", "feed", "direct", "connection"])
            
            try:
                db.execute(
                    '''INSERT INTO profile_analytics (user_id, viewer_id, view_type, source, viewed_at)
                       VALUES (%s, %s, %s, %s, %s)''',
                    (user_id, viewer_id, view_type, source,
                     datetime.now() - timedelta(days=random.randint(0, 90)))
                )
                count += 1
            except Exception as e:
                print(f"  Error creating profile analytics: {e}")
    
    print(f"  ✓ Generated {count} profile analytics records")


def generate_users_context(db: Database, user_ids: List[int]) -> None:
    """Generate users context records"""
    print("\n[15/20] Generating users context records...")
    count = 0
    
    for user_id in user_ids:
        # Check if context already exists
        existing = db.fetch_one("SELECT id FROM users_context WHERE user_id = %s", (user_id,))
        if existing:
            continue
        
        user = db.fetch_one("SELECT name, user_email FROM users WHERE uid = %s", (user_id,))
        user_name = user['name'] if user else "User"
        
        zed_context = f"""User Profile: {user_name}
Interests: {', '.join(random.sample(SKILLS, 5))}
Skills: {', '.join(random.sample(SKILLS, 8))}
Current Status: {random.choice(['Looking for opportunities', 'Open to networking', 'Currently employed'])}
Experience: {random.randint(2, 10)} years in software development
"""
        
        runtime_context = {
            "activities": [
                {"type": "view_job", "content": f"Viewed job posting for {random.choice(JOB_TITLES)}"},
                {"type": "like_post", "content": "Liked a post about React"},
                {"type": "complete_course", "content": f"Completed course: {random.choice(['React Basics', 'Node.js Advanced'])}"}
            ]
        }
        
        try:
            db.execute(
                '''INSERT INTO users_context (user_id, zed, runtime_context)
                   VALUES (%s, %s, %s)''',
                (user_id, zed_context, json.dumps(runtime_context))
            )
            count += 1
        except Exception as e:
            print(f"  Error creating context for user {user_id}: {e}")
    
    print(f"  ✓ Generated {count} context records")


def generate_jobs(db: Database, user_ids: List[int]) -> None:
    """Generate job records (legacy job table)"""
    print("\n[16/20] Generating job records...")
    count = 0
    
    for user_id in user_ids:
        if random.random() < 0.5:  # Only some users have job records
            job_desc = random.choice(JOB_DESCRIPTIONS).format(
                title=random.choice(JOB_TITLES),
                skills=", ".join(random.sample(SKILLS, 3))
            )
            designation = random.choice(JOB_TITLES)
            
            try:
                db.execute(
                    '''INSERT INTO job (uid, job_desc, designation, created_at)
                       VALUES (%s, %s, %s, %s)''',
                    (user_id, job_desc, designation, datetime.now() - timedelta(days=random.randint(0, 180)))
                )
                count += 1
            except Exception as e:
                print(f"  Error creating job: {e}")
    
    print(f"  ✓ Generated {count} job records")


def generate_job_postings(db: Database, user_ids: List[int]) -> None:
    """Generate job postings"""
    print("\n[17/20] Generating job postings...")
    count = 0
    
    for user_id in user_ids:
        if random.random() < 0.3:  # Only some users post jobs
            num_postings = random.randint(1, 3)
            for _ in range(num_postings):
                title = random.choice(JOB_TITLES)
                description = random.choice(JOB_DESCRIPTIONS).format(
                    title=title,
                    skills=", ".join(random.sample(SKILLS, 5))
                )
                company_name = random.choice(COMPANIES)
                location = random.choice(LOCATIONS)
                job_type = random.choice(JOB_TYPES)
                is_remote = random.random() < 0.4
                experience_level = random.choice(EXPERIENCE_LEVELS)
                skills_required = ", ".join(random.sample(SKILLS, random.randint(3, 8)))
                salary_min = random.randint(60000, 120000)
                salary_max = salary_min + random.randint(20000, 50000)
                
                try:
                    db.execute(
                        '''INSERT INTO job_postings (poster_id, title, description, company_name, location, job_type, is_remote, experience_level, skills_required, salary_min, salary_max, status)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                        (user_id, title, description, company_name, location, job_type, is_remote,
                         experience_level, skills_required, salary_min, salary_max, "active")
                    )
                    count += 1
                except Exception as e:
                    print(f"  Error creating job posting: {e}")
    
    print(f"  ✓ Generated {count} job postings")


def generate_job_applications(db: Database, user_ids: List[int]) -> None:
    """Generate job applications"""
    print("\n[18/20] Generating job applications...")
    count = 0
    
    job_postings = get_existing_job_postings(db)
    if not job_postings:
        print("  ⚠ No job postings found, skipping applications")
        return
    
    for user_id in user_ids:
        if random.random() < 0.4:  # 40% of users apply for jobs
            num_applications = random.randint(1, 5)
            applied_jobs = random.sample(job_postings, min(num_applications, len(job_postings)))
            
            for job in applied_jobs:
                status = random.choice(["pending", "reviewed", "interview", "accepted", "rejected"])
                cover_letter = f"Dear Hiring Manager, I am interested in this position and believe my skills in {', '.join(random.sample(SKILLS, 3))} make me a great fit." if random.random() < 0.7 else None
                match_score = random.randint(60, 95)
                
                try:
                    db.execute(
                        '''INSERT INTO job_applications (job_id, applicant_id, status, cover_letter, match_score, applied_at)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           ON CONFLICT (job_id, applicant_id) DO NOTHING''',
                        (job['job_id'], user_id, status, cover_letter, match_score,
                         datetime.now() - timedelta(days=random.randint(0, 60)))
                    )
                    count += 1
                except Exception as e:
                    pass  # Ignore conflicts
    
    print(f"  ✓ Generated {count} job applications")


def generate_job_saved(db: Database, user_ids: List[int]) -> None:
    """Generate saved jobs"""
    print("\n[19/20] Generating saved jobs...")
    count = 0
    
    job_postings = get_existing_job_postings(db)
    if not job_postings:
        print("  ⚠ No job postings found, skipping saved jobs")
        return
    
    for user_id in user_ids:
        if random.random() < 0.5:  # 50% of users save jobs
            num_saved = random.randint(1, 8)
            saved_jobs = random.sample(job_postings, min(num_saved, len(job_postings)))
            
            for job in saved_jobs:
                try:
                    db.execute(
                        '''INSERT INTO job_saved (job_id, user_id, saved_at)
                           VALUES (%s, %s, %s)
                           ON CONFLICT (job_id, user_id) DO NOTHING''',
                        (job['job_id'], user_id, datetime.now() - timedelta(days=random.randint(0, 90)))
                    )
                    count += 1
                except Exception as e:
                    pass  # Ignore conflicts
    
    print(f"  ✓ Generated {count} saved jobs")


def generate_lms_data(db: Database, user_ids: List[int]) -> None:
    """Generate LMS-related data"""
    print("\n[20/20] Generating LMS data...")
    
    courses = get_existing_courses(db)
    domains = get_existing_domains(db)
    sections = get_existing_sections(db)
    questions = get_existing_questions(db)
    
    if not courses:
        print("  ⚠ No courses found, skipping LMS data generation")
        return
    
    # Generate LMS Dashboard
    print("  Generating LMS dashboards...")
    dashboard_count = 0
    for user_id in user_ids:
        try:
            db.execute(
                '''INSERT INTO lms_dashboard (user_id, total_questions, correct_answers, wrong_answers, overall_accuracy, day_streak, last_activity_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (user_id) DO NOTHING''',
                (user_id, random.randint(10, 100), random.randint(5, 80), random.randint(2, 20),
                 round(random.uniform(60, 95), 2), random.randint(0, 30), date.today() - timedelta(days=random.randint(0, 7)))
            )
            dashboard_count += 1
        except Exception as e:
            pass
    
    print(f"    ✓ Generated {dashboard_count} LMS dashboards")
    
    # Generate User Courses
    print("  Generating user courses...")
    course_count = 0
    for user_id in user_ids:
        if random.random() < 0.7:  # 70% of users enroll in courses
            num_courses = random.randint(1, min(5, len(courses)))
            enrolled_courses = random.sample(courses, num_courses)
            
            for course in enrolled_courses:
                status = random.choice(["not_started", "in_progress", "completed"])
                progress = random.randint(0, 100) if status != "not_started" else 0
                started_at = datetime.now() - timedelta(days=random.randint(0, 90)) if status != "not_started" else None
                completed_at = datetime.now() - timedelta(days=random.randint(0, 30)) if status == "completed" else None
                
                try:
                    db.execute(
                        '''INSERT INTO lms_user_courses (user_id, course_id, progress, status, started_at, completed_at, last_accessed_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (user_id, course_id) DO NOTHING''',
                        (user_id, course['id'], progress, status, started_at, completed_at,
                         datetime.now() - timedelta(days=random.randint(0, 7)) if started_at else None)
                    )
                    course_count += 1
                except Exception as e:
                    pass
    
    print(f"    ✓ Generated {course_count} user course enrollments")
    
    # Generate Domain Performance
    print("  Generating domain performance...")
    domain_count = 0
    for user_id in user_ids:
        if domains and random.random() < 0.6:
            num_domains = random.randint(1, min(3, len(domains)))
            user_domains = random.sample(domains, num_domains)
            
            for domain in user_domains:
                questions_answered = random.randint(5, 50)
                correct_answers = random.randint(3, questions_answered)
                accuracy = round((correct_answers / questions_answered) * 100, 2) if questions_answered > 0 else 0
                
                try:
                    db.execute(
                        '''INSERT INTO lms_user_domain_performance (user_id, domain_id, questions_answered, correct_answers, accuracy_percentage)
                           VALUES (%s, %s, %s, %s, %s)
                           ON CONFLICT (user_id, domain_id) DO NOTHING''',
                        (user_id, domain['id'], questions_answered, correct_answers, accuracy)
                    )
                    domain_count += 1
                except Exception as e:
                    pass
    
    print(f"    ✓ Generated {domain_count} domain performance records")
    
    # Generate Course Performance
    print("  Generating course performance...")
    perf_count = 0
    for user_id in user_ids:
        if courses and random.random() < 0.5:
            num_courses = random.randint(1, min(3, len(courses)))
            user_courses = random.sample(courses, num_courses)
            
            for course in user_courses:
                questions_answered = random.randint(5, 40)
                correct_answers = random.randint(3, questions_answered)
                wrong_answers = questions_answered - correct_answers
                accuracy = round((correct_answers / questions_answered) * 100, 2) if questions_answered > 0 else 0
                total_points = random.randint(10, 200)
                
                try:
                    db.execute(
                        '''INSERT INTO lms_user_course_performance (user_id, course_id, questions_answered, correct_answers, wrong_answers, accuracy_percentage, total_points_earned, last_activity_date)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (user_id, course_id) DO NOTHING''',
                        (user_id, course['id'], questions_answered, correct_answers, wrong_answers, accuracy,
                         total_points, date.today() - timedelta(days=random.randint(0, 7)))
                    )
                    perf_count += 1
                except Exception as e:
                    pass
    
    print(f"    ✓ Generated {perf_count} course performance records")
    
    # Generate Weekly Performance
    print("  Generating weekly performance...")
    weekly_count = 0
    for user_id in user_ids:
        if random.random() < 0.6:
            # Generate last 4 weeks of data
            for week_offset in range(4):
                week_date = date.today() - timedelta(weeks=week_offset)
                questions_answered = random.randint(0, 20)
                correct_answers = random.randint(0, questions_answered) if questions_answered > 0 else 0
                wrong_answers = questions_answered - correct_answers
                study_time = random.randint(0, 300)  # minutes
                
                try:
                    db.execute(
                        '''INSERT INTO lms_weekly_performance (user_id, date, questions_answered, correct_answers, wrong_answers, study_time_minutes)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           ON CONFLICT (user_id, date) DO NOTHING''',
                        (user_id, week_date, questions_answered, correct_answers, wrong_answers, study_time)
                    )
                    weekly_count += 1
                except Exception as e:
                    pass
    
    print(f"    ✓ Generated {weekly_count} weekly performance records")
    
    # Generate Activities
    print("  Generating activities...")
    activity_count = 0
    activity_types = [
        ("course_started", "Started Course", "You started a new course"),
        ("course_completed", "Course Completed", "Congratulations! You completed a course"),
        ("question_answered", "Question Answered", "You answered a question"),
        ("certificate_earned", "Certificate Earned", "You earned a certificate"),
    ]
    
    for user_id in user_ids:
        num_activities = random.randint(5, 15)
        for _ in range(num_activities):
            activity_type, title, description = random.choice(activity_types)
            course = random.choice(courses) if courses else None
            
            try:
                db.execute(
                    '''INSERT INTO lms_activities (user_id, course_id, activity_type, title, description, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (user_id, course['id'] if course else None, activity_type, title, description,
                     datetime.now() - timedelta(days=random.randint(0, 60)))
                )
                activity_count += 1
            except Exception as e:
                pass
    
    print(f"    ✓ Generated {activity_count} activity records")
    
    # Generate Section Progress
    print("  Generating section progress...")
    section_count = 0
    for user_id in user_ids:
        if sections and random.random() < 0.5:
            num_sections = random.randint(1, min(5, len(sections)))
            user_sections = random.sample(sections, num_sections)
            
            for section in user_sections:
                completed_items = random.randint(0, 10)
                is_completed = random.random() < 0.3
                
                try:
                    db.execute(
                        '''INSERT INTO lms_user_section_progress (user_id, section_id, completed_items, is_completed)
                           VALUES (%s, %s, %s, %s)
                           ON CONFLICT (user_id, section_id) DO NOTHING''',
                        (user_id, section['id'], completed_items, is_completed)
                    )
                    section_count += 1
                except Exception as e:
                    pass
    
    print(f"    ✓ Generated {section_count} section progress records")
    
    # Generate User Answers
    print("  Generating user answers...")
    answer_count = 0
    for user_id in user_ids:
        if questions and random.random() < 0.4:
            num_answers = random.randint(1, min(10, len(questions)))
            user_questions = random.sample(questions, num_answers)
            
            for question in user_questions:
                answer_text = f"Sample answer for question {question['id']}"
                is_correct = random.random() < 0.7
                points_earned = random.randint(0, 10) if is_correct else 0
                feedback = "Great answer!" if is_correct else "Try to be more specific."
                
                try:
                    db.execute(
                        '''INSERT INTO lms_user_answers (user_id, question_id, answer_text, is_correct, points_earned, submitted_at, evaluated_at, feedback)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                        (user_id, question['id'], answer_text, is_correct, points_earned,
                         datetime.now() - timedelta(days=random.randint(0, 30)),
                         datetime.now() - timedelta(days=random.randint(0, 30)),
                         feedback)
                    )
                    answer_count += 1
                except Exception as e:
                    pass
    
    print(f"    ✓ Generated {answer_count} user answers")
    
    print("  ✓ LMS data generation complete")


def main():
    """Main function to generate all user data"""
    print("=" * 70)
    print("User Data Generation Script")
    print("=" * 70)
    print("\nThis script will generate comprehensive data for all existing users")
    print("(excluding admin@roshaan.com)")
    print("\n⚠️  WARNING: This will add data to your database!")
    print("=" * 70)
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    db = None
    try:
        db = get_db()
        print("\n✓ Connected to database")
        
        # Get all users except admin
        users = get_all_users_except_admin(db)
        if not users:
            print("\n⚠️  No users found (excluding admin@roshaan.com)")
            return
        
        user_ids = [user['uid'] for user in users]
        print(f"\n✓ Found {len(user_ids)} users to process")
        print(f"  Users: {', '.join([u['username'] or u['user_email'] for u in users[:5]])}{'...' if len(users) > 5 else ''}")
        
        # Generate all data
        desc_map = generate_descriptions(db, user_ids)
        generate_posts(db, user_ids)
        generate_likes(db, user_ids)
        generate_connections(db, user_ids)
        generate_network(db, user_ids)
        generate_connection_requests(db, user_ids)
        generate_notifications(db, user_ids)
        generate_payments(db, user_ids)
        generate_user_experience(db, user_ids)
        generate_user_education(db, user_ids)
        generate_user_projects(db, user_ids)
        generate_user_recommendations(db, user_ids)
        generate_user_interests(db, user_ids)
        generate_profile_analytics(db, user_ids)
        generate_users_context(db, user_ids)
        generate_jobs(db, user_ids)
        generate_job_postings(db, user_ids)
        generate_job_applications(db, user_ids)
        generate_job_saved(db, user_ids)
        generate_lms_data(db, user_ids)
        
        print("\n" + "=" * 70)
        print("✅ Data generation completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db:
            db.close()
            print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
