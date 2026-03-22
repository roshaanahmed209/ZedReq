import React from 'react'
import { ZEDREQ_EMAIL, zedreqMailto } from '../config/contact'

/** Shared Privacy Policy body for Get Started modal and /privacy page. */
export function LegalPrivacyBody() {
  return (
    <>
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
      <p><strong>ZedReq Support</strong><br />Email: <a href={zedreqMailto()} className="get-started-modal-email">{ZEDREQ_EMAIL}</a></p>

      <p className="get-started-modal-footer">By using ZedReq, you acknowledge that you have read and understood this Privacy Policy.</p>
    </>
  )
}
