import React, { useState, useEffect, useCallback, useRef } from 'react'
import styled from 'styled-components'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { postAPI } from '../services/api'
import { generateProfileUrl } from '../utils/profileUrl'

const Root = styled.div`
  width: 100%;
  margin-top: ${p => (p.$flush ? '0' : '8px')};
`

const ToggleBtn = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--text-lighter);
  cursor: pointer;
  font-size: 0.9em;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.15s ease, color 0.15s ease;

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  svg {
    width: 18px;
    height: 18px;
  }
`

const Panel = styled.div`
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);

  ${p =>
    p.$belowActionBar &&
    `
    margin-top: 8px;
    border-top: none;
  `}
`

const SectionTitle = styled.h3`
  margin: 0 0 12px;
  font-size: 0.95em;
  font-weight: 600;
  color: var(--text);
`

const CommentList = styled.ul`
  list-style: none;
  margin: 0 0 14px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
`

const CommentRow = styled.li`
  display: flex;
  gap: 10px;
  align-items: flex-start;
`

const CAvatar = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85em;
  font-weight: 500;
  flex-shrink: 0;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`

const CBody = styled.div`
  flex: 1;
  min-width: 0;
`

const CMeta = styled.div`
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px 10px;
  margin-bottom: 4px;
`

const CAuthor = styled(Link)`
  font-weight: 500;
  font-size: 0.88em;
  color: var(--text);
  text-decoration: none;

  &:hover {
    color: var(--primary);
  }
`

const CTime = styled.span`
  font-size: 0.78em;
  color: var(--text-lighter);
`

const CText = styled.p`
  margin: 0;
  font-size: 0.88em;
  line-height: 1.5;
  color: var(--text-light);
  white-space: pre-wrap;
  word-break: break-word;
`

const DeleteC = styled.button`
  background: none;
  border: none;
  padding: 2px 6px;
  font-size: 0.75em;
  color: var(--text-lighter);
  cursor: pointer;
  border-radius: 4px;

  &:hover {
    color: #b91c1c;
    background: rgba(185, 28, 28, 0.08);
  }
`

const Composer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`

const TextArea = styled.textarea`
  width: 100%;
  min-height: 72px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.9em;
  font-family: inherit;
  resize: vertical;
  background: var(--bg-white);
  color: var(--text);

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
`

const SubmitRow = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  align-items: center;
`

const SubmitBtn = styled.button`
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: var(--primary);
  color: #fff;
  font-size: 0.88em;
  font-weight: 500;
  cursor: pointer;

  &:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }

  &:hover:not(:disabled) {
    filter: brightness(1.05);
  }
`

const Hint = styled.p`
  margin: 0;
  font-size: 0.82em;
  color: var(--text-lighter);
`

const LoadState = styled.p`
  margin: 0 0 10px;
  font-size: 0.85em;
  color: var(--text-lighter);
`

function formatCommentTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString(undefined, {
      dateStyle: 'short',
      timeStyle: 'short',
    })
  } catch {
    return ''
  }
}

function initialsFrom(name, username) {
  const s = (name || username || 'U').trim()
  return s
    .split(/\s+/)
    .map(x => x[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export default function PostComments({
  postId,
  initialCount = 0,
  defaultExpanded = false,
  onCountChange,
  flush = false,
  /** Parent renders the toggle; use with expanded + onExpandedChange */
  hideToggle = false,
  /** Controlled open state when hideToggle */
  expanded: expandedProp,
  onExpandedChange,
}) {
  const { user } = useAuth()
  const uid = user?.id ?? user?.uid

  const [internalExpanded, setInternalExpanded] = useState(!!defaultExpanded)
  const expanded = hideToggle ? !!expandedProp : (defaultExpanded || internalExpanded)

  const setExpanded = (next) => {
    if (hideToggle) {
      const cur = !!expandedProp
      const v = typeof next === 'function' ? next(cur) : next
      onExpandedChange?.(v)
    } else {
      setInternalExpanded(prev => {
        if (defaultExpanded) return true
        return typeof next === 'function' ? next(prev) : next
      })
    }
  }

  const [count, setCount] = useState(Number(initialCount) || 0)
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [draft, setDraft] = useState('')

  const onCountChangeRef = useRef(onCountChange)
  onCountChangeRef.current = onCountChange

  useEffect(() => {
    setCount(Number(initialCount) || 0)
  }, [initialCount, postId])

  useEffect(() => {
    if (!expanded || !postId) return
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const r = await postAPI.getComments(postId, { limit: 50, offset: 0 })
        const data = r.data
        if (!cancelled) {
          setComments(data.comments || [])
          const total =
            typeof data.total === 'number'
              ? data.total
              : (data.comments || []).length
          setCount(total)
          onCountChangeRef.current?.(total)
        }
      } catch {
        if (!cancelled) setComments([])
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [expanded, postId])

  const bumpCount = useCallback(
    (n) => {
      setCount(n)
      onCountChange?.(n)
    },
    [onCountChange]
  )

  const submit = async () => {
    const text = draft.trim()
    if (!text || !postId || submitting) return
    setSubmitting(true)
    try {
      const r = await postAPI.createComment(postId, { content: text })
      const data = r.data
      const row = data.comment
      if (row) {
        setComments(prev => [row, ...prev])
      }
      const next = data.comment_count ?? count + 1
      bumpCount(next)
      setDraft('')
    } catch (e) {
      window.alert(e.response?.data?.detail || e.message || 'Could not post comment.')
    } finally {
      setSubmitting(false)
    }
  }

  const remove = async (commentId) => {
    if (!postId || !commentId) return
    try {
      await postAPI.deleteComment(postId, commentId)
      setComments(prev => prev.filter(c => (c.id || c.comment_id) !== commentId))
      bumpCount(Math.max(0, count - 1))
    } catch (e) {
      window.alert(e.response?.data?.detail || e.message || 'Could not delete comment.')
    }
  }

  const showPanel = expanded

  return (
    <Root $flush={flush}>
      {!defaultExpanded && !hideToggle && (
        <ToggleBtn
          type="button"
          onClick={() => setExpanded(e => !e)}
          aria-expanded={expanded}
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
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <span>
            {expanded ? 'Hide comments' : 'Comments'} ({count})
          </span>
        </ToggleBtn>
      )}

      {showPanel && (
        <Panel $belowActionBar={hideToggle}>
          {defaultExpanded && (
            <SectionTitle>Comments ({count})</SectionTitle>
          )}
          {loading ? (
            <LoadState>Loading comments…</LoadState>
          ) : comments.length === 0 ? (
            <Hint>No comments yet. Be the first to comment.</Hint>
          ) : (
            <CommentList>
              {comments.map(c => {
                const cid = c.id || c.comment_id
                const href = generateProfileUrl(
                  c.user_id,
                  c.username || `user${c.user_id}`
                )
                return (
                  <CommentRow key={cid}>
                    <CAvatar>
                      {c.profile_pic ? (
                        <img src={c.profile_pic} alt="" />
                      ) : (
                        initialsFrom(c.full_name, c.username)
                      )}
                    </CAvatar>
                    <CBody>
                      <CMeta>
                        <CAuthor to={href}>
                          {c.full_name || c.username || 'Member'}
                        </CAuthor>
                        <CTime>{formatCommentTime(c.created_at)}</CTime>
                        {uid != null && c.user_id === uid && (
                          <DeleteC
                            type="button"
                            onClick={() => remove(cid)}
                          >
                            Delete
                          </DeleteC>
                        )}
                      </CMeta>
                      <CText>{c.body}</CText>
                    </CBody>
                  </CommentRow>
                )
              })}
            </CommentList>
          )}

          <Composer>
            <TextArea
              value={draft}
              onChange={e => setDraft(e.target.value)}
              placeholder="Write a comment…"
              maxLength={2000}
              rows={3}
            />
            <SubmitRow>
              <SubmitBtn
                type="button"
                disabled={submitting || !draft.trim()}
                onClick={submit}
              >
                {submitting ? 'Posting…' : 'Comment'}
              </SubmitBtn>
            </SubmitRow>
          </Composer>
        </Panel>
      )}
    </Root>
  )
}
