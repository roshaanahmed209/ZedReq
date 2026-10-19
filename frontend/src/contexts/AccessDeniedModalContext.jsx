import React, { createContext, useCallback, useContext, useState } from 'react'
import { parseAccessDeniedError } from '../utils/accessDenied'

const AccessDeniedModalContext = createContext(null)

const DEFAULT_STATE = {
  isOpen: false,
  payload: null,
}

export function AccessDeniedModalProvider({ children }) {
  const [modal, setModal] = useState(DEFAULT_STATE)

  const showAccessDeniedModal = useCallback((input) => {
    const payload =
      input?.response || input?.userMessage
        ? parseAccessDeniedError(input)
        : input

    if (!payload?.message) return

    setModal({ isOpen: true, payload })
  }, [])

  const closeAccessDeniedModal = useCallback(() => {
    setModal(DEFAULT_STATE)
  }, [])

  return (
    <AccessDeniedModalContext.Provider
      value={{ modal, showAccessDeniedModal, closeAccessDeniedModal }}
    >
      {children}
    </AccessDeniedModalContext.Provider>
  )
}

export function useAccessDeniedModal() {
  const ctx = useContext(AccessDeniedModalContext)
  if (!ctx) {
    throw new Error('useAccessDeniedModal must be used inside AccessDeniedModalProvider')
  }
  return {
    showAccessDeniedModal: ctx.showAccessDeniedModal,
    closeAccessDeniedModal: ctx.closeAccessDeniedModal,
  }
}

export function useAccessDeniedModalState() {
  const ctx = useContext(AccessDeniedModalContext)
  if (!ctx) {
    throw new Error('useAccessDeniedModalState must be used inside AccessDeniedModalProvider')
  }
  return {
    modal: ctx.modal,
    closeAccessDeniedModal: ctx.closeAccessDeniedModal,
  }
}
