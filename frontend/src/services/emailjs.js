/**
 * EmailJS Service for sending emails from frontend
 * Uses EmailJS client-side SDK with public key
 */
import emailjs from '@emailjs/browser'
import { ZEDREQ_EMAIL } from '../config/contact'

// EmailJS configuration - these should be in .env file
const EMAILJS_SERVICE_ID = import.meta.env.VITE_EMAILJS_SERVICE_ID
const EMAILJS_TEMPLATE_ID = import.meta.env.VITE_EMAILJS_TEMPLATE_ID
const EMAILJS_PUBLIC_KEY = import.meta.env.VITE_EMAILJS_PUBLIC_KEY

// Initialize EmailJS with public key (only once)
let emailjsInitialized = false

function initializeEmailJS() {
  if (!emailjsInitialized && EMAILJS_PUBLIC_KEY) {
    emailjs.init(EMAILJS_PUBLIC_KEY)
    emailjsInitialized = true
  }
}

/**
 * Generate HTML email template for reservation confirmation
 */
function getReservationEmailTemplate(promoCode, websiteLink = 'https://zedreq.ai', companyEmail = ZEDREQ_EMAIL) {
  return `
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; font-size: 16px; background-color: #000000; color: #ffffff; padding: 0; margin: 0;">
  <div style="max-width: 600px; margin: auto; padding: 0;">
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #00B4D8 0%, #0096b8 100%); padding: 40px 20px; text-align: center;">
      <h1 style="margin: 0; color: #ffffff; font-size: 36px; font-weight: 300; letter-spacing: -2px;">ZedReq</h1>
    </div>
    
    <!-- Main Content -->
    <div style="padding: 40px 24px; background-color: #000000;">
      <h2 style="margin: 0 0 20px; color: #ffffff; font-size: 28px; font-weight: 300; line-height: 1.3;">
        Your Seat is Reserved!
      </h2>
      
      <p style="margin: 0 0 24px; color: #cccccc; font-size: 16px; line-height: 1.7;">
        Welcome to the ZedReq family! We're excited to have you on board.
      </p>
      
      <p style="margin: 0 0 24px; color: #cccccc; font-size: 16px; line-height: 1.7;">
        Your seat has been successfully reserved for the Pro Plan, and you're now ready to explore all the great features we offer when we launch.
      </p>
      
      <!-- Promo Code Box -->
      <div style="background: rgba(0, 180, 216, 0.1); border: 2px solid #00B4D8; border-radius: 12px; padding: 24px; margin: 30px 0; text-align: center;">
        <p style="margin: 0 0 12px; color: #999; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; font-weight: 400;">
          Your Reference Code
        </p>
        <p style="margin: 0; color: #00B4D8; font-size: 32px; font-weight: 300; letter-spacing: 3px; font-family: 'Courier New', monospace;">
          ${promoCode}
        </p>
      </div>
      
      <p style="margin: 24px 0; color: #cccccc; font-size: 16px; line-height: 1.7;">
        Save this reference code! When you share it with friends, both you and they will receive a discount on the Pro Plan.
      </p>
      
      <!-- Referral Section -->
      <div style="background: rgba(0, 180, 216, 0.05); border-left: 4px solid #00B4D8; border-radius: 8px; padding: 24px; margin: 30px 0;">
        <h3 style="margin: 0 0 12px; color: #00B4D8; font-size: 20px; font-weight: 400;">
          Share and Save
        </h3>
        <p style="margin: 0; color: #cccccc; font-size: 15px; line-height: 1.7;">
          Share your reference code with friends and colleagues. When they use it to reserve their seat, both you and they will receive a discount on the Pro Plan. It's our way of saying thank you for being part of the ZedReq community!
        </p>
      </div>
      
      <!-- CTA Button -->
      <div style="text-align: center; margin: 30px 0;">
        <a
          style="
            display: inline-block;
            text-decoration: none;
            outline: none;
            color: #ffffff;
            background-color: #00B4D8;
            padding: 14px 32px;
            border-radius: 8px;
            font-weight: 400;
            font-size: 16px;
          "
          href="${websiteLink}"
          target="_blank"
        >
          Visit ZedReq
        </a>
      </div>
      
      <p style="margin: 30px 0 0; color: #999; font-size: 14px; line-height: 1.7;">
        We'll notify you as soon as we're ready to launch. Stay tuned for updates!
      </p>
      
      <p style="margin: 24px 0 0; color: #999; font-size: 14px; line-height: 1.7;">
        If you have any questions or need help, our support team is just an email away at
        <a href="mailto:${companyEmail}" style="text-decoration: none; outline: none; color: #00B4D8;">${companyEmail}</a>.
        We're here to assist you every step of the way!
      </p>
    </div>
    
    <!-- Footer -->
    <div style="padding: 30px 24px; background-color: #0d0d0d; text-align: center; border-top: 1px solid #2a2a2a;">
      <p style="margin: 0 0 12px; color: #666; font-size: 14px;">
        © 2024 ZedReq. All rights reserved.
      </p>
      <p style="margin: 0; color: #666; font-size: 12px;">
        You're receiving this email because you reserved a seat for the Pro Plan at ZedReq.
      </p>
    </div>
  </div>
</div>
  `
}

/**
 * Send reservation confirmation email using EmailJS
 * @param {string} email - Recipient email address
 * @param {string} promoCode - User's promo code
 * @returns {Promise<{ ok: true } | { ok: false, reason: string }>}
 */
export async function sendReservationEmail(email, promoCode) {
  if (!EMAILJS_SERVICE_ID || !EMAILJS_TEMPLATE_ID || !EMAILJS_PUBLIC_KEY) {
    return { ok: false, reason: 'emailjs_not_configured' }
  }

  // Initialize EmailJS
  initializeEmailJS()

  try {
    // Prepare template parameters
    // These should match your EmailJS template variables
    // Note: If your EmailJS template uses HTML, you can either:
    // 1. Use simple variables and configure HTML in EmailJS dashboard template
    // 2. Or send the full HTML as a variable (if your template supports it)
    const websiteLink = import.meta.env.VITE_WEBSITE_URL || 'https://zedreq.ai'
    const companyEmail = ZEDREQ_EMAIL
    
    const templateParams = {
      to_email: email,
      to_name: 'Zedreq',
      promo_code: promoCode,
      website_link: websiteLink,
      company_email: companyEmail,
      subject: 'Your Seat is Reserved at ZedReq!',
      // Optional: Include full HTML if your template supports it
      message_html: getReservationEmailTemplate(promoCode, websiteLink, companyEmail),
    }

    // Send email via EmailJS
    const response = await emailjs.send(
      EMAILJS_SERVICE_ID,
      EMAILJS_TEMPLATE_ID,
      templateParams
    )

    if (response.status === 200) {
      return { ok: true }
    }
    return { ok: false, reason: `emailjs_status_${response.status}` }
  } catch (error) {
    const name = error && typeof error === 'object' && 'name' in error ? String(error.name) : 'Error'
    return { ok: false, reason: `emailjs_exception:${name}` }
  }
}

/**
 * Validate email format
 * @param {string} email - Email address to validate
 * @returns {boolean} - True if email is valid
 */
export function validateEmail(email) {
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailPattern.test(email)
}
