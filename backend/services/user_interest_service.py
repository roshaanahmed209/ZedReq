"""
User Interest Vector Service

Builds the per-user vector that posts are ranked against in the personalized feed.

Blend = profile component (description.embedding, the cold-start signal) mixed with
a behavioral component (recency-weighted average of embeddings of posts the user
liked / commented on). The behavioral weight (alpha) grows with interaction count,
so new/sparse users lean on their profile and active users lean on their behavior.

All vectors use text-embedding-3-large (3072 dims), matching post.embedding, so the
result is directly comparable to posts via cosine distance.
"""
import math
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.orm import Like, PostComment
from utils.job_embeddings import get_user_embedding
from config.database import get_database
from config.cache import get_cached, set_cached
from utils.logger import setup_logger

logger = setup_logger(__name__)

# How many recent interactions feed the behavioral vector
MAX_INTERACTIONS = 50
# Per-rank recency decay (most recent interaction weighted highest)
RANK_DECAY = 0.9
# alpha = min(ALPHA_CAP, interactions / ALPHA_SATURATION)
ALPHA_CAP = 0.8
ALPHA_SATURATION = 25.0
# Cache TTL for a computed interest vector (seconds)
INTEREST_VEC_TTL = 3600


def _parse_vec(value) -> Optional[List[float]]:
    """Parse a pgvector value (string like '[0.1,0.2,...]') into a list of floats."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [float(x) for x in value]
    if isinstance(value, str):
        s = value.strip().strip('[]')
        if not s:
            return None
        try:
            return [float(x.strip()) for x in s.split(',')]
        except ValueError:
            return None
    return None


def _normalize(vec: List[float]) -> Optional[List[float]]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return None
    return [v / norm for v in vec]


def _recent_interacted_post_ids(user_id: int, db: Session, limit: int) -> List[int]:
    """Most recent post_ids the user liked or commented on, newest first, deduped."""
    likes = (
        db.query(Like.post_id, Like.created_at)
        .filter(Like.uid == user_id, Like.post_id.isnot(None))
        .order_by(desc(Like.created_at))
        .limit(limit)
        .all()
    )
    comments = (
        db.query(PostComment.post_id, PostComment.created_at)
        .filter(PostComment.uid == user_id)
        .order_by(desc(PostComment.created_at))
        .limit(limit)
        .all()
    )

    combined: List[Tuple[int, object]] = [(pid, ts) for (pid, ts) in likes] + [
        (pid, ts) for (pid, ts) in comments
    ]
    # Newest first; rows with no timestamp sort last
    combined.sort(key=lambda r: (r[1] is not None, r[1]), reverse=True)

    ordered_ids: List[int] = []
    seen = set()
    for pid, _ in combined:
        if pid in seen:
            continue
        seen.add(pid)
        ordered_ids.append(pid)
        if len(ordered_ids) >= limit:
            break
    return ordered_ids


def _behavioral_vector(post_ids: List[int]) -> Optional[List[float]]:
    """Recency-weighted (by rank) average of the given posts' embeddings."""
    if not post_ids:
        return None

    db_raw = get_database()
    # Fetch embeddings; preserve order via the input list (ANY adapts the Python list to a Postgres array)
    rows = db_raw.fetch_all(
        """
        SELECT post_id, embedding
        FROM post
        WHERE post_id = ANY(%s) AND embedding IS NOT NULL
        """,
        (post_ids,),
    )
    if not rows:
        return None

    by_id = {row['post_id']: _parse_vec(row['embedding']) for row in rows}

    acc: Optional[List[float]] = None
    total_weight = 0.0
    rank = 0
    for pid in post_ids:  # post_ids is newest-first → rank 0 is most recent
        vec = by_id.get(pid)
        if not vec:
            continue
        weight = RANK_DECAY ** rank
        rank += 1
        if acc is None:
            acc = [0.0] * len(vec)
        if len(vec) != len(acc):
            continue  # skip dimension mismatch defensively
        for i, v in enumerate(vec):
            acc[i] += weight * v
        total_weight += weight

    if acc is None or total_weight == 0:
        return None
    return [v / total_weight for v in acc]


def get_user_interest_vector(
    user_id: int,
    db: Session,
    max_interactions: int = MAX_INTERACTIONS,
) -> Optional[List[float]]:
    """
    Build (or read from cache) the user's interest vector.

    Returns a normalized 3072-dim vector, or None when the user has neither a
    profile embedding nor any usable interaction embeddings (→ cold-start path).
    """
    # Interaction count doubles as a cache version: new likes/comments bust the cache.
    interaction_count = (
        db.query(Like).filter(Like.uid == user_id).count()
        + db.query(PostComment).filter(PostComment.uid == user_id).count()
    )

    cache_key = f"feed:interest_vec:{user_id}:{interaction_count}"
    cached = get_cached(cache_key)
    if cached is not None:
        # Empty list is the cached "cold-start / no vector" sentinel
        return cached or None

    profile = _parse_vec(get_user_embedding(user_id, db))
    profile = _normalize(profile) if profile else None

    behavioral = None
    if interaction_count > 0:
        post_ids = _recent_interacted_post_ids(user_id, db, max_interactions)
        behavioral = _behavioral_vector(post_ids)
        behavioral = _normalize(behavioral) if behavioral else None

    result: Optional[List[float]]
    if profile and behavioral:
        alpha = min(ALPHA_CAP, interaction_count / ALPHA_SATURATION)
        blended = [alpha * b + (1 - alpha) * p for b, p in zip(behavioral, profile)]
        result = _normalize(blended)
    elif behavioral:
        result = behavioral
    elif profile:
        result = profile
    else:
        result = None

    # Cache the result (or the empty-list sentinel for cold-start) to avoid recompute churn
    try:
        set_cached(cache_key, result if result else [], ttl=INTEREST_VEC_TTL)
    except Exception as e:
        logger.debug(f"Failed to cache interest vector for user {user_id}: {e}")

    return result
