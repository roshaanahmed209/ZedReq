import React, { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { fetchPublicBlogPost } from '../services/api'
import { formatBlogDate, setPageMeta } from '../utils/pageMeta'
import '../css/pages/Blogs.css'

export default function BlogPost() {
  const { slug } = useParams()
  const [post, setPost] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [error, setError] = useState('')

  const loadPost = useCallback(async () => {
    if (!slug) {
      setNotFound(true)
      setLoading(false)
      return
    }
    setError('')
    setNotFound(false)
    setLoading(true)
    try {
      const { data } = await fetchPublicBlogPost(slug)
      setPost(data)
      setPageMeta({
        title: data.seo_title || `${data.title} | ZedReq Blog`,
        description: data.seo_description || data.excerpt || LISTING_FALLBACK.description,
      })
    } catch (err) {
      setPost(null)
      if (err.response?.status === 404) {
        setNotFound(true)
      } else {
        const msg =
          err.response?.data?.detail ||
          err.message ||
          'Could not load this post.'
        setError(typeof msg === 'string' ? msg : 'Could not load this post.')
      }
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => {
    loadPost()
  }, [loadPost])

  if (loading) {
    return (
      <PublicSubpageLayout title="">
        <div className="blogs-skeleton" aria-busy="true" aria-label="Loading post">
          <div className="blogs-skeleton__card" style={{ height: 320 }} />
        </div>
      </PublicSubpageLayout>
    )
  }

  if (notFound) {
    return (
      <PublicSubpageLayout title="Post not found">
        <Link to="/blogs" className="blogs-back">
          ← All posts
        </Link>
        <div className="public-subpage-prose">
          <p>This article does not exist or is not published yet.</p>
        </div>
      </PublicSubpageLayout>
    )
  }

  if (error) {
    return (
      <PublicSubpageLayout title="">
        <Link to="/blogs" className="blogs-back">
          ← All posts
        </Link>
        <div className="blogs-state blogs-state--error">
          <p>{error}</p>
          <button type="button" className="blogs-retry" onClick={loadPost}>
            Try again
          </button>
        </div>
      </PublicSubpageLayout>
    )
  }

  if (!post) return null

  return (
    <PublicSubpageLayout title={post.title}>
      <article>
        <Link to="/blogs" className="blogs-back">
          ← All posts
        </Link>

        <div className="blogs-post-meta">
          {post.published_at ? (
            <time dateTime={post.published_at}>{formatBlogDate(post.published_at)}</time>
          ) : null}
          {post.author_name ? <span>{post.author_name}</span> : null}
        </div>

        {post.cover_image_url ? (
          <img
            src={post.cover_image_url}
            alt=""
            className="blogs-post-cover"
            loading="lazy"
          />
        ) : null}

        {post.tags?.length ? (
          <div className="blogs-card__tags" style={{ marginBottom: '1.5rem' }}>
            {post.tags.map((tag) => (
              <span key={tag} className="blogs-tag">
                {tag}
              </span>
            ))}
          </div>
        ) : null}

        <div className="public-subpage-prose blogs-markdown">
          <ReactMarkdown>{post.body || ''}</ReactMarkdown>
        </div>
      </article>
    </PublicSubpageLayout>
  )
}

const LISTING_FALLBACK = {
  description:
    'Hiring tips, product updates, and career advice from ZedReq.',
}
