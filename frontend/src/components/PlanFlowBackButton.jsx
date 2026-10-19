import React from 'react'
import { useNavigate } from 'react-router-dom'
import '../css/components/PlanFlowBackButton.css'

/**
 * Fixed top-left back control for plan onboarding routes.
 * @param {'history' | 'choose-plan'} [to] - 'history' uses navigate(-1); 'choose-plan' goes to /choose-plan
 */
const PlanFlowBackButton = ({ to = 'history', label = 'Back' }) => {
  const navigate = useNavigate()

  const handleClick = () => {
    if (to === 'choose-plan') {
      navigate('/choose-plan')
      return
    }
    navigate(-1)
  }

  return (
    <button
      type="button"
      className="plan-flow-back-btn"
      onClick={handleClick}
      aria-label={label}
    >
      <span className="plan-flow-back-btn__arrow" aria-hidden="true">
        ←
      </span>
      <span className="plan-flow-back-btn__text">{label}</span>
    </button>
  )
}

export default PlanFlowBackButton
