import React, { useEffect, useState, useCallback } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import PlanFlowBackButton from '../components/PlanFlowBackButton'
import '../css/pages/Checkout.css'

const PADDLE_SCRIPT = 'https://cdn.paddle.com/paddle/v2/paddle.js'

const loadPaddleScript = () =>
  new Promise((resolve, reject) => {
    if (typeof window !== 'undefined' && window.Paddle) {
      resolve(window.Paddle)
      return
    }
    const existing = document.querySelector(`script[src="${PADDLE_SCRIPT}"]`)
    if (existing) {
      existing.addEventListener('load', () => resolve(window.Paddle))
      existing.addEventListener('error', reject)
      return
    }
    const s = document.createElement('script')
    s.src = PADDLE_SCRIPT
    s.async = true
    s.onload = () => resolve(window.Paddle)
    s.onerror = () => reject(new Error('Failed to load Paddle'))
    document.body.appendChild(s)
  })

const Checkout = () => {
  const [searchParams] = useSearchParams()
  const plan = (searchParams.get('plan') || '').toLowerCase()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [paddleReady, setPaddleReady] = useState(false)
  const [initError, setInitError] = useState('')
  const [opening, setOpening] = useState(false)

  const validPlan = plan === 'pro' || plan === 'premium'

  useEffect(() => {
    const token = import.meta.env.VITE_PADDLE_CLIENT_TOKEN
    if (!token) {
      setInitError('Checkout is not configured (missing VITE_PADDLE_CLIENT_TOKEN). Use Free plan or set env vars.')
      return
    }
    let cancelled = false
    loadPaddleScript()
      .then((Paddle) => {
        if (cancelled || !Paddle) return
        const env = import.meta.env.VITE_PADDLE_ENV === 'production' ? 'production' : 'sandbox'
        if (Paddle.Environment?.set) {
          Paddle.Environment.set(env)
        }
        if (Paddle.Initialize) {
          Paddle.Initialize({ token })
        }
        setPaddleReady(true)
      })
      .catch(() => {
        if (!cancelled) setInitError('Could not load payment SDK.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  const pollSubscription = useCallback(async () => {
    for (let i = 0; i < 15; i += 1) {
      try {
        const { data } = await api.get('/api/user/subscription')
        if (!data?.requires_plan_selection) {
          navigate('/feed', { replace: true })
          return
        }
      } catch (_) {
        /* ignore */
      }
      await new Promise((r) => setTimeout(r, 800))
    }
    navigate('/feed', { replace: true })
  }, [navigate])

  useEffect(() => {
    if (!paddleReady || !validPlan || typeof window === 'undefined') return
    const Paddle = window.Paddle
    if (!Paddle?.Checkout?.open) return

    const onComplete = () => {
      pollSubscription()
    }
    if (Paddle.on) {
      Paddle.on('checkout.completed', onComplete)
    }
    return () => {
      if (Paddle.off) {
        Paddle.off('checkout.completed', onComplete)
      }
    }
  }, [paddleReady, validPlan, pollSubscription])

  const openCheckout = () => {
    const uid = user?.id ?? user?.uid
    if (!uid) {
      setInitError('You must be signed in.')
      return
    }
    const priceId =
      plan === 'pro'
        ? import.meta.env.VITE_PADDLE_PRICE_PRO
        : import.meta.env.VITE_PADDLE_PRICE_PREMIUM
    if (!priceId) {
      setInitError('Missing VITE_PADDLE_PRICE_PRO or VITE_PADDLE_PRICE_PREMIUM.')
      return
    }
    const Paddle = window.Paddle
    if (!Paddle?.Checkout?.open) {
      setInitError('Paddle Checkout is not available.')
      return
    }
    setOpening(true)
    try {
      Paddle.Checkout.open({
        items: [{ priceId, quantity: 1 }],
        customData: { zedreq_user_id: String(uid) },
      })
    } catch (e) {
      setInitError(e?.message || 'Could not open checkout.')
    } finally {
      setOpening(false)
    }
  }

  if (!validPlan) {
    return (
      <div className="checkout-page">
        <PlanFlowBackButton to="choose-plan" />
        <div className="checkout-inner">
          <h1>Checkout</h1>
          <p>Invalid or missing plan. Use <code>?plan=pro</code> or <code>?plan=premium</code>.</p>
          <Link to="/choose-plan">← Back to plans</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="checkout-page">
      <PlanFlowBackButton to="choose-plan" />
      <div className="checkout-inner">
        <h1>Checkout</h1>
        <p>
          You are subscribing to the <strong>{plan}</strong> plan. Complete payment in the Paddle window.
        </p>
        {initError && <div className="checkout-error">{initError}</div>}
        {paddleReady && !initError && (
          <button type="button" className="checkout-open-btn" onClick={openCheckout} disabled={opening}>
            {opening ? 'Opening…' : 'Open checkout'}
          </button>
        )}
        <p className="checkout-hint">
          After payment, your plan updates via webhook. If you stay on this page, we will redirect when your subscription is active.
        </p>
        <Link to="/choose-plan">← Back to plans</Link>
      </div>
    </div>
  )
}

export default Checkout
