import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import FirstPage from './pages/FirstPage'
import GetStarted from './pages/GetStarted'
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
import ChoosePlan from './pages/ChoosePlan'
import Checkout from './pages/Checkout'
import EnterpriseInquiry from './pages/EnterpriseInquiry'
import Features from './pages/Features'
import PricingPublic from './pages/PricingPublic'
import About from './pages/About'
import Careers from './pages/Careers'
import Contact from './pages/Contact'
import Blog from './pages/Blog'
import HelpCenter from './pages/HelpCenter'
import PrivacyPolicy from './pages/PrivacyPolicy'
import TermsOfService from './pages/TermsOfService'
import CookiePolicy from './pages/CookiePolicy'
import ProtectedRoute from './components/ProtectedRoute'
import RequirePlanSelected from './components/RequirePlanSelected'
import { initAnalytics, trackPageView } from './utils/analytics'

function WithPlanGate({ children }) {
  return (
    <ProtectedRoute>
      <RequirePlanSelected>{children}</RequirePlanSelected>
    </ProtectedRoute>
  )
}

// Component to track route changes
function RouteTracker() {
  const location = useLocation()
  
  useEffect(() => {
    trackPageView(location.pathname + location.search)
  }, [location])
  
  return null
}

function App() {
  useEffect(() => {
    // Initialize analytics on app load
    initAnalytics()
  }, [])
  
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <RouteTracker />
        <Routes>
          <Route path="/first-page" element={<FirstPage />} />
          <Route path="/" element={<FirstPage />} />
          <Route path="/features" element={<Features />} />
          <Route path="/pricing" element={<PricingPublic />} />
          <Route path="/about" element={<About />} />
          <Route path="/careers" element={<Careers />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/help" element={<HelpCenter />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/cookies" element={<CookiePolicy />} />
          <Route path="/get-started" element={<GetStarted />} />
          <Route path="/landing" element={<Landing />} />
          <Route
            path="/choose-plan"
            element={
              <ProtectedRoute>
                <ChoosePlan />
              </ProtectedRoute>
            }
          />
          <Route
            path="/checkout"
            element={
              <ProtectedRoute>
                <Checkout />
              </ProtectedRoute>
            }
          />
          <Route
            path="/enterprise-inquiry"
            element={
              <ProtectedRoute>
                <EnterpriseInquiry />
              </ProtectedRoute>
            }
          />
          <Route path="/feed" element={<WithPlanGate><Feed /></WithPlanGate>} />
          <Route path="/network" element={<WithPlanGate><Network /></WithPlanGate>} />
          <Route path="/jobs" element={<WithPlanGate><Jobs /></WithPlanGate>} />
          <Route path="/lms" element={<WithPlanGate><LMS /></WithPlanGate>} />
          <Route path="/evaluation" element={<WithPlanGate><Evaluation /></WithPlanGate>} />
          <Route path="/ai-mode" element={<WithPlanGate><AIMode /></WithPlanGate>} />
          <Route path="/ai-interviews" element={<WithPlanGate><AIInterviews /></WithPlanGate>} />
          <Route path="/notifications" element={<WithPlanGate><Notifications /></WithPlanGate>} />
          <Route path="/messages" element={<WithPlanGate><Messages /></WithPlanGate>} />
          <Route
            path="/profile/:username-:hashedId"
            element={<WithPlanGate><Profile /></WithPlanGate>}
          />
          <Route path="/profile/:userId" element={<WithPlanGate><Profile /></WithPlanGate>} />
          <Route path="/settings" element={<WithPlanGate><Settings /></WithPlanGate>} />
        </Routes>
      </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
