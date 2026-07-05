import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { fetchPublicBlogPosts } from '../services/api'
import { formatBlogDate, setPageMeta } from '../utils/pageMeta'
import '../css/pages/Blogs.css'

const LISTING_META = {
  title: 'Blog | ZedReq',
  description:
    'Hiring tips, product updates, and career advice from ZedReq — AI-powered job matching and mock interviews.',
}

export default function Blogs() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadPosts = useCallback(async () => {
    setError('')
    setLoading(true)
    try {
      const { data } = await fetchPublicBlogPosts({ page: 1, limit: 50 })
      setItems(data.items || [])
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        'Could not load blog posts.'
      setItems([])
      setError(typeof msg === 'string' ? msg : 'Could not load blog posts.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    setPageMeta(LISTING_META)
  }, [])

  useEffect(() => {
    loadPosts()
  }, [loadPosts])

  return (
    <PublicSubpageLayout title="Blog">
      {loading ? (
        <div className="blogs-skeleton" aria-busy="true" aria-label="Loading posts">
          <div className="blogs-skeleton__card" />
          <div className="blogs-skeleton__card" />
        </div>
      ) : error ? (
        <div className="blogs-state blogs-state--error">
          <p>{error}</p>
          <button type="button" className="blogs-retry" onClick={loadPosts}>
            Try again
          </button>
        </div>
      ) : items.length === 0 ? (
        <div className="blogs-state">
          <p>No posts published yet. Check back soon.</p>
        </div>
      ) : (
        <div className="blogs-grid">
          {items.map((post) => (
            <Link key={post.slug} to={`/blogs/${post.slug}`} className="blogs-card">
              <div className="blogs-card__meta">
                {post.published_at ? (
                  <time dateTime={post.published_at}>{formatBlogDate(post.published_at)}</time>
                ) : null}
                {post.author_name ? <span>{post.author_name}</span> : null}
              </div>
              <h2 className="blogs-card__title">{post.title}</h2>
              {post.excerpt ? <p className="blogs-card__excerpt">{post.excerpt}</p> : null}
              {post.tags?.length ? (
                <div className="blogs-card__tags">
                  {post.tags.map((tag) => (
                    <span key={tag} className="blogs-tag">
                      {tag}
                    </span>
                  ))}
                </div>
              ) : null}
            </Link>
          ))}
        </div>
      )}
    </PublicSubpageLayout>
  )
}
