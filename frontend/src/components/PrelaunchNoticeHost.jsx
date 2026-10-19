import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { fetchPublicPrelaunchNotice } from '../services/api'
import {
  isPrelaunchNoticePending,
  clearPrelaunchNoticePending,
  PRELAUNCH_NOTICE_FALLBACK,
} from '../utils/prelaunchNotice'
import PrelaunchNoticeModal from './PrelaunchNoticeModal'

export default function PrelaunchNoticeHost() {
  const { user, loading } = useAuth()
  const [open, setOpen] = useState(false)
  const [config, setConfig] = useState(null)

  useEffect(() => {
    if (loading || !user || !isPrelaunchNoticePending()) {
      return
    }

    let cancelled = false

    ;(async () => {
      try {
        const { data } = await fetchPublicPrelaunchNotice()
        if (cancelled) return
        if (!data?.enabled) {
          clearPrelaunchNoticePending()
          return
        }
        setConfig(data)
        setOpen(true)
      } catch {
        if (cancelled) return
        setConfig(PRELAUNCH_NOTICE_FALLBACK)
        setOpen(true)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [user, loading])

  const handleDismiss = () => {
    clearPrelaunchNoticePending()
    setOpen(false)
  }

  if (!open || !config) return null
  return <PrelaunchNoticeModal config={config} onDismiss={handleDismiss} />
}
