import React, { useEffect, useState } from 'react'
import styled, { keyframes } from 'styled-components'
import { useConfirmModalState } from '../contexts/ConfirmModalContext'

const fadeIn = keyframes`
  from { opacity: 0; }
  to   { opacity: 1; }
`

const slideUp = keyframes`
  from { opacity: 0; transform: translateY(12px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)    scale(1);    }
`

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(3px);
  animation: ${fadeIn} 0.18s ease;
`

const Dialog = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow-lg, 0 8px 40px rgba(0, 0, 0, 0.18));
  width: 100%;
  max-width: 420px;
  padding: 28px 28px 24px;
  animation: ${slideUp} 0.2s ease;
`

const Title = styled.h3`
  margin: 0 0 10px;
  font-size: 1.1em;
  font-weight: 600;
  color: var(--text);
  line-height: 1.3;
`

const Message = styled.p`
  margin: 0 0 24px;
  font-size: 0.92em;
  color: var(--text-light);
  line-height: 1.6;
`

const InputLabel = styled.label`
  display: block;
  font-size: 0.85em;
  font-weight: 500;
  color: var(--text-light);
  margin-bottom: 6px;
`

const InputField = styled.input`
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-white);
  color: var(--text);
  font-size: 0.92em;
  margin-bottom: 20px;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.15s;

  &:focus { border-color: var(--primary); }
`

const ButtonRow = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
`

const Btn = styled.button`
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s, background 0.15s, border-color 0.15s;
  border: 1px solid transparent;

  &:hover { opacity: 0.85; }
  &:active { opacity: 0.7; }

  ${({ $variant }) => {
    switch ($variant) {
      case 'danger':
        return `
          background: #dc3545;
          color: #fff;
          border-color: #dc3545;
        `
      case 'primary':
        return `
          background: var(--primary);
          color: #fff;
          border-color: var(--primary);
        `
      case 'secondary':
      default:
        return `
          background: none;
          color: var(--text-light);
          border-color: var(--border);
          &:hover { background: var(--hover-bg); opacity: 1; }
        `
    }
  }}
`

export default function ConfirmModal() {
  const { modal, handleButtonClick, handleClose } = useConfirmModalState()
  const { isOpen, title, message, buttons, input } = modal
  const [inputValue, setInputValue] = useState('')

  // Reset input value whenever a new modal opens
  useEffect(() => {
    if (isOpen) setInputValue('')
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return
    const onKey = (e) => { if (e.key === 'Escape') handleClose() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [isOpen, handleClose])

  if (!isOpen) return null

  const resolveButton = (btn) => {
    // If this button submits the input, resolve with the typed value
    if (btn.submitsInput) return handleButtonClick(inputValue)
    handleButtonClick(btn.value !== undefined ? btn.value : null)
  }

  return (
    <Overlay onClick={handleClose} role="dialog" aria-modal="true" aria-labelledby="confirm-modal-title">
      <Dialog onClick={(e) => e.stopPropagation()}>
        {title && <Title id="confirm-modal-title">{title}</Title>}
        {message && <Message>{message}</Message>}
        {input && (
          <>
            {input.label && <InputLabel>{input.label}</InputLabel>}
            <InputField
              type={input.type || 'text'}
              placeholder={input.placeholder || ''}
              value={inputValue}
              autoFocus
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const submitBtn = buttons.find(b => b.submitsInput)
                  if (submitBtn) resolveButton(submitBtn)
                }
              }}
            />
          </>
        )}
        {buttons.length > 0 && (
          <ButtonRow>
            {buttons.map((btn, i) => (
              <Btn
                key={i}
                $variant={btn.variant || 'secondary'}
                onClick={() => resolveButton(btn)}
              >
                {btn.label}
              </Btn>
            ))}
          </ButtonRow>
        )}
      </Dialog>
    </Overlay>
  )
}
