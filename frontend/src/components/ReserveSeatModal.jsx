import React, { useState } from 'react'
import '../css/components/ReserveSeatModal.css'
import { sendReservationEmail, validateEmail } from '../services/emailjs'

const ReserveSeatModal = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [promoCode, setPromoCode] = useState('')
  const [alreadyReserved, setAlreadyReserved] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email) return

    // Validate email format
    if (!validateEmail(email)) {
      setError('Please enter a valid email address')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Step 1: Reserve seat in backend (stores in database and generates promo code)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/reserved-seats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Failed to reserve seat')
      }

      if (!data.success) {
        throw new Error(data.message || 'Failed to reserve seat')
      }

      // Step 2: Send email from frontend using EmailJS
      const promoCodeFromBackend = data.promo_code || ''
      setPromoCode(promoCodeFromBackend)
      setAlreadyReserved(data.already_reserved || false)

      // Only send email if it's a new reservation (not already reserved)
      if (!data.already_reserved && promoCodeFromBackend) {
        const emailSent = await sendReservationEmail(email, promoCodeFromBackend)
        if (!emailSent) {
          console.warn('Email sending failed, but reservation was created. Promo code:', promoCodeFromBackend)
          // Don't fail the whole process if email fails - reservation is already created
        }
      }

      setSubmitted(true)
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
      console.error('Error reserving seat:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setEmail('')
    setSubmitted(false)
    setError('')
    setPromoCode('')
    setAlreadyReserved(false)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button 
          className="modal-close" 
          onClick={handleClose}
          aria-label="Close modal"
        >
          ×
        </button>
        {!submitted ? (
          <>
            <h2 className="modal-title">Reserve Your Seat for Pro Plan</h2>
            <p className="modal-description">
              Enter your email to reserve your spot and get early access to ZedReq Pro Plan.
            </p>
            <div className="reserve-info-box">
              <p className="reserve-info-text">
                <strong>Important:</strong> Please enter your correct email address. A reference code will be generated when you reserve your seat, offering both you and any person you refer a discount on the Pro Plan.
              </p>
            </div>
            <form 
              className="reserve-form"
              onSubmit={handleSubmit}
            >
              <input
                type="email"
                className="modal-input"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
                disabled={loading}
              />
              {error && (
                <div className="modal-error">
                  {error}
                </div>
              )}
              <button 
                type="submit" 
                className="modal-submit-btn"
                disabled={loading}
              >
                {loading ? 'Reserving...' : 'Reserve Seat'}
              </button>
            </form>
          </>
        ) : (
          <div className="modal-success">
            <div className="success-icon">✓</div>
            <h2 className="modal-title">Thank You!</h2>
            <p className="modal-description">
              {alreadyReserved 
                ? "You've already reserved your seat! Check your email for your promo code."
                : "We've received your email. You'll receive a confirmation shortly."}
            </p>
            {promoCode && (
              <div className="promo-code-display">
                <p className="promo-label">Your Promo Code:</p>
                <p className="promo-code">{promoCode}</p>
              </div>
            )}
            <div className="referral-message">
              <h3>Get a Discount by Referring a Friend</h3>
              <p>
                Share ZedReq with a friend and you'll both get a special discount when we launch! 
                We'll send you a unique referral link in your confirmation email.
              </p>
            </div>
            <button 
              className="modal-close-btn"
              onClick={handleClose}
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ReserveSeatModal
