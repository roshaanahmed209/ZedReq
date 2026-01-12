"""
Generate Sample Data for ZedRec Database
A comprehensive sample data generator for testing and development
"""

import os
import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# SAMPLE DATA CONSTANTS
# ============================================================================

FIRST_NAMES = [
    "John", "Jane", "Michael", "Emily", "David", "Sarah", "James", "Emma",
    "Robert", "Olivia", "William", "Ava", "Joseph", "Isabella", "Charles",
    "Sophia", "Thomas", "Mia", "Daniel", "Charlotte", "Matthew", "Amelia",
    "Anthony", "Harper", "Mark", "Evelyn", "Donald", "Abigail", "Steven",
    "Luna", "Paul", "Ella", "Andrew", "Chloe", "Joshua", "Penelope"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King"
]

JOB_TITLES = [
    "Software Engineer", "Senior Developer", "Data Scientist", "DevOps Engineer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "UI/UX Designer", "Product Manager", "QA Engineer", "Security Engineer",
    "Mobile Developer", "Cloud Architect", "ML Engineer", "Tech Lead",
    "Engineering Manager", "Solutions Architect", "Site Reliability Engineer"
]

JOB_DESCRIPTIONS = [
    "Building scalable web applications using modern frameworks and best practices",
    "Developing and maintaining microservices architecture",
    "Creating machine learning models for predictive analytics",
    "Managing CI/CD pipelines and cloud infrastructure",
    "Designing responsive user interfaces with React and Vue",
    "Building RESTful APIs and GraphQL endpoints",
    "Conducting code reviews and mentoring junior developers",
    "Implementing security best practices and vulnerability assessments",
    "Developing cross-platform mobile applications",
    "Optimizing database performance and query efficiency"
]

SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Vue.js", "Node.js",
    "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS",
    "Azure", "GCP", "GraphQL", "REST API", "Git", "CI/CD", "Agile",
    "TensorFlow", "PyTorch", "SQL", "NoSQL", "Linux", "Terraform"
]

CURRENT_STATUSES = [
    "Available for work", "Open to opportunities", "Currently employed",
    "Freelancing", "Looking for remote work", "Open to hybrid roles",
    "Consulting", "Not actively looking"
]

POST_CONTENTS = [
    "Just finished a great tutorial on React hooks! The useEffect hook is incredibly powerful.",
    "Anyone else excited about the new TypeScript 5.0 features? The improvements are amazing!",
    "Pro tip: Always use meaningful variable names. Your future self will thank you!",
    "Started learning GraphQL today. The query language is so intuitive compared to REST.",
    "Docker has completely changed the way I deploy applications. No more 'it works on my machine'!",
    "Just got AWS certified! Hard work pays off. Never stop learning!",
    "Code review tip: Focus on the logic and architecture, not just the syntax.",
    "Python's list comprehensions are a game changer for data processing. Clean and efficient!",
    "Remember to take breaks while coding. Your brain needs rest too!",
    "Just deployed my first Kubernetes cluster. Feeling accomplished!",
    "Hot take: TypeScript should be the default for all new JavaScript projects.",
    "Contributing to open source has been the best decision for my career growth.",
    "Just finished refactoring a 5000-line file into proper modules. What a journey!",
    "Testing is not optional. It's an investment in your future self.",
    "The best code is the code you didn't have to write. Keep it simple!"
]

COURSE_DATA = [
    {
        "title": "Introduction to React",
        "description": "Learn the fundamentals of React and build modern web applications with components, state, and hooks",
        "icon": "RC",
        "lessons": 24,
        "duration": "6h 30m",
        "category": "Frontend",
        "difficulty": "beginner"
    },
    {
        "title": "Advanced JavaScript Patterns",
        "description": "Master advanced JavaScript concepts including closures, prototypes, async patterns, and ES6+ features",
        "icon": "JS",
        "lessons": 32,
        "duration": "8h 15m",
        "category": "Frontend",
        "difficulty": "intermediate"
    },
    {
        "title": "Node.js Backend Development",
        "description": "Build scalable backend applications with Node.js, Express, and modern API design patterns",
        "icon": "ND",
        "lessons": 28,
        "duration": "7h 45m",
        "category": "Backend",
        "difficulty": "intermediate"
    },
    {
        "title": "Database Design Fundamentals",
        "description": "Learn SQL, NoSQL databases, normalization, indexing, and query optimization techniques",
        "icon": "DB",
        "lessons": 20,
        "duration": "5h 20m",
        "category": "Database",
        "difficulty": "beginner"
    },
    {
        "title": "UI/UX Design Principles",
        "description": "Create beautiful and user-friendly interfaces using design thinking and modern UX methodologies",
        "icon": "UI",
        "lessons": 18,
        "duration": "4h 30m",
        "category": "Design",
        "difficulty": "beginner"
    },
    {
        "title": "Python for Data Science",
        "description": "Data analysis and visualization with pandas, numpy, matplotlib, and scikit-learn",
        "icon": "PY",
        "lessons": 30,
        "duration": "9h 00m",
        "category": "Data Science",
        "difficulty": "intermediate"
    },
    {
        "title": "TypeScript Essentials",
        "description": "Learn TypeScript and build type-safe applications with interfaces, generics, and decorators",
        "icon": "TS",
        "lessons": 26,
        "duration": "7h 00m",
        "category": "Frontend",
        "difficulty": "beginner"
    },
    {
        "title": "Docker & Containerization",
        "description": "Master containerization, Docker Compose, and deployment strategies for modern applications",
        "icon": "DK",
        "lessons": 22,
        "duration": "6h 15m",
        "category": "DevOps",
        "difficulty": "intermediate"
    },
    {
        "title": "GraphQL API Development",
        "description": "Build modern, efficient APIs with GraphQL, Apollo Server, and best practices",
        "icon": "GQ",
        "lessons": 25,
        "duration": "6h 45m",
        "category": "Backend",
        "difficulty": "advanced"
    },
    {
        "title": "AWS Cloud Services",
        "description": "Deploy and manage applications on Amazon Web Services including EC2, S3, Lambda, and more",
        "icon": "AWS",
        "lessons": 35,
        "duration": "10h 30m",
        "category": "Cloud",
        "difficulty": "advanced"
    },
    {
        "title": "Machine Learning Fundamentals",
        "description": "Introduction to ML algorithms, model training, evaluation, and deployment with Python",
        "icon": "ML",
        "lessons": 40,
        "duration": "12h 00m",
        "category": "Data Science",
        "difficulty": "advanced"
    },
    {
        "title": "Kubernetes Orchestration",
        "description": "Container orchestration, deployments, services, and scaling with Kubernetes",
        "icon": "K8",
        "lessons": 28,
        "duration": "8h 30m",
        "category": "DevOps",
        "difficulty": "advanced"
    }
]

DOMAIN_DATA = [
    {"name": "React & Frontend", "description": "Frontend development with React ecosystem", "icon": "react"},
    {"name": "JavaScript ES6+", "description": "Modern JavaScript programming", "icon": "javascript"},
    {"name": "Node.js & Backend", "description": "Server-side development", "icon": "nodejs"},
    {"name": "Database & SQL", "description": "Database management and queries", "icon": "database"},
    {"name": "UI/UX Design", "description": "User interface and experience design", "icon": "design"},
    {"name": "Python & Data Science", "description": "Python programming and data analysis", "icon": "python"},
    {"name": "DevOps & Cloud", "description": "Infrastructure and deployment", "icon": "devops"},
    {"name": "TypeScript", "description": "Type-safe JavaScript development", "icon": "typescript"},
    {"name": "Machine Learning", "description": "AI and machine learning concepts", "icon": "ml"}
]

QUESTION_DATA = [
    {"text": "What is the virtual DOM in React?", "type": "text", "points": 2},
    {"text": "Explain the difference between let and const in JavaScript.", "type": "text", "points": 1},
    {"text": "What is closure in JavaScript?", "type": "text", "points": 2},
    {"text": "How does async/await work?", "type": "text", "points": 2},
    {"text": "What is the event loop in Node.js?", "type": "text", "points": 3},
    {"text": "Explain REST API principles.", "type": "text", "points": 2},
    {"text": "What are React hooks?", "type": "text", "points": 1},
    {"text": "Describe the box model in CSS.", "type": "text", "points": 1},
    {"text": "What is containerization?", "type": "text", "points": 2},
    {"text": "Explain SQL joins.", "type": "text", "points": 2}
]


def get_db():
    """Get database connection"""
    from config.database import get_connection_params, Database
    params = get_connection_params()
    return Database(params)


def generate_username(first_name: str, last_name: str) -> str:
    """Generate a unique username"""
    base = f"{first_name.lower()}_{last_name.lower()}"
    return f"{base}{random.randint(10, 99)}"


def generate_email(first_name: str, last_name: str) -> str:
    """Generate a unique email"""
    domains = ["gmail.com", "outlook.com", "yahoo.com", "protonmail.com", "icloud.com"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}"


def random_date(start_days_ago: int, end_days_ago: int = 0) -> datetime:
    """Generate a random date between start_days_ago and end_days_ago"""
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    delta = (end - start).days
    random_days = random.randint(0, max(1, delta))
    return start + timedelta(days=random_days)


# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def generate_descriptions(db, count: int = 20) -> List[int]:
    """Generate description/profile records"""
    print(f"Generating {count} descriptions...")
    desc_ids = []
    
    for _ in range(count):
        skills_list = random.sample(SKILLS, random.randint(4, 8))
        try:
            result = db.execute_returning(
                '''INSERT INTO description (short_desc, about, certificates, skills, current_status)
                   VALUES (%s, %s, %s, %s, %s) RETURNING desc_id''',
                (
                    random.choice(JOB_TITLES),
                    random.choice(JOB_DESCRIPTIONS),
                    f"Certification in {random.choice(SKILLS)}",
                    ", ".join(skills_list),
                    random.choice(CURRENT_STATUSES)
                )
            )
            if result:
                desc_ids.append(result['desc_id'])
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"  Created {len(desc_ids)} descriptions")
    return desc_ids


def generate_users(db, count: int = 20, desc_ids: List[int] = None) -> List[int]:
    """Generate user records"""
    from utils.auth import hash_password
    
    print(f"Generating {count} users...")
    user_ids = []
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = generate_username(first_name, last_name)
        email = generate_email(first_name, last_name)
        full_name = f"{first_name} {last_name}"
        desc_id = desc_ids[i] if desc_ids and i < len(desc_ids) else None
        
        try:
            result = db.execute_returning(
                '''INSERT INTO users (username, name, user_email, password_hash, email_verified, description_id)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (username) DO NOTHING
                   RETURNING uid''',
                (username, full_name, email, hash_password("Password123"), True, desc_id)
            )
            if result:
                user_ids.append(result['uid'])
                print(f"  Created: {username}")
        except Exception as e:
            print(f"  Error creating user: {e}")
    
    print(f"  Created {len(user_ids)} users")
    return user_ids


def generate_jobs(db, user_ids: List[int]) -> List[int]:
    """Generate job records for users"""
    print(f"Generating jobs for {len(user_ids)} users...")
    job_ids = []
    
    for user_id in user_ids:
        try:
            result = db.execute_returning(
                '''INSERT INTO job (uid, job_desc, designation)
                   VALUES (%s, %s, %s) RETURNING job_id''',
                (user_id, random.choice(JOB_DESCRIPTIONS), random.choice(JOB_TITLES))
            )
            if result:
                job_ids.append(result['job_id'])
                db.execute('UPDATE users SET job_id = %s WHERE uid = %s', (result['job_id'], user_id))
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"  Created {len(job_ids)} jobs")
    return job_ids


def generate_payments(db, user_ids: List[int], count: int = None) -> List[int]:
    """Generate payment records for users"""
    count = count or len(user_ids) // 2
    print(f"Generating {count} payment records...")
    pay_ids = []
    
    plans = ['free', 'basic', 'premium', 'enterprise']
    card_brands = ['visa', 'mastercard', 'amex', 'discover']
    
    for user_id in random.sample(user_ids, min(count, len(user_ids))):
        try:
            result = db.execute_returning(
                '''INSERT INTO payment (uid, payment_provider, provider_customer_id, 
                   card_last_four, card_brand, billing_name, subscription_status, subscription_plan)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING pay_id''',
                (
                    user_id, 'stripe', f'cus_mock_{user_id}_{random.randint(1000, 9999)}',
                    str(random.randint(1000, 9999)), random.choice(card_brands),
                    f"User {user_id}", 'active', random.choice(plans)
                )
            )
            if result:
                pay_ids.append(result['pay_id'])
                db.execute('UPDATE users SET pay_id = %s WHERE uid = %s', (result['pay_id'], user_id))
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"  Created {len(pay_ids)} payment records")
    return pay_ids


def generate_posts(db, user_ids: List[int], count: int = 30) -> List[int]:
    """Generate post records"""
    print(f"Generating {count} posts...")
    post_ids = []
    
    for _ in range(count):
        user_id = random.choice(user_ids)
        content = random.choice(POST_CONTENTS)
        likes = random.randint(0, 100)
        comments = random.randint(0, 25)
        
        try:
            result = db.execute_returning(
                '''INSERT INTO post (uid, post_desc, likes, comments)
                   VALUES (%s, %s, %s, %s) RETURNING post_id''',
                (user_id, content, likes, comments)
            )
            if result:
                post_ids.append(result['post_id'])
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"  Created {len(post_ids)} posts")
    return post_ids


def generate_connections(db, user_ids: List[int]):
    """Generate connection and network records"""
    print("Generating networks and connections...")
    
    # Create network for each user
    for user_id in user_ids:
        try:
            db.execute(
                '''INSERT INTO network (uid, num_connections) VALUES (%s, 0)
                   ON CONFLICT DO NOTHING''', (user_id,)
            )
        except:
            pass
    
    # Create random connections
    connection_count = 0
    for user_id in user_ids:
        others = [u for u in user_ids if u != user_id]
        to_follow = random.sample(others, min(random.randint(3, 8), len(others)))
        
        for followed_id in to_follow:
            try:
                db.execute(
                    '''INSERT INTO connections (follower_uid, followed_uid)
                       VALUES (%s, %s) ON CONFLICT DO NOTHING''',
                    (user_id, followed_id)
                )
                db.execute(
                    'UPDATE network SET num_connections = num_connections + 1 WHERE uid = %s',
                    (followed_id,)
                )
                connection_count += 1
            except:
                pass
    
    print(f"  Created {connection_count} connections")


def generate_courses(db) -> List[int]:
    """Generate LMS course records"""
    print("Generating courses...")
    course_ids = []
    
    for course in COURSE_DATA:
        try:
            result = db.execute_returning(
                '''INSERT INTO lms_courses (title, description, icon, lessons, duration, category, difficulty)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                (course["title"], course["description"], course["icon"],
                 course["lessons"], course["duration"], course["category"], course["difficulty"])
            )
            if result:
                course_ids.append(result['id'])
                print(f"  Created course: {course['title']}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"  Created {len(course_ids)} courses")
    return course_ids


def generate_domains(db) -> List[int]:
    """Generate LMS domain records"""
    print("Generating domains...")
    domain_ids = []
    
    for domain in DOMAIN_DATA:
        try:
            result = db.execute_returning(
                '''INSERT INTO lms_domains (name, description, icon)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (name) DO NOTHING
                   RETURNING id''',
                (domain["name"], domain["description"], domain["icon"])
            )
            if result:
                domain_ids.append(result['id'])
        except Exception as e:
            print(f"  Error: {e}")
    
    # Fetch existing if none created
    if not domain_ids:
        existing = db.fetch_all("SELECT id FROM lms_domains LIMIT 20")
        domain_ids = [d['id'] for d in existing]
    
    print(f"  Created/found {len(domain_ids)} domains")
    return domain_ids


def generate_course_sections(db, course_ids: List[int]) -> List[int]:
    """Generate course sections"""
    print("Generating course sections...")
    section_ids = []
    
    section_templates = [
        "Introduction", "Getting Started", "Core Concepts", "Advanced Topics",
        "Best Practices", "Project Setup", "Deep Dive", "Final Project"
    ]
    
    for course_id in course_ids:
        num_sections = random.randint(3, 6)
        for i, title in enumerate(random.sample(section_templates, num_sections)):
            try:
                result = db.execute_returning(
                    '''INSERT INTO lms_course_sections (course_id, title, order_index, total_items)
                       VALUES (%s, %s, %s, %s) RETURNING id''',
                    (course_id, title, i, random.randint(5, 15))
                )
                if result:
                    section_ids.append(result['id'])
            except:
                pass
    
    print(f"  Created {len(section_ids)} course sections")
    return section_ids


def generate_questions(db, course_ids: List[int], section_ids: List[int]) -> List[int]:
    """Generate quiz questions"""
    print("Generating questions...")
    question_ids = []
    
    for course_id in course_ids:
        num_questions = random.randint(5, 15)
        for i in range(num_questions):
            q = random.choice(QUESTION_DATA)
            section_id = random.choice(section_ids) if section_ids else None
            
            try:
                result = db.execute_returning(
                    '''INSERT INTO lms_questions (course_id, section_id, question_text, question_type, points, order_index)
                       VALUES (%s, %s, %s, %s, %s, %s) RETURNING id''',
                    (course_id, section_id, q["text"], q["type"], q["points"], i)
                )
                if result:
                    question_ids.append(result['id'])
            except:
                pass
    
    print(f"  Created {len(question_ids)} questions")
    return question_ids


def generate_lms_dashboards(db, user_ids: List[int]):
    """Generate LMS dashboard data for users"""
    print("Generating LMS dashboards...")
    
    for user_id in user_ids:
        total_q = random.randint(50, 500)
        correct = int(total_q * random.uniform(0.6, 0.95))
        wrong = total_q - correct
        accuracy = round((correct / total_q) * 100, 2)
        streak = random.randint(1, 45)
        
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
        except:
            pass
    
    print(f"  Created dashboards for {len(user_ids)} users")


def generate_user_courses(db, user_ids: List[int], course_ids: List[int]):
    """Generate user course enrollments"""
    print("Generating user course enrollments...")
    count = 0
    
    for user_id in user_ids:
        num_courses = random.randint(2, min(6, len(course_ids)))
        enrolled = random.sample(course_ids, num_courses)
        
        for course_id in enrolled:
            progress = random.randint(0, 100)
            status = 'completed' if progress == 100 else ('in_progress' if progress > 0 else 'not_started')
            
            try:
                db.execute(
                    '''INSERT INTO lms_user_courses (user_id, course_id, progress, status, started_at, last_accessed_at)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (user_id, course_id) DO NOTHING''',
                    (user_id, course_id, progress, status,
                     random_date(90, 30), random_date(7, 0))
                )
                count += 1
            except:
                pass
    
    print(f"  Created {count} course enrollments")


def generate_weekly_performance(db, user_ids: List[int]):
    """Generate weekly performance data"""
    print("Generating weekly performance...")
    
    for user_id in user_ids:
        for day_offset in range(14):  # Last 2 weeks
            date = datetime.now().date() - timedelta(days=day_offset)
            questions = random.randint(10, 80)
            correct = int(questions * random.uniform(0.5, 0.95))
            
            try:
                db.execute(
                    '''INSERT INTO lms_weekly_performance (user_id, date, questions_answered, correct_answers, wrong_answers, study_time_minutes)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (user_id, date) DO NOTHING''',
                    (user_id, date, questions, correct, questions - correct, random.randint(15, 120))
                )
            except:
                pass
    
    print(f"  Created weekly performance for {len(user_ids)} users")


def generate_domain_performance(db, user_ids: List[int], domain_ids: List[int]):
    """Generate domain performance data"""
    print("Generating domain performance...")
    
    for user_id in user_ids:
        for domain_id in domain_ids:
            questions = random.randint(20, 150)
            correct = int(questions * random.uniform(0.4, 0.98))
            accuracy = round((correct / questions) * 100, 2)
            
            try:
                db.execute(
                    '''INSERT INTO lms_user_domain_performance (user_id, domain_id, questions_answered, correct_answers, accuracy_percentage)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (user_id, domain_id) DO NOTHING''',
                    (user_id, domain_id, questions, correct, accuracy)
                )
            except:
                pass
    
    print(f"  Created domain performance data")


def generate_activities(db, user_ids: List[int], course_ids: List[int]):
    """Generate learning activity logs"""
    print("Generating activities...")
    activity_types = ['completed_lesson', 'passed_quiz', 'started_course', 'earned_badge', 'watched_video']
    activity_titles = [
        "Completed Introduction Module", "Mastered Core Concepts", "Started New Course",
        "Passed Assessment Quiz", "Earned Achievement Badge", "Watched Tutorial Video",
        "Completed Practice Exercise", "Finished Code Challenge"
    ]
    
    count = 0
    for user_id in user_ids:
        num_activities = random.randint(5, 15)
        for _ in range(num_activities):
            try:
                db.execute(
                    '''INSERT INTO lms_activities (user_id, course_id, activity_type, title, icon)
                       VALUES (%s, %s, %s, %s, %s)''',
                    (user_id, random.choice(course_ids), random.choice(activity_types),
                     random.choice(activity_titles), random.choice(['RC', 'JS', 'ND', 'TS', 'PY']))
                )
                count += 1
            except:
                pass
    
    print(f"  Created {count} activities")


def generate_deadlines(db, user_ids: List[int], course_ids: List[int]):
    """Generate upcoming deadlines"""
    print("Generating deadlines...")
    deadline_titles = [
        "Complete Module Assessment", "Submit Project", "Quiz Deadline",
        "Assignment Due", "Final Exam", "Code Review", "Peer Assessment"
    ]
    
    count = 0
    for user_id in user_ids:
        num_deadlines = random.randint(2, 5)
        for _ in range(num_deadlines):
            try:
                db.execute(
                    '''INSERT INTO lms_deadlines (user_id, course_id, title, due_date)
                       VALUES (%s, %s, %s, %s)''',
                    (user_id, random.choice(course_ids), random.choice(deadline_titles),
                     datetime.now() + timedelta(days=random.randint(1, 21)))
                )
                count += 1
            except:
                pass
    
    print(f"  Created {count} deadlines")


def generate_certificates(db, user_ids: List[int], course_ids: List[int]):
    """Generate certificates for completed courses"""
    import uuid
    print("Generating certificates...")
    
    count = 0
    for user_id in user_ids:
        # Give some users certificates
        if random.random() > 0.5:
            num_certs = random.randint(1, 3)
            for course_id in random.sample(course_ids, min(num_certs, len(course_ids))):
                cert_number = f"CERT-{uuid.uuid4().hex[:12].upper()}"
                try:
                    db.execute(
                        '''INSERT INTO lms_certificates (user_id, course_id, certificate_number, title)
                           VALUES (%s, %s, %s, %s)
                           ON CONFLICT (user_id, course_id) DO NOTHING''',
                        (user_id, course_id, cert_number, f"Certificate of Completion")
                    )
                    count += 1
                except:
                    pass
    
    print(f"  Created {count} certificates")


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_all(user_count: int = 20, post_count: int = 30):
    """Generate all sample data"""
    print("=" * 60)
    print("Generating sample data for ZedRec database")
    print("=" * 60)
    
    db = get_db()
    
    try:
        # Core data
        desc_ids = generate_descriptions(db, user_count)
        user_ids = generate_users(db, user_count, desc_ids)
        
        if not user_ids:
            # Try to use existing users
            existing = db.fetch_all("SELECT uid FROM users LIMIT 20")
            user_ids = [u['uid'] for u in existing]
            if not user_ids:
                print("ERROR: No users available. Aborting.")
                return
            print(f"Using {len(user_ids)} existing users")
        
        generate_jobs(db, user_ids)
        generate_payments(db, user_ids)
        generate_posts(db, user_ids, post_count)
        generate_connections(db, user_ids)
        
        # LMS data
        course_ids = generate_courses(db)
        domain_ids = generate_domains(db)
        section_ids = generate_course_sections(db, course_ids)
        question_ids = generate_questions(db, course_ids, section_ids)
        
        generate_lms_dashboards(db, user_ids)
        generate_user_courses(db, user_ids, course_ids)
        generate_weekly_performance(db, user_ids)
        generate_domain_performance(db, user_ids, domain_ids)
        generate_activities(db, user_ids, course_ids)
        generate_deadlines(db, user_ids, course_ids)
        generate_certificates(db, user_ids, course_ids)
        
        print("=" * 60)
        print("Sample data generation completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample data for ZedRec database')
    parser.add_argument('--users', type=int, default=20, help='Number of users to generate')
    parser.add_argument('--posts', type=int, default=30, help='Number of posts to generate')
    parser.add_argument('--all', action='store_true', help='Generate all data (default)')
    
    args = parser.parse_args()
    
    generate_all(user_count=args.users, post_count=args.posts)
