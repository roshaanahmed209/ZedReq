import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import '../css/pages/GetStarted.css'

const SLIDE_IMAGES = [
  { src: '/static/slide1.jpg', alt: 'Career growth' },
  { src: '/static/slide2.jpg', alt: 'Professional development' },
  { src: '/static/slide3.png', alt: 'Networking' },
  { src: '/static/networkinggg.jpg', alt: 'Professional networking' }
]

const GetStarted = () => {
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [privacyAccepted, setPrivacyAccepted] = useState(false)
  const [showTermsModal, setShowTermsModal] = useState(false)
  const [showPrivacyModal, setShowPrivacyModal] = useState(false)
  const [slideIndex, setSlideIndex] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    const interval = setInterval(() => {
      setSlideIndex((prev) => (prev + 1) % SLIDE_IMAGES.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const canProceed = termsAccepted && privacyAccepted

  const handleGetStarted = (e) => {
    if (!canProceed) {
      e.preventDefault()
      return
    }
    navigate('/landing')
  }

  return (
    <div className="get-started-page">
      <div className="get-started-bg" />

      <div className="get-started-layout">
        <div className="get-started-left-panel">
          {SLIDE_IMAGES.map((slide, i) => (
            <img
              key={slide.src}
              src={slide.src}
              alt={slide.alt}
              className={`get-started-panel-image get-started-slide ${i === slideIndex ? 'get-started-slide-active' : ''}`}
            />
          ))}
        </div>
        <div className="get-started-right-panel">
          <div className="get-started-content">
        <h1 className="get-started-title">
          <span className="get-started-title-line">Start your</span>
          <span className="get-started-title-accent"> career journey</span>
        </h1>
        <p className="get-started-subtitle">
          One step away from smarter job matching and AI-powered growth.
        </p>

        <div className="get-started-card">
          <div className="get-started-checkboxes">
            <label className="get-started-checkbox-label">
              <input
                type="checkbox"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="get-started-checkbox"
              />
              <span className="get-started-checkbox-custom" />
              <span className="get-started-checkbox-text">
                I agree to the{' '}
                <button
                  type="button"
                  className="get-started-link get-started-link-btn"
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); setShowTermsModal(true); }}
                >
                  Terms and Conditions
                </button>
              </span>
            </label>
            <label className="get-started-checkbox-label">
              <input
                type="checkbox"
                checked={privacyAccepted}
                onChange={(e) => setPrivacyAccepted(e.target.checked)}
                className="get-started-checkbox"
              />
              <span className="get-started-checkbox-custom" />
              <span className="get-started-checkbox-text">
                I agree to the{' '}
                <button
                  type="button"
                  className="get-started-link get-started-link-btn"
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); setShowPrivacyModal(true); }}
                >
                  Privacy Policy
                </button>
              </span>
            </label>
          </div>

          <button
            type="button"
            className={`get-started-btn ${canProceed ? 'get-started-btn-active' : ''}`}
            onClick={handleGetStarted}
            disabled={!canProceed}
          >
            Get Started
          </button>
        </div>

        <Link to="/" className="get-started-back">← Back to home</Link>
          </div>
        </div>
      </div>

      {/* Terms and Conditions Modal */}
      {showTermsModal && (
        <div className="get-started-modal-overlay" onClick={() => setShowTermsModal(false)}>
          <div className="get-started-modal" onClick={(e) => e.stopPropagation()}>
            <div className="get-started-modal-header">
              <h2 className="get-started-modal-title">Terms and Conditions</h2>
              <button type="button" className="get-started-modal-close" onClick={() => setShowTermsModal(false)} aria-label="Close">×</button>
            </div>
            <div className="get-started-modal-body">
              <p className="get-started-modal-updated"><strong>Last Updated:</strong> February 2026</p>
              <p>Welcome to <strong>ZedReq</strong> (&quot;Platform&quot;, &quot;Service&quot;, &quot;we&quot;, &quot;our&quot;, &quot;us&quot;). These Terms and Conditions (&quot;Terms&quot;) govern your access to and use of the ZedReq website, applications, and services. By accessing or using ZedReq, you agree to be bound by these Terms. If you do not agree, you must not use the Platform.</p>

              <h3>1. Eligibility</h3>
              <p>You must be at least <strong>16 years old</strong> (or the minimum legal age in your jurisdiction) to use ZedReq. By using the Platform, you represent that you meet this requirement and have the legal capacity to enter into these Terms.</p>

              <h3>2. Account Registration</h3>
              <ul>
                <li>You must provide accurate, current, and complete information during registration.</li>
                <li>You are responsible for maintaining the confidentiality of your login credentials.</li>
                <li>You are responsible for all activity occurring under your account.</li>
                <li>We reserve the right to suspend or terminate accounts that violate these Terms.</li>
              </ul>

              <h3>3. Platform Description</h3>
              <p>ZedReq is an <strong>AI-powered career SaaS platform</strong> offering professional networking, job matching, learning tools, AI career assistance, mock interviews, and related services. ZedReq does <strong>not</strong> guarantee employment, job offers, or interview outcomes.</p>

              <h3>4. User Content</h3>
              <p>&quot;User Content&quot; includes profile data, posts, messages, resumes, media, and any information you submit.</p>
              <p>You agree that:</p>
              <ul>
                <li>You own or have rights to all User Content you submit.</li>
                <li>Your content does not violate any laws or third‑party rights.</li>
                <li>You grant ZedReq a <strong>non‑exclusive, worldwide, royalty‑free license</strong> to host, store, process, and display User Content solely for operating and improving the Platform.</li>
              </ul>
              <p>We reserve the right to remove content that violates these Terms.</p>

              <h4>Personalization and use of your Platform data</h4>
              <p>
                By accepting these Terms, you acknowledge and agree that ZedReq may use <strong>information and data that you provide, submit, or generate through the Platform</strong> (including profile fields, documents and media you upload, messages and posts you create, and your in‑app interactions and preferences) to operate, improve, secure, and <strong>personalize</strong> the Service—such as job matching, recommendations, career tools, AI‑assisted features, and other experiences tailored to you—so that the Platform is more useful and relevant for your needs.
              </p>
              <p>
                For personalization and tailoring as described above, ZedReq relies on <strong>the details and information you enter, upload, or otherwise supply through the Platform</strong>, together with <strong>activity that occurs within the Service</strong> in direct connection with that information (for example, how you use features you have chosen to engage with). We <strong>do not access or use personal data from unrelated sources</strong>—such as data stored elsewhere on your device, other applications, or external accounts—except where you <strong>explicitly connect</strong> a third‑party integration or where <strong>minimal technical processing</strong> is strictly necessary to deliver, secure, or maintain the Platform, as further explained in our <strong>Privacy Policy</strong>. Nothing in this section limits non‑waivable rights under applicable law or the disclosures in the Privacy Policy.
              </p>

              <h3>5. Prohibited Conduct</h3>
              <p>You agree <strong>not</strong> to:</p>
              <ul>
                <li>Impersonate another person or entity.</li>
                <li>Post misleading, fraudulent, or false information.</li>
                <li>Harass, abuse, or harm other users.</li>
                <li>Upload malicious code, spam, or automated scripts.</li>
                <li>Attempt unauthorized access to systems or data.</li>
                <li>Scrape, reverse engineer, or exploit the Platform.</li>
              </ul>

              <h3>6. AI‑Generated Content Disclaimer</h3>
              <p>ZedReq uses artificial intelligence to provide recommendations, career advice, evaluations, and interview simulations.</p>
              <ul>
                <li>AI outputs are <strong>informational only</strong> and not professional advice.</li>
                <li>We do not guarantee accuracy, completeness, or suitability.</li>
                <li>Users remain solely responsible for decisions made based on AI outputs.</li>
              </ul>

              <h3>7. Payments & Subscriptions</h3>
              <ul>
                <li>Some features may require payment or subscription.</li>
                <li>Payments are processed through third‑party providers.</li>
                <li>ZedReq <strong>does not store credit card details</strong>.</li>
                <li>Trial access may be modified or terminated at our discretion.</li>
              </ul>
              <h4>Refund policy</h4>
              <p>
                Except where applicable law requires otherwise, <strong>all fees, charges, and subscription payments are final and non‑refundable</strong>. ZedReq does not provide refunds, credits, charge reversals, or prorated amounts for partial billing periods, unused or partially used features, voluntary account closure, termination of access (whether by you or by us), or dissatisfaction with the Service. By completing a purchase, you acknowledge that you have reviewed the applicable pricing and features and accept that you are not entitled to a refund except as expressly stated at the point of sale or in a separate written agreement with ZedReq. Nothing in this section limits any non‑waivable rights you may have under mandatory consumer protection laws in your jurisdiction.
              </p>

              <h3>8. Third‑Party Services</h3>
              <p>ZedReq may integrate with third‑party tools (payment processors, storage providers, AI services).</p>
              <p>We are <strong>not responsible</strong> for third‑party services, content, or policies. Use of third‑party services is subject to their terms.</p>

              <h3>9. Privacy</h3>
              <p>Your use of ZedReq is also governed by our <strong>Privacy Policy</strong>, which explains how we collect, use, and protect your data. By using ZedReq, you consent to data processing as described therein.</p>

              <h3>10. Intellectual Property</h3>
              <ul>
                <li>ZedReq, including all software, designs, algorithms, and branding, is our intellectual property.</li>
                <li>You may not copy, modify, distribute, or create derivative works without permission.</li>
                <li>User content remains owned by the user.</li>
              </ul>

              <h3>11. Account Termination</h3>
              <p>We may suspend or terminate your access:</p>
              <ul>
                <li>For violation of these Terms</li>
                <li>For unlawful or harmful activity</li>
                <li>At our discretion to protect the Platform</li>
              </ul>
              <p>Upon termination, your access rights cease immediately.</p>

              <h3>12. Disclaimer of Warranties</h3>
              <p>ZedReq is provided <strong>&quot;as is&quot;</strong> and <strong>&quot;as available&quot;</strong>.</p>
              <p>We make no warranties regarding:</p>
              <ul>
                <li>Continuous availability</li>
                <li>Accuracy of content</li>
                <li>Job placement or hiring outcomes</li>
              </ul>

              <h3>13. Limitation of Liability</h3>
              <p>To the maximum extent permitted by law:</p>
              <ul>
                <li>ZedReq shall not be liable for indirect, incidental, or consequential damages.</li>
                <li>Our total liability shall not exceed the amount paid by you (if any) in the last 12 months.</li>
              </ul>

              <h3>14. Indemnification</h3>
              <p>You agree to indemnify and hold harmless ZedReq from any claims arising out of:</p>
              <ul>
                <li>Your use of the Platform</li>
                <li>Violation of these Terms</li>
                <li>Infringement of third‑party rights</li>
              </ul>

              <h3>15. Governing Law</h3>
              <p>These Terms are governed by and construed in accordance with applicable laws, without regard to conflict‑of‑law principles.</p>

              <h3>16. Changes to Terms</h3>
              <p>We may update these Terms at any time. Continued use of ZedReq after changes constitutes acceptance of the updated Terms.</p>

              <h3>17. Contact Information</h3>
              <p>For questions regarding these Terms:</p>
              <p><strong>Email:</strong> <a href="mailto:support@zedreq.com" className="get-started-modal-email">support@zedreq.com</a></p>

              <p className="get-started-modal-footer">By using ZedReq, you acknowledge that you have read, understood, and agreed to these Terms and Conditions.</p>
            </div>
          </div>
        </div>
      )}

      {/* Privacy Policy Modal */}
      {showPrivacyModal && (
        <div className="get-started-modal-overlay" onClick={() => setShowPrivacyModal(false)}>
          <div className="get-started-modal" onClick={(e) => e.stopPropagation()}>
            <div className="get-started-modal-header">
              <h2 className="get-started-modal-title">Privacy Policy</h2>
              <button type="button" className="get-started-modal-close" onClick={() => setShowPrivacyModal(false)} aria-label="Close">×</button>
            </div>
            <div className="get-started-modal-body">
              <p className="get-started-modal-updated"><strong>Last Updated:</strong> February 2026</p>
              <p>ZedReq (&quot;we&quot;, &quot;our&quot;, &quot;us&quot;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, store, disclose, and safeguard your information when you use the ZedReq platform, including our website, mobile applications, AI-powered features, and related services (collectively, the &quot;Service&quot;).</p>
              <p>By accessing or using ZedReq, you agree to the practices described in this Privacy Policy.</p>

              <h3>1. Information We Collect</h3>
              <h4>1.1 Information You Provide Directly</h4>
              <p>We may collect the following information when you register, interact with, or use the Service:</p>
              <ul>
                <li>Personal identifiers (name, email address, username)</li>
                <li>Profile information (bio, skills, experience, education, certifications)</li>
                <li>Uploaded content (posts, messages, media, resumes, profile images)</li>
                <li>Payment-related metadata (payment status, subscription type; <strong>we do not store card numbers</strong>)</li>
                <li>Communications with us (support requests, feedback)</li>
              </ul>

              <h4>1.2 Information Collected Automatically</h4>
              <p>When you use ZedReq, we may automatically collect:</p>
              <ul>
                <li>Device and browser information</li>
                <li>IP address and approximate location</li>
                <li>Log data (access times, pages viewed, actions taken)</li>
                <li>Cookies and similar tracking technologies</li>
              </ul>

              <h4>1.3 AI & Interaction Data</h4>
              <p>To provide AI-powered features (career guidance, recommendations, interviews, assessments), we may collect and process:</p>
              <ul>
                <li>User prompts, queries, and interactions with AI features</li>
                <li>AI-generated responses linked to your account</li>
              </ul>
              <p>This data is used <strong>only</strong> to provide, improve, and secure the Service.</p>

              <h3>2. How We Use Your Information</h3>
              <p>We use collected information to:</p>
              <ul>
                <li>Create and manage user accounts</li>
                <li>Provide professional networking and career services</li>
                <li>Deliver AI-powered features and recommendations</li>
                <li>Process subscriptions and payments</li>
                <li>Communicate updates, security alerts, and support messages</li>
                <li>Improve platform performance and user experience</li>
                <li>Detect fraud, abuse, or violations of our Terms</li>
                <li>Comply with legal obligations</li>
              </ul>

              <h3>3. Legal Basis for Processing (GDPR)</h3>
              <p>If you are located in the European Economic Area (EEA), we process your data based on:</p>
              <ul>
                <li>Your consent</li>
                <li>Performance of a contract</li>
                <li>Legitimate business interests</li>
                <li>Legal compliance</li>
              </ul>

              <h3>4. How We Share Your Information</h3>
              <p>We do <strong>not sell</strong> your personal data.</p>
              <p>We may share information only with:</p>
              <ul>
                <li>Service providers (cloud hosting, analytics, payment processors)</li>
                <li>AI technology partners (strictly for service delivery)</li>
                <li>Legal authorities when required by law</li>
                <li>Other users, according to your privacy and visibility settings</li>
              </ul>
              <p>All third parties are contractually obligated to protect your data.</p>

              <h3>5. Data Storage & Security</h3>
              <ul>
                <li>Data is stored on secure servers using industry-standard safeguards</li>
                <li>Media files (images, videos) may be stored on third-party cloud storage</li>
                <li>Access controls, encryption, and monitoring are applied where appropriate</li>
              </ul>
              <p>While we take reasonable measures, no system is 100% secure.</p>

              <h3>6. Data Retention</h3>
              <p>We retain personal data only as long as:</p>
              <ul>
                <li>Your account remains active</li>
                <li>Required to provide services</li>
                <li>Required to comply with legal obligations</li>
              </ul>
              <p>You may request account deletion at any time.</p>

              <h3>7. Your Rights</h3>
              <p>Depending on your location, you may have the right to:</p>
              <ul>
                <li>Access your personal data</li>
                <li>Correct inaccurate information</li>
                <li>Request deletion of your data</li>
                <li>Restrict or object to processing</li>
                <li>Request data portability</li>
                <li>Withdraw consent at any time</li>
              </ul>
              <p>Requests can be submitted via support channels.</p>

              <h3>8. Cookies & Tracking</h3>
              <p>ZedReq uses cookies and similar technologies to:</p>
              <ul>
                <li>Maintain sessions</li>
                <li>Improve performance</li>
                <li>Analyze usage</li>
              </ul>
              <p>You may control cookies through your browser settings.</p>

              <h3>9. Children&apos;s Privacy</h3>
              <p>ZedReq is not intended for individuals under the age of 16. We do not knowingly collect data from children.</p>

              <h3>10. International Data Transfers</h3>
              <p>Your data may be processed in countries outside your residence. We ensure appropriate safeguards are in place for cross-border transfers.</p>

              <h3>11. Changes to This Privacy Policy</h3>
              <p>We may update this Privacy Policy from time to time. Material changes will be communicated through the Service.</p>

              <h3>12. Contact Us</h3>
              <p>If you have questions or concerns about this Privacy Policy, please contact:</p>
              <p><strong>ZedReq Support</strong><br />Email: <a href="mailto:support@zedreq.com" className="get-started-modal-email">support@zedreq.com</a></p>

              <p className="get-started-modal-footer">By using ZedReq, you acknowledge that you have read and understood this Privacy Policy.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GetStarted
