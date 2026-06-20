"""
Post Embedding Utilities
Functions for generating and storing embeddings for posts (personalized feed).

Mirrors utils/job_embeddings.py and reuses its OpenAI client so post vectors use
the same model (text-embedding-3-large, 3072 dims) as description.embedding. This
keeps user interest vectors and post vectors directly comparable via cosine.
"""
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from models.orm.post import Post
# Reuse the shared embeddings client (text-embedding-3-large, 3072 dims)
from utils.job_embeddings import get_embeddings_client
from config.database import get_database

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 3072


def post_to_text(post: Post) -> str:
    """
    Convert a Post object to a structured text representation for embedding.

    Args:
        post: Post ORM object

    Returns:
        Structured text string combining the post's content
    """
    parts = []

    if post.post_desc:
        parts.append(f"Post: {post.post_desc.strip()}")

    if post.media_type:
        parts.append(f"Media Type: {post.media_type}")

    # Fallback so we never embed an empty string
    if not parts:
        parts.append(f"Post {post.post_id}")

    return "\n".join(parts)


def generate_post_embedding(post: Post) -> Optional[List[float]]:
    """
    Generate embedding for a post using OpenAI text-embedding-3-large.

    Args:
        post: Post ORM object

    Returns:
        3072-dimensional embedding vector or None if generation fails
    """
    embeddings_client = get_embeddings_client()
    if not embeddings_client:
        logger.error("Embeddings client not available")
        return None

    try:
        post_text = post_to_text(post)
        embedding = embeddings_client.embed_query(post_text)

        if len(embedding) != EMBEDDING_DIM:
            logger.warning(f"Expected {EMBEDDING_DIM} dimensions, got {len(embedding)}")

        logger.debug(f"Generated embedding for post {post.post_id}")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding for post {post.post_id}: {e}")
        return None


def store_post_embedding(post_id: int, embedding: List[float], db: Session) -> bool:
    """
    Store post embedding in PostgreSQL using raw SQL (pgvector support).

    Args:
        post_id: Post ID
        embedding: 3072-dimensional embedding vector
        db: SQLAlchemy database session (kept for signature parity; raw conn used internally)

    Returns:
        True if successful, False otherwise
    """
    try:
        # pgvector expects a string representation: '[0.1, 0.2, ...]'
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'

        # SQLAlchemy doesn't natively support pgvector, so we use raw SQL
        db_raw = get_database()
        query = """
        UPDATE post
        SET embedding = %s::vector
        WHERE post_id = %s
        """
        db_raw.execute(query, (embedding_str, post_id))
        logger.debug(f"Stored embedding for post {post_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store embedding for post {post_id}: {e}")
        import traceback
        traceback.print_exc()
        return False
