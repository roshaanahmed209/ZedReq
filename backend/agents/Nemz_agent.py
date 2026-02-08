"""
Nemz Agent - AI Career Assistant
AI-powered agent that searches jobs, profiles, and posts using Qdrant vector database
"""

import os
import logging
from typing import Optional, List, Dict, Any
import json

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

logger = logging.getLogger(__name__)


# System prompt for query intent detection
QUERY_INTENT_PROMPT = """You are an AI assistant that determines the intent of user queries for a career assistant system.

The user can search for:
1. Jobs - job postings, career opportunities, positions
2. Profiles - user profiles, people, professionals, HR, recruiters
3. Posts - social media posts, content, discussions

Analyze the user query and determine:
- search_type: "jobs", "profiles", "posts", or "all" if unclear
- key_terms: Important keywords and phrases for the search

Return ONLY a JSON object with:
{
    "search_type": "jobs" | "profiles" | "posts" | "all",
    "key_terms": ["keyword1", "keyword2", ...]
}

Example queries:
- "find mechanical engineering jobs" -> {"search_type": "jobs", "key_terms": ["mechanical engineering"]}
- "I'm looking for HR professionals" -> {"search_type": "profiles", "key_terms": ["HR", "human resources"]}
- "show me posts about AI" -> {"search_type": "posts", "key_terms": ["AI", "artificial intelligence"]}
"""


class NemzAgent:
    """AI Agent for searching jobs, profiles, and posts using Qdrant vector database"""
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini"
    ):
        """
        Initialize Nemz Agent with Qdrant and OpenAI clients
        
        Args:
            qdrant_url: Qdrant server URL (default: from env or localhost)
            qdrant_api_key: Qdrant API key (optional)
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use
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
            logger.warning("OpenAI API key not found. Search will not work.")
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
        self.collections = {
            'jobs': 'nemz_jobs',
            'users': 'nemz_users',
            'posts': 'nemz_posts'
        }
        self.search_limit = int(os.environ.get('NEMZ_SEARCH_LIMIT', 10))
    
    def _determine_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Determine search intent from user query using LLM
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with search_type and key_terms
        """
        if not self.openai_available or not self.llm:
            # Fallback: simple keyword matching
            query_lower = query.lower()
            if any(word in query_lower for word in ['job', 'position', 'career', 'hiring', 'vacancy']):
                return {"search_type": "jobs", "key_terms": [query]}
            elif any(word in query_lower for word in ['profile', 'person', 'people', 'user', 'hr', 'recruiter']):
                return {"search_type": "profiles", "key_terms": [query]}
            elif any(word in query_lower for word in ['post', 'content', 'discussion']):
                return {"search_type": "posts", "key_terms": [query]}
            else:
                return {"search_type": "all", "key_terms": [query]}
        
        try:
            messages = [
                SystemMessage(content=QUERY_INTENT_PROMPT),
                HumanMessage(content=f"User query: {query}")
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            intent = json.loads(content)
            return intent
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return {"search_type": "all", "key_terms": [query]}
        except Exception as e:
            logger.error(f"Failed to determine query intent: {e}")
            return {"search_type": "all", "key_terms": [query]}
    
    def _search_collection(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search a Qdrant collection with query embedding
        
        Args:
            collection_name: Name of the Qdrant collection
            query_embedding: Query embedding vector
            limit: Maximum number of results
            
        Returns:
            List of search results with scores
        """
        if not self.qdrant_available or not self.qdrant_client:
            return []
        
        try:
            search_results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit * 3  # Get more results to account for deduplication
            )
            
            results = []
            seen_entities = {}  # For deduplication: entity_id -> best match
            
            for result in search_results:
                payload = result.payload
                entity_type = payload.get('entity_type', '')
                
                # Determine entity ID based on type
                if entity_type == 'job':
                    entity_id = payload.get('job_id')
                elif entity_type == 'user':
                    entity_id = payload.get('user_id')
                elif entity_type == 'post':
                    entity_id = payload.get('post_id')
                else:
                    continue
                
                if entity_id is None:
                    continue
                
                # Deduplicate: keep best match score per entity
                entity_key = f"{entity_type}_{entity_id}"
                if entity_key not in seen_entities:
                    seen_entities[entity_key] = {
                        'score': result.score,
                        'payload': payload
                    }
                else:
                    # Keep the chunk with highest score
                    if result.score > seen_entities[entity_key]['score']:
                        seen_entities[entity_key] = {
                            'score': result.score,
                            'payload': payload
                        }
            
            # Convert to results list, sorted by score
            for entity_key, data in sorted(
                seen_entities.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )[:limit]:
                results.append({
                    'match_score': data['score'],
                    **data['payload']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search collection {collection_name}: {e}")
            return []
    
    def search_jobs(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for jobs matching the query
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of job results with match scores
        """
        if not self.openai_available or not self.embeddings:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search jobs collection
            results = self._search_collection(
                collection_name=self.collections['jobs'],
                query_embedding=query_embedding,
                limit=limit
            )
            
            logger.info(f"Found {len(results)} jobs matching query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search jobs: {e}")
            return []
    
    def search_profiles(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for user profiles matching the query
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of profile results with match scores
        """
        if not self.openai_available or not self.embeddings:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search users collection
            results = self._search_collection(
                collection_name=self.collections['users'],
                query_embedding=query_embedding,
                limit=limit
            )
            
            logger.info(f"Found {len(results)} profiles matching query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search profiles: {e}")
            return []
    
    def search_posts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for posts matching the query
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of post results with match scores
        """
        if not self.openai_available or not self.embeddings:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search posts collection
            results = self._search_collection(
                collection_name=self.collections['posts'],
                query_embedding=query_embedding,
                limit=limit
            )
            
            logger.info(f"Found {len(results)} posts matching query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search posts: {e}")
            return []
    
    def process_query(
        self,
        user_query: str,
        search_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Process user query and return search results
        
        Args:
            user_query: User's search query
            search_type: Optional explicit search type ("jobs", "profiles", "posts")
            limit: Maximum results per type
            
        Returns:
            Dictionary with search results and metadata
        """
        if not search_type:
            # Determine intent from query
            intent = self._determine_query_intent(user_query)
            search_type = intent.get('search_type', 'all')
        
        results = {
            'query': user_query,
            'search_type': search_type,
            'jobs': [],
            'profiles': [],
            'posts': [],
            'total_results': 0
        }
        
        # Determine which searches to perform
        search_types = []
        if search_type in ['jobs', 'all']:
            search_types.append('jobs')
        if search_type in ['profiles', 'all']:
            search_types.append('profiles')
        if search_type in ['posts', 'all']:
            search_types.append('posts')
        
        # If multiple search types, parallelize them
        if len(search_types) > 1:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import os
            
            max_workers = int(os.environ.get('NEMZ_SEARCH_MAX_WORKERS', 3))
            
            def search_jobs_wrapper():
                return self.search_jobs(user_query, limit=limit)
            
            def search_profiles_wrapper():
                return self.search_profiles(user_query, limit=limit)
            
            def search_posts_wrapper():
                return self.search_posts(user_query, limit=limit)
            
            # Map search types to functions
            search_functions = {
                'jobs': search_jobs_wrapper,
                'profiles': search_profiles_wrapper,
                'posts': search_posts_wrapper
            }
            
            # Execute searches in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_type = {
                    executor.submit(search_functions[st]): st
                    for st in search_types
                }
                
                for future in as_completed(future_to_type):
                    search_type_name = future_to_type[future]
                    try:
                        search_results = future.result()
                        results[search_type_name] = search_results
                    except Exception as e:
                        logger.error(f"Error in {search_type_name} search: {e}")
                        results[search_type_name] = []
        else:
            # Single search type, execute sequentially
            if 'jobs' in search_types:
                results['jobs'] = self.search_jobs(user_query, limit=limit)
            if 'profiles' in search_types:
                results['profiles'] = self.search_profiles(user_query, limit=limit)
            if 'posts' in search_types:
                results['posts'] = self.search_posts(user_query, limit=limit)
        
        results['total_results'] = (
            len(results['jobs']) +
            len(results['profiles']) +
            len(results['posts'])
        )
        
        return results
    
    def is_available(self) -> bool:
        """Check if agent is available (both Qdrant and OpenAI working)"""
        return self.qdrant_available and self.openai_available


# Global agent instance (lazy initialization)
_agent_instance: Optional[NemzAgent] = None


def get_nemz_agent() -> NemzAgent:
    """Get or create global Nemz agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = NemzAgent()
    
    return _agent_instance
