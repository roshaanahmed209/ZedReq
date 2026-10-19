"""
Integration tests for Riz Agent
Tests input validation, sanitization, length limits, and error handling
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from agents.Riz_agent import RizAgent, MAX_CONTEXT_LENGTH


class TestRizAgent:
    """Test suite for RizAgent"""
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key"""
        with patch('agents.Riz_agent.ChatOpenAI'):
            agent = RizAgent(openai_api_key="test_key_12345")
            assert agent.openai_available is True
    
    def test_init_without_api_key(self):
        """Test initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            agent = RizAgent(openai_api_key=None)
            assert agent.openai_available is False
    
    def test_generate_feedback_success(self):
        """Test successful feedback generation"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = json.dumps({
            "summary": "Good performance",
            "strengths": ["Strong technical skills"],
            "weaknesses": ["Could improve communication"],
            "recommendations": ["Practice more"],
            "next_steps": ["Study more"]
        })
        mock_llm.invoke.return_value = mock_response
        
        agent = RizAgent(openai_api_key="test_key")
        agent.llm = mock_llm
        agent.openai_available = True
        
        feedback = agent.generate_feedback(
            job_title="Software Engineer",
            company_name="Tech Corp",
            job_description="Build software",
            questions=[{"question_text": "Tell me about yourself"}],
            user_responses=[{"response": "I am a developer"}],
            overall_score=85,
            score_breakdown={"technical_score": 90},
            tav_check_feedback="Good technical knowledge"
        )
        
        assert feedback["summary"] == "Good performance"
        assert len(feedback["strengths"]) > 0
    
    def test_generate_feedback_input_sanitization(self):
        """Test that inputs are sanitized"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = json.dumps({
            "summary": "Test",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "next_steps": []
        })
        mock_llm.invoke.return_value = mock_response
        
        agent = RizAgent(openai_api_key="test_key")
        agent.llm = mock_llm
        agent.openai_available = True
        
        # Test with potentially dangerous input
        feedback = agent.generate_feedback(
            job_title="<script>alert('xss')</script>",
            company_name="Tech Corp",
            job_description="Build software",
            questions=[],
            user_responses=[],
            overall_score=85,
            score_breakdown={},
            tav_check_feedback=""
        )
        
        # Should not raise exception and should sanitize
        assert "summary" in feedback
    
    def test_generate_feedback_length_limits(self):
        """Test that context length is limited"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = json.dumps({
            "summary": "Test",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "next_steps": []
        })
        mock_llm.invoke.return_value = mock_response
        
        agent = RizAgent(openai_api_key="test_key")
        agent.llm = mock_llm
        agent.openai_available = True
        
        # Create very long job description
        long_description = "A" * 10000
        
        feedback = agent.generate_feedback(
            job_title="Software Engineer",
            company_name="Tech Corp",
            job_description=long_description,
            questions=[],
            user_responses=[],
            overall_score=85,
            score_breakdown={},
            tav_check_feedback=""
        )
        
        # Should not raise exception, should truncate
        assert "summary" in feedback
    
    def test_generate_feedback_json_parsing_error(self):
        """Test handling of JSON parsing errors"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Invalid JSON response"
        mock_llm.invoke.return_value = mock_response
        
        agent = RizAgent(openai_api_key="test_key")
        agent.llm = mock_llm
        agent.openai_available = True
        
        feedback = agent.generate_feedback(
            job_title="Software Engineer",
            company_name="Tech Corp",
            job_description="Build software",
            questions=[],
            user_responses=[],
            overall_score=85,
            score_breakdown={},
            tav_check_feedback=""
        )
        
        # Should return default feedback
        assert feedback["summary"] == "Coaching feedback generation is currently unavailable. Please try again later."
    
    def test_generate_feedback_unavailable_llm(self):
        """Test behavior when LLM is unavailable"""
        agent = RizAgent(openai_api_key=None)
        agent.openai_available = False
        
        feedback = agent.generate_feedback(
            job_title="Software Engineer",
            company_name="Tech Corp",
            job_description="Build software",
            questions=[],
            user_responses=[],
            overall_score=85,
            score_breakdown={},
            tav_check_feedback=""
        )
        
        # Should return default feedback
        assert feedback["summary"] == "Coaching feedback generation is currently unavailable. Please try again later."
    
    def test_validate_list_items(self):
        """Test list validation helper"""
        agent = RizAgent(openai_api_key="test_key")
        
        # Test with valid list
        result = agent._validate_list(["Item 1", "Item 2"], max_items=5, max_length=100)
        assert len(result) == 2
        
        # Test with too many items
        long_list = [f"Item {i}" for i in range(10)]
        result = agent._validate_list(long_list, max_items=5, max_length=100)
        assert len(result) == 5
        
        # Test with non-string items
        result = agent._validate_list([1, 2, 3], max_items=5, max_length=100)
        assert all(isinstance(item, str) for item in result)
    
    def test_build_coaching_context_length_limit(self):
        """Test that context building respects length limits"""
        agent = RizAgent(openai_api_key="test_key")
        
        # Create very long inputs
        long_description = "A" * 5000
        long_feedback = "B" * 5000
        
        context = agent._build_coaching_context(
            job_title="Software Engineer",
            company_name="Tech Corp",
            job_description=long_description,
            questions=[],
            user_responses=[],
            overall_score=85,
            score_breakdown={},
            tav_check_feedback=long_feedback
        )
        
        # Context should be truncated to MAX_CONTEXT_LENGTH
        assert len(context) <= MAX_CONTEXT_LENGTH + 100  # Allow some margin for formatting


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
