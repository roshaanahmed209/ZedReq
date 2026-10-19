import React, { useEffect, useState, useCallback } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate, useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import PostComments from '../components/PostComments'
import SharePostButton from '../components/SharePostButton'
import { postAPI } from '../services/api'
import { generateProfileUrl } from '../utils/profileUrl'
import { shouldSkipMediaLoad } from '../utils/mediaUrl'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(12px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const Container = styled.div`
  min-height: 100vh;
  background: var(--bg-light);
  animation: ${fadeIn} 0.5s ease-in;
`

const Toolbar = styled.div`
  max-width: 720px;
  margin: 0 auto;
  padding: 20px 20px 0;
  display: flex;
  align-items: center;
  gap: 12px;
`

const BackButton = styled.button`
  padding: 10px 16px;
  background: var(--bg-white);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
  }
`

const FeedLink = styled(Link)`
  margin-left: auto;
  font-size: 0.9em;
  color: var(--primary);
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
`

const Main = styled.main`
  max-width: 720px;
  margin: 0 auto;
  padding: 12px 16px 40px;

  @media (min-width: 480px) {
    padding: 16px 20px 48px;
  }
`

const PostCard = styled.article`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: ${slideUp} 0.35s ease-out;
`

const PostHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
`

const Avatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 1.1em;
  flex-shrink: 0;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`

const AuthorBlock = styled.div`
  flex: 1;
  min-width: 0;
`

const AuthorName = styled(Link)`
  display: block;
  font-size: 1em;
  font-weight: 500;
  color: var(--text);
  text-decoration: none;
  margin-bottom: 2px;

  &:hover {
    color: var(--primary);
  }
`

const AuthorMeta = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
`

const PostBody = styled.div`
  line-height: 1.65;
  color: var(--text);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin-bottom: 16px;
`

const PostMedia = styled.div`
  margin-bottom: 16px;
  border-radius: 10px;
  overflow: hidden;

  img,
  video {
    display: block;
    width: 100%;
    max-height: 480px;
    object-fit: contain;
    background: var(--bg-light);
  }
`

const Actions = styled.div`
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
`

const ActionsStart = styled.div`
  justify-self: start;
`

const ActionsCenter = styled.div`
  justify-self: center;
`

const ActionsEnd = styled.div`
  justify-self: end;
`

const CommentStat = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-lighter);
  font-size: 0.9em;
  min-height: 44px;
  padding: 8px 12px;
  font-variant-numeric: tabular-nums;

  svg {
    width: 22px;
    height: 22px;
    flex-shrink: 0;
  }

  @media (min-width: 769px) {
    min-height: 40px;
    padding: 6px 10px;

    svg {
      width: 20px;
      height: 20px;
    }
  }
`

const ActionBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  color: ${p => (p.$active ? 'var(--primary)' : 'var(--text-light)')};
  cursor: pointer;
  font-size: 0.9em;
  padding: 8px 12px;
  border-radius: 8px;
  min-height: 44px;
  transition: color 0.15s ease, background 0.15s ease;

  &:hover:not(:disabled) {
    color: var(--primary);
    background: var(--hover-bg);
  }

  &:disabled {
    opacity: 0.85;
    cursor: wait;
  }

  svg {
    width: 22px;
    height: 22px;
    flex-shrink: 0;
  }

  @media (min-width: 769px) {
    min-height: 40px;
    padding: 6px 10px;

    svg {
      width: 20px;
      height: 20px;
    }
  }
`

const LikeCountText = styled.span`
  font-variant-numeric: tabular-nums;
`

const Centered = styled.div`
  text-align: center;
  padding: 48px 20px;
  color: var(--text-light);
`

const ErrorText = styled.div`
  color: #b91c1c;
  text-align: center;
  padding: 32px 20px;
`

function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    })
  } catch {
    return ''
  }
}

export default function PostDetail() {
  const { postId } = useParams()
  const navigate = useNavigate()
  const id = postId ? parseInt(postId, 10) : NaN

  const [post, setPost] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [likeBusy, setLikeBusy] = useState(false)

  const load = useCallback(async () => {
    if (!id || Number.isNaN(id)) {
      setError('Invalid post link.')
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await postAPI.getPost(id)
      setPost(res.data)
    } catch (e) {
      setPost(null)
      setError(e.response?.data?.detail || 'This post could not be loaded.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  const handleLike = async () => {
    if (!post || likeBusy) return
    const id = post.id
    const prevLiked = !!post.is_liked
    const prevCount = Number(post.like_count) || 0

    setLikeBusy(true)
    setPost(prev => {
      if (!prev) return prev
      return {
        ...prev,
        is_liked: !prevLiked,
        like_count: Math.max(0, prevCount + (prevLiked ? -1 : 1)),
      }
    })

    try {
      const r = await postAPI.toggleLike(id)
      const data = r.data
      setPost(prev =>
        prev
          ? {
              ...prev,
              is_liked: data.is_liked,
              like_count: data.like_count,
            }
          : prev
      )
    } catch (e) {
      console.error(e)
      setPost(prev =>
        prev
          ? {
              ...prev,
              is_liked: prevLiked,
              like_count: prevCount,
            }
          : prev
      )
    } finally {
      setLikeBusy(false)
    }
  }

  const profileHref =
    post && post.user_id
      ? generateProfileUrl(post.user_id, post.username || `user${post.user_id}`)
      : '/feed'

  const initials = post
    ? (post.full_name || post.username || 'U')
        .split(/\s+/)
        .map(s => s[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : ''

  return (
    <Container>
      <Navbar />
      <Toolbar>
        <BackButton type="button" onClick={() => navigate(-1)}>
          ← Back
        </BackButton>
        <FeedLink to="/feed">Go to feed</FeedLink>
      </Toolbar>

      <Main>
        {loading ? (
          <Centered>Loading post…</Centered>
        ) : error ? (
          <ErrorText>{error}</ErrorText>
        ) : post ? (
          <PostCard>
            <PostHeader>
              <Avatar>
                {post.profile_pic ? (
                  <img src={post.profile_pic} alt="" />
                ) : (
                  initials
                )}
              </Avatar>
              <AuthorBlock>
                <AuthorName to={profileHref}>{post.full_name || post.username || 'Member'}</AuthorName>
                <AuthorMeta>
                  @{post.username || 'user'} · {formatTime(post.created_at)}
                </AuthorMeta>
              </AuthorBlock>
            </PostHeader>

            <PostBody>{post.content || ''}</PostBody>

            {post.media_url && !shouldSkipMediaLoad(post.media_url) && (
              <PostMedia>
                {post.media_type === 'video' ? (
                  <video src={post.media_url} controls playsInline />
                ) : (
                  <img src={post.media_url} alt="" />
                )}
              </PostMedia>
            )}

            <Actions>
              <ActionsStart>
                <ActionBtn
                  type="button"
                  aria-label={post.is_liked ? 'Unlike' : 'Like'}
                  $active={post.is_liked}
                  onClick={handleLike}
                  disabled={likeBusy}
                >
                  <svg viewBox="0 0 24 24" fill={post.is_liked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
                  </svg>
                  <LikeCountText>{post.like_count ?? 0}</LikeCountText>
                </ActionBtn>
              </ActionsStart>
              <ActionsCenter>
                <CommentStat role="status" aria-label={`${post.comment_count ?? 0} comments`}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  <LikeCountText>{post.comment_count ?? 0}</LikeCountText>
                </CommentStat>
              </ActionsCenter>
              <ActionsEnd>
                <SharePostButton postId={post.id} />
              </ActionsEnd>
            </Actions>
            <PostComments
              postId={post.id}
              initialCount={post.comment_count ?? 0}
              defaultExpanded
              flush
              onCountChange={(n) =>
                setPost(prev => (prev ? { ...prev, comment_count: n } : prev))
              }
            />
          </PostCard>
        ) : null}
      </Main>
    </Container>
  )
}
