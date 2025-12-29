"""
Database Seed Data Generator
Generates sample data for all tables in the ZedRec database
"""

import os
import sys
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_connection_params, Database

# Sample data constants
SAMPLE_USERS = [
    ("john_doe", "john@example.com", "password123", "John Doe", "Software Engineer", "Full-stack developer with 5 years of experience"),
    ("jane_smith", "jane@example.com", "password123", "Jane Smith", "Data Scientist", "ML enthusiast and Python expert"),
    ("bob_wilson", "bob@example.com", "password123", "Bob Wilson", "DevOps Engineer", "Cloud infrastructure specialist"),
    ("alice_johnson", "alice@example.com", "password123", "Alice Johnson", "Frontend Developer", "React and Vue.js developer"),
    ("charlie_brown", "charlie@example.com", "password123", "Charlie Brown", "Backend Developer", "Node.js and Python backend expert"),
    ("diana_ross", "diana@example.com", "password123", "Diana Ross", "UI/UX Designer", "Creating beautiful user experiences"),
    ("edward_chen", "edward@example.com", "password123", "Edward Chen", "Mobile Developer", "iOS and Android specialist"),
    ("fiona_green", "fiona@example.com", "password123", "Fiona Green", "Product Manager", "Turning ideas into products"),
    ("george_kim", "george@example.com", "password123", "George Kim", "Security Engineer", "Cybersecurity and penetration testing"),
    ("hannah_lee", "hannah@example.com", "password123", "Hannah Lee", "QA Engineer", "Quality assurance and test automation"),
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


def seed_users(db: Database) -> list:
    """Seed users table and return list of created user IDs (UUIDs)"""
    print("Seeding users...")
    user_ids = []
    
    for username, email, password, full_name, headline, bio in SAMPLE_USERS:
        try:
            result = db.execute_returning(
                '''INSERT INTO users (username, email, password, full_name, headline, bio)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (username) DO NOTHING
                   RETURNING id''',
                (username, email, generate_password_hash(password), full_name, headline, bio)
            )
            if result:
                user_ids.append(str(result['id']))
                print(f"  Created user: {username} ({result['id']})")
        except Exception as e:
            print(f"  Error creating user {username}: {e}")
    
    # If no new users created, fetch existing ones
    if not user_ids:
        existing = db.fetch_all("SELECT id FROM users LIMIT 10")
        user_ids = [str(u['id']) for u in existing]
        print(f"  Using {len(user_ids)} existing users")
    
    print(f"Total users: {len(user_ids)}")
    return user_ids


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


def seed_posts(db: Database, user_ids: list) -> list:
    """Seed posts table"""
    print("Seeding posts...")
    post_ids = []
    
    for i, content in enumerate(SAMPLE_POSTS):
        user_id = random.choice(user_ids)
        try:
            result = db.execute_returning(
                '''INSERT INTO posts (user_id, content)
                   VALUES (%s, %s)
                   RETURNING id''',
                (user_id, content)
            )
            if result:
                post_ids.append(result['id'])
                print(f"  Created post #{result['id']}")
        except Exception as e:
            print(f"  Error creating post: {e}")
    
    print(f"Total posts: {len(post_ids)}")
    return post_ids


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
            print(f"  Dashboard for user {user_id[:8]}... - {accuracy}% accuracy")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("LMS dashboards seeded")


def seed_user_courses(db: Database, user_ids: list, course_ids: list):
    """Seed user course enrollments"""
    print("Seeding user course enrollments...")
    statuses = ['not_started', 'in_progress', 'completed']
    
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
        # Core data
        user_ids = seed_users(db)
        course_ids = seed_courses(db)
        domain_ids = seed_domains(db)
        
        if not user_ids:
            print("ERROR: No users created/found. Aborting.")
            return
        
        # Posts
        post_ids = seed_posts(db, user_ids)
        
        # LMS data
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
            seed_users(db)
        if args.courses:
            seed_courses(db)
        if args.domains:
            seed_domains(db)
        db.close()

