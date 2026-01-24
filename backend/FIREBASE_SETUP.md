# Firebase Setup Guide

## What are Firebase Credentials?

Firebase credentials come in two forms:

### 1. Service Account JSON File (Recommended for Server-Side)
A JSON file containing private key and service account information. This is the most secure method for server-side applications.

### 2. API Key (For REST API Fallback)
A simple API key string that can be used with Firebase REST API.

## How to Get Firebase Credentials

### Option 1: Service Account JSON File (Recommended)

1. **Go to Firebase Console**
   - Visit https://console.firebase.google.com/
   - Select your project: `zedreg-messages`

2. **Navigate to Project Settings**
   - Click the gear icon ⚙️ next to "Project Overview"
   - Select "Project settings"

3. **Go to Service Accounts Tab**
   - Click on the "Service accounts" tab
   - You'll see options for Node.js, Python, Java, etc.

4. **Generate New Private Key**
   - Click "Generate new private key" button
   - A dialog will warn you about keeping the key secure - click "Generate key"
   - A JSON file will be downloaded (e.g., `zedreg-messages-firebase-adminsdk-xxxxx.json`)

5. **Save the File Securely**
   - Store this file in a secure location (NOT in your git repository!)
   - Recommended location: `backend/firebase/credentials.json` (add to `.gitignore`)
   - Or store it outside the project directory

6. **Set Environment Variable**
   - Add to your `.env` file:
     ```
     FIREBASE_CREDENTIALS_PATH=backend/firebase/credentials.json
     ```
   - Or use absolute path:
     ```
     FIREBASE_CREDENTIALS_PATH=/path/to/your/credentials.json
     ```

### Option 2: API Key (For REST API)

1. **Go to Firebase Console**
   - Visit https://console.firebase.google.com/
   - Select your project: `zedreg-messages`

2. **Navigate to Project Settings**
   - Click the gear icon ⚙️ next to "Project Overview"
   - Select "Project settings"

3. **Get API Key**
   - Scroll down to "Your apps" section
   - If you have a web app, you'll see the API key
   - Or go to "General" tab and look for "Web API Key"
   - Copy the API key

4. **Set Environment Variable**
   - Add to your `.env` file:
     ```
     FIREBASE_API_KEY=AIzaSyCtf57BJ3fqMRHZKxPkQzE13Zha8FQHZiY
     ```

## What the Service Account JSON File Looks Like

```json
{
  "type": "service_account",
  "project_id": "zedreg-messages",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@zedreg-messages.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

## Environment Variables for Firebase

Add these to your `.env` file:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=zedreg-messages
FIREBASE_DATABASE_URL=https://zedreg-messages-default-rtdb.firebaseio.com/
FIREBASE_CREDENTIALS_PATH=backend/firebase/credentials.json
FIREBASE_API_KEY=your-api-key-here
```

## Security Best Practices

1. **Never commit credentials to git**
   - Add `credentials.json` to `.gitignore`
   - Add `*.json` to `.gitignore` in the firebase folder

2. **Use environment variables**
   - Never hardcode credentials in code
   - Use `.env` file (which should also be in `.gitignore`)

3. **Restrict permissions**
   - In Firebase Console, go to IAM & Admin
   - Ensure the service account has only necessary permissions
   - For Realtime Database, it needs "Firebase Realtime Database Admin" role

4. **Rotate keys regularly**
   - Generate new keys periodically
   - Revoke old keys when no longer needed

## Setting Up Realtime Database Rules

1. **Go to Realtime Database**
   - In Firebase Console, select "Realtime Database"
   - Click "Create database" if not already created

2. **Set Security Rules**
   - Go to "Rules" tab
   - For development, you can use:
     ```json
     {
       "rules": {
         ".read": "auth != null",
         ".write": "auth != null"
       }
     }
     ```
   - For production, use more restrictive rules based on your needs

3. **Choose Database Location**
   - Select a region close to your users
   - Note: The database URL might include the region

## Testing Your Setup

After setting up credentials, test the connection:

```python
from firebase.firebase_client import get_firebase_db, get_database_url

# Test database URL
print(f"Database URL: {get_database_url()}")

# Test database connection
db_ref = get_firebase_db()
if db_ref:
    print("✅ Firebase Admin SDK initialized successfully")
    # Test write
    test_ref = db_ref.child("test")
    test_ref.set({"message": "Connection test", "timestamp": "2024-01-01"})
    print("✅ Write test successful")
else:
    print("⚠️ Using REST API fallback")
```

## Troubleshooting

### Error: "Could not initialize Firebase"
- Check that `FIREBASE_CREDENTIALS_PATH` points to a valid file
- Verify the JSON file is not corrupted
- Ensure the service account has proper permissions

### Error: "Permission denied"
- Check Firebase Realtime Database security rules
- Verify the service account has "Firebase Realtime Database Admin" role
- Check that the database exists and is in the correct region

### Error: "Database URL not found"
- Verify `FIREBASE_DATABASE_URL` is set correctly
- Check that the Realtime Database is created in Firebase Console
- The URL format should be: `https://<project-id>-default-rtdb.firebaseio.com/`
