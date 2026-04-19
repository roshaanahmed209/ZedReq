"""
Unit tests for LMS quiz resume (get_quiz_resume_state).

Manual QA checklist (enrolled learner, LMS portal):
1. Open a course, select a section, answer a full page, click Next, close modal, reopen same course:
   expect page 2 (or next) with prior answers prefilled where applicable.
2. Answer all questions in a section, reopen: expect last page and filled answers.
3. Submit the same question twice in DB (duplicate rows): UI should show latest answer text only.
4. Call GET /api/lms/courses/{id}/questions?section_id=X without enrollment: expect 403.
5. Call with include_resume=true but omit section_id: expect 400.
"""
from datetime import datetime
from unittest.mock import MagicMock

from models.orm import LMSQuestion, LMSUserAnswer
from services.lms_service import LMSService


def _svc_with_queries(question_rows, answer_rows):
    svc = LMSService.__new__(LMSService)
    mock_db = MagicMock()

    def query_side(model):
        chain = MagicMock()
        if model is LMSQuestion:
            chain.filter.return_value.order_by.return_value.all.return_value = question_rows
        elif model is LMSUserAnswer:
            chain.filter.return_value.order_by.return_value.all.return_value = answer_rows
        else:
            chain.filter.return_value.order_by.return_value.all.return_value = []
        return chain

    mock_db.query.side_effect = query_side
    svc.db = mock_db
    return svc


def test_resume_empty_section():
    svc = _svc_with_queries([], [])
    out = svc.get_quiz_resume_state(user_id=1, course_id=10, section_id=20)
    assert out["latest_answers"] == {}
    assert out["first_unanswered_index"] is None
    assert out["all_answered"] is True


def test_resume_first_unanswered():
    q1 = MagicMock(spec=LMSQuestion)
    q1.id = 101
    q2 = MagicMock(spec=LMSQuestion)
    q2.id = 102
    a1 = MagicMock(spec=LMSUserAnswer)
    a1.question_id = 101
    a1.answer_text = "first"
    a1.submitted_at = datetime(2025, 1, 1)
    a1.id = 1
    svc = _svc_with_queries([q1, q2], [a1])
    out = svc.get_quiz_resume_state(user_id=5, course_id=10, section_id=20)
    assert out["latest_answers"] == {101: "first"}
    assert out["first_unanswered_index"] == 1
    assert out["all_answered"] is False


def test_resume_all_answered():
    q1 = MagicMock(spec=LMSQuestion)
    q1.id = 1
    q2 = MagicMock(spec=LMSQuestion)
    q2.id = 2
    a1 = MagicMock(spec=LMSUserAnswer)
    a1.question_id = 1
    a1.answer_text = "A"
    a1.submitted_at = datetime(2025, 1, 2)
    a1.id = 10
    a2 = MagicMock(spec=LMSUserAnswer)
    a2.question_id = 2
    a2.answer_text = "B"
    a2.submitted_at = datetime(2025, 1, 1)
    a2.id = 9
    svc = _svc_with_queries([q1, q2], [a1, a2])
    out = svc.get_quiz_resume_state(user_id=1, course_id=1, section_id=1)
    assert out["latest_answers"] == {1: "A", 2: "B"}
    assert out["first_unanswered_index"] is None
    assert out["all_answered"] is True


def test_resume_latest_row_wins_per_question():
    q1 = MagicMock(spec=LMSQuestion)
    q1.id = 50
    older = MagicMock(spec=LMSUserAnswer)
    older.question_id = 50
    older.answer_text = "old"
    older.submitted_at = datetime(2025, 1, 1)
    older.id = 1
    newer = MagicMock(spec=LMSUserAnswer)
    newer.question_id = 50
    newer.answer_text = "new"
    newer.submitted_at = datetime(2025, 2, 1)
    newer.id = 2
    # Service orders by submitted_at desc, id desc — first row wins in loop
    svc = _svc_with_queries([q1], [newer, older])
    out = svc.get_quiz_resume_state(user_id=1, course_id=1, section_id=1)
    assert out["latest_answers"] == {50: "new"}
    assert out["first_unanswered_index"] is None
    assert out["all_answered"] is True


def test_resume_whitespace_not_counted_answered():
    q1 = MagicMock(spec=LMSQuestion)
    q1.id = 7
    a1 = MagicMock(spec=LMSUserAnswer)
    a1.question_id = 7
    a1.answer_text = "   "
    a1.submitted_at = datetime(2025, 1, 1)
    a1.id = 1
    svc = _svc_with_queries([q1], [a1])
    out = svc.get_quiz_resume_state(user_id=1, course_id=1, section_id=1)
    assert out["latest_answers"] == {}
    assert out["first_unanswered_index"] == 0
    assert out["all_answered"] is False
