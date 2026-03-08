import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import DarkVeil from '../components/DarkVeil'
import Beams from '../components/Beams'
import CardSwap, { Card } from '../components/CardSwap'
import ReserveSeatModal from '../components/ReserveSeatModal'
import CombinedSkillGapAndNetwork from '../components/CombinedSkillGapAndNetwork'
import JobDiscoveryFlow from '../components/JobDiscoveryFlow'
import { Timeline } from '../components/Timeline'
import '../css/pages/FirstPage.css'

const FirstPage = () => {
  const [activeLoop, setActiveLoop] = useState(0)
  const [activeTestimonial, setActiveTestimonial] = useState(0)
  const [showReserveModal, setShowReserveModal] = useState(false)
  const [activeTrustFaq, setActiveTrustFaq] = useState(0)
  const [matchPercent, setMatchPercent] = useState(0)
  const trustSectionRef = useRef(null)

  // 3D card tilt effect
  const handleCardMouseMove = (e) => {
    const card = e.currentTarget
    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    
    const percentX = (x / rect.width) * 100
    const percentY = (y / rect.height) * 100
    
    const rotateX = ((percentX - 50) / 5).toFixed(2)
    const rotateY = (-(percentY - 50) / 4).toFixed(2)
    
    card.style.setProperty('--pointer-x', `${percentX}%`)
    card.style.setProperty('--pointer-y', `${percentY}%`)
    card.style.setProperty('--rotate-x', `${rotateX}deg`)
    card.style.setProperty('--rotate-y', `${rotateY}deg`)
    card.style.setProperty('--background-x', `${35 + (percentX / 100) * 30}%`)
    card.style.setProperty('--background-y', `${35 + (percentY / 100) * 30}%`)
    
    const fromCenter = Math.min(Math.hypot(percentY - 50, percentX - 50) / 50, 1)
    card.style.setProperty('--pointer-from-center', fromCenter)
    card.style.setProperty('--pointer-from-top', percentY / 100)
    card.style.setProperty('--pointer-from-left', percentX / 100)
  }

  const handleCardMouseLeave = (e) => {
    const card = e.currentTarget
    card.style.setProperty('--pointer-x', '50%')
    card.style.setProperty('--pointer-y', '50%')
    card.style.setProperty('--rotate-x', '0deg')
    card.style.setProperty('--rotate-y', '0deg')
    card.style.setProperty('--background-x', '50%')
    card.style.setProperty('--background-y', '50%')
    card.style.setProperty('--pointer-from-center', '0')
    card.style.setProperty('--pointer-from-top', '0.5')
    card.style.setProperty('--pointer-from-left', '0.5')
  }

  const loopTexts = [
    'Curated to your skills.',
    'Optimized for hiring managers.',
    'Practice until you ace it.',
    'Private, secure, and bias-aware.'
  ]

  const testimonials = [
    {
      quote: "ZedReq helped me find the right role in two weeks — perfect fit and smooth process.",
      author: "— Ayesha K., Data Analyst"
    },
    {
      quote: "The mock interviews made all the difference; the feedback was actionable and specific.",
      author: "— Bilal R., Software Engineer"
    },
    {
      quote: "AI-powered matching saved me hours of searching — precise recommendations every time.",
      author: "— Sarah M., Product Manager"
    }
  ]

  const trustFaqs = [
    {
      question: 'How is my interview data stored?',
      answer: 'Interview recordings and transcripts are encrypted in transit and at rest. Access is tightly controlled with role-based permissions and audit logs for every critical action.'
    },
    {
      question: 'Does ZedReq sell my data?',
      answer: 'No. ZedReq does not sell personal data. Your information is used only to deliver platform features like matching, coaching, and analytics that you explicitly use.'
    },
    {
      question: 'How does bias detection work?',
      answer: 'Our scoring pipelines are continuously monitored with fairness checks across demographic and experience segments. Detected drifts are flagged for review and model adjustments.'
    },
    {
      question: 'Can I permanently delete my data?',
      answer: 'Yes. You can request permanent deletion of account data. Deletion workflows remove profile, activity, and related artifacts according to platform retention policy.'
    },
    {
      question: 'Who can access my profile?',
      answer: 'Profile visibility follows your privacy settings and platform permissions. Sensitive data remains protected and is not exposed to unauthorized users or systems.'
    }
  ]

  useEffect(() => {
    const loopInterval = setInterval(() => {
      setActiveLoop((prev) => (prev + 1) % loopTexts.length)
    }, 2000)

    return () => clearInterval(loopInterval)
  }, [])

  useEffect(() => {
    const testimonialInterval = setInterval(() => {
      setActiveTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)

    return () => clearInterval(testimonialInterval)
  }, [])

  useEffect(() => {
    const section = trustSectionRef.current
    if (!section) return undefined

    let counterInterval
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return

          let current = 0
          counterInterval = setInterval(() => {
            current += 2
            if (current >= 94) {
              current = 94
              clearInterval(counterInterval)
            }
            setMatchPercent(current)
          }, 30)

          observer.unobserve(entry.target)
        })
      },
      { threshold: 0.25 }
    )

    observer.observe(section)

    return () => {
      if (counterInterval) clearInterval(counterInterval)
      observer.disconnect()
    }
  }, [])

  // Scroll-triggered fade-in animation
  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -40px 0px'
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          observer.unobserve(entry.target)
        }
      })
    }, observerOptions)

    // Observe all elements with scroll-reveal, scroll-reveal-left, scroll-reveal-right, scroll-reveal-scale classes
    const elements = document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right, .scroll-reveal-scale')
    elements.forEach((el) => observer.observe(el))

    return () => {
      elements.forEach((el) => observer.unobserve(el))
    }
  }, [])



  return (
    <div className="first-page-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-background">
          <DarkVeil 
            hueShift={399}
            noiseIntensity={0.0}
            scanlineIntensity={0.2}
            speed={0.8}
            scanlineFrequency={0.0}
            warpAmount={1.0}
            resolutionScale={1.0}
          />
        </div>
        <div className="hero-watermark">ZedReq</div>
        <div className="hero-content">
          <div className="logo-container">
            <h1 className="main-logo">
              <span className="typewriter-text">ZedReq</span>
            </h1>
          </div>
          <h2 className="hero-headline">Find the role that fits you — faster, smarter, with AI.</h2>
          <p className="hero-subheadline">AI job matching • Intelligent career assistant • Realistic mock interviews</p>
          <div className="hero-cta">
            <Link to="/landing" className="btn-primary">Get Matched — It's Free</Link>
            <button 
              onClick={() => setShowReserveModal(true)} 
              className="btn-secondary"
            >
              Reserve A Seat
            </button>
          </div>
          <p className="hero-microcopy">No résumé required — AI builds a smart profile in minutes.</p>
          
          {/* Text Loop */}
          <div className="text-loop">
            {loopTexts.map((text, index) => (
              <p key={index} className={`loop-item ${activeLoop === index ? 'active' : ''}`}>
                {text}
              </p>
            ))}
          </div>
        </div>
      </section>

      {/* Showcase Sections */}
      {/* Feature Cards */}
      <section className="features-section-cardswap">
        <div className="features-content-wrapper">
          <div className="features-text-section scroll-reveal">
            <h2 className="features-title">Powerful Features to Accelerate Your Career</h2>
            <p className="features-description">
              Our AI-powered platform provides comprehensive tools and assistance to help you navigate every step of your career journey—from finding the perfect role to acing your interviews.
            </p>
            <div className="features-highlights">
              <div className="highlight-item scroll-reveal">
                <span className="highlight-number">01</span>
                <p>Intelligent matching algorithm connects you with opportunities that truly fit</p>
              </div>
              <div className="highlight-item scroll-reveal">
                <span className="highlight-number">02</span>
                <p>Personalized coaching adapts to your unique career goals and experience</p>
              </div>
              <div className="highlight-item scroll-reveal">
                <span className="highlight-number">03</span>
                <p>Practice and prepare with realistic mock interviews and actionable feedback</p>
              </div>
            </div>
          </div>
          
          <div className="features-cards-section scroll-reveal">
            <CardSwap
              width={400}
              height={500}
              cardDistance={65}
              verticalDistance={85}
              delay={3500}
              skewAmount={9}
              pauseOnHover={true}
            >
              <Card>
                <div className="feature-card-content">
                  <div className="feature-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
                      <circle cx="7" cy="7" r="1.5"/>
                    </svg>
                  </div>
                  <h3>AI Job Matching</h3>
                  <p className="feature-one-liner">Precision matches based on skills, goals, and culture fit.</p>
                  <ul className="feature-bullets">
                    <li>Smart skill parsing from CVs and profiles</li>
                    <li>Role-fit score and interview readiness indicator</li>
                    <li>Curated shortlists — apply faster</li>
                  </ul>
                  <a href="#" className="feature-cta">See Matches</a>
                </div>
              </Card>
              
              <Card>
                <div className="feature-card-content">
                  <div className="feature-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                      <path d="M13 8H7"/>
                      <path d="M17 12H7"/>
                      <circle cx="18" cy="5" r="3"/>
                      <path d="M16 3v4M20 3v4M18 1v2M18 7v2"/>
                    </svg>
                  </div>
                  <h3>AI Career Assistant</h3>
                  <p className="feature-one-liner">Personalized coaching for résumés, cover letters, and applications.</p>
                  <ul className="feature-bullets">
                    <li>Interactive profile refinement</li>
                    <li>Custom application templates & ATS-friendly output</li>
                    <li>Instant answers to career queries</li>
                  </ul>
                  <a href="#" className="feature-cta">Talk to Assistant</a>
                </div>
              </Card>
              
              <Card>
                <div className="feature-card-content">
                  <div className="feature-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                      <line x1="12" y1="19" x2="12" y2="23"/>
                      <line x1="8" y1="23" x2="16" y2="23"/>
                    </svg>
                  </div>
                  <h3>AI Mock Interviews</h3>
                  <p className="feature-one-liner">Practice with dynamic interviews and receive structured feedback.</p>
                  <ul className="feature-bullets">
                    <li>Role-specific question sets</li>
                    <li>Real-time scoring and tips</li>
                    <li>Playback + transcript for review</li>
                  </ul>
                  <a href="#" className="feature-cta">Start a Mock Interview</a>
                </div>
              </Card>
            </CardSwap>
          </div>
        </div>
      </section>

      {/* SHOWCASE TIMELINE — images change as you scroll through features */}
      <Timeline data={[
        {
          title: "AI Career Assistant",
          content: (
            <div className="timeline-content">
              <span className="timeline-label">Career Assistant</span>
              <h4>Your personal AI career copilot</h4>
              <p>
                Search jobs, discover profiles, optimize your resume, and get instant answers
                to any career question — all through a natural conversation.
              </p>
              <ul className="timeline-features">
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  Natural language job and profile search
                </li>
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  Interactive profile refinement and ATS-ready output
                </li>
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  Instant, context-aware career guidance
                </li>
              </ul>
              <div className="timeline-image-grid">
                <img className="timeline-image" src="/static/Ai mode Ai assistant.png" alt="AI Career Assistant interface showing chat, profile matching, and job search" />
              </div>
            </div>
          ),
        },
        {
          title: "Mock Interviews",
          content: (
            <div className="timeline-content">
              <span className="timeline-label">Mock Interviews</span>
              <h4>Practice until you&apos;re unstoppable</h4>
              <p>
                Face realistic, AI-powered video interviews tailored to your target roles.
                Receive detailed scoring, strengths analysis, and coaching feedback.
              </p>
              <ul className="timeline-features">
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  Role-specific question sets with dynamic difficulty
                </li>
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  Real-time scoring across technical &amp; communication
                </li>
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  AI coaching feedback with actionable next steps
                </li>
              </ul>
              <div className="timeline-image-grid">
                <img className="timeline-image" src="/static/AI mock interview.png" alt="AI Mock Interview platform with video interface, recommended jobs, and skills analysis" />
              </div>
            </div>
          ),
        },
        {
          title: "Adaptive Learning",
          content: (
            <div className="timeline-content">
              <span className="timeline-label">Adaptive Learning</span>
              <h4>Learn exactly what matters for your career</h4>
              <p>
                Our intelligent LMS analyzes your interactions — job views, post likes,
                profile activity — and generates personalized courses to close your skill gaps.
              </p>
              <ul className="timeline-features">
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  AI-generated courses from your career context
                </li>
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  Domain and weekly performance tracking
                </li>
                <li>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  Web-sourced knowledge base for up-to-date content
                </li>
              </ul>
              <div className="timeline-image-grid">
                <img className="timeline-image" src="/static/AI powered LMS.png" alt="AI-Powered Learning Management System with courses, performance tracking, and analytics" />
              </div>
            </div>
          ),
        },
      ]} />

      {/* Skill Gap Heatmap & Network Expansion (Combined) */}
      <CombinedSkillGapAndNetwork />

      {/* Job Discovery & Hiring Flow */}
      <JobDiscoveryFlow />

      {/* Trust and Privacy */}
      <section className="trust-section scroll-reveal" ref={trustSectionRef} aria-labelledby="trust-title">
        <div className="trust-grid-overlay" />
        <div className="trust-particles" />
        <div className="trust-container">
          <header className="trust-header scroll-reveal">
            <h2 id="trust-title">Your Data. Your Career. Fully Protected.</h2>
            <p>Built with enterprise-grade security, privacy-first architecture, and bias-aware AI systems.</p>
            <div className="trust-divider" />
          </header>

          <div className="trust-cards-grid">
            <article className="trust-card scroll-reveal-scale">
              <div className="trust-card-head">
                <div className="trust-icon-wrap" aria-hidden="true">
                  <svg viewBox="0 0 24 24" role="img" aria-label="End-to-end encryption icon">
                    <path d="M12 2l7 3v6c0 5-3.2 8.7-7 10-3.8-1.3-7-5-7-10V5l7-3z" />
                    <rect x="9" y="11" width="6" height="5" rx="1" />
                    <path d="M10 11V9a2 2 0 1 1 4 0v2" />
                  </svg>
                </div>
                <h3>End-to-End Encryption</h3>
              </div>
              <p>All personal data, conversations, and interview recordings are encrypted in transit and at rest using modern cryptographic standards.</p>
              <div className="trust-micro trust-micro-encryption" aria-hidden="true">
                <span className="trust-node">User</span>
                <span className="trust-link" />
                <span className="trust-lock-core" />
                <span className="trust-link" />
                <span className="trust-node">DB</span>
              </div>
            </article>

            <article className="trust-card scroll-reveal-scale">
              <div className="trust-card-head">
                <div className="trust-icon-wrap" aria-hidden="true">
                  <svg viewBox="0 0 24 24" role="img" aria-label="Smart recommendations icon">
                    <circle cx="12" cy="8" r="3.5" />
                    <path d="M5 20c1.5-4 4.2-6 7-6s5.5 2 7 6" />
                    <path d="M17 8l2 2-2 2" />
                    <path d="M19 10h-4" />
                  </svg>
                </div>
                <h3>Smart Recommendations</h3>
              </div>
              <p>AI-driven suggestions tailored to your profile, skills, and activity history — so every match gets more accurate over time.</p>
              <div className="trust-micro trust-micro-anon" aria-hidden="true">
                <div className="trust-profile-card trust-profile-faded">
                  <span className="trust-line short" />
                  <span className="trust-line" />
                  <span className="trust-line short" />
                </div>
                <div className="trust-profile-link" />
                <div className="trust-profile-card trust-profile-skill">
                  <span className="trust-line active" />
                  <span className="trust-line active short" />
                  <span className="trust-line active" />
                </div>
                <div className="trust-counter">{matchPercent}% match</div>
              </div>
            </article>

            <article className="trust-card scroll-reveal-scale">
              <div className="trust-card-head">
                <div className="trust-icon-wrap" aria-hidden="true">
                  <svg viewBox="0 0 24 24" role="img" aria-label="Bias-aware AI systems icon">
                    <path d="M12 4v16" />
                    <path d="M5 7h14" />
                    <path d="M7 7l-2 5h4l-2-5z" />
                    <path d="M17 7l-2 5h4l-2-5z" />
                    <circle cx="12" cy="16.5" r="2.2" />
                  </svg>
                </div>
                <h3>Bias-Aware AI Systems</h3>
              </div>
              <p>Our AI models are continuously evaluated to ensure balanced scoring and fairness across diverse candidate backgrounds.</p>
              <div className="trust-micro trust-micro-fairness" aria-hidden="true">
                <div className="trust-radar">
                  <span className="ring ring-1" />
                  <span className="ring ring-2" />
                  <span className="ring ring-3" />
                  <span className="radar-fill" />
                </div>
                <span className="trust-fairness-badge">Fairness Check</span>
              </div>
            </article>
          </div>

          <div className="trust-badge-row scroll-reveal">
            <div className="trust-badge-item scroll-reveal">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h14v16H5z" /><path d="M8 8h8M8 12h8M8 16h5" /></svg>
              <span>GDPR-ready architecture</span>
            </div>
            <div className="trust-badge-item scroll-reveal">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 19h12M8 19V9l4-4 4 4v10" /></svg>
              <span>Secure cloud infrastructure</span>
            </div>
            <div className="trust-badge-item scroll-reveal">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 18h16M7 14l3-3 2 2 5-5" /></svg>
              <span>Transparent AI scoring</span>
            </div>
            <div className="trust-badge-item scroll-reveal">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6h12M6 12h8M6 18h10" /></svg>
              <span>Data minimization policy</span>
            </div>
            <div className="trust-badge-item scroll-reveal">
              <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="8" r="3" /><circle cx="16" cy="16" r="3" /><path d="M10.5 10.5l3 3" /></svg>
              <span>Human-in-the-loop validation</span>
            </div>
          </div>

          <div className="trust-faq scroll-reveal">
            {trustFaqs.map((faq, index) => (
              <div key={faq.question} className={`trust-faq-item ${activeTrustFaq === index ? 'open' : ''}`}>
                <button
                  id={`trust-faq-button-${index}`}
                  className="trust-faq-trigger"
                  aria-expanded={activeTrustFaq === index}
                  aria-controls={`trust-faq-panel-${index}`}
                  onClick={() => setActiveTrustFaq(index)}
                >
                  <span>{faq.question}</span>
                  <span className="trust-faq-chevron" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" /></svg>
                  </span>
                </button>
                <div
                  id={`trust-faq-panel-${index}`}
                  role="region"
                  aria-labelledby={`trust-faq-button-${index}`}
                  className="trust-faq-panel"
                >
                  <p>{faq.answer}</p>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* Testimonials */}
      <section className="testimonials-section">
        <h2 className="section-title scroll-reveal">What Candidates Say</h2>
        <div className="testimonials-carousel scroll-reveal">
          {testimonials.map((testimonial, index) => (
            <div key={index} className={`testimonial-card ${activeTestimonial === index ? 'active' : ''}`}>
              <p className="testimonial-quote">"{testimonial.quote}"</p>
              <p className="testimonial-author">{testimonial.author}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section className="pricing-section" style={{ position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, opacity: 0.6 }}>
          <Beams
            beamWidth={1.5}
            beamHeight={25}
            beamNumber={40}
            speed={3.1}
            noiseIntensity={2.4}
            scale={0.29}
            rotation={45}
            lightColor="#00b4d8"
          />
        </div>
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(13, 13, 13, 0.3)', zIndex: 1, pointerEvents: 'none' }} />
        <div style={{ position: 'relative', zIndex: 2 }}>
          <h2 className="section-title scroll-reveal">Simple, Transparent Pricing</h2>
          <p className="pricing-subtitle scroll-reveal">Start free. Upgrade when you're ready. Every plan includes our core AI engine.</p>
          <div className="pricing-grid">

            {/* Starter Plan */}
            <div className="pricing-card scroll-reveal-scale">
              <div className="pricing-card-header">
                <h3>Starter</h3>
                <p className="pricing-card-desc">Perfect for exploring the platform and getting your AI profile set up.</p>
              </div>
              <div className="price">
                $0<span className="price-period">/month</span>
              </div>
              <Link to="/landing" className="btn-primary pricing-btn">Get Started Free</Link>
              <div className="pricing-divider"></div>
              <ul className="pricing-features">
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  AI-generated smart profile
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Basic job matching (up to 10/week)
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  3 mock interviews per month
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Career assistant chat (limited)
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Community support
                </li>
                <li className="pricing-feature-item excluded">
                  <span className="pricing-x">✕</span>
                  Priority job matches
                </li>
                <li className="pricing-feature-item excluded">
                  <span className="pricing-x">✕</span>
                  Advanced analytics & reports
                </li>
                <li className="pricing-feature-item excluded">
                  <span className="pricing-x">✕</span>
                  Resume & cover letter builder
                </li>
              </ul>
            </div>

            {/* Pro Plan */}
            <div className="pricing-card featured scroll-reveal-scale">
              <span className="badge">Most Popular</span>
              <div className="pricing-card-header">
                <h3>Pro</h3>
                <p className="pricing-card-desc">Everything you need to land your dream role — faster and smarter.</p>
              </div>
              <div className="price">
                $9<span className="price-period">.99/month</span>
              </div>
              <a href="#" className="btn-primary pricing-btn">Upgrade to Pro</a>
              <div className="pricing-divider"></div>
              <p className="pricing-includes">Everything in Starter, plus:</p>
              <ul className="pricing-features">
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Unlimited AI job matching
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Unlimited mock interviews with AI feedback
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Personalized career coaching sessions
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Priority matching & shortlists
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Interview playback & transcript review
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  AI resume & cover letter builder
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Performance analytics dashboard
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Access to all AI agents (Zed, Riz, Seez & more)
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Priority email support
                </li>
              </ul>
            </div>

            {/* Enterprise Plan */}
            <div className="pricing-card scroll-reveal-scale">
              <div className="pricing-card-header">
                <h3>Enterprise</h3>
                <p className="pricing-card-desc">For teams and organizations that need scale, security, and control.</p>
              </div>
              <div className="price">
                Custom
              </div>
              <a href="#" className="btn-secondary pricing-btn">Contact Sales</a>
              <div className="pricing-divider"></div>
              <p className="pricing-includes">Everything in Pro, plus:</p>
              <ul className="pricing-features">
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Bulk candidate screening & ranking
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Custom AI agent configuration
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Team management dashboard
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  SSO & advanced privacy controls
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Custom API integrations
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Dedicated account manager
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  SLA & uptime guarantee
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  On-premise deployment option
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  White-label & branding
                </li>
              </ul>
            </div>

          </div>
          <p className="pricing-note scroll-reveal">All plans include 256-bit encryption, GDPR compliance, and 99.9% uptime. Cancel anytime.</p>
        </div>
      </section>

      {/* CTA Band */}
      <section className="cta-band scroll-reveal">
        <div className="cta-content">
          <h2 className="scroll-reveal">Ready to level up your career?</h2>
          <p className="scroll-reveal">Create your AI profile in minutes — get matched today.</p>
          <div className="cta-buttons scroll-reveal">
            <Link to="/landing" className="btn-primary large">Create Free Profile</Link>
          </div>
        </div>
      </section>

      {/* Reserve Seat Modal */}
      <ReserveSeatModal 
        isOpen={showReserveModal}
        onClose={() => setShowReserveModal(false)}
      />

      {/* Footer */}
      <footer className="footer scroll-reveal">
        <div className="footer-content">
          <div className="footer-section scroll-reveal">
            <h4>Product</h4>
            <ul>
              <li><a href="#">Features</a></li>
              <li><a href="#">Pricing</a></li>
            </ul>
          </div>
          <div className="footer-section scroll-reveal">
            <h4>Company</h4>
            <ul>
              <li><a href="#">About</a></li>
              <li><a href="#">Careers</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
          <div className="footer-section scroll-reveal">
            <h4>Resources</h4>
            <ul>
              <li><a href="#">Blog</a></li>
              <li><a href="#">Help Center</a></li>
              <li><a href="#">Privacy Policy</a></li>
            </ul>
          </div>
          <div className="footer-section scroll-reveal">
            <h4>Legal</h4>
            <ul>
              <li><a href="#">Terms of Service</a></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom scroll-reveal">
          <p>&copy; 2024 ZedReq — All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default FirstPage
