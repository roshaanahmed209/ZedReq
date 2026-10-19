"""
One-time backfill: Ensure sections exist, assign orphan questions, then populate
lms_user_section_progress evaluation columns from existing evaluated answers.

This script:
1. Creates default level sections (Basic/Intermediate/Expert) for every course
   that doesn't have them yet.
2. Assigns orphan questions (section_id IS NULL) to the first section of their
   course (typically "Basic").
3. Aggregates all evaluated answers by (user_id, section_id) and upserts the
   totals into lms_user_section_progress.

Usage:
    python backend/db/migrations/backfill_section_performance.py

Safe to re-run — all operations are idempotent.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database_orm import SessionLocal
from models.orm import LMSCourse, LMSCourseSection, LMSQuestion
from services.lms_service import LMSService


def run_backfill():
    print("=" * 60)
    print("Backfill: Section Performance from existing evaluated answers")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = LMSService(db)

        # --- Step 1: Ensure every course has default level sections ---
        courses = db.query(LMSCourse).all()
        print(f"\n[Step 1] Found {len(courses)} course(s). Ensuring default sections...")
        for course in courses:
            created = service.ensure_default_level_sections(course.id)
            section_titles = [s.title for s in created]
            print(f"  Course #{course.id} ({course.title}): sections = {section_titles}")

        # --- Step 2: Backfill orphan questions ---
        orphan_count = db.query(LMSQuestion).filter(LMSQuestion.section_id.is_(None)).count()
        print(f"\n[Step 2] Orphan questions (NULL section_id): {orphan_count}")
        if orphan_count > 0:
            for course in courses:
                service.backfill_orphan_questions(course.id)
            remaining = db.query(LMSQuestion).filter(LMSQuestion.section_id.is_(None)).count()
            print(f"  After backfill: {remaining} orphan(s) remaining")
        else:
            print("  No orphan questions — skipping.")

        # --- Step 3: Aggregate evaluated answers into section performance ---
        print(f"\n[Step 3] Aggregating evaluated answers into section performance...")

        # Use raw SQL for the efficient upsert
        from sqlalchemy import text
        result = db.execute(text("""
            WITH section_stats AS (
                SELECT
                    a.user_id,
                    q.section_id,
                    COUNT(*)                                                     AS questions_answered,
                    COALESCE(SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END), 0)  AS correct_answers,
                    ROUND(
                        COALESCE(SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END), 0)::numeric
                        / NULLIF(COUNT(*), 0) * 100,
                        2
                    )                                                            AS accuracy_percentage,
                    COALESCE(SUM(a.points_earned), 0)                            AS total_points_earned
                FROM lms_user_answers a
                JOIN lms_questions q ON q.id = a.question_id
                WHERE a.is_correct IS NOT NULL
                  AND q.section_id IS NOT NULL
                GROUP BY a.user_id, q.section_id
            )
            INSERT INTO lms_user_section_progress
                (user_id, section_id, questions_answered, correct_answers, accuracy_percentage, total_points_earned)
            SELECT
                user_id, section_id, questions_answered, correct_answers, accuracy_percentage, total_points_earned
            FROM section_stats
            ON CONFLICT (user_id, section_id)
            DO UPDATE SET
                questions_answered   = EXCLUDED.questions_answered,
                correct_answers      = EXCLUDED.correct_answers,
                accuracy_percentage  = EXCLUDED.accuracy_percentage,
                total_points_earned  = EXCLUDED.total_points_earned,
                updated_at           = NOW()
        """))
        db.commit()

        # Report results
        from models.orm import LMSUserSectionProgress
        rows = (
            db.query(LMSUserSectionProgress, LMSCourseSection)
            .join(LMSCourseSection, LMSCourseSection.id == LMSUserSectionProgress.section_id)
            .filter(LMSUserSectionProgress.questions_answered > 0)
            .order_by(LMSUserSectionProgress.user_id, LMSCourseSection.order_index)
            .all()
        )

        if rows:
            print(f"\n  Populated {len(rows)} section performance row(s):\n")
            print(f"  {'User':>6}  {'Section':<16} {'Answered':>8}  {'Correct':>7}  {'Accuracy':>8}  {'Points':>6}")
            print(f"  {'-' * 6}  {'-' * 16} {'-' * 8}  {'-' * 7}  {'-' * 8}  {'-' * 6}")
            for progress, section in rows:
                print(
                    f"  {progress.user_id:>6}  {section.title:<16} "
                    f"{progress.questions_answered:>8}  {progress.correct_answers:>7}  "
                    f"{float(progress.accuracy_percentage):>7.1f}%  {progress.total_points_earned:>6}"
                )
        else:
            print("\n  No evaluated answers found — nothing to populate.")

        print("\n" + "=" * 60)
        print("Backfill completed successfully!")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\nBackfill FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_backfill()
