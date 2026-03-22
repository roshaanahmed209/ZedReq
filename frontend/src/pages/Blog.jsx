import React from 'react'
import PublicSubpageLayout from '../components/PublicSubpageLayout'

export default function Blog() {
  return (
    <PublicSubpageLayout title="Blog">
      <div className="public-subpage-prose">
        <p>
          Product updates, hiring tips, and platform news will appear here as we publish them. Check back soon or follow announcements in the app.
        </p>
      </div>
    </PublicSubpageLayout>
  )
}
