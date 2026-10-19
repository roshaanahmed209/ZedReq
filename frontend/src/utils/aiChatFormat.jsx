import React from 'react'

/**
 * Turn **segments** into <strong> for AI chat (no raw HTML from the model).
 */
export function parseBoldToNodes(str) {
  if (str == null || str === '') return null
  const nodes = []
  const re = /\*\*([\s\S]*?)\*\*/g
  let last = 0
  let m
  while ((m = re.exec(str)) !== null) {
    if (m.index > last) nodes.push(str.slice(last, m.index))
    nodes.push(<strong key={`b-${m.index}`}>{m[1]}</strong>)
    last = m.index + m[0].length
  }
  if (last < str.length) nodes.push(str.slice(last))
  return nodes.length ? nodes : [str]
}

/**
 * Splits intro text from "1. ... 2. ..." style numbered blocks and renders lists + paragraphs.
 */
export function AiFormattedChatContent({ text }) {
  if (text == null || text === '') return null

  const trimmed = String(text).trim()

  function expandNumberedLines(segment) {
    const t = segment.trim()
    if (!t) return []
    if (/^\d+\.\s+/.test(t) && /\n\s*\d+\.\s+/.test(t)) {
      return t.split(/\n(?=\s*\d+\.\s+)/).map((s) => s.trim()).filter(Boolean)
    }
    return [t]
  }

  // After ":" before "1. ..." (inline list), or newline before "2. ..." etc.
  // Avoids false splits on years like "in 2024. Next" (no ":" / newline+number pattern).
  const stage1 = trimmed.split(/(?<=:)\s*(?=\d+\.\s+)|\n(?=\s*\d+\.\s+)/)
  const chunks = stage1.flatMap((s) => expandNumberedLines(s)).filter(Boolean)

  const elements = []
  let listItems = []

  const flushList = () => {
    if (listItems.length === 0) return
    elements.push(
      <ol key={`ol-${elements.length}`}>
        {listItems.map((item, idx) => (
          <li key={idx}>{parseBoldToNodes(item)}</li>
        ))}
      </ol>
    )
    listItems = []
  }

  for (const chunk of chunks) {
    if (/^\d+\.\s+/.test(chunk)) {
      listItems.push(chunk.replace(/^\d+\.\s+/, ''))
    } else {
      flushList()
      elements.push(
        <p key={`p-${elements.length}`}>{parseBoldToNodes(chunk)}</p>
      )
    }
  }
  flushList()

  return <>{elements}</>
}
