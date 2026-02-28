"""
Security tests for Interview Service
Tests input validation, authorization, error handling, and security logging
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from services.interview_service import (
    InterviewService,
    InterviewNotFoundError,
    InterviewStateError,
    JobNotFoundError,
    JobNotActiveError,
    TavusServiceError
)
from models.orm.live_interview import LiveInterview
from models.orm.job_posting import JobPosting


class TestInterviewServiceSecurity:
    """Test suite for InterviewService security features"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def interview_service(self, mock_db):
        """Create InterviewService instance with mocked dependencies"""
        with patch('services.interview_service.TavusService'), \
             patch('services.interview_service.InterviewQuestionService'), \
             patch('services.interview_service.TavCheckAgent'):
            service = InterviewService(mock_db)
            return service
    
    def test_start_interview_invalid_user_id(self, interview_service):
        """Test that invalid user_id is rejected"""
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            interview_service.start_interview(user_id=0, job_id=1)
        
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            interview_service.start_interview(user_id=-1, job_id=1)
    
    def test_start_interview_invalid_job_id(self, interview_service):
        """Test that invalid job_id is rejected"""
        with pytest.raises(ValueError, match="job_id must be a positive integer"):
            interview_service.start_interview(user_id=1, job_id=0)
        
        with pytest.raises(ValueError, match="job_id must be a positive integer"):
            interview_service.start_interview(user_id=1, job_id=-1)
    
    def test_start_interview_job_not_found(self, interview_service, mock_db):
        """Test that non-existent job raises JobNotFoundError"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(JobNotFoundError):
            interview_service.start_interview(user_id=1, job_id=999)
    
    def test_start_interview_job_not_active(self, interview_service, mock_db):
        """Test that inactive job raises JobNotActiveError"""
        mock_job = Mock(spec=JobPosting)
        mock_job.job_id = 1
        mock_job.status = "inactive"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_job
        
        with pytest.raises(JobNotActiveError):
            interview_service.start_interview(user_id=1, job_id=1)
    
    def test_complete_interview_invalid_id(self, interview_service):
        """Test that invalid interview_id is rejected"""
        with pytest.raises(ValueError, match="interview_id must be a positive integer"):
            interview_service.complete_interview(interview_id=0)
        
        with pytest.raises(ValueError, match="interview_id must be a positive integer"):
            interview_service.complete_interview(interview_id=-1)
    
    def test_complete_interview_not_found(self, interview_service, mock_db):
        """Test that non-existent interview raises InterviewNotFoundError"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(InterviewNotFoundError):
            interview_service.complete_interview(interview_id=999)
    
    def test_complete_interview_invalid_state(self, interview_service, mock_db):
        """Test that invalid interview state raises InterviewStateError"""
        mock_interview = Mock(spec=LiveInterview)
        mock_interview.interview_id = 1
        mock_interview.status = "cancelled"
        mock_interview.tavus_conversation_id = "conv_123"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_interview
        
        with pytest.raises(InterviewStateError):
            interview_service.complete_interview(interview_id=1)
    
    def test_extract_user_responses_empty_transcript(self, interview_service):
        """Test handling of empty transcript"""
        responses = interview_service._extract_user_responses({})
        assert responses == []
        
        responses = interview_service._extract_user_responses(None)
        assert responses == []
    
    def test_extract_user_responses_multiple_formats(self, interview_service):
        """Test extraction with different transcript formats"""
        # Format 1: messages array
        transcript1 = {
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00Z"}
            ]
        }
        responses = interview_service._extract_user_responses(transcript1)
        assert len(responses) == 1
        assert responses[0]["response"] == "Hello"
        
        # Format 2: transcript array
        transcript2 = {
            "transcript": [
                {"role": "candidate", "text": "Hi there"}
            ]
        }
        responses = interview_service._extract_user_responses(transcript2)
        assert len(responses) == 1
        
        # Format 3: responses array
        transcript3 = {
            "responses": [
                {"text": "Response 1"}
            ]
        }
        responses = interview_service._extract_user_responses(transcript3)
        assert len(responses) == 1
    
    def test_extract_user_responses_sanitization(self, interview_service):
        """Test that responses are sanitized"""
        transcript = {
            "messages": [
                {
                    "role": "user",
                    "content": "<script>alert('xss')</script>Hello",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }
        responses = interview_service._extract_user_responses(transcript)
        assert len(responses) == 1
        # Script tags should be removed
        assert "<script>" not in responses[0]["response"]
    
    def test_get_interview_user_verification(self, interview_service, mock_db):
        """Test that user_id verification works"""
        mock_interview = Mock(spec=LiveInterview)
        mock_interview.interview_id = 1
        mock_interview.user_id = 1
        mock_interview.job_id = 1
        mock_interview.to_dict.return_value = {"interview_id": 1}
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_interview
        mock_db.query.return_value = mock_query
        
        # Should return interview for correct user
        result = interview_service.get_interview(interview_id=1, user_id=1)
        assert result is not None
        
        # Should return None for wrong user
        mock_query.filter.return_value.first.return_value = None
        result = interview_service.get_interview(interview_id=1, user_id=2)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
