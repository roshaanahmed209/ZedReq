"""
Test script for Firebase Realtime Database messaging functionality

This script tests:
1. Firebase connection and configuration
2. Sending a test message
3. Retrieving messages
4. Verifying message storage

Usage:
    python backend/scripts/test_firebase_messaging.py
"""
import sys
import os
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Firebase client
<<<<<<< HEAD
from utils.firebase_client import get_firebase_db, get_database_url, get_api_key
=======
from firebase.firebase_client import get_firebase_db, get_database_url, get_api_key
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe
from services.messaging_service import MessagingService


def test_firebase_connection():
    """Test Firebase connection and configuration"""
    print("\n" + "="*60)
    print("TEST 1: Firebase Connection & Configuration")
    print("="*60)
    
    try:
        # Test database URL
        database_url = get_database_url()
        print(f"[OK] Database URL: {database_url}")
        
        # Test API key
        api_key = get_api_key()
        if api_key:
            print(f"[OK] API Key: {api_key[:20]}... (hidden)")
        else:
            print("[WARN] API Key: Not set (REST API fallback may not work)")
        
        # Test Firebase Admin SDK
        db_ref = get_firebase_db()
        if db_ref:
            print("[OK] Firebase Admin SDK: Initialized successfully")
            
            # Try to read from database
            try:
                test_ref = db_ref.child("test")
                test_ref.set({"test": "connection", "timestamp": datetime.utcnow().isoformat()})
                test_data = test_ref.get()
                if test_data:
                    print("[OK] Database Write/Read: Success")
                    # Clean up test data
                    test_ref.delete()
                    print("[OK] Test data cleaned up")
                else:
                    print("[WARN] Database Write/Read: Write succeeded but read returned None")
            except Exception as e:
                print(f"[ERROR] Database Write/Read: Failed - {e}")
        else:
            print("[WARN] Firebase Admin SDK: Not initialized (will use REST API)")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Firebase Connection Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_send_message():
    """Test sending a message through MessagingService"""
    print("\n" + "="*60)
    print("TEST 2: Send Test Message")
    print("="*60)
    
    try:
        messaging_service = MessagingService()
        
        # Test user IDs (you can change these)
        sender_id = 1
        recipient_id = 2
        
        test_content = f"Test message from Firebase test script - {datetime.utcnow().isoformat()}"
        
        print(f"Sending test message:")
        print(f"  From: User {sender_id}")
        print(f"  To: User {recipient_id}")
        print(f"  Content: {test_content}")
        
        # Send message
        sent_message = await messaging_service.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=test_content,
            message_type="text"
        )
        
        if sent_message:
            print("[OK] Message sent successfully!")
            print(f"  Message ID: {sent_message.get('id')}")
            print(f"  Timestamp: {sent_message.get('timestamp')}")
            print(f"  Content: {sent_message.get('content')}")
            return sent_message
        else:
            print("[ERROR] Message send failed: send_message returned None")
            return None
            
    except Exception as e:
        print(f"[ERROR] Send Message Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_get_messages():
    """Test retrieving messages"""
    print("\n" + "="*60)
    print("TEST 3: Retrieve Messages")
    print("="*60)
    
    try:
        messaging_service = MessagingService()
        
        user1_id = 1
        user2_id = 2
        
        print(f"Retrieving messages between User {user1_id} and User {user2_id}...")
        
        messages = await messaging_service.get_messages(
            user1_id=user1_id,
            user2_id=user2_id,
            limit=10
        )
        
        if messages:
            print(f"[OK] Retrieved {len(messages)} messages")
            for i, msg in enumerate(messages[:5], 1):  # Show first 5
                print(f"  Message {i}:")
                print(f"    ID: {msg.get('id')}")
                print(f"    From: User {msg.get('sender_id')}")
                print(f"    Content: {msg.get('content', '')[:50]}...")
                print(f"    Timestamp: {msg.get('timestamp')}")
        else:
            print("[WARN] No messages found (this is OK if no messages exist)")
        
        return messages
        
    except Exception as e:
        print(f"[ERROR] Get Messages Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_conversations():
    """Test retrieving conversations"""
    print("\n" + "="*60)
    print("TEST 4: Retrieve Conversations")
    print("="*60)
    
    try:
        messaging_service = MessagingService()
        
        user_id = 1
        
        print(f"Retrieving conversations for User {user_id}...")
        
        conversations = await messaging_service.get_conversations(
            user_id=user_id,
            connected_user_ids=None  # Get all conversations
        )
        
        if conversations:
            print(f"[OK] Retrieved {len(conversations)} conversations")
            for i, conv in enumerate(conversations[:5], 1):  # Show first 5
                print(f"  Conversation {i}:")
                print(f"    Other User: {conv.get('other_user_id')}")
                if conv.get('last_message'):
                    print(f"    Last Message: {conv.get('last_message', {}).get('content', '')[:50]}...")
                    print(f"    Updated: {conv.get('last_message', {}).get('timestamp')}")
        else:
            print("[WARN] No conversations found (this is OK if no conversations exist)")
        
        return conversations
        
    except Exception as e:
        print(f"[ERROR] Get Conversations Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Firebase Realtime Database Messaging Test Suite")
    print("="*60)
    
    # Test 1: Connection
    connection_ok = test_firebase_connection()
    
    if not connection_ok:
        print("\n[ERROR] Firebase connection test failed. Please check your configuration.")
        print("\nRequired environment variables:")
        print("  - FIREBASE_PROJECT_ID")
        print("  - FIREBASE_DATABASE_URL")
        print("  - FIREBASE_API_KEY (optional, for REST API)")
        print("  - FIREBASE_CREDENTIALS_PATH (optional, for Admin SDK)")
        return
    
    # Test 2: Send message
    sent_message = await test_send_message()
    
    if not sent_message:
        print("\n[ERROR] Message sending failed. Check Firebase configuration and permissions.")
        return
    
    # Test 3: Get messages
    await test_get_messages()
    
    # Test 4: Get conversations
    await test_conversations()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("[OK] All tests completed!")
    print("\nIf you see any [ERROR] messages above, check:")
    print("  1. Firebase environment variables in .env file")
    print("  2. Firebase Realtime Database is enabled in Firebase Console")
    print("  3. Database security rules allow read/write")
    print("  4. Service account has proper permissions (if using Admin SDK)")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
