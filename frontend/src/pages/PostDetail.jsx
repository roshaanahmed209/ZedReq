import React, { useEffect, useState, useCallback } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate, useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { postAPI, contextAPI } from '../services/api'
import { generateProfileUrl } from '../utils/profileUrl'

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
  padding: 16px 20px 48px;
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
  display: flex;
  align-items: center;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
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
  padding: 6px 0;

  &:hover {
    color: var(--primary);
  }

  svg {
    width: 20px;
    height: 20px;
  }
`

const MetaStat = styled.span`
  font-size: 0.9em;
  color: var(--text-lighter);
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
    setLikeBusy(true)
    try {
      await postAPI.toggleLike(post.id)
      setPost(prev => {
        if (!prev) return prev
        const nextLiked = !prev.is_liked
        const delta = nextLiked ? 1 : -1
        return {
          ...prev,
          is_liked: nextLiked,
          like_count: Math.max(0, (prev.like_count || 0) + delta),
        }
      })
      contextAPI.updateContext('like', 'post', post.id).catch(() => {})
    } catch (e) {
      console.error(e)
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

            {post.media_url && (
              <PostMedia>
                {post.media_type === 'video' ? (
                  <video src={post.media_url} controls playsInline />
                ) : (
                  <img src={post.media_url} alt="" />
                )}
              </PostMedia>
            )}

            <Actions>
              <ActionBtn type="button" $active={post.is_liked} onClick={handleLike} disabled={likeBusy}>
                <svg viewBox="0 0 24 24" fill={post.is_liked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                </svg>
                {post.like_count ?? 0}
              </ActionBtn>
              <MetaStat>{post.comment_count ?? 0} comments</MetaStat>
            </Actions>
          </PostCard>
        ) : null}
      </Main>
    </Container>
  )
}
