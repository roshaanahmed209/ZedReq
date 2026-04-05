import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  isPrelaunchNoticePending,
  clearPrelaunchNoticePending,
} from '../utils/prelaunchNotice'
import PrelaunchNoticeModal from './PrelaunchNoticeModal'

export default function PrelaunchNoticeHost() {
  const { user, loading } = useAuth()
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (loading || !user) {
      return
    }
    if (isPrelaunchNoticePending()) {
      setOpen(true)
    }
  }, [user, loading])

  const handleDismiss = () => {
    clearPrelaunchNoticePending()
    setOpen(false)
  }

  if (!open) return null
  return <PrelaunchNoticeModal onDismiss={handleDismiss} />
}
