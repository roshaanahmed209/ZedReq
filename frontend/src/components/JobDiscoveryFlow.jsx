import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './JobDiscoveryFlow.css'

// ─── SVG Icons for pipeline stages ──────────────────────────────────────────
const StageIcons = {
  profile: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8" r="4" />
      <path d="M5 20c1.5-4 4-6 7-6s5.5 2 7 6" />
    </svg>
  ),
  analysis: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a7 7 0 0 1 7 7c0 2.5-1.5 5-3 6.5L12 22l-4-6.5C6.5 14 5 11.5 5 9a7 7 0 0 1 7-7z" />
      <circle cx="12" cy="9" r="2.5" />
    </svg>
  ),
  match: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  ),
  application: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  ),
  interview: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" y1="19" x2="12" y2="23" />
      <line x1="8" y1="23" x2="16" y2="23" />
    </svg>
  ),
  lms: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      <path d="M8 7h8" />
      <path d="M8 11h8" />
      <path d="M8 15h4" />
    </svg>
  ),
  mock: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  ),
  offer: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  ),
}


// ─── Checkmark SVG icon ─────────────────────────────────────────────────────
const CheckCircleIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
)

// ─── Pipeline stages ────────────────────────────────────────────────────────
const PIPELINE_STAGES = [
  { id: 'profile', label: 'Profile', description: 'Complete your professional profile' },
  { id: 'analysis', label: 'Skill Analysis', description: 'AI analyzes your skills & experience' },
  { id: 'lms', label: 'AI LMS Practice', description: 'Practice with AI-powered learning modules' },
  { id: 'mock', label: 'Mock Interview', description: 'Prepare with AI mock interviews' },
  { id: 'match', label: 'Job Match', description: 'Intelligent job matching' },
  { id: 'application', label: 'Application', description: 'Submit your application' },
  { id: 'interview', label: 'Interview', description: 'AI-powered interview prep' },
  { id: 'offer', label: 'Offer', description: 'Receive your offer' },
]

// ─── Job match cards data ───────────────────────────────────────────────────
const JOB_MATCHES = [
  { title: 'Software Engineer', company: 'TechVenture Inc.', location: 'Remote', match: 92 },
  { title: 'Full Stack Developer', company: 'NexaLabs', location: 'San Francisco, CA', match: 87 },
  { title: 'Frontend Engineer', company: 'DesignCraft', location: 'New York, NY', match: 84 },
]

// ─── Live job opportunities ─────────────────────────────────────────────────
const LIVE_JOBS = [
  { title: 'Senior React Developer', company: 'CloudScale', location: 'Remote', match: 94, type: 'Full-time' },
  { title: 'AI/ML Engineer', company: 'DeepMind Labs', location: 'London, UK', match: 89, type: 'Full-time' },
  { title: 'Product Designer', company: 'Figma', location: 'San Francisco', match: 86, type: 'Full-time' },
  { title: 'DevOps Engineer', company: 'AWS', location: 'Seattle, WA', match: 82, type: 'Contract' },
  { title: 'Data Scientist', company: 'Spotify', location: 'Stockholm', match: 79, type: 'Full-time' },
]

const JobDiscoveryFlow = () => {
  const [activeStage, setActiveStage] = useState(-1)
  const [showMatchCards, setShowMatchCards] = useState(false)
  const [applicationSent, setApplicationSent] = useState(false)
  const [pipelineComplete, setPipelineComplete] = useState(false)
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef(null)

  // Trigger pipeline animation on scroll
  useEffect(() => {
    const section = sectionRef.current
    if (!section) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.15 }
    )

    observer.observe(section)
    return () => observer.disconnect()
  }, [])

  // Animate pipeline stages once
  useEffect(() => {
    if (!isVisible) return

    const timeouts = []

    // Sequence through stages
    PIPELINE_STAGES.forEach((_, index) => {
      const timeout = setTimeout(() => {
        setActiveStage(index)

        // Show match cards at "Job Match" stage
        if (index === 4) {
          setTimeout(() => setShowMatchCards(true), 400)
        }

        // Show application animation at "Application" stage
        if (index === 5) {
          setTimeout(() => setApplicationSent(true), 400)
        }

        // Mark complete at last stage
        if (index === PIPELINE_STAGES.length - 1) {
          setTimeout(() => setPipelineComplete(true), 600)
        }
      }, index * 1400)

      timeouts.push(timeout)
    })

    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout))
    }
  }, [isVisible])

  return (
    <section className="job-discovery-section scroll-reveal" ref={sectionRef}>
      <div className="job-discovery-container">
        {/* Section Header */}
        <div className="job-header">
          <h2 className="job-headline">
            <span className="job-headline-glow">Find the Right Job Faster</span>
          </h2>
          <p className="job-subheading">
            Our intelligent matching system connects you with opportunities that fit your skills and career goals.
          </p>
        </div>

        {/* Chrome Browser UI */}
        <div className="browser-window">
          {/* Browser Tab Bar */}
          <div className="browser-tabs">
            <div className="browser-tab active">
              <div className="tab-favicon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
              </div>
              <span className="tab-title">ZedReq - Job Discovery</span>
              <button className="tab-close">×</button>
            </div>
          </div>

          {/* Browser Address Bar */}
          <div className="browser-address-bar">
            <div className="address-bar-controls">
              <button className="nav-btn back" disabled>‹</button>
              <button className="nav-btn forward" disabled>›</button>
              <button className="nav-btn refresh">↻</button>
            </div>
            <div className="address-bar-url">
              <svg className="lock-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
              <span className="url-text">https://zedreq.com/job-discovery</span>
            </div>
            <div className="address-bar-actions">
              <button className="action-btn">⋮</button>
            </div>
          </div>

          {/* Browser Content Area */}
          <div className="browser-content">
            {/* Main Content */}
            <div className="job-content">
              {/* Left: Application Interface (60%) */}
              <div className="app-main-panel">
                {/* Progress Tracker Section */}
                <div className="app-section">
                  <div className="section-header">
                    <h3 className="section-title">Your Journey</h3>
                    <span className="section-subtitle">Track your progress</span>
                  </div>
                  
                  <div className="progress-tracker">
                    <div className="progress-steps-container">
                      {PIPELINE_STAGES.map((stage, index) => {
                        const isActive = index <= activeStage
                        const isCurrent = index === activeStage
                        const isCompleted = index < activeStage
                        const isPending = index > activeStage

                        return (
                          <div key={stage.id} className="progress-step-wrapper">
                            {/* Step Item */}
                            <div className={`progress-step-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''} ${isPending ? 'pending' : ''}`}>
                              <div className="step-indicator-wrapper">
                                {isCompleted ? (
                                  <div className="step-check-circle">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                                      <polyline points="20 6 9 17 4 12"></polyline>
                                    </svg>
                                  </div>
                                ) : (
                                  <div className={`step-number-circle ${isCurrent ? 'pulsing' : ''}`}>
                                    {index + 1}
                                  </div>
                                )}
                              </div>
                              <div className="step-info">
                                <div className="step-label-row">
                                  <span className="step-label">{stage.label}</span>
                                  {isCompleted && (
                                    <span className="step-checkmark">✓</span>
                                  )}
                                </div>
                                {isCurrent && (
                                  <div className="step-progress-indicator">
                                    <div className="progress-dot"></div>
                                    <span className="step-status-text">In Progress</span>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Connector Line */}
                            {index < PIPELINE_STAGES.length - 1 && (
                              <div className={`step-connector-line ${isActive ? 'active' : ''}`} />
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>

                {/* Job Matches Section */}
                <AnimatePresence>
                  {showMatchCards && (
                    <motion.div
                      className="app-section"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.4 }}
                    >
                      <div className="section-header">
                        <h3 className="section-title">Recommended Jobs</h3>
                        <span className="section-subtitle">Based on your profile</span>
                      </div>
                      
                      <div className="job-listings-grid">
                        {JOB_MATCHES.map((job, index) => (
                          <motion.div
                            className="job-listing-card"
                            key={job.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1, duration: 0.3 }}
                            whileHover={{ y: -2, boxShadow: '0 8px 24px rgba(0,0,0,0.15)' }}
                          >
                            <div className="job-card-header">
                              <div className="job-title-section">
                                <h4 className="job-title">{job.title}</h4>
                                <span className="job-company">{job.company}</span>
                              </div>
                              <div className="match-badge">
                                <MatchScoreCircle score={job.match} />
                                <span className="match-label">Match</span>
                              </div>
                            </div>
                            <div className="job-details">
                              <span className="job-location">📍 {job.location}</span>
                            </div>
                            <button className="job-apply-button">Apply Now</button>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Application Status Section */}
                <AnimatePresence>
                  {applicationSent && (
                    <motion.div
                      className="app-section status-section"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <div className="status-card success">
                        <div className="status-icon">✓</div>
                        <div className="status-content">
                          <h4 className="status-title">Application Submitted</h4>
                          <p className="status-message">Your application has been sent successfully. You'll receive updates via email.</p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Completion Status */}
                <AnimatePresence>
                  {pipelineComplete && (
                    <motion.div
                      className="app-section status-section"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <div className="status-card success large">
                        <div className="status-icon large"><CheckCircleIcon /></div>
                        <div className="status-content">
                          <h4 className="status-title">Congratulations!</h4>
                          <p className="status-message">You've completed your journey. Welcome to your new role!</p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Right: Sidebar (40%) */}
              <div className="app-sidebar">
                <div className="sidebar-section">
                  <div className="sidebar-header">
                    <h3 className="sidebar-title">Live Opportunities</h3>
                    <span className="sidebar-count">{LIVE_JOBS.length} jobs</span>
                  </div>
                  
                  <div className="sidebar-job-list">
                    {LIVE_JOBS.map((job, index) => (
                      <motion.div
                        className="sidebar-job-item"
                        key={job.title}
                        initial={{ opacity: 0, x: 20 }}
                        animate={isVisible ? { opacity: 1, x: 0 } : {}}
                        transition={{ delay: 0.2 + index * 0.08, duration: 0.3 }}
                        whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.03)' }}
                      >
                        <div className="sidebar-job-content">
                          <div className="sidebar-job-main">
                            <h4 className="sidebar-job-title">{job.title}</h4>
                            <span className="sidebar-job-company">{job.company}</span>
                            <div className="sidebar-job-meta">
                              <span className="sidebar-job-location">📍 {job.location}</span>
                              <span className="sidebar-job-type">{job.type}</span>
                            </div>
                          </div>
                          <div className="sidebar-job-match">
                            <MatchScoreCircle score={job.match} size={40} />
                          </div>
                        </div>
                        <button className="sidebar-apply-btn">Apply</button>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Match Score Circle Component ───────────────────────────────────────────
const MatchScoreCircle = ({ score, size = 42 }) => {
  const r = (size - 8) / 2
  const circumference = 2 * Math.PI * r

  return (
    <div className="match-score-circle" style={{ width: size, height: size }}>
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(0,180,216,0.12)"
          strokeWidth="3"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#00B4D8"
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference * (1 - score / 100) }}
          transition={{ duration: 1.2, delay: 0.3, ease: 'easeOut' }}
          style={{ transformOrigin: 'center', transform: 'rotate(-90deg)', filter: 'drop-shadow(0 0 4px rgba(0,180,216,0.5))' }}
        />
      </svg>
      <span className="match-score-text" style={{ fontSize: size * 0.26 }}>
        {score}%
      </span>
    </div>
  )
}

export default JobDiscoveryFlow
