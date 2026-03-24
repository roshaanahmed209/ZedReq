"""
Tavus Service
Handles integration with Tavus AI API for video interviews
"""
import os
import logging
import time
from typing import Dict, Any, Optional
import httpx

from config.settings import settings
from utils.api_security import (
    validate_api_key,
    mask_api_key,
    safe_log_api_call,
    sanitize_input,
    validate_url_safe,
    sanitize_dict_for_logging
)

logger = logging.getLogger(__name__)


class TavusService:
    """Service for interacting with Tavus AI API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize Tavus service
        
        Args:
            api_key: Tavus API key (default: from settings)
            api_url: Tavus API URL (default: from settings)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.api_key = api_key or settings.TAVUS_API_KEY
        self.api_url = api_url or settings.TAVUS_API_URL
        self.timeout = max(5.0, min(300.0, timeout))  # Between 5s and 5min
        self.max_retries = max(0, min(5, max_retries))  # Between 0 and 5
        
        # Validate API key
        if not self.api_key or not validate_api_key(self.api_key, "TAVUS_API_KEY"):
            logger.warning("Tavus API key not found or invalid. Tavus integration will not work.")
            self.available = False
            self.api_key = None
        else:
            self.available = True
            # Log masked API key for debugging
            masked_key = mask_api_key(self.api_key)
            logger.info(f"Tavus service initialized with API key: {masked_key}")
        
        # Validate and sanitize API URL
        if self.api_url:
            try:
                self.api_url = validate_url_safe(self.api_url, allowed_schemes=['https'])
                logger.info(f"Tavus API URL validated: {self.api_url}")
            except ValueError as e:
                logger.error(f"Invalid Tavus API URL: {e}")
                self.available = False
                self.api_url = None
        
        # Tavus v2 uses x-api-key (not Bearer). See https://docs.tavus.io/api-reference/authentication
        if self.available and self.api_key:
            self.headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
        else:
            self.headers = {"Content-Type": "application/json"}
    
    def create_conversation(
        self,
        replica_id: str,
        persona_id: str,
        conversation_name: str,
        system_prompt: str,
        first_message: str,
        max_call_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new Tavus conversation (v2 API: POST /v2/conversations).
        
        Args:
            replica_id: Tavus replica ID for the interviewer
            persona_id: Tavus persona ID (required by v2 full-pipeline conversations)
            conversation_name: Name for the conversation
            system_prompt: Interview context (sent as conversational_context)
            first_message: Opening line (sent as custom_greeting)
            max_call_duration: Maximum call duration in seconds (nested under properties)
            
        Returns:
            Dictionary with conversation details including conversation_id
            
        Raises:
            ValueError: If API key not configured or inputs invalid
            Exception: If Tavus API call fails after retries
        """
        if not self.available:
            raise ValueError("Tavus API key not configured")
        
        # Sanitize and validate inputs
        replica_id = sanitize_input(str(replica_id), max_length=255)
        persona_id = sanitize_input(str(persona_id), max_length=255)
        conversation_name = sanitize_input(conversation_name, max_length=255)
        system_prompt = sanitize_input(system_prompt, max_length=10000)  # Reasonable limit for prompts
        first_message = sanitize_input(first_message, max_length=1000)
        
        if not replica_id:
            raise ValueError("replica_id cannot be empty")
        if not persona_id:
            raise ValueError("persona_id cannot be empty")
        
        url = f"{self.api_url}/conversations"
        
        # v2 schema: https://docs.tavus.io/api-reference/conversations/create-conversation
        payload: Dict[str, Any] = {
            "replica_id": replica_id,
            "persona_id": persona_id,
            "conversation_name": conversation_name,
        }
        if system_prompt:
            payload["conversational_context"] = system_prompt
        if first_message:
            payload["custom_greeting"] = first_message
        
        properties: Dict[str, Any] = {}
        if max_call_duration is not None and isinstance(max_call_duration, int) and max_call_duration > 0:
            properties["max_call_duration"] = max_call_duration
            logger.info(f"Tavus conversation max_call_duration set to {max_call_duration}s")
        # Avoid "meeting does not exist" when users join after Tavus' default 300s no-join window
        pa = settings.TAVUS_PARTICIPANT_ABSENT_TIMEOUT
        if isinstance(pa, int) and pa > 0:
            properties["participant_absent_timeout"] = min(pa, 86400)
            logger.info(
                f"Tavus participant_absent_timeout set to {properties['participant_absent_timeout']}s"
            )
        if properties:
            payload["properties"] = properties
        
        # Log API call (sanitized)
        safe_log_api_call(
            service_name="Tavus",
            endpoint="/conversations",
            method="POST",
            has_api_key=True,
            replica_id=replica_id,
            conversation_name=conversation_name
        )
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        url,
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    result = response.json()
                    conversation_id = result.get('conversation_id')
                    
                    # Log success (sanitized)
                    logger.info(f"Created Tavus conversation: {conversation_id}")
                    return result
                    
            except httpx.HTTPStatusError as e:
                last_exception = e
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    logger.error(
                        f"Tavus API client error (attempt {attempt + 1}/{self.max_retries + 1}): "
                        f"{e.response.status_code} - {e.response.text[:200]}"
                    )
                    raise Exception(f"Tavus API client error: {e.response.status_code}")
                
                # Retry on 5xx errors (server errors)
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5  # Exponential backoff: 0.5s, 1s, 2s
                    logger.warning(
                        f"Tavus API server error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {e.response.status_code}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API server error after {self.max_retries + 1} attempts: {e.response.status_code}")
                    
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API timeout (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API timeout after {self.max_retries + 1} attempts")
                    
            except (httpx.ConnectError, httpx.NetworkError, OSError) as e:
                # Network/DNS errors - more specific handling
                last_exception = e
                error_type = "network"
                if "getaddrinfo" in str(e).lower() or "name resolution" in str(e).lower():
                    error_type = "DNS resolution"
                elif "connection" in str(e).lower():
                    error_type = "connection"
                
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API {error_type} error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {str(e)[:200]}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API {error_type} error after {self.max_retries + 1} attempts: {str(e)[:200]}")
                    
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {str(e)[:200]}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API error after {self.max_retries + 1} attempts: {str(e)[:200]}")
        
        # If we get here, all retries failed
        error_msg = f"Tavus API error after {self.max_retries + 1} attempts"
        if last_exception:
            error_str = str(last_exception)
            # Provide user-friendly error messages for common network issues
            if "getaddrinfo" in error_str.lower() or "name resolution" in error_str.lower():
                error_msg = f"Unable to connect to Tavus API: DNS resolution failed. Please check your internet connection and ensure the API URL ({self.api_url}) is correct."
            elif "connection" in error_str.lower() and "refused" in error_str.lower():
                error_msg = f"Unable to connect to Tavus API: Connection refused. The API server may be down or unreachable."
            elif "timeout" in error_str.lower():
                error_msg = f"Tavus API request timed out after {self.timeout} seconds. The API may be slow or unavailable."
            else:
                error_msg += f": {error_str[:200]}"
        raise Exception(error_msg)
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation details and status
        
        Args:
            conversation_id: Tavus conversation ID
            
        Returns:
            Dictionary with conversation details
            
        Raises:
            ValueError: If API key not configured or conversation_id invalid
            Exception: If Tavus API call fails after retries
        """
        if not self.available:
            raise ValueError("Tavus API key not configured")
        
        # Sanitize and validate conversation_id
        conversation_id = sanitize_input(str(conversation_id), max_length=255)
        if not conversation_id:
            raise ValueError("conversation_id cannot be empty")
        
        url = f"{self.api_url}/conversations/{conversation_id}"
        
        # Log API call
        safe_log_api_call(
            service_name="Tavus",
            endpoint=f"/conversations/{conversation_id}",
            method="GET",
            has_api_key=True
        )
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(url, headers=self.headers)
                    response.raise_for_status()
                    result = response.json()
                    logger.debug(f"Retrieved Tavus conversation: {conversation_id}")
                    return result
                    
            except httpx.HTTPStatusError as e:
                last_exception = e
                # Don't retry on 4xx errors
                if 400 <= e.response.status_code < 500:
                    logger.error(
                        f"Tavus API client error (attempt {attempt + 1}/{self.max_retries + 1}): "
                        f"{e.response.status_code} - {e.response.text[:200]}"
                    )
                    raise Exception(f"Tavus API client error: {e.response.status_code}")
                
                # Retry on 5xx errors
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API server error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {e.response.status_code}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API server error after {self.max_retries + 1} attempts: {e.response.status_code}")
                    
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API timeout (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API timeout after {self.max_retries + 1} attempts")
                    
            except (httpx.ConnectError, httpx.NetworkError, OSError) as e:
                # Network/DNS errors - more specific handling
                last_exception = e
                error_type = "network"
                if "getaddrinfo" in str(e).lower() or "name resolution" in str(e).lower():
                    error_type = "DNS resolution"
                elif "connection" in str(e).lower():
                    error_type = "connection"
                
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API {error_type} error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {str(e)[:200]}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API {error_type} error after {self.max_retries + 1} attempts: {str(e)[:200]}")
                    
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {str(e)[:200]}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API error after {self.max_retries + 1} attempts: {str(e)[:200]}")
        
        # If we get here, all retries failed
        error_msg = f"Tavus API error after {self.max_retries + 1} attempts"
        if last_exception:
            error_str = str(last_exception)
            # Provide user-friendly error messages for common network issues
            if "getaddrinfo" in error_str.lower() or "name resolution" in error_str.lower():
                error_msg = f"Unable to connect to Tavus API: DNS resolution failed. Please check your internet connection and ensure the API URL ({self.api_url}) is correct."
            elif "connection" in error_str.lower() and "refused" in error_str.lower():
                error_msg = f"Unable to connect to Tavus API: Connection refused. The API server may be down or unreachable."
            elif "timeout" in error_str.lower():
                error_msg = f"Tavus API request timed out after {self.timeout} seconds. The API may be slow or unavailable."
            else:
                error_msg += f": {error_str[:200]}"
        raise Exception(error_msg)
    
    def get_conversation_transcript(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get full conversation transcript/responses
        
        Args:
            conversation_id: Tavus conversation ID
            
        Returns:
            Dictionary with conversation transcript and responses
            
        Raises:
            ValueError: If API key not configured or conversation_id invalid
            Exception: If Tavus API call fails after retries
        """
        if not self.available:
            raise ValueError("Tavus API key not configured")
        
        # Sanitize and validate conversation_id
        conversation_id = sanitize_input(str(conversation_id), max_length=255)
        if not conversation_id:
            raise ValueError("conversation_id cannot be empty")
        
        # Try to get transcript from conversation details
        # Tavus API structure may vary - adjust endpoint as needed
        url = f"{self.api_url}/conversations/{conversation_id}/transcript"
        
        # Log API call
        safe_log_api_call(
            service_name="Tavus",
            endpoint=f"/conversations/{conversation_id}/transcript",
            method="GET",
            has_api_key=True
        )
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(url, headers=self.headers)
                    response.raise_for_status()
                    result = response.json()
                    logger.debug(f"Retrieved Tavus transcript: {conversation_id}")
                    return result
                    
            except httpx.HTTPStatusError as e:
                last_exception = e
                if e.response.status_code == 404:
                    # If transcript endpoint doesn't exist, try getting full conversation
                    logger.warning(f"Transcript endpoint not found (404), using conversation details")
                    try:
                        return self.get_conversation(conversation_id)
                    except Exception as fallback_error:
                        logger.error(f"Fallback to get_conversation also failed: {fallback_error}")
                        raise Exception(f"Tavus transcript not available: {e.response.status_code}")
                
                # Don't retry on 4xx errors (except 404 which we handle above)
                if 400 <= e.response.status_code < 500:
                    logger.error(
                        f"Tavus API client error (attempt {attempt + 1}/{self.max_retries + 1}): "
                        f"{e.response.status_code} - {e.response.text[:200]}"
                    )
                    raise Exception(f"Tavus API client error: {e.response.status_code}")
                
                # Retry on 5xx errors
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API server error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {e.response.status_code}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API server error after {self.max_retries + 1} attempts: {e.response.status_code}")
                    
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API timeout (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API timeout after {self.max_retries + 1} attempts")
                    
            except (httpx.ConnectError, httpx.NetworkError, OSError) as e:
                # Network/DNS errors - more specific handling
                last_exception = e
                error_type = "network"
                if "getaddrinfo" in str(e).lower() or "name resolution" in str(e).lower():
                    error_type = "DNS resolution"
                elif "connection" in str(e).lower():
                    error_type = "connection"
                
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API {error_type} error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {str(e)[:200]}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API {error_type} error after {self.max_retries + 1} attempts: {str(e)[:200]}")
                    
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.warning(
                        f"Tavus API error (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {str(e)[:200]}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Tavus API error after {self.max_retries + 1} attempts: {str(e)[:200]}")
        
        # If we get here, all retries failed
        error_msg = f"Tavus API error after {self.max_retries + 1} attempts"
        if last_exception:
            error_str = str(last_exception)
            # Provide user-friendly error messages for common network issues
            if "getaddrinfo" in error_str.lower() or "name resolution" in error_str.lower():
                error_msg = f"Unable to connect to Tavus API: DNS resolution failed. Please check your internet connection and ensure the API URL ({self.api_url}) is correct."
            elif "connection" in error_str.lower() and "refused" in error_str.lower():
                error_msg = f"Unable to connect to Tavus API: Connection refused. The API server may be down or unreachable."
            elif "timeout" in error_str.lower():
                error_msg = f"Tavus API request timed out after {self.timeout} seconds. The API may be slow or unavailable."
            else:
                error_msg += f": {error_str[:200]}"
        raise Exception(error_msg)
