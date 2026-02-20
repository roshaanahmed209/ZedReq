import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'

// Firebase configuration for Google Auth (separate from messaging Firebase)
// Uses FIREBASE_AUTH_* environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_AUTH_API_KEY,
  authDomain: `${import.meta.env.VITE_FIREBASE_AUTH_PROJECT_ID}.firebaseapp.com`,
  projectId: import.meta.env.VITE_FIREBASE_AUTH_PROJECT_ID,
  storageBucket: `${import.meta.env.VITE_FIREBASE_AUTH_PROJECT_ID}.appspot.com`,
  messagingSenderId: import.meta.env.VITE_FIREBASE_AUTH_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_AUTH_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_AUTH_MEASUREMENT_ID
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app)

// Initialize Google Auth Provider
export const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({
  prompt: 'select_account'
})

export default app
