import React from 'react'

function linkifyPlain(text) {
  if (text == null || text === '') return null
  const urlRe = /(https?:\/\/[^\s]+)/gi
  const parts = text.split(urlRe)
  return parts.map((part, i) => {
    if (/^https?:\/\//i.test(part)) {
      const href = part.replace(/[.,;:!?)'\]]+$/g, '')
      return (
        <a
          key={i}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="get-started-modal-email"
        >
          {part}
        </a>
      )
    }
    return <React.Fragment key={i}>{part}</React.Fragment>
  })
}

/**
 * Renders ZedReq/privacy.txt or terms.txt with preserved line breaks and clickable URLs.
 */
export function LegalPlainDocument({ text }) {
  return (
    <div className="legal-plain-document">
      <div className="legal-plain-body">{linkifyPlain(text)}</div>
    </div>
  )
}
