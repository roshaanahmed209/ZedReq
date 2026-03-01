import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import DarkVeil from '../components/DarkVeil'
import Beams from '../components/Beams'
import CardSwap, { Card } from '../components/CardSwap'
import ReserveSeatModal from '../components/ReserveSeatModal'
import '../css/pages/FirstPage.css'

const FirstPage = () => {
  const [activeLoop, setActiveLoop] = useState(0)
  const [activeTestimonial, setActiveTestimonial] = useState(0)
  const [showReserveModal, setShowReserveModal] = useState(false)

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

  // Scroll-triggered fade-in animation
  useEffect(() => {
    const observerOptions = {
      threshold: 0.15,
      rootMargin: '0px 0px -50px 0px'
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          
          observer.unobserve(entry.target)
        }
      })
    }, observerOptions)

    // Observe all elements with scroll-reveal class
    const elements = document.querySelectorAll('.scroll-reveal')
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
      {/* SHOWCASE 1: JOB MATCHING */}
      <section className="showcase">
        <div className="container">
          <div className="showcase-visual reveal scroll-reveal">
            <div className="showcase-glow"></div>
            <div className="showcase-image">
              <img src="/static/ai_matching.png" alt="AI Matching: Neural network connecting resumes to job opportunities" />
            </div>
          </div>
          <div className="showcase-text reveal reveal-delay-1 scroll-reveal">
            <span className="section-label">Smart Matching</span>
            <h2>AI that truly understands your career DNA</h2>
            <p>Our vector-powered engine doesn't just keyword-match — it understands your skills, ambitions, and work preferences to surface roles you'd actually love.</p>
            <div className="showcase-points">
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Smart skill parsing from profiles and resumes</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Role-fit scoring with interview readiness indicator</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Curated shortlists — apply faster, with confidence</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SHOWCASE 2: CAREER ASSISTANT */}
      <section className="showcase reverse">
        <div className="container">
          <div className="showcase-visual reveal scroll-reveal">
            <div className="showcase-glow"></div>
            <div className="showcase-image showcase-image-large">
              <img src="/static/Ai mode Ai assistant.png" alt="AI Career Assistant interface showing chat, profile matching, and job search" />
            </div>
          </div>
          <div className="showcase-text reveal reveal-delay-1 scroll-reveal">
            <span className="section-label">Career Assistant</span>
            <h2>Your personal AI career copilot</h2>
            <p>Search jobs, discover profiles, optimize your resume, and get instant answers to any career question — all through a natural conversation.</p>
            <div className="showcase-points">
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Natural language job and profile search</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Interactive profile refinement and ATS-ready output</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Instant, context-aware career guidance</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SHOWCASE 3: MOCK INTERVIEWS */}
      <section className="showcase">
        <div className="container">
          <div className="showcase-visual reveal scroll-reveal">
            <div className="showcase-glow"></div>
            <div className="showcase-image">
              <img src="/static/AI mock interview.png" alt="AI Mock Interview platform with video interface, recommended jobs, and skills analysis" />
            </div>
          </div>
          <div className="showcase-text reveal reveal-delay-1 scroll-reveal">
            <span className="section-label">Mock Interviews</span>
            <h2>Practice until you're unstoppable</h2>
            <p>Face realistic, AI-powered video interviews tailored to your target roles. Receive detailed scoring, strengths analysis, and coaching feedback.</p>
            <div className="showcase-points">
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Role-specific question sets with dynamic difficulty</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Real-time scoring across technical & communication</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>AI coaching feedback with actionable next steps</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SHOWCASE 4: LEARNING */}
      <section className="showcase reverse">
        <div className="container">
          <div className="showcase-visual reveal scroll-reveal">
            <div className="showcase-glow"></div>
            <div className="showcase-image showcase-image-large">
              <img src="/static/AI powered LMS.png" alt="AI-Powered Learning Management System with courses, performance tracking, and analytics" />
            </div>
          </div>
          <div className="showcase-text reveal reveal-delay-1 scroll-reveal">
            <span className="section-label">Adaptive Learning</span>
            <h2>Learn exactly what matters for your career</h2>
            <p>Our intelligent LMS analyzes your interactions — job views, post likes, profile activity — and generates personalized courses to close your skill gaps.</p>
            <div className="showcase-points">
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>AI-generated courses from your career context</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Domain and weekly performance tracking</span>
              </div>
              <div className="showcase-point">
                <span className="showcase-point-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </span>
                <span>Web-sourced knowledge base for up-to-date content</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="features-section-cardswap">
        <div className="features-content-wrapper">
          <div className="features-text-section scroll-reveal">
            <h2 className="features-title">Powerful Features to Accelerate Your Career</h2>
            <p className="features-description">
              Our AI-powered platform provides comprehensive tools and assistance to help you navigate every step of your career journey—from finding the perfect role to acing your interviews.
            </p>
            <div className="features-highlights">
              <div className="highlight-item">
                <span className="highlight-number">01</span>
                <p>Intelligent matching algorithm connects you with opportunities that truly fit</p>
              </div>
              <div className="highlight-item">
                <span className="highlight-number">02</span>
                <p>Personalized coaching adapts to your unique career goals and experience</p>
              </div>
              <div className="highlight-item">
                <span className="highlight-number">03</span>
                <p>Practice and prepare with realistic mock interviews and actionable feedback</p>
              </div>
            </div>
          </div>
          
          <div className="features-cards-section">
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
          <div className="pricing-grid">
            <div className="pricing-card scroll-reveal">
              <h3>Starter</h3>
              <div className="price">Free</div>
              <p>Personal profile, basic matching, limited mock interviews.</p>
              <Link to="/landing" className="btn-primary">Create Free Account</Link>
            </div>
            <div className="pricing-card featured scroll-reveal">
              <span className="badge">Most Popular</span>
              <h3>Pro</h3>
              <div className="price">For job seekers</div>
              <p>Unlimited mock interviews, personalized coaching, priority matches.</p>
              <a href="#" className="btn-primary">Upgrade to Pro</a>
            </div>
            <div className="pricing-card scroll-reveal">
              <h3>Enterprise</h3>
              <div className="price">For teams</div>
              <p>Custom integrations, bulk screening, privacy controls.</p>
              <a href="#" className="btn-secondary">Contact Sales</a>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Band */}
      <section className="cta-band scroll-reveal">
        <div className="cta-content">
          <h2>Ready to level up your career?</h2>
          <p>Create your AI profile in minutes — get matched today.</p>
          <div className="cta-buttons">
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
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>Product</h4>
            <ul>
              <li><a href="#">Features</a></li>
              <li><a href="#">Pricing</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Company</h4>
            <ul>
              <li><a href="#">About</a></li>
              <li><a href="#">Careers</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Resources</h4>
            <ul>
              <li><a href="#">Blog</a></li>
              <li><a href="#">Help Center</a></li>
              <li><a href="#">Privacy Policy</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><a href="#">Terms of Service</a></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 ZedReq — All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default FirstPage
