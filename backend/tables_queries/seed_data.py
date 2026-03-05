"""
Database Seed Data Generator
Generates sample data for all tables in the ZedReq database
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_connection_params, Database
from utils.auth import hash_password

# Sample data constants
SAMPLE_USERS = [
    ("john_doe", "john@example.com", "Password123", "John Doe"),
    ("jane_smith", "jane@example.com", "Password123", "Jane Smith"),
    ("bob_wilson", "bob@example.com", "Password123", "Bob Wilson"),
    ("alice_johnson", "alice@example.com", "Password123", "Alice Johnson"),
    ("charlie_brown", "charlie@example.com", "Password123", "Charlie Brown"),
    ("diana_ross", "diana@example.com", "Password123", "Diana Ross"),
    ("edward_chen", "edward@example.com", "Password123", "Edward Chen"),
    ("fiona_green", "fiona@example.com", "Password123", "Fiona Green"),
    ("george_kim", "george@example.com", "Password123", "George Kim"),
    ("hannah_lee", "hannah@example.com", "Password123", "Hannah Lee"),
]

SAMPLE_DESCRIPTIONS = [
    ("Software Engineer", "Full-stack developer with 5 years of experience in Python and JavaScript", "AWS Certified, Google Cloud Professional", "Python, JavaScript, React, Node.js", "Available for work"),
    ("Data Scientist", "ML enthusiast and Python expert working on predictive analytics", "TensorFlow Certified, Coursera ML Specialization", "Python, TensorFlow, PyTorch, SQL", "Open to opportunities"),
    ("DevOps Engineer", "Cloud infrastructure specialist with expertise in Kubernetes", "CKA, AWS Solutions Architect", "Docker, Kubernetes, AWS, Terraform", "Currently employed"),
    ("Frontend Developer", "React and Vue.js developer passionate about UI/UX", "Meta Frontend Certified", "React, Vue.js, TypeScript, CSS", "Freelancing"),
    ("Backend Developer", "Node.js and Python backend expert focused on scalability", "MongoDB Certified", "Node.js, Python, PostgreSQL, Redis", "Looking for remote work"),
    ("UI/UX Designer", "Creating beautiful user experiences with Figma and Adobe XD", "Google UX Design Certificate", "Figma, Sketch, Adobe XD, CSS", "Available for projects"),
    ("Mobile Developer", "iOS and Android specialist with React Native expertise", "Apple Developer Certified", "Swift, Kotlin, React Native, Flutter", "Open to hybrid roles"),
    ("Product Manager", "Turning ideas into products with agile methodologies", "PMP, Scrum Master", "Agile, Scrum, JIRA, Analytics", "Currently employed"),
    ("Security Engineer", "Cybersecurity and penetration testing professional", "CISSP, CEH", "Python, Network Security, Penetration Testing", "Consulting"),
    ("QA Engineer", "Quality assurance and test automation specialist", "ISTQB Certified", "Selenium, Cypress, Python, Postman", "Full-time"),
]

SAMPLE_JOBS = [
    ("Developing and maintaining web applications using React and Node.js", "Senior Software Engineer"),
    ("Building ML models for customer behavior prediction", "Data Scientist"),
    ("Managing CI/CD pipelines and cloud infrastructure", "DevOps Lead"),
    ("Creating responsive UI components with React", "Frontend Developer"),
    ("Designing RESTful APIs and microservices", "Backend Engineer"),
    ("Designing user interfaces for mobile applications", "UI/UX Designer"),
    ("Developing cross-platform mobile applications", "Mobile Developer"),
    ("Leading product development initiatives", "Product Manager"),
    ("Conducting security audits and vulnerability assessments", "Security Analyst"),
    ("Writing and maintaining automated test suites", "QA Lead"),
]

SAMPLE_COURSES = [
    ("Introduction to React", "Learn the fundamentals of React and build modern web applications", "RC", 24, "6h 30m", "Frontend", "beginner"),
    ("Advanced JavaScript", "Master advanced JavaScript concepts and ES6+ features", "JS", 32, "8h 15m", "Frontend", "intermediate"),
    ("Node.js Backend Development", "Build scalable backend applications with Node.js and Express", "ND", 28, "7h 45m", "Backend", "intermediate"),
    ("Database Design", "Learn SQL, NoSQL databases and database optimization techniques", "DB", 20, "5h 20m", "Database", "beginner"),
    ("UI/UX Design Principles", "Create beautiful and user-friendly interfaces", "UI", 18, "4h 30m", "Design", "beginner"),
    ("Python for Data Science", "Data analysis and visualization with Python libraries", "PY", 30, "9h 00m", "Data Science", "intermediate"),
    ("TypeScript Fundamentals", "Learn TypeScript and build type-safe applications", "TS", 26, "7h 00m", "Frontend", "beginner"),
    ("Docker & Containerization", "Master containerization and deployment with Docker", "DK", 22, "6h 15m", "DevOps", "intermediate"),
    ("GraphQL API Development", "Build modern APIs with GraphQL and Apollo", "GQ", 25, "6h 45m", "Backend", "advanced"),
    ("AWS Cloud Services", "Deploy and manage applications on Amazon Web Services", "AWS", 35, "10h 30m", "Cloud", "advanced"),
]

SAMPLE_DOMAINS = [
    ("React & Frontend", "Frontend development with React", "react"),
    ("JavaScript ES6+", "Modern JavaScript programming", "javascript"),
    ("Node.js & Backend", "Server-side development", "nodejs"),
    ("Database & SQL", "Database management and queries", "database"),
    ("UI/UX Design", "User interface and experience design", "design"),
    ("Python & Data Science", "Python programming and data analysis", "python"),
    ("DevOps & Cloud", "Infrastructure and deployment", "devops"),
]

SAMPLE_POSTS = [
    "Just finished a great tutorial on React hooks! The useEffect hook is incredibly powerful.",
    "Anyone else excited about the new TypeScript 5.0 features?",
    "Pro tip: Always use meaningful variable names. Your future self will thank you!",
    "Started learning GraphQL today. The query language is so intuitive!",
    "Docker has changed the way I deploy applications. No more 'it works on my machine'!",
    "Just got AWS certified! Hard work pays off.",
    "Code review tip: Focus on the logic, not just the syntax.",
    "Python's list comprehensions are a game changer for data processing.",
    "Remember to take breaks while coding. Your brain needs rest too!",
    "Just deployed my first Kubernetes cluster. Feeling accomplished!",
]


def get_db():
    """Get database connection"""
    params = get_connection_params()
    return Database(params)


def seed_descriptions(db: Database) -> list:
    """Seed description table and return list of desc_ids"""
    print("Seeding descriptions...")
    desc_ids = []
    
    for short_desc, about, certs, skills, status in SAMPLE_DESCRIPTIONS:
        try:
            result = db.execute_returning(
                '''INSERT INTO description (short_desc, about, certificates, skills, current_status)
                   VALUES (%s, %s, %s, %s, %s)
                   RETURNING desc_id''',
                (short_desc, about, certs, skills, status)
            )
            if result:
                desc_ids.append(result['desc_id'])
                print(f"  Created description: {short_desc}")
        except Exception as e:
            print(f"  Error creating description: {e}")
    
    print(f"Total descriptions: {len(desc_ids)}")
    return desc_ids


def seed_users(db: Database, desc_ids: list) -> list:
    """Seed users table and return list of created user IDs"""
    print("Seeding users...")
    user_ids = []
    
    for i, (username, email, password, full_name) in enumerate(SAMPLE_USERS):
        try:
            desc_id = desc_ids[i] if i < len(desc_ids) else None
            result = db.execute_returning(
                '''INSERT INTO users (username, name, user_email, password_hash, email_verified, description_id)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (username) DO NOTHING
                   RETURNING uid''',
                (username, full_name, email, hash_password(password), True, desc_id)
            )
            if result:
                user_ids.append(result['uid'])
                print(f"  Created user: {username} (uid: {result['uid']})")
        except Exception as e:
            print(f"  Error creating user {username}: {e}")
    
    # If no new users created, fetch existing ones
    if not user_ids:
        existing = db.fetch_all("SELECT uid FROM users LIMIT 10")
        user_ids = [u['uid'] for u in existing]
        print(f"  Using {len(user_ids)} existing users")
    
    print(f"Total users: {len(user_ids)}")
    return user_ids


def seed_jobs(db: Database, user_ids: list) -> list:
    """Seed jobs table"""
    print("Seeding jobs...")
    job_ids = []
    
    for i, (job_desc, designation) in enumerate(SAMPLE_JOBS):
        if i >= len(user_ids):
            break
        user_id = user_ids[i]
        try:
            result = db.execute_returning(
                '''INSERT INTO job (uid, job_desc, designation)
                   VALUES (%s, %s, %s)
                   RETURNING job_id''',
                (user_id, job_desc, designation)
            )
            if result:
                job_ids.append(result['job_id'])
                # Update user with job_id
                db.execute(
                    'UPDATE users SET job_id = %s WHERE uid = %s',
                    (result['job_id'], user_id)
                )
                print(f"  Created job: {designation}")
        except Exception as e:
            print(f"  Error creating job: {e}")
    
    print(f"Total jobs: {len(job_ids)}")
    return job_ids


def seed_payment(db: Database, user_ids: list):
    """Seed payment table with PCI-compliant mock data"""
    print("Seeding payment records...")
    
    plans = ['free', 'basic', 'premium', 'enterprise']
    card_brands = ['visa', 'mastercard', 'amex']
    
    for i, user_id in enumerate(user_ids[:5]):  # Only first 5 users have payment
        try:
            result = db.execute_returning(
                '''INSERT INTO payment (uid, payment_provider, provider_customer_id, 
                   card_last_four, card_brand, billing_name, subscription_status, subscription_plan)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING pay_id''',
                (user_id, 'stripe', f'cus_mock_{user_id}',
                 str(random.randint(1000, 9999)), random.choice(card_brands),
                 SAMPLE_USERS[i][3], 'active', random.choice(plans))
            )
            if result:
                # Update user with pay_id
                db.execute(
                    'UPDATE users SET pay_id = %s WHERE uid = %s',
                    (result['pay_id'], user_id)
                )
                print(f"  Created payment for user {user_id}")
        except Exception as e:
            print(f"  Error creating payment: {e}")
    
    print("Payment records seeded")


def seed_posts(db: Database, user_ids: list) -> list:
    """Seed posts table"""
    print("Seeding posts...")
    post_ids = []
    
    for content in SAMPLE_POSTS:
        user_id = random.choice(user_ids)
        try:
            result = db.execute_returning(
                '''INSERT INTO post (uid, post_desc)
                   VALUES (%s, %s)
                   RETURNING post_id''',
                (user_id, content)
            )
            if result:
                post_ids.append(result['post_id'])
                print(f"  Created post #{result['post_id']}")
        except Exception as e:
            print(f"  Error creating post: {e}")
    
    print(f"Total posts: {len(post_ids)}")
    return post_ids


def seed_network_and_connections(db: Database, user_ids: list):
    """Seed network and connections tables"""
    print("Seeding networks and connections...")
    
    # Create network for each user
    for user_id in user_ids:
        try:
            db.execute(
                '''INSERT INTO network (uid, num_connections)
                   VALUES (%s, 0)
                   ON CONFLICT DO NOTHING''',
                (user_id,)
            )
        except Exception as e:
            print(f"  Error creating network: {e}")
    
    # Create some random connections
    for user_id in user_ids:
        # Each user follows 2-5 other users
        to_follow = random.sample([u for u in user_ids if u != user_id], 
                                  min(random.randint(2, 5), len(user_ids) - 1))
        for followed_id in to_follow:
            try:
                db.execute(
                    '''INSERT INTO connections (follower_uid, followed_uid)
                       VALUES (%s, %s)
                       ON CONFLICT DO NOTHING''',
                    (user_id, followed_id)
                )
                # Update connection counts
                db.execute(
                    'UPDATE network SET num_connections = num_connections + 1 WHERE uid = %s',
                    (followed_id,)
                )
            except Exception as e:
                pass
    
    print("Networks and connections seeded")


def seed_courses(db: Database) -> list:
    """Seed LMS courses and return list of course IDs"""
    print("Seeding courses...")
    course_ids = []
    
    for title, desc, icon, lessons, duration, category, difficulty in SAMPLE_COURSES:
        try:
            result = db.execute_returning(
                '''INSERT INTO lms_courses (title, description, icon, lessons, duration, category, difficulty)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   RETURNING id''',
                (title, desc, icon, lessons, duration, category, difficulty)
            )
            if result:
                course_ids.append(result['id'])
                print(f"  Created course: {title}")
        except Exception as e:
            print(f"  Error creating course {title}: {e}")
    
    if not course_ids:
        existing = db.fetch_all("SELECT id FROM lms_courses LIMIT 10")
        course_ids = [c['id'] for c in existing]
        print(f"  Using {len(course_ids)} existing courses")
    
    print(f"Total courses: {len(course_ids)}")
    return course_ids


def seed_domains(db: Database) -> list:
    """Seed LMS domains and return list of domain IDs"""
    print("Seeding domains...")
    domain_ids = []
    
    for name, desc, icon in SAMPLE_DOMAINS:
        try:
            result = db.execute_returning(
                '''INSERT INTO lms_domains (name, description, icon)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (name) DO NOTHING
                   RETURNING id''',
                (name, desc, icon)
            )
            if result:
                domain_ids.append(result['id'])
                print(f"  Created domain: {name}")
        except Exception as e:
            print(f"  Error creating domain {name}: {e}")
    
    if not domain_ids:
        existing = db.fetch_all("SELECT id FROM lms_domains LIMIT 10")
        domain_ids = [d['id'] for d in existing]
        print(f"  Using {len(domain_ids)} existing domains")
    
    print(f"Total domains: {len(domain_ids)}")
    return domain_ids


def seed_lms_dashboard(db: Database, user_ids: list):
    """Seed LMS dashboard for each user"""
    print("Seeding LMS dashboards...")
    
    for user_id in user_ids:
        total_q = random.randint(100, 1000)
        correct = int(total_q * random.uniform(0.6, 0.95))
        wrong = total_q - correct
        accuracy = round((correct / total_q) * 100, 2)
        streak = random.randint(1, 30)
        
        try:
            db.execute(
                '''INSERT INTO lms_dashboard (user_id, total_questions, correct_answers, wrong_answers, overall_accuracy, day_streak, last_activity_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (user_id) DO UPDATE SET
                   total_questions = EXCLUDED.total_questions,
                   correct_answers = EXCLUDED.correct_answers,
                   updated_at = CURRENT_TIMESTAMP''',
                (user_id, total_q, correct, wrong, accuracy, streak, datetime.now().date())
            )
            print(f"  Dashboard for user {user_id} - {accuracy}% accuracy")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("LMS dashboards seeded")


def seed_user_courses(db: Database, user_ids: list, course_ids: list):
    """Seed user course enrollments"""
    print("Seeding user course enrollments...")
    
    for user_id in user_ids:
        enrolled = random.sample(course_ids, min(random.randint(3, 7), len(course_ids)))
        for course_id in enrolled:
            progress = random.randint(0, 100)
            status = 'completed' if progress == 100 else ('in_progress' if progress > 0 else 'not_started')
            
            try:
                db.execute(
                    '''INSERT INTO lms_user_courses (user_id, course_id, progress, status, started_at, last_accessed_at)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (user_id, course_id) DO NOTHING''',
                    (user_id, course_id, progress, status, 
                     datetime.now() - timedelta(days=random.randint(1, 60)),
                     datetime.now() - timedelta(days=random.randint(0, 7)))
                )
            except Exception as e:
                print(f"  Error: {e}")
    
    print("User course enrollments seeded")


def seed_weekly_performance(db: Database, user_ids: list):
    """Seed weekly performance data"""
    print("Seeding weekly performance...")
    
    for user_id in user_ids:
        for day_offset in range(7):
            date = datetime.now().date() - timedelta(days=day_offset)
            questions = random.randint(20, 100)
            correct = int(questions * random.uniform(0.6, 0.95))
            
            try:
                db.execute(
                    '''INSERT INTO lms_weekly_performance (user_id, date, questions_answered, correct_answers, wrong_answers, study_time_minutes)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (user_id, date) DO NOTHING''',
                    (user_id, date, questions, correct, questions - correct, random.randint(15, 120))
                )
            except Exception as e:
                pass
    
    print("Weekly performance seeded")


def seed_domain_performance(db: Database, user_ids: list, domain_ids: list):
    """Seed user domain performance"""
    print("Seeding domain performance...")
    
    for user_id in user_ids:
        for domain_id in domain_ids:
            questions = random.randint(50, 200)
            correct = int(questions * random.uniform(0.5, 0.98))
            accuracy = round((correct / questions) * 100, 2)
            
            try:
                db.execute(
                    '''INSERT INTO lms_user_domain_performance (user_id, domain_id, questions_answered, correct_answers, accuracy_percentage)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (user_id, domain_id) DO NOTHING''',
                    (user_id, domain_id, questions, correct, accuracy)
                )
            except Exception as e:
                pass
    
    print("Domain performance seeded")


def seed_activities(db: Database, user_ids: list, course_ids: list):
    """Seed learning activities"""
    print("Seeding activities...")
    activity_types = ['completed_lesson', 'passed_quiz', 'started_course', 'earned_badge']
    titles = [
        "Completed React Hooks Module",
        "Mastered Async/Await Patterns",
        "Started Express.js Basics",
        "SQL Joins Practice",
        "Passed TypeScript Quiz",
        "Earned JavaScript Badge"
    ]
    
    for user_id in user_ids:
        for i in range(random.randint(3, 8)):
            try:
                db.execute(
                    '''INSERT INTO lms_activities (user_id, course_id, activity_type, title, icon)
                       VALUES (%s, %s, %s, %s, %s)''',
                    (user_id, random.choice(course_ids), random.choice(activity_types),
                     random.choice(titles), random.choice(['RC', 'JS', 'ND', 'TS']))
                )
            except Exception as e:
                pass
    
    print("Activities seeded")


def seed_deadlines(db: Database, user_ids: list, course_ids: list):
    """Seed user deadlines"""
    print("Seeding deadlines...")
    deadline_titles = [
        "TypeScript Final Project",
        "React Quiz - Advanced Concepts",
        "GraphQL Assignment Submission",
        "Database Design Review",
        "Node.js Project Deadline"
    ]
    
    for user_id in user_ids:
        for title in random.sample(deadline_titles, random.randint(2, 4)):
            try:
                db.execute(
                    '''INSERT INTO lms_deadlines (user_id, course_id, title, due_date)
                       VALUES (%s, %s, %s, %s)''',
                    (user_id, random.choice(course_ids), title,
                     datetime.now() + timedelta(days=random.randint(1, 14)))
                )
            except Exception as e:
                pass
    
    print("Deadlines seeded")


def seed_all():
    """Run all seed functions"""
    print("=" * 50)
    print("Starting database seeding...")
    print("=" * 50)
    
    db = get_db()
    
    try:
        # Core data - order matters for foreign keys
        desc_ids = seed_descriptions(db)
        user_ids = seed_users(db, desc_ids)
        
        if not user_ids:
            print("ERROR: No users created/found. Aborting.")
            return
        
        seed_jobs(db, user_ids)
        seed_payment(db, user_ids)
        seed_posts(db, user_ids)
        seed_network_and_connections(db, user_ids)
        
        # LMS data
        course_ids = seed_courses(db)
        domain_ids = seed_domains(db)
        
        seed_lms_dashboard(db, user_ids)
        seed_user_courses(db, user_ids, course_ids)
        seed_weekly_performance(db, user_ids)
        seed_domain_performance(db, user_ids, domain_ids)
        seed_activities(db, user_ids, course_ids)
        seed_deadlines(db, user_ids, course_ids)
        
        print("=" * 50)
        print("Database seeding completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed database with sample data')
    parser.add_argument('--all', action='store_true', help='Seed all tables')
    parser.add_argument('--users', action='store_true', help='Seed users only')
    parser.add_argument('--courses', action='store_true', help='Seed courses only')
    parser.add_argument('--domains', action='store_true', help='Seed domains only')
    
    args = parser.parse_args()
    
    if args.all or not any([args.users, args.courses, args.domains]):
        seed_all()
    else:
        db = get_db()
        if args.users:
            desc_ids = seed_descriptions(db)
            seed_users(db, desc_ids)
        if args.courses:
            seed_courses(db)
        if args.domains:
            seed_domains(db)
        db.close()
