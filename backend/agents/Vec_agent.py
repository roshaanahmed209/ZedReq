"""
Vec Agent - Vector Database Population Agent
AI-powered agent that populates Qdrant vector database with embeddings from jobs, users, and posts
"""

import os
import logging
import hashlib
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config.database_orm import get_db
from models.orm.job_posting import JobPosting
from models.orm.user import User
from models.orm.description import Description
from models.orm.post import Post

logger = logging.getLogger(__name__)


# System prompt for extracting user interests
EXTRACT_INTERESTS_PROMPT = """You are an AI assistant that extracts professional interests from user profile data.

Analyze the following user profile information and extract a comma-separated list of professional interests, skills, career goals, and areas of expertise.

Focus on:
- Professional interests and career domains
- Technical skills and technologies
- Industry preferences
- Learning and development interests
- Career goals and aspirations

Return ONLY a comma-separated list of interests (e.g., "AI/ML, Web Development, Career Growth, Data Science, Software Engineering").
Do not include explanations or additional text."""


class VecAgent:
    """AI Agent for populating Qdrant vector database with embeddings from database entities"""
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini"
    ):
        """
        Initialize Vec Agent with Qdrant and OpenAI clients
        
        Args:
            qdrant_url: Qdrant server URL (default: from env or localhost)
            qdrant_api_key: Qdrant API key (optional)
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use for LLM operations
        """
        # Initialize Qdrant client
        qdrant_url = qdrant_url or os.environ.get('QDRANT_URL', 'http://localhost:6333')
        qdrant_api_key = qdrant_api_key or os.environ.get('QDRANT_API_KEY')
        
        try:
            if qdrant_api_key:
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key
                )
            else:
                self.qdrant_client = QdrantClient(url=qdrant_url)
            
            # Test connection
            self.qdrant_client.get_collections()
            logger.info(f"Qdrant client connected to {qdrant_url}")
            self.qdrant_available = True
        except Exception as e:
            logger.warning(f"Qdrant not available: {e}")
            self.qdrant_client = None
            self.qdrant_available = False
        
        # Initialize OpenAI API key
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Vector indexing will not work.")
            self.openai_available = False
        else:
            self.openai_available = True
        
        # Initialize LangChain OpenAI clients
        if self.openai_available:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.3,
                    api_key=openai_api_key
                )
                self.embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=openai_api_key
                )
                logger.info(f"LangChain OpenAI clients initialized with model {model_name}")
            except Exception as e:
                logger.warning(f"LangChain OpenAI client initialization failed: {e}")
                self.llm = None
                self.embeddings = None
                self.openai_available = False
        else:
            self.llm = None
            self.embeddings = None
        
        # Configuration
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small dimension
        self.chunk_size = int(os.environ.get('VEC_CHUNK_SIZE', 6000))
        self.chunk_overlap = int(os.environ.get('VEC_CHUNK_OVERLAP', 200))
        self.batch_size = int(os.environ.get('VEC_SYNC_BATCH_SIZE', 50))  # Smaller batches for better memory management
        self.embedding_batch_size = int(os.environ.get('VEC_EMBEDDING_BATCH_SIZE', 100))  # Batch embeddings for efficiency
        self.rate_limit_delay = float(os.environ.get('VEC_RATE_LIMIT_DELAY', 0.1))  # Delay between API calls (seconds)
        self.max_retries = int(os.environ.get('VEC_MAX_RETRIES', 3))
        self.use_llm_for_interests = os.environ.get('VEC_USE_LLM_INTERESTS', 'false').lower() == 'true'  # Disable by default for scale
        
        # Collection names
        self.collections = {
            'jobs': 'nemz_jobs',
            'users': 'nemz_users',
            'posts': 'nemz_posts'
        }
        
        # Initialize collections
        for collection_name in self.collections.values():
            self._create_collection_if_not_exists(collection_name)
    
    def _create_collection_if_not_exists(self, collection_name: str) -> bool:
        """
        Create Qdrant collection if it doesn't exist
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        if not self.qdrant_available or not self.qdrant_client:
            return False
        
        try:
            collections = self.qdrant_client.get_collections()
            existing_names = [col.name for col in collections.collections]
            
            if collection_name not in existing_names:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {collection_name}")
            else:
                logger.debug(f"Collection {collection_name} already exists")
            
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks for embedding
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk (default: self.chunk_size)
            overlap: Overlap between chunks in characters (default: self.chunk_overlap)
            
        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = self.chunk_size
        if overlap is None:
            overlap = self.chunk_overlap
        
        # If text is shorter than chunk_size, return as single chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position forward by (chunk_size - overlap)
            start += chunk_size - overlap
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text (single)
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.openai_available or not self.embeddings:
            return None
        
        try:
            embedding = self.embeddings.embed_query(text)
            time.sleep(self.rate_limit_delay)  # Rate limiting
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def _get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch (more efficient)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        if not self.openai_available or not self.embeddings:
            return [None] * len(texts)
        
        if not texts:
            return []
        
        try:
            # Use embed_documents for batch processing (more efficient)
            embeddings = self.embeddings.embed_documents(texts)
            time.sleep(self.rate_limit_delay)  # Rate limiting after batch
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            # Fallback to individual embeddings
            return [self._get_embedding(text) for text in texts]
    
    def _extract_user_interests(
        self,
        about: Optional[str] = None,
        skills: Optional[str] = None,
        current_status: Optional[str] = None,
        short_desc: Optional[str] = None
    ) -> str:
        """
        Extract user interests - optimized for scale (LLM disabled by default)
        
        Args:
            about: User's about section
            skills: User's skills
            current_status: User's current status
            short_desc: User's short description
            
        Returns:
            Comma-separated list of interests
        """
        # For scale, use simple concatenation instead of LLM (much faster)
        # LLM extraction is disabled by default (VEC_USE_LLM_INTERESTS=false)
        if not self.use_llm_for_interests:
            parts = []
            if skills:
                parts.append(skills)
            if current_status:
                parts.append(current_status)
            if short_desc:
                parts.append(short_desc[:100])  # Limit length
            if about:
                parts.append(about[:200])  # Limit length
            return ", ".join(parts) if parts else ""
        
        # LLM extraction (only if enabled)
        if not self.openai_available or not self.llm:
            # Fallback: combine available fields
            parts = []
            if short_desc:
                parts.append(short_desc)
            if about:
                parts.append(about)
            if skills:
                parts.append(skills)
            if current_status:
                parts.append(current_status)
            return ", ".join(parts) if parts else ""
        
        try:
            # Build profile data string
            profile_data = []
            if short_desc:
                profile_data.append(f"Short Description: {short_desc}")
            if about:
                profile_data.append(f"About: {about}")
            if skills:
                profile_data.append(f"Skills: {skills}")
            if current_status:
                profile_data.append(f"Current Status: {current_status}")
            
            if not profile_data:
                return ""
            
            prompt = "\n".join(profile_data)
            
            messages = [
                SystemMessage(content=EXTRACT_INTERESTS_PROMPT),
                HumanMessage(content=f"Extract professional interests from this profile:\n\n{prompt}")
            ]
            
            response = self.llm.invoke(messages)
            interests = response.content.strip()
            
            # Clean up response (remove quotes, extra whitespace)
            interests = interests.strip('"\'')
            interests = ", ".join([i.strip() for i in interests.split(",")])
            
            logger.debug(f"Extracted interests: {interests}")
            return interests
            
        except Exception as e:
            logger.error(f"Failed to extract user interests: {e}")
            # Fallback
            parts = []
            if short_desc:
                parts.append(short_desc)
            if about:
                parts.append(about)
            if skills:
                parts.append(skills)
            return ", ".join(parts) if parts else ""
    
    def _construct_profile_link(self, user_id: int) -> str:
        """Construct profile link for user"""
        return f"/profile/{user_id}"
    
    def _construct_post_link(self, post_id: int) -> str:
        """Construct post link"""
        return f"/post/{post_id}"
    
    def index_jobs(self, limit: Optional[int] = None, since: Optional[datetime] = None) -> int:
        """
        Index jobs from job_postings table into Qdrant (with pagination for scale)
        
        Args:
            limit: Maximum number of jobs to index (None = all)
            since: Only index jobs created/updated after this datetime
            
        Returns:
            Number of jobs indexed
        """
        if not self.qdrant_available or not self.openai_available:
            logger.warning("Qdrant or OpenAI not available, cannot index jobs")
            return 0
        
        db = next(get_db())
        indexed_count = 0
        total_processed = 0
        start_time = time.time()
        
        try:
            # Build base query
            base_query = db.query(JobPosting).filter(JobPosting.status == 'active')
            
            if since:
                base_query = base_query.filter(
                    (JobPosting.created_at >= since) | (JobPosting.updated_at >= since)
                )
            
            # Get total count for progress tracking
            total_count = base_query.count()
            logger.info(f"Starting to index jobs (total: {total_count}, batch size: {self.batch_size})")
            
            offset = 0
            all_chunks = []  # Collect all chunks for batch embedding
            
            while True:
                # Fetch batch
                jobs = base_query.offset(offset).limit(self.batch_size).all()
                
                if not jobs:
                    break
                
                # Process batch
                batch_chunks = []
                batch_metadata = []
                
                for job in jobs:
                    try:
                        # Build searchable text
                        text_parts = [
                            f"Title: {job.title or ''}",
                            f"Description: {job.description or ''}",
                            f"Company: {job.company_name or ''}",
                            f"Location: {job.location or ''}",
                            f"Skills Required: {job.skills_required or ''}",
                            f"Experience Level: {job.experience_level or ''}",
                            f"Job Type: {job.job_type or ''}",
                            f"Remote: {'Yes' if job.is_remote else 'No'}"
                        ]
                        searchable_text = "\n".join(text_parts)
                        
                        # Chunk text if needed
                        chunks = self._chunk_text(searchable_text)
                        
                        # Store chunks and metadata for batch embedding
                        for chunk_idx, chunk in enumerate(chunks):
                            batch_chunks.append(chunk)
                            batch_metadata.append({
                                'job': job,
                                'chunk_idx': chunk_idx,
                                'total_chunks': len(chunks)
                            })
                        
                    except Exception as e:
                        logger.error(f"Failed to process job {job.job_id}: {e}")
                        continue
                
                # Generate embeddings in batch (much more efficient)
                if batch_chunks:
                    embeddings = self._get_embeddings_batch(batch_chunks)
                    
                    # Create points
                    points = []
                    for i, (embedding, metadata) in enumerate(zip(embeddings, batch_metadata)):
                        if not embedding:
                            continue
                        
                        job = metadata['job']
                        point_id = abs(hash(f"job_{job.job_id}_{metadata['chunk_idx']}"))
                        
                        point = PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload={
                                "entity_type": "job",
                                "job_id": job.job_id,
                                "chunk_index": metadata['chunk_idx'],
                                "total_chunks": metadata['total_chunks'],
                                "title": job.title or "",
                                "description": job.description or "",
                                "company_name": job.company_name or "",
                                "location": job.location or "",
                                "job_link": job.job_link or "",
                                "skills_required": job.skills_required or "",
                                "experience_level": job.experience_level or "",
                                "job_type": job.job_type or "",
                                "is_remote": job.is_remote,
                                "salary_min": job.salary_min,
                                "salary_max": job.salary_max,
                                "status": job.status or "active",
                                "created_at": job.created_at.isoformat() if job.created_at else None,
                                "indexed_at": datetime.now().isoformat()
                            }
                        )
                        points.append(point)
                    
                    # Upsert batch to Qdrant
                    if points:
                        self.qdrant_client.upsert(
                            collection_name=self.collections['jobs'],
                            points=points
                        )
                    
                    indexed_count += len(jobs)
                    total_processed += len(jobs)
                    
                    # Progress logging
                    if total_processed % (self.batch_size * 10) == 0:
                        elapsed = time.time() - start_time
                        rate = total_processed / elapsed if elapsed > 0 else 0
                        logger.info(f"Progress: {total_processed}/{total_count} jobs indexed ({rate:.1f} jobs/sec)")
                
                offset += self.batch_size
                
                # Check limit
                if limit and total_processed >= limit:
                    break
            
            elapsed = time.time() - start_time
            logger.info(f"Indexed {indexed_count} jobs in {elapsed:.1f}s ({indexed_count/elapsed:.1f} jobs/sec)")
            
        except Exception as e:
            logger.error(f"Failed to index jobs: {e}")
        finally:
            db.close()
        
        return indexed_count
    
    def index_users(self, limit: Optional[int] = None, since: Optional[datetime] = None) -> int:
        """
        Index users from users and description tables into Qdrant (with pagination for scale)
        
        Args:
            limit: Maximum number of users to index (None = all)
            since: Only index users created/updated after this datetime
            
        Returns:
            Number of users indexed
        """
        if not self.qdrant_available or not self.openai_available:
            logger.warning("Qdrant or OpenAI not available, cannot index users")
            return 0
        
        db = next(get_db())
        indexed_count = 0
        total_processed = 0
        start_time = time.time()
        
        try:
            # Build base query with join to description
            base_query = db.query(User, Description).outerjoin(
                Description, User.description_id == Description.desc_id
            )
            
            if since:
                base_query = base_query.filter(
                    (User.created_at >= since) | (User.updated_at >= since)
                )
            
            # Get total count for progress tracking
            total_count = base_query.count()
            logger.info(f"Starting to index users (total: {total_count}, batch size: {self.batch_size})")
            
            offset = 0
            
            while True:
                # Fetch batch
                results = base_query.offset(offset).limit(self.batch_size).all()
                
                if not results:
                    break
                
                # Process batch
                batch_chunks = []
                batch_metadata = []
                
                for user, description in results:
                    try:
                        # Get description fields (handle None description)
                        about = description.about if description else None
                        short_desc = description.short_desc if description else None
                        skills = description.skills if description else None
                        current_status = description.current_status if description else None
                        certificates = description.certificates if description else None
                        profile_pic = description.profile_pic if description else None
                        
                        # Extract interests (optimized - no LLM by default)
                        interests = self._extract_user_interests(
                            about=about,
                            skills=skills,
                            current_status=current_status,
                            short_desc=short_desc
                        )
                        
                        # Build searchable text
                        text_parts = [
                            f"Name: {user.name or ''}",
                            f"About: {about or ''}",
                            f"Short Description: {short_desc or ''}",
                            f"Skills: {skills or ''}",
                            f"Current Status: {current_status or ''}",
                            f"Certificates: {certificates or ''}",
                            f"Interests: {interests}"
                        ]
                        searchable_text = "\n".join(text_parts)
                        
                        # Chunk text if needed
                        chunks = self._chunk_text(searchable_text)
                        
                        # Store chunks and metadata for batch embedding
                        for chunk_idx, chunk in enumerate(chunks):
                            batch_chunks.append(chunk)
                            batch_metadata.append({
                                'user': user,
                                'description': description,
                                'chunk_idx': chunk_idx,
                                'total_chunks': len(chunks),
                                'about': about,
                                'short_desc': short_desc,
                                'skills': skills,
                                'current_status': current_status,
                                'certificates': certificates,
                                'profile_pic': profile_pic,
                                'interests': interests
                            })
                        
                    except Exception as e:
                        logger.error(f"Failed to process user {user.uid}: {e}")
                        continue
                
                # Generate embeddings in batch
                if batch_chunks:
                    embeddings = self._get_embeddings_batch(batch_chunks)
                    
                    # Create points
                    points = []
                    for i, (embedding, metadata) in enumerate(zip(embeddings, batch_metadata)):
                        if not embedding:
                            continue
                        
                        user = metadata['user']
                        point_id = abs(hash(f"user_{user.uid}_{metadata['chunk_idx']}"))
                        
                        point = PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload={
                                "entity_type": "user",
                                "user_id": user.uid,
                                "chunk_index": metadata['chunk_idx'],
                                "total_chunks": metadata['total_chunks'],
                                "name": user.name or "",
                                "about": metadata['about'] or "",
                                "short_desc": metadata['short_desc'] or "",
                                "skills": metadata['skills'] or "",
                                "current_status": metadata['current_status'] or "",
                                "certificates": metadata['certificates'] or "",
                                "profile_link": self._construct_profile_link(user.uid),
                                "profile_pic": metadata['profile_pic'] or "",
                                "interests": metadata['interests'],
                                "created_at": user.created_at.isoformat() if user.created_at else None,
                                "indexed_at": datetime.now().isoformat()
                            }
                        )
                        points.append(point)
                    
                    # Upsert batch to Qdrant
                    if points:
                        self.qdrant_client.upsert(
                            collection_name=self.collections['users'],
                            points=points
                        )
                    
                    indexed_count += len(results)
                    total_processed += len(results)
                    
                    # Progress logging
                    if total_processed % (self.batch_size * 10) == 0:
                        elapsed = time.time() - start_time
                        rate = total_processed / elapsed if elapsed > 0 else 0
                        logger.info(f"Progress: {total_processed}/{total_count} users indexed ({rate:.1f} users/sec)")
                
                offset += self.batch_size
                
                # Check limit
                if limit and total_processed >= limit:
                    break
            
            elapsed = time.time() - start_time
            logger.info(f"Indexed {indexed_count} users in {elapsed:.1f}s ({indexed_count/elapsed:.1f} users/sec)")
            
        except Exception as e:
            logger.error(f"Failed to index users: {e}")
        finally:
            db.close()
        
        return indexed_count
    
    def index_posts(self, limit: Optional[int] = None, since: Optional[datetime] = None) -> int:
        """
        Index posts from post table into Qdrant (with pagination for scale)
        
        Args:
            limit: Maximum number of posts to index (None = all)
            since: Only index posts created/updated after this datetime
            
        Returns:
            Number of posts indexed
        """
        if not self.qdrant_available or not self.openai_available:
            logger.warning("Qdrant or OpenAI not available, cannot index posts")
            return 0
        
        db = next(get_db())
        indexed_count = 0
        total_processed = 0
        start_time = time.time()
        
        try:
            # Build base query with join to user
            base_query = db.query(Post, User).join(
                User, Post.uid == User.uid
            ).filter(Post.is_deleted == False)
            
            if since:
                base_query = base_query.filter(Post.created_at >= since)
            
            # Get total count for progress tracking
            total_count = base_query.count()
            logger.info(f"Starting to index posts (total: {total_count}, batch size: {self.batch_size})")
            
            offset = 0
            
            while True:
                # Fetch batch
                results = base_query.offset(offset).limit(self.batch_size).all()
                
                if not results:
                    break
                
                # Process batch
                batch_chunks = []
                batch_metadata = []
                
                for post, user in results:
                    try:
                        # Build searchable text
                        searchable_text = f"Post Description: {post.post_desc or ''}"
                        
                        # Chunk text if needed
                        chunks = self._chunk_text(searchable_text)
                        
                        # Store chunks and metadata for batch embedding
                        for chunk_idx, chunk in enumerate(chunks):
                            batch_chunks.append(chunk)
                            batch_metadata.append({
                                'post': post,
                                'user': user,
                                'chunk_idx': chunk_idx,
                                'total_chunks': len(chunks)
                            })
                        
                    except Exception as e:
                        logger.error(f"Failed to process post {post.post_id}: {e}")
                        continue
                
                # Generate embeddings in batch
                if batch_chunks:
                    embeddings = self._get_embeddings_batch(batch_chunks)
                    
                    # Create points
                    points = []
                    for i, (embedding, metadata) in enumerate(zip(embeddings, batch_metadata)):
                        if not embedding:
                            continue
                        
                        post = metadata['post']
                        user = metadata['user']
                        point_id = abs(hash(f"post_{post.post_id}_{metadata['chunk_idx']}"))
                        
                        point = PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload={
                                "entity_type": "post",
                                "post_id": post.post_id,
                                "chunk_index": metadata['chunk_idx'],
                                "total_chunks": metadata['total_chunks'],
                                "post_desc": post.post_desc or "",
                                "user_id": post.uid,
                                "user_name": user.name if user else "",
                                "post_link": self._construct_post_link(post.post_id),
                                "media_url": post.media_url or "",
                                "media_type": post.media_type or "",
                                "likes": post.likes or 0,
                                "comments": post.comments or 0,
                                "created_at": post.created_at.isoformat() if post.created_at else None,
                                "indexed_at": datetime.now().isoformat()
                            }
                        )
                        points.append(point)
                    
                    # Upsert batch to Qdrant
                    if points:
                        self.qdrant_client.upsert(
                            collection_name=self.collections['posts'],
                            points=points
                        )
                    
                    indexed_count += len(results)
                    total_processed += len(results)
                    
                    # Progress logging
                    if total_processed % (self.batch_size * 10) == 0:
                        elapsed = time.time() - start_time
                        rate = total_processed / elapsed if elapsed > 0 else 0
                        logger.info(f"Progress: {total_processed}/{total_count} posts indexed ({rate:.1f} posts/sec)")
                
                offset += self.batch_size
                
                # Check limit
                if limit and total_processed >= limit:
                    break
            
            elapsed = time.time() - start_time
            logger.info(f"Indexed {indexed_count} posts in {elapsed:.1f}s ({indexed_count/elapsed:.1f} posts/sec)")
            
        except Exception as e:
            logger.error(f"Failed to index posts: {e}")
        finally:
            db.close()
        
        return indexed_count
    
    def sync_all_entities(self, force: bool = False) -> Dict[str, Any]:
        """
        Main method for scheduled job - sync all entities to Qdrant (scalable for 100k+ users)
        
        Args:
            force: If True, re-index all entities regardless of timestamps
            
        Returns:
            Dictionary with statistics: jobs_indexed, users_indexed, posts_indexed
        """
        logger.info("Starting Vec Agent sync for all entities (scalable mode)")
        sync_start_time = time.time()
        
        since = None if force else datetime.now() - timedelta(days=1)
        
        # Process all entities (no limit) - pagination handles it
        jobs_indexed = self.index_jobs(limit=None, since=since)
        users_indexed = self.index_users(limit=None, since=since)
        posts_indexed = self.index_posts(limit=None, since=since)
        
        total_time = time.time() - sync_start_time
        
        result = {
            'success': True,
            'jobs_indexed': jobs_indexed,
            'users_indexed': users_indexed,
            'posts_indexed': posts_indexed,
            'total_indexed': jobs_indexed + users_indexed + posts_indexed,
            'total_time_seconds': round(total_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Vec Agent sync completed: {result}")
        return result
    
    def is_available(self) -> bool:
        """Check if agent is available (both Qdrant and OpenAI working)"""
        return self.qdrant_available and self.openai_available


# Global agent instance (lazy initialization)
_agent_instance: Optional[VecAgent] = None


def get_vec_agent() -> VecAgent:
    """Get or create global Vec agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = VecAgent()
    
    return _agent_instance
