import React, { useState, useCallback } from 'react'
import styled from 'styled-components'

const Btn = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--text-lighter);
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.9em;
  min-height: 44px;

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }
`

export default function SharePostButton({
  postId,
  title = 'Post on ZedReq',
  className,
  variant = 'default',
}) {
  const [copied, setCopied] = useState(false)

  const share = useCallback(
    async (e) => {
      e?.stopPropagation?.()
      e?.preventDefault?.()
      if (postId == null) return
      const url = `${window.location.origin}/post/${postId}`

      try {
        if (typeof navigator !== 'undefined' && navigator.share) {
          await navigator.share({ url, title, text: title })
          return
        }
      } catch (err) {
        if (err?.name === 'AbortError') return
      }

      try {
        await navigator.clipboard.writeText(url)
        setCopied(true)
        window.setTimeout(() => setCopied(false), 2000)
      } catch {
        window.alert('Could not copy link.')
      }
    },
    [postId, title]
  )

  if (variant === 'iconOnly') {
    return (
      <Btn
        type="button"
        className={className}
        onClick={share}
        aria-label={copied ? 'Link copied' : 'Share post'}
        title={copied ? 'Copied!' : 'Share'}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden
        >
          <circle cx="18" cy="5" r="3" />
          <circle cx="6" cy="12" r="3" />
          <circle cx="18" cy="19" r="3" />
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
        </svg>
      </Btn>
    )
  }

  return (
    <Btn
      type="button"
      className={className}
      onClick={share}
      aria-label={copied ? 'Link copied' : 'Share post'}
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden
      >
        <circle cx="18" cy="5" r="3" />
        <circle cx="6" cy="12" r="3" />
        <circle cx="18" cy="19" r="3" />
        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
        <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
      </svg>
      <span>{copied ? 'Copied' : 'Share'}</span>
    </Btn>
  )
}
