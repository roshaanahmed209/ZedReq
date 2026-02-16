import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import FirstPage from './pages/FirstPage'
import Landing from './pages/Landing'
import Feed from './pages/Feed'
import Network from './pages/Network'
import Jobs from './pages/Jobs'
import LMS from './pages/LMS'
import Evaluation from './pages/Evaluation'
import AIMode from './pages/AIMode'
import AIInterviews from './pages/AIInterviews'
import Notifications from './pages/Notifications'
import Messages from './pages/Messages'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/first-page" element={<FirstPage />} />
          <Route path="/" element={<FirstPage />} />
          <Route path="/landing" element={<Landing />} />
          <Route 
            path="/feed" 
            element={
              <ProtectedRoute>
                <Feed />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/network" 
            element={
              <ProtectedRoute>
                <Network />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/jobs" 
            element={
              <ProtectedRoute>
                <Jobs />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/lms" 
            element={
              <ProtectedRoute>
                <LMS />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/evaluation" 
            element={
              <ProtectedRoute>
                <Evaluation />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai-mode" 
            element={
              <ProtectedRoute>
                <AIMode />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai-interviews" 
            element={
              <ProtectedRoute>
                <AIInterviews />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/notifications" 
            element={
              <ProtectedRoute>
                <Notifications />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/messages" 
            element={
              <ProtectedRoute>
                <Messages />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile/:username-:hashedId" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile/:userId" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
