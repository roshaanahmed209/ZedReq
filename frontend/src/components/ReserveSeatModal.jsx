import React, { useState } from 'react'
import '../css/components/ReserveSeatModal.css'

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

    setLoading(true)
    setError('')

    try {
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

      if (data.success) {
        setSubmitted(true)
        setPromoCode(data.promo_code || '')
        setAlreadyReserved(data.already_reserved || false)
      } else {
        throw new Error(data.message || 'Failed to reserve seat')
      }
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
            <h2 className="modal-title">Reserve Your Seat</h2>
            <p className="modal-description">
              Enter your email to reserve your spot and get early access to ZedReq.
            </p>
            <form 
              className="reserve-form"
              onSubmit={handleSubmit}
            >
              <input
                type="email"
                className="modal-input"
                placeholder="Enter your email"
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
