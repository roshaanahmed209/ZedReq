"""Feed Router - Feed and post listing endpoints"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from dependencies.auth import get_current_user
from config.database import get_database
from models.post import Post
from models.like import Like
from models.connection import Connection

router = APIRouter()


@router.get("")
async def get_feed(
    limit: int = Query(default=20, ge=1, le=50, description="Number of posts"),
    cursor: Optional[str] = Query(default=None, description="Pagination cursor"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized feed for current user.
    Shows posts from followed users and own posts.
    """
    db = get_database()
    post_model = Post(db)
    like_model = Like(db)
    connection_model = Connection(db)
    
    user_id = current_user["id"]
    
    # Get users that current user follows
    following = connection_model.get_following(user_id)
    following_uids = [f['followed_uid'] for f in following]
    
    # Parse cursor if provided
    parsed_cursor = None
    if cursor:
        try:
            parts = cursor.rsplit('_', 1)
            if len(parts) == 2:
                parsed_cursor = (parts[0], int(parts[1]))
        except (ValueError, AttributeError):
            pass
    
    # Get posts from feed
    # If user has connections, show personalized feed (own posts + followed users)
    # Otherwise, show global feed (all posts) so new users see content
    if following_uids:
        posts = post_model.get_feed_with_connections(
            user_id=user_id,
            following_uids=following_uids,
            cursor=parsed_cursor,
            limit=limit + 1  # Fetch one extra to check for more
        )
    else:
        # No connections yet - show global feed
        posts = post_model.get_feed(limit=limit + 1, offset=0)
    
    # Check if there are more posts
    has_more = len(posts) > limit
    if has_more:
        posts = posts[:limit]
    
    # Build next cursor
    next_cursor = None
    if has_more and posts:
        last_post = posts[-1]
        created_at = last_post['created_at']
        if hasattr(created_at, 'isoformat'):
            timestamp_str = created_at.isoformat()
        else:
            timestamp_str = str(created_at)
        next_cursor = f"{timestamp_str}_{last_post['post_id']}"
    
    # Enrich posts with like status
    enriched_posts = []
    for post in posts:
        is_liked = like_model.has_liked(post['post_id'], user_id)
        
        created_at = post['created_at']
        if hasattr(created_at, 'isoformat'):
            created_str = created_at.isoformat()
        else:
            created_str = str(created_at)
        
        enriched_posts.append({
            'id': post['post_id'],
            'user_id': post['uid'],
            'content': post['post_desc'],
            'media_url': post.get('media_url'),
            'media_type': post.get('media_type'),
            'created_at': created_str,
            'username': post.get('username', ''),
            'full_name': post.get('name', ''),
            'profile_pic': post.get('profile_pic'),
            'like_count': post.get('likes', 0),
            'comment_count': post.get('comments', 0),
            'is_liked': is_liked
        })
    
    return {
        'posts': enriched_posts,
        'pagination': {
            'next_cursor': next_cursor,
            'has_more': has_more,
            'limit': limit
        },
        'meta': {
            'following_count': len(following_uids),
            'cache_hit': False
        }
    }
