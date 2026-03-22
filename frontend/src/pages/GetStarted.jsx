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
  const [slideIndex, setSlideIndex] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    const interval = setInterval(() => {
      setSlideIndex((prev) => (prev + 1) % SLIDE_IMAGES.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

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
              <button
                type="button"
                className="get-started-btn get-started-btn-active"
                onClick={() => navigate('/landing')}
              >
                Get Started
              </button>
            </div>

            <Link to="/" className="get-started-back">← Back to home</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GetStarted
