"""
Integration tests for Tavus Service
Tests API key validation, input sanitization, error handling, and retry logic
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
from services.tavus_service import TavusService
from utils.api_security import validate_api_key
from config.settings import parse_tavus_replica_ids_value


class TestParseTavusReplicaIds:
    """Bracket / CSV env values for TAVUS_REPLICA_ID and TAVUS_REPLICA_IDS"""

    def test_bracket_list_with_spaces(self):
        raw = "[rf4703150052, r92debe21318, r9fa0878977a, r6ae5b6efc9d]"
        assert parse_tavus_replica_ids_value(raw) == [
            "rf4703150052",
            "r92debe21318",
            "r9fa0878977a",
            "r6ae5b6efc9d",
        ]

    def test_comma_separated(self):
        assert parse_tavus_replica_ids_value("a,b, c") == ["a", "b", "c"]

    def test_single_id(self):
        assert parse_tavus_replica_ids_value("rf4703150052") == ["rf4703150052"]


class TestTavusService:
    """Test suite for TavusService"""
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key"""
        service = TavusService(api_key="test_key_12345", api_url="https://tavusapi.com/v2")
        assert service.available is True
        assert service.api_key == "test_key_12345"
        assert "x-api-key" in service.headers
    
    def test_init_without_api_key(self):
        """Test initialization without API key"""
        service = TavusService(api_key=None, api_url="https://tavusapi.com/v2")
        assert service.available is False
        assert service.api_key is None
    
    def test_init_with_invalid_api_key(self):
        """Test initialization with invalid API key"""
        service = TavusService(api_key="", api_url="https://tavusapi.com/v2")
        assert service.available is False
    
    def test_create_conversation_success(self):
        """Test successful conversation creation"""
        service = TavusService(api_key="test_key_12345", api_url="https://tavusapi.com/v2")
        
        mock_response = Mock()
        mock_response.json.return_value = {"conversation_id": "conv_123"}
        mock_response.raise_for_status = Mock()
        
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.post.return_value = mock_response
            
            result = service.create_conversation(
                replica_id="replica_123",
                persona_id="pcb7a34da5fe",
                conversation_name="Test Interview",
                system_prompt="You are an interviewer",
                first_message="Hello"
            )
            
            assert result["conversation_id"] == "conv_123"
    
    def test_create_conversation_input_sanitization(self):
        """Test that inputs are sanitized"""
        service = TavusService(api_key="test_key_12345", api_url="https://tavusapi.com/v2")
        
        mock_response = Mock()
        mock_response.json.return_value = {"conversation_id": "conv_123"}
        mock_response.raise_for_status = Mock()
        
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.post.return_value = mock_response
            
            # Test with potentially dangerous input
            result = service.create_conversation(
                replica_id="replica_123",
                persona_id="pcb7a34da5fe",
                conversation_name="Test<script>alert('xss')</script>",
                system_prompt="You are an interviewer",
                first_message="Hello"
            )
            
            # Should not raise exception and should sanitize
            assert result["conversation_id"] == "conv_123"
    
    def test_create_conversation_retry_on_server_error(self):
        """Test retry logic on server errors"""
        service = TavusService(
            api_key="test_key_12345",
            api_url="https://tavusapi.com/v2",
            max_retries=2
        )
        
        # First two calls fail with 500, third succeeds
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"conversation_id": "conv_123"}
        mock_response_success.raise_for_status = Mock()
        
        mock_response_error = Mock()
        mock_response_error.status_code = 500
        mock_response_error.text = "Internal Server Error"
        mock_response_error.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response_error
        )
        
        with patch('httpx.Client') as mock_client, patch('time.sleep'):
            mock_post = mock_client.return_value.__enter__.return_value.post
            mock_post.side_effect = [
                httpx.HTTPStatusError("Server Error", request=Mock(), response=mock_response_error),
                httpx.HTTPStatusError("Server Error", request=Mock(), response=mock_response_error),
                mock_response_success
            ]
            
            result = service.create_conversation(
                replica_id="replica_123",
                persona_id="pcb7a34da5fe",
                conversation_name="Test",
                system_prompt="Prompt",
                first_message="Hello"
            )
            
            assert result["conversation_id"] == "conv_123"
            assert mock_post.call_count == 3  # 2 retries + 1 success
    
    def test_create_conversation_no_retry_on_client_error(self):
        """Test that client errors (4xx) are not retried"""
        service = TavusService(api_key="test_key_12345", api_url="https://tavusapi.com/v2")
        
        mock_response_error = Mock()
        mock_response_error.status_code = 400
        mock_response_error.text = "Bad Request"
        mock_response_error.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=Mock(), response=mock_response_error
        )
        
        with patch('httpx.Client') as mock_client:
            mock_post = mock_client.return_value.__enter__.return_value.post
            mock_post.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=Mock(), response=mock_response_error
            )
            
            with pytest.raises(Exception):
                service.create_conversation(
                    replica_id="replica_123",
                    persona_id="pcb7a34da5fe",
                    conversation_name="Test",
                    system_prompt="Prompt",
                    first_message="Hello"
                )
            
            # Should only be called once (no retries)
            assert mock_post.call_count == 1
    
    def test_get_conversation_success(self):
        """Test successful conversation retrieval"""
        service = TavusService(api_key="test_key_12345", api_url="https://tavusapi.com/v2")
        
        mock_response = Mock()
        mock_response.json.return_value = {"conversation_id": "conv_123", "status": "active"}
        mock_response.raise_for_status = Mock()
        
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            result = service.get_conversation("conv_123")
            
            assert result["conversation_id"] == "conv_123"
            assert result["status"] == "active"
    
    def test_get_conversation_transcript_success(self):
        """Test successful transcript retrieval"""
        service = TavusService(api_key="test_key_12345", api_url="https://tavusapi.com/v2")
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00Z"}
            ]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            result = service.get_conversation_transcript("conv_123")
            
            assert "messages" in result
    
    def test_get_conversation_transcript_fallback(self):
        """Test transcript retrieval with 404 fallback"""
        service = TavusService(api_key="test_key_12345", api_url="https://tavusapi.com/v2")
        
        # First call returns 404
        mock_response_404 = Mock()
        mock_response_404.status_code = 404
        mock_response_404.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response_404
        )
        
        # Fallback call succeeds
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"conversation_id": "conv_123"}
        mock_response_success.raise_for_status = Mock()
        
        with patch('httpx.Client') as mock_client:
            mock_get = mock_client.return_value.__enter__.return_value.get
            mock_get.side_effect = [
                httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response_404),
                mock_response_success
            ]
            
            result = service.get_conversation_transcript("conv_123")
            
            assert result["conversation_id"] == "conv_123"
            assert mock_get.call_count == 2  # One failed, one fallback


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
