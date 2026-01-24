"""Messaging Service using Firebase Realtime Database"""
import json
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import httpx
import os

from firebase.firebase_client import get_firebase_db, get_database_url, get_api_key

logger = logging.getLogger(__name__)


class MessagingService:
    """Service for handling messages with Firebase Realtime Database"""
    
    def __init__(self):
        self.db_ref = get_firebase_db()
        self.database_url = get_database_url()
        self.api_key = get_api_key() or ""
        
    def _get_rest_url(self, path: str = "") -> str:
        """Get REST API URL for Firebase Realtime Database"""
        base_url = self.database_url.rstrip('/')
        path = path.lstrip('/')
        return f"{base_url}/{path}.json"
    
    async def _firebase_rest_request(
        self, 
        method: str, 
        path: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make REST API request to Firebase Realtime Database"""
        url = self._get_rest_url(path)
        
        # Add auth token if available
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            params = params or {}
            params["auth"] = self.api_key
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, params=params, headers=headers)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data, params=params, headers=headers)
                elif method.upper() == "PATCH":
                    response = await client.patch(url, json=data, params=params, headers=headers)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, params=params, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json() if response.content else None
                
        except httpx.HTTPError as e:
            logger.error(f"Firebase REST API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error making Firebase request: {e}")
            return None
    
    def _generate_message_id(self, sender_id: int, recipient_id: int) -> str:
        """Generate a unique message ID"""
        timestamp = int(time.time() * 1000)  # milliseconds
        return f"{sender_id}_{recipient_id}_{timestamp}"
    
    def _get_conversation_path(self, user1_id: int, user2_id: int) -> str:
        """Get the conversation path in Firebase (sorted to ensure consistency)"""
        # Sort user IDs to ensure same conversation path regardless of order
        sorted_ids = sorted([user1_id, user2_id])
        return f"conversations/{sorted_ids[0]}_{sorted_ids[1]}"
    
    def _get_messages_path(self, user1_id: int, user2_id: int) -> str:
        """Get the messages path for a conversation"""
        return f"{self._get_conversation_path(user1_id, user2_id)}/messages"
    
    async def send_message(
        self,
        sender_id: int,
        recipient_id: int,
        content: str,
        message_type: str = "text"
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message and store it in Firebase Realtime Database
        
        Args:
            sender_id: ID of the user sending the message
            recipient_id: ID of the user receiving the message
            content: Message content
            message_type: Type of message (text, image, file, etc.)
        
        Returns:
            Dictionary containing message data or None if failed
        """
        try:
            message_id = self._generate_message_id(sender_id, recipient_id)
            timestamp = datetime.utcnow().isoformat()
            
            message_data = {
                "id": message_id,
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "content": content,
                "message_type": message_type,
                "timestamp": timestamp,
                "created_at": timestamp,
                "read": False
            }
            
            # Store message in Firebase
            messages_path = self._get_messages_path(sender_id, recipient_id)
            
            if self.db_ref:
                # Use Firebase Admin SDK
                ref = self.db_ref.child(messages_path).child(message_id)
                ref.set(message_data)
            else:
                # Use REST API
                result = await self._firebase_rest_request(
                    "PUT",
                    f"{messages_path}/{message_id}",
                    data=message_data
                )
                if result is None:
                    return None
            
            # Update conversation metadata
            await self._update_conversation_metadata(sender_id, recipient_id, message_data)
            
            logger.info(f"Message sent: {message_id} from {sender_id} to {recipient_id}")
            return message_data
            
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            return None
    
    async def _update_conversation_metadata(
        self,
        user1_id: int,
        user2_id: int,
        last_message: Dict[str, Any]
    ):
        """Update conversation metadata with last message info"""
        try:
            conversation_path = self._get_conversation_path(user1_id, user2_id)
            metadata = {
                "last_message": last_message,
                "updated_at": datetime.utcnow().isoformat(),
                "participants": sorted([user1_id, user2_id])
            }
            
            if self.db_ref:
                ref = self.db_ref.child(conversation_path)
                ref.update(metadata)
            else:
                await self._firebase_rest_request(
                    "PATCH",
                    conversation_path,
                    data=metadata
                )
        except Exception as e:
            logger.error(f"Error updating conversation metadata: {e}")
    
    async def get_messages(
        self,
        user1_id: int,
        user2_id: int,
        limit: int = 50,
        start_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            limit: Maximum number of messages to retrieve
            start_after: Message ID to start after (for pagination)
        
        Returns:
            List of message dictionaries
        """
        try:
            messages_path = self._get_messages_path(user1_id, user2_id)
            
            if self.db_ref:
                # Use Firebase Admin SDK
                ref = self.db_ref.child(messages_path)
                messages_data = ref.order_by_key().limit_to_last(limit).get()
                
                if messages_data:
                    messages = list(messages_data.values())
                    # Sort by timestamp (newest first)
                    messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                    return messages
                return []
            else:
                # Use REST API
                params = {"orderBy": '"$key"', "limitToLast": limit}
                messages_data = await self._firebase_rest_request("GET", messages_path, params=params)
                
                if messages_data:
                    messages = list(messages_data.values())
                    messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                    return messages
                return []
                
        except Exception as e:
            logger.error(f"Error getting messages: {e}", exc_info=True)
            return []
    
    async def get_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user
        
        Args:
            user_id: ID of the user
        
        Returns:
            List of conversation dictionaries
        """
        try:
            conversations = []
            
            if self.db_ref:
                # Use Firebase Admin SDK
                ref = self.db_ref.child("conversations")
                all_conversations = ref.get()
                
                if all_conversations:
                    for conv_key, conv_data in all_conversations.items():
                        participants = conv_data.get("participants", [])
                        if user_id in participants:
                            # Get the other participant
                            other_id = [p for p in participants if p != user_id]
                            if other_id:
                                conversations.append({
                                    "conversation_id": conv_key,
                                    "other_user_id": other_id[0],
                                    "last_message": conv_data.get("last_message"),
                                    "updated_at": conv_data.get("updated_at")
                                })
            else:
                # Use REST API - need to fetch all and filter
                all_conversations = await self._firebase_rest_request("GET", "conversations")
                
                if all_conversations:
                    for conv_key, conv_data in all_conversations.items():
                        participants = conv_data.get("participants", [])
                        if user_id in participants:
                            other_id = [p for p in participants if p != user_id]
                            if other_id:
                                conversations.append({
                                    "conversation_id": conv_key,
                                    "other_user_id": other_id[0],
                                    "last_message": conv_data.get("last_message"),
                                    "updated_at": conv_data.get("updated_at")
                                })
            
            # Sort by updated_at (most recent first)
            conversations.sort(
                key=lambda x: x.get("updated_at", ""), 
                reverse=True
            )
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations: {e}", exc_info=True)
            return []
    
    async def mark_message_as_read(
        self,
        user1_id: int,
        user2_id: int,
        message_id: str
    ) -> bool:
        """
        Mark a message as read
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            message_id: ID of the message to mark as read
        
        Returns:
            True if successful, False otherwise
        """
        try:
            messages_path = self._get_messages_path(user1_id, user2_id)
            
            if self.db_ref:
                ref = self.db_ref.child(messages_path).child(message_id)
                ref.update({"read": True})
            else:
                await self._firebase_rest_request(
                    "PATCH",
                    f"{messages_path}/{message_id}",
                    data={"read": True}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return False
    
    async def mark_conversation_as_read(
        self,
        user1_id: int,
        user2_id: int
    ) -> bool:
        """
        Mark all messages in a conversation as read
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            messages_path = self._get_messages_path(user1_id, user2_id)
            
            # Get all unread messages
            messages = await self.get_messages(user1_id, user2_id, limit=1000)
            unread_messages = [msg for msg in messages if not msg.get("read", False) and msg.get("recipient_id") == user1_id]
            
            # Mark each as read
            for message in unread_messages:
                await self.mark_message_as_read(user1_id, user2_id, message["id"])
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking conversation as read: {e}")
            return False
