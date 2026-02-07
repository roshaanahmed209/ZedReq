"""
Tavus Service
Handles integration with Tavus AI API for video interviews
"""
import os
import logging
from typing import Dict, Any, Optional
import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class TavusService:
    """Service for interacting with Tavus AI API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        """
        Initialize Tavus service
        
        Args:
            api_key: Tavus API key (default: from settings)
            api_url: Tavus API URL (default: from settings)
        """
        self.api_key = api_key or settings.TAVUS_API_KEY
        self.api_url = api_url or settings.TAVUS_API_URL
        
        if not self.api_key:
            logger.warning("Tavus API key not found. Tavus integration will not work.")
            self.available = False
        else:
            self.available = True
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_conversation(
        self,
        replica_id: str,
        conversation_name: str,
        system_prompt: str,
        first_message: str
    ) -> Dict[str, Any]:
        """
        Create a new Tavus conversation
        
        Args:
            replica_id: Tavus replica ID for the interviewer
            conversation_name: Name for the conversation
            system_prompt: System prompt for the interviewer
            first_message: First message to start the conversation
            
        Returns:
            Dictionary with conversation details including conversation_id
        """
        if not self.available:
            raise ValueError("Tavus API key not configured")
        
        url = f"{self.api_url}/conversations"
        
        payload = {
            "replica_id": replica_id,
            "conversation_name": conversation_name,
            "system_prompt": system_prompt,
            "first_message": first_message
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Created Tavus conversation: {result.get('conversation_id')}")
                return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to create Tavus conversation: {e}")
            raise Exception(f"Tavus API error: {e}")
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation details and status
        
        Args:
            conversation_id: Tavus conversation ID
            
        Returns:
            Dictionary with conversation details
        """
        if not self.available:
            raise ValueError("Tavus API key not configured")
        
        url = f"{self.api_url}/conversations/{conversation_id}"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get Tavus conversation {conversation_id}: {e}")
            raise Exception(f"Tavus API error: {e}")
    
    def get_conversation_transcript(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get full conversation transcript/responses
        
        Args:
            conversation_id: Tavus conversation ID
            
        Returns:
            Dictionary with conversation transcript and responses
        """
        if not self.available:
            raise ValueError("Tavus API key not configured")
        
        # Try to get transcript from conversation details
        # Tavus API structure may vary - adjust endpoint as needed
        url = f"{self.api_url}/conversations/{conversation_id}/transcript"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # If transcript endpoint doesn't exist, try getting full conversation
                logger.warning(f"Transcript endpoint not found, using conversation details")
                return self.get_conversation(conversation_id)
            raise
        except httpx.HTTPError as e:
            logger.error(f"Failed to get Tavus transcript {conversation_id}: {e}")
            raise Exception(f"Tavus API error: {e}")
