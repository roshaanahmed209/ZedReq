import React, { createContext, useCallback, useContext, useRef, useState } from 'react'

const ConfirmModalContext = createContext(null)

const DEFAULT_STATE = {
  isOpen: false,
  title: '',
  message: '',
  buttons: [],
  input: null, // optional: { type, placeholder, label }
}

export function ConfirmModalProvider({ children }) {
  const [modal, setModal] = useState(DEFAULT_STATE)
  const resolveRef = useRef(null)

  const showConfirm = useCallback(({ title = '', message = '', buttons = [], input = null }) => {
    return new Promise((resolve) => {
      resolveRef.current = resolve
      setModal({ isOpen: true, title, message, buttons, input })
    })
  }, [])

  const handleButtonClick = useCallback((value) => {
    setModal(DEFAULT_STATE)
    if (resolveRef.current) {
      resolveRef.current(value)
      resolveRef.current = null
    }
  }, [])

  const handleClose = useCallback(() => {
    setModal(DEFAULT_STATE)
    if (resolveRef.current) {
      resolveRef.current(null)
      resolveRef.current = null
    }
  }, [])

  return (
    <ConfirmModalContext.Provider value={{ modal, showConfirm, handleButtonClick, handleClose }}>
      {children}
    </ConfirmModalContext.Provider>
  )
}

export function useConfirm() {
  const ctx = useContext(ConfirmModalContext)
  if (!ctx) throw new Error('useConfirm must be used inside ConfirmModalProvider')
  return ctx.showConfirm
}

export function useConfirmModalState() {
  const ctx = useContext(ConfirmModalContext)
  if (!ctx) throw new Error('useConfirmModalState must be used inside ConfirmModalProvider')
  return { modal: ctx.modal, handleButtonClick: ctx.handleButtonClick, handleClose: ctx.handleClose }
}
