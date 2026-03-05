"""
Firebase Admin SDK Client for Realtime Database

This module reads Firebase configuration from .env file:
- FIREBASE_PROJECT_ID (required)
- FIREBASE_DATABASE_URL (required)
- FIREBASE_API_KEY (optional, for REST API fallback)
- FIREBASE_CREDENTIALS_PATH (optional, auto-detects credentials.json in firebase dir)

It automatically:
1. Loads environment variables from .env
2. Looks for credentials.json in the firebase directory if FIREBASE_CREDENTIALS_PATH is not set
3. Uses Firebase Admin SDK if credentials.json is found
4. Falls back to REST API with FIREBASE_API_KEY if credentials.json is missing
"""
import os
import firebase_admin
from firebase_admin import credentials, db
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Firebase app instance
_firebase_app: Optional[firebase_admin.App] = None
_database_url: Optional[str] = None
_api_key: Optional[str] = None


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app, _database_url
    
    # #region agent log
    import json
    try:
        with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps({"runId":"initial","hypothesisId":"A,B,C,D,E","location":"firebase_client.py:34","message":"initialize_firebase called","data":{"cwd":os.getcwd(),"firebase_app_exists":_firebase_app is not None,"file_location":os.path.abspath(__file__)},"timestamp":int(__import__("time").time()*1000)}) + "\n")
    except: pass
    # #endregion
    
    if _firebase_app is not None:
        logger.debug("Firebase Admin SDK already initialized, returning existing app")
        return _firebase_app
    
    # Check if Firebase Admin SDK was already initialized by another process/module
    try:
        existing_app = firebase_admin.get_app()
        if existing_app:
            logger.info("Found existing Firebase app from previous initialization, using it")
            _firebase_app = existing_app
            # Get database URL from existing app config
            if hasattr(existing_app, 'project_id'):
                _database_url = os.getenv("FIREBASE_DATABASE_URL") or f"https://{existing_app.project_id}-default-rtdb.firebaseio.com/"
            return _firebase_app
    except ValueError:
        # No app exists yet, continue with initialization
        logger.debug("No existing Firebase app found, proceeding with initialization")
    except Exception as e:
        logger.debug(f"Error checking for existing Firebase app: {e}")
    
    try:
        # Get Firebase configuration from environment variables
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        if not project_id:
            raise ValueError("FIREBASE_PROJECT_ID is required in .env file")
        
        database_url = os.getenv("FIREBASE_DATABASE_URL")
        if not database_url:
            # Fallback to default format if not provided
            database_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
            logger.warning(f"FIREBASE_DATABASE_URL not set, using default: {database_url}")
        
        # Store API key for REST API fallback
        global _api_key
        _api_key = os.getenv("FIREBASE_API_KEY")
        if not _api_key:
            logger.warning("FIREBASE_API_KEY not set in .env - REST API fallback may not work")
        
        # Check if Firebase credentials file exists
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        
        # #region agent log
        try:
            with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"runId":"initial","hypothesisId":"A,D","location":"firebase_client.py:77","message":"Checking credential path","data":{"env_cred_path":cred_path,"cwd":os.getcwd()},"timestamp":int(__import__("time").time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        # If env var is set, resolve it (handle relative paths)
        if cred_path:
            # If it's a relative path, resolve it relative to the firebase_client.py file location
            # This ensures it works regardless of the current working directory
            if not os.path.isabs(cred_path):
                # Get the directory containing this file (firebase_client.py)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # If path starts with "backend/", resolve from project root (parent of backend/)
                if cred_path.startswith("backend" + os.sep) or cred_path.startswith("backend/"):
                    # Go up from backend/utils/ to backend/ to project root, then append the path
                    project_root = os.path.dirname(os.path.dirname(current_dir))
                    cred_path = os.path.join(project_root, cred_path)
                else:
                    # Otherwise, resolve relative to utils directory
                    cred_path = os.path.join(current_dir, cred_path)
                cred_path = os.path.normpath(cred_path)
            
            # #region agent log
            try:
                with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"runId":"initial","hypothesisId":"A,D","location":"firebase_client.py:85","message":"Resolved credential path","data":{"resolved_path":cred_path,"exists":os.path.exists(cred_path) if cred_path else False},"timestamp":int(__import__("time").time()*1000)}) + "\n")
            except: pass
            # #endregion
        
        # If not set, check for credentials.json in firebase directory
        if not cred_path:
            # Check in the firebase directory (not utils directory)
            # Use absolute path based on file location, not current working directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up from backend/utils/ to backend/, then to firebase/
            backend_dir = os.path.dirname(current_dir)
            firebase_dir = os.path.join(backend_dir, "firebase")
            default_cred_path = os.path.join(firebase_dir, "credentials.json")
            # Normalize path for cross-platform compatibility
            default_cred_path = os.path.normpath(default_cred_path)
            logger.info(f"Checking for credentials at: {default_cred_path}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Firebase client file location: {os.path.abspath(__file__)}")
            
            # #region agent log
            try:
                with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"runId":"initial","hypothesisId":"A,D","location":"firebase_client.py:84","message":"Path resolution","data":{"default_cred_path":default_cred_path,"exists":os.path.exists(default_cred_path),"current_dir":current_dir},"timestamp":int(__import__("time").time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            if os.path.exists(default_cred_path):
                cred_path = default_cred_path
                logger.info(f"✓ Found credentials.json in firebase directory: {cred_path}")
            else:
                logger.warning(f"✗ Credentials file not found at: {default_cred_path}")
                logger.warning(f"  File exists check: {os.path.exists(default_cred_path)}")
                # Try alternative paths
                alt_paths = [
                    os.path.join(os.getcwd(), "backend", "firebase", "credentials.json"),
                    os.path.join(os.path.dirname(os.path.dirname(current_dir)), "backend", "firebase", "credentials.json"),
                ]
                for alt_path in alt_paths:
                    alt_path = os.path.normpath(alt_path)
                    logger.info(f"  Trying alternative path: {alt_path}")
                    
                    # #region agent log
                    try:
                        with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                            f.write(json.dumps({"runId":"initial","hypothesisId":"A,D","location":"firebase_client.py:98","message":"Trying alternative path","data":{"alt_path":alt_path,"exists":os.path.exists(alt_path)},"timestamp":int(__import__("time").time()*1000)}) + "\n")
                    except: pass
                    # #endregion
                    
                    if os.path.exists(alt_path):
                        cred_path = alt_path
                        logger.info(f"✓ Found credentials at alternative path: {cred_path}")
                        break
        
        if cred_path and os.path.exists(cred_path):
            # Use service account credentials file
            logger.info(f"Using Firebase credentials from: {cred_path}")
            try:
                cred = credentials.Certificate(cred_path)
                _firebase_app = firebase_admin.initialize_app(
                    cred,
                    {
                        "databaseURL": database_url
                    }
                )
                
                # #region agent log
                try:
                    with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps({"runId":"initial","hypothesisId":"A,B,C,D,E","location":"firebase_client.py:113","message":"Firebase initialized successfully","data":{"cred_path":cred_path,"database_url":database_url},"timestamp":int(__import__("time").time()*1000)}) + "\n")
                except: pass
                # #endregion
                
            except Exception as e:
                logger.error(f"Failed to initialize Firebase with credentials file: {e}")
                logger.warning("Falling back to REST API")
                
                # #region agent log
                try:
                    with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps({"runId":"initial","hypothesisId":"A,B,C,D,E","location":"firebase_client.py:121","message":"Firebase initialization failed","data":{"error":str(e),"cred_path":cred_path},"timestamp":int(__import__("time").time()*1000)}) + "\n")
                except: pass
                # #endregion
                
                _database_url = database_url
                _firebase_app = None
                return None
        else:
            # No credentials file found - skip Admin SDK initialization
            logger.info("No Firebase credentials file found. Will use REST API.")
            logger.info("To use Firebase Admin SDK, set FIREBASE_CREDENTIALS_PATH in .env or place credentials.json in backend/firebase/")
            
            # #region agent log
            try:
                with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"runId":"initial","hypothesisId":"A,D","location":"firebase_client.py:128","message":"No credentials file found","data":{"cred_path":cred_path,"checked_paths":[default_cred_path if not cred_path else None]},"timestamp":int(__import__("time").time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            _database_url = database_url
            _firebase_app = None  # Explicitly set to None
            return None
        
        _database_url = database_url
        logger.info(f"Firebase initialized successfully with database URL: {database_url}")
        return _firebase_app
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        # Set database URL for REST API fallback
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        if project_id:
            _database_url = os.getenv("FIREBASE_DATABASE_URL")
            if not _database_url:
                _database_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
        else:
            logger.error("FIREBASE_PROJECT_ID is required in .env file")
        return None


def get_firebase_db():
    """Get Firebase Realtime Database reference"""
    global _firebase_app, _database_url
    
    # #region agent log
    import json
    import traceback
    try:
        with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps({"runId":"initial","hypothesisId":"B","location":"firebase_client.py:151","message":"get_firebase_db called","data":{"firebase_app_is_none":_firebase_app is not None,"cwd":os.getcwd(),"caller":traceback.extract_stack()[-2].name if len(traceback.extract_stack()) > 1 else "unknown"},"timestamp":int(__import__("time").time()*1000)}) + "\n")
    except: pass
    # #endregion
    
    # Initialize if not already done
    if _firebase_app is None:
        logger.info("Firebase app not initialized, attempting to initialize now...")
        initialize_firebase()
    
    # Only try to get reference if app is properly initialized
    if _firebase_app is not None:
        try:
            ref = db.reference()
            logger.debug("Successfully obtained Firebase database reference")
            
            # #region agent log
            try:
                with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"runId":"initial","hypothesisId":"B","location":"firebase_client.py:227","message":"get_firebase_db returning ref","data":{"ref_exists":ref is not None},"timestamp":int(__import__("time").time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            return ref
        except Exception as e:
            logger.error(f"Failed to get Firebase database reference: {e}", exc_info=True)
            logger.warning("Falling back to REST API")
            
            # #region agent log
            try:
                with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"runId":"initial","hypothesisId":"B","location":"firebase_client.py:231","message":"get_firebase_db failed to get ref","data":{"error":str(e)},"timestamp":int(__import__("time").time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            # Reset app to None so we use REST API
            _firebase_app = None
            return None
    else:
        logger.debug("Firebase app is None, returning None (will use REST API)")
        
        # #region agent log
        try:
            with open(r"e:\professional\ZedRec\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"runId":"initial","hypothesisId":"B","location":"firebase_client.py:252","message":"get_firebase_db returning None (app is None)","data":{"firebase_app_is_none":True},"timestamp":int(__import__("time").time()*1000)}) + "\n")
        except: pass
        # #endregion
    
    # Return None if not initialized (will use REST API)
    return None


def get_database_url() -> str:
    """Get the Firebase Realtime Database URL"""
    global _database_url
    
    if _database_url is None:
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        if not project_id:
            raise ValueError("FIREBASE_PROJECT_ID is required in .env file")
        
        _database_url = os.getenv("FIREBASE_DATABASE_URL")
        if not _database_url:
            _database_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
    
    return _database_url


def get_api_key() -> Optional[str]:
    """Get the Firebase API Key for REST API"""
    global _api_key
    
    if _api_key is None:
        _api_key = os.getenv("FIREBASE_API_KEY")
    
    return _api_key


# Initialize on import (but don't fail if credentials are missing)
# Note: This happens when the module is first imported
# The server startup will also call initialize_firebase() explicitly
try:
    initialize_firebase()
except Exception as e:
    logger.debug(f"Firebase initialization failed on import (this is OK, will retry at server startup): {e}")
