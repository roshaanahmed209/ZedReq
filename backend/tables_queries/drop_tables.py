"""
Drop All Tables for ZedRec Database
Generates SQL for dropping all tables in the correct order (child tables first)
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# TABLE DROP SQL - Ordered by dependencies (child tables first)
# ============================================================================

# Tables must be dropped in REVERSE dependency order
TABLES_DROP_ORDER = [
    # Level 5: Depends on lms_questions (drop first)
    "lms_user_answers",
    
    # Level 4: Depends on lms_course_sections
    "lms_questions",
    "lms_user_section_progress",
    
    # Level 3: Depends on users and lms_domains
    "lms_user_domain_performance",
    "lms_weekly_performance",
    
    # Level 2: Depends on users and lms_courses
    "lms_user_courses",
    "lms_activities",
    "lms_deadlines",
    "lms_certificates",
    "lms_recommendations",
    "lms_course_sections",
    "lms_course_resources",
    
    # Level 1: Depends on users
    "post",
    "job",
    "connections",
    "network",
    "payment",
    "lms_dashboard",
    
    # Level 0: No dependencies (drop last)
    "users",
    "description",
    "lms_courses",
    "lms_domains",
]

# All indexes (will be automatically dropped with tables, but listed for reference)
INDEXES = [
    "idx_users_email",
    "idx_users_name",
    "idx_users_username",
    "idx_post_uid",
    "idx_post_created",
    "idx_job_uid",
    "idx_connections_follower",
    "idx_connections_followed",
    "idx_network_uid",
    "idx_payment_uid",
    "idx_payment_provider_customer",
    "idx_payment_status",
    "idx_lms_dashboard_user",
    "idx_lms_user_courses_user",
    "idx_lms_user_courses_course",
    "idx_lms_user_courses_status",
    "idx_lms_domain_perf_user",
    "idx_lms_weekly_perf_user_date",
    "idx_lms_activities_user",
    "idx_lms_activities_created",
    "idx_lms_deadlines_user_due",
    "idx_lms_certificates_user",
    "idx_lms_recommendations_user",
    "idx_lms_questions_course",
    "idx_lms_user_answers_user",
    "idx_lms_user_answers_question",
]


def get_db():
    """Get database connection"""
    from config.database import get_connection_params, Database
    params = get_connection_params()
    return Database(params)


def drop_all_tables(db=None, cascade: bool = True, confirm: bool = True):
    """
    Drop all tables from the database
    
    Args:
        db: Database connection (optional)
        cascade: Use CASCADE to force drop with dependencies
        confirm: Require user confirmation before dropping
    """
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    if confirm:
        print("=" * 60)
        print("WARNING: This will DROP ALL TABLES!")
        print("=" * 60)
        print("\nThe following tables will be deleted:")
        for table in TABLES_DROP_ORDER:
            print(f"  - {table}")
        print("\nALL DATA WILL BE PERMANENTLY LOST!")
        
        response = input("\nType 'DROP ALL' to confirm: ")
        if response != "DROP ALL":
            print("Operation cancelled.")
            if close_db:
                db.close()
            return False
    
    print("\n" + "=" * 60)
    print("Dropping all tables...")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    cascade_sql = " CASCADE" if cascade else ""
    
    for table_name in TABLES_DROP_ORDER:
        try:
            db.execute(f"DROP TABLE IF EXISTS {table_name}{cascade_sql}")
            print(f"  [OK] Dropped table: {table_name}")
            success_count += 1
        except Exception as e:
            print(f"  [ERROR] Error dropping {table_name}: {e}")
            error_count += 1
    
    print("=" * 60)
    print(f"Table drop complete: {success_count} succeeded, {error_count} failed")
    print("=" * 60)
    
    if close_db:
        db.close()
    
    return error_count == 0


def drop_indexes(db=None):
    """Drop all indexes (usually not needed as they drop with tables)"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("Dropping indexes...")
    
    for index_name in INDEXES:
        try:
            db.execute(f"DROP INDEX IF EXISTS {index_name}")
            print(f"  [OK] Dropped index: {index_name}")
        except Exception as e:
            print(f"  [ERROR] Error dropping {index_name}: {e}")
    
    if close_db:
        db.close()


def truncate_all_tables(db=None, cascade: bool = True, confirm: bool = True):
    """
    Truncate all tables (keep structure, remove data)
    
    Args:
        db: Database connection (optional)
        cascade: Use CASCADE to truncate with dependencies
        confirm: Require user confirmation before truncating
    """
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    if confirm:
        print("=" * 60)
        print("WARNING: This will TRUNCATE ALL TABLES!")
        print("=" * 60)
        print("\nAll data in the following tables will be deleted:")
        for table in TABLES_DROP_ORDER:
            print(f"  - {table}")
        print("\nALL DATA WILL BE PERMANENTLY LOST!")
        print("(Table structures will be preserved)")
        
        response = input("\nType 'TRUNCATE ALL' to confirm: ")
        if response != "TRUNCATE ALL":
            print("Operation cancelled.")
            if close_db:
                db.close()
            return False
    
    print("\n" + "=" * 60)
    print("Truncating all tables...")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    cascade_sql = " CASCADE" if cascade else ""
    
    for table_name in TABLES_DROP_ORDER:
        try:
            db.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY{cascade_sql}")
            print(f"  [OK] Truncated table: {table_name}")
            success_count += 1
        except Exception as e:
            print(f"  [ERROR] Error truncating {table_name}: {e}")
            error_count += 1
    
    print("=" * 60)
    print(f"Table truncation complete: {success_count} succeeded, {error_count} failed")
    print("=" * 60)
    
    if close_db:
        db.close()
    
    return error_count == 0


def get_drop_sql(cascade: bool = True):
    """Get all DROP TABLE SQL as a single string"""
    cascade_sql = " CASCADE" if cascade else ""
    sql_parts = [
        "-- ZedRec Database Cleanup",
        "-- Generated table drop script",
        "-- WARNING: This will delete ALL tables and data!\n"
    ]
    
    for table_name in TABLES_DROP_ORDER:
        sql_parts.append(f"DROP TABLE IF EXISTS {table_name}{cascade_sql};")
    
    return "\n".join(sql_parts)


def get_truncate_sql(cascade: bool = True):
    """Get all TRUNCATE TABLE SQL as a single string"""
    cascade_sql = " CASCADE" if cascade else ""
    sql_parts = [
        "-- ZedRec Database Data Cleanup",
        "-- Generated table truncation script",
        "-- WARNING: This will delete ALL data but keep table structures!\n"
    ]
    
    for table_name in TABLES_DROP_ORDER:
        sql_parts.append(f"TRUNCATE TABLE {table_name} RESTART IDENTITY{cascade_sql};")
    
    return "\n".join(sql_parts)


def export_sql(filename: str = "drop_tables.sql", truncate: bool = False):
    """Export SQL to a file"""
    sql = get_truncate_sql() if truncate else get_drop_sql()
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w') as f:
        f.write(sql)
    
    print(f"SQL exported to: {filepath}")
    return filepath


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Drop or truncate all database tables')
    parser.add_argument('--drop', action='store_true', help='Drop all tables')
    parser.add_argument('--truncate', action='store_true', help='Truncate all tables (keep structure)')
    parser.add_argument('--export', action='store_true', help='Export SQL to file instead of executing')
    parser.add_argument('--export-truncate', action='store_true', help='Export truncate SQL to file')
    parser.add_argument('--print', action='store_true', dest='print_sql', help='Print SQL to console')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--no-cascade', action='store_true', help='Do not use CASCADE')
    
    args = parser.parse_args()
    
    cascade = not args.no_cascade
    confirm = not args.no_confirm
    
    if args.export:
        export_sql("drop_tables.sql")
    elif args.export_truncate:
        export_sql("truncate_tables.sql", truncate=True)
    elif args.print_sql:
        print(get_drop_sql(cascade))
    elif args.truncate:
        truncate_all_tables(cascade=cascade, confirm=confirm)
    elif args.drop:
        drop_all_tables(cascade=cascade, confirm=confirm)
    else:
        print("Usage: python drop_tables.py [--drop | --truncate | --export | --print]")
        print("\nOptions:")
        print("  --drop         Drop all tables (requires confirmation)")
        print("  --truncate     Truncate all tables (keep structure)")
        print("  --export       Export DROP SQL to file")
        print("  --export-truncate  Export TRUNCATE SQL to file")
        print("  --print        Print DROP SQL to console")
        print("  --no-confirm   Skip confirmation prompt")
        print("  --no-cascade   Do not use CASCADE option")
