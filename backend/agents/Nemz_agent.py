"""
Nemz Agent - AI Career Assistant
AI-powered agent that searches jobs, profiles, and posts using Qdrant vector database
"""

import os
import logging
import re
from typing import Optional, List, Dict, Any
import json

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

logger = logging.getLogger(__name__)


# System prompt for conversational AI career assistant
NEMZ_CONVERSATIONAL_PROMPT = """You are Nemz, an AI career assistant chatbot. You are friendly, helpful, and knowledgeable about careers, job searching, and professional development.

Your capabilities:
1. **Search Tool**: You can search for jobs, profiles, and posts when users ask for them
2. **Career Advice**: Provide guidance on career development, resume optimization, interview tips, and professional growth
3. **General Conversation**: Have natural, helpful conversations about careers and professional topics

When to use search:
- User explicitly asks to find/search for jobs, profiles, or posts
- User asks "show me", "find me", "look for", "get me" something
- User mentions specific skills, roles, or companies they want to find

When NOT to search:
- General questions about careers, advice, or information
- Greetings and casual conversation
- Questions about how you work or what you can do
- Requests for explanations or guidance

Search format: When you need to search, respond with:
SEARCH: [search_type] [query]
Where search_type is: "jobs", "profiles", "posts", or "all"
And query is the search terms

Example responses:
- User: "hi" -> "Hello! I'm Nemz, your AI career assistant. I can help you find jobs, connect with professionals, discover content, and get career advice. How can I assist you today?"
- User: "what can you help me with?" -> "I can help you with several things: 1) Search for job opportunities, 2) Find professionals and profiles, 3) Discover relevant posts and content, 4) Provide career advice and guidance, 5) Help with resume optimization and interview tips. What would you like to explore?"
- User: "find software engineering jobs" -> "SEARCH: jobs software engineering jobs"
- User: "show me HR professionals" -> "SEARCH: profiles HR professionals"

Be conversational, helpful, and natural. Keep responses concise but informative."""

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
        
        # Get timeout from environment or default to 150 seconds
        qdrant_timeout = float(os.environ.get('QDRANT_TIMEOUT', 150.0))
        
        try:
            if qdrant_api_key:
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    timeout=qdrant_timeout
                )
            else:
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    timeout=qdrant_timeout
                )
            
            # Test connection
            self.qdrant_client.get_collections()
            logger.info(f"Qdrant client connected to {qdrant_url} (timeout: {qdrant_timeout}s)")
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
        self.min_score_threshold = float(os.environ.get('NEMZ_MIN_SCORE_THRESHOLD', 0.0))  # Filter low-quality results
        self.deduplication_multiplier = int(os.environ.get('NEMZ_DEDUP_MULTIPLIER', 3))  # For deduplication buffer
    
    def _check_collection_exists(self, collection_name: str) -> bool:
        """
        Check if a Qdrant collection exists
        
        Args:
            collection_name: Name of the collection to check
            
        Returns:
            True if collection exists, False otherwise
        """
        if not self.qdrant_available or not self.qdrant_client:
            return False
        
        try:
            collections = self.qdrant_client.get_collections()
            existing_names = [col.name for col in collections.collections]
            return collection_name in existing_names
        except Exception as e:
            logger.error(f"Failed to check collection existence for {collection_name}: {e}")
            return False
    
    def _determine_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Determine search intent from user query using LLM
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with search_type and key_terms
        """
        # Validate query
        if not query or not isinstance(query, str) or not query.strip():
            logger.warning("Empty or invalid query provided for intent detection")
            return {"search_type": "all", "key_terms": []}
        
        query = query.strip()
        logger.debug(f"Determining intent for query: {query[:100]}...")
        
        if not self.openai_available or not self.llm:
            # Fallback: simple keyword matching
            logger.debug("Using fallback keyword matching for intent detection")
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
            
            # Validate intent structure
            if not isinstance(intent, dict):
                raise ValueError("Intent response is not a dictionary")
            
            search_type = intent.get('search_type', 'all')
            if search_type not in ['jobs', 'profiles', 'posts', 'all']:
                logger.warning(f"Invalid search_type '{search_type}', defaulting to 'all'")
                search_type = 'all'
            
            key_terms = intent.get('key_terms', [])
            if not isinstance(key_terms, list):
                key_terms = [query]
            
            logger.debug(f"Intent detected: {search_type} with key_terms: {key_terms}")
            return {"search_type": search_type, "key_terms": key_terms}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return {"search_type": "all", "key_terms": [query]}
        except ValueError as e:
            logger.error(f"Invalid intent response format: {e}")
            return {"search_type": "all", "key_terms": [query]}
        except Exception as e:
            logger.error(f"Failed to determine query intent: {e}", exc_info=True)
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
            logger.warning(f"Cannot search {collection_name}: Qdrant not available")
            return []
        
        # Validate inputs
        if not query_embedding or not isinstance(query_embedding, list):
            logger.error(f"Invalid query embedding provided for {collection_name}")
            return []
        
        if limit <= 0:
            logger.warning(f"Invalid limit {limit}, using default 10")
            limit = 10
        
        # Check if collection exists
        if not self._check_collection_exists(collection_name):
            logger.warning(f"Collection {collection_name} does not exist")
            return []
        
        try:
            logger.debug(f"Searching collection {collection_name} with limit {limit}")
            
            # Use query_points method (correct API for qdrant-client >= 1.7.0)
            # query_points accepts the vector directly as a list of floats
            query_response = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=query_embedding,  # Pass vector directly as list of floats
                limit=limit * self.deduplication_multiplier,  # Get more results for deduplication
                with_payload=True,
                with_vectors=False
            )
            
            results = []
            seen_entities = {}  # For deduplication: entity_id -> best match
            
            # query_points returns a QueryResponse with points
            if not hasattr(query_response, 'points') or not query_response.points:
                logger.debug(f"No points returned from {collection_name}")
                return []
            
            logger.debug(f"Received {len(query_response.points)} points from {collection_name}")
            
            for point in query_response.points:
                if not hasattr(point, 'payload') or not point.payload:
                    logger.debug(f"Skipping point without payload")
                    continue
                
                payload = point.payload
                entity_type = payload.get('entity_type', '')
                
                # Determine entity ID based on type
                if entity_type == 'job':
                    entity_id = payload.get('job_id')
                elif entity_type == 'user':
                    entity_id = payload.get('user_id')
                elif entity_type == 'post':
                    entity_id = payload.get('post_id')
                else:
                    logger.debug(f"Skipping point with unknown entity_type: {entity_type}")
                    continue
                
                if entity_id is None:
                    logger.debug(f"Skipping point with missing entity_id for type {entity_type}")
                    continue
                
                # Get score from point - handle different response structures
                # Qdrant query_points returns scores in different formats depending on version
                score = 0.0
                
                # Try multiple ways to extract score
                if hasattr(point, 'score') and point.score is not None:
                    score = float(point.score)
                    logger.debug(f"Extracted score from point.score: {score}")
                elif hasattr(point, 'distance') and point.distance is not None:
                    # Some Qdrant versions return distance instead of score
                    # Convert distance to similarity score (1 - distance for cosine)
                    distance = float(point.distance)
                    score = max(0.0, 1.0 - distance) if distance <= 1.0 else 0.0
                    logger.debug(f"Converted distance {distance} to score: {score}")
                elif isinstance(point, dict):
                    if 'score' in point:
                        score = float(point['score'])
                    elif 'distance' in point:
                        distance = float(point['distance'])
                        score = max(0.0, 1.0 - distance) if distance <= 1.0 else 0.0
                else:
                    # Try accessing as attribute with getattr
                    score = getattr(point, 'score', None)
                    if score is None:
                        score = getattr(point, 'distance', None)
                        if score is not None:
                            score = max(0.0, 1.0 - float(score)) if float(score) <= 1.0 else 0.0
                    else:
                        score = float(score)
                
                # Ensure score is a valid float
                try:
                    score = float(score)
                    if score < 0.0 or score > 1.0:
                        logger.warning(f"Score {score} out of range [0, 1], clamping")
                        score = max(0.0, min(1.0, score))
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert score to float: {score}, using 0.0")
                    score = 0.0
                
                logger.debug(f"Final score for entity {entity_type}_{entity_id}: {score}")
                
                # Filter by minimum score threshold
                if score < self.min_score_threshold:
                    logger.debug(f"Filtering result with score {score} below threshold {self.min_score_threshold}")
                    continue
                
                # Deduplicate: keep best match score per entity
                entity_key = f"{entity_type}_{entity_id}"
                if entity_key not in seen_entities:
                    seen_entities[entity_key] = {
                        'score': score,
                        'payload': payload
                    }
                else:
                    # Keep the chunk with highest score
                    if score > seen_entities[entity_key]['score']:
                        seen_entities[entity_key] = {
                            'score': score,
                            'payload': payload
                        }
            
            # Convert to results list, sorted by score, filtered by threshold
            sorted_entities = sorted(
                seen_entities.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            # Apply limit and filter by score threshold
            for entity_key, data in sorted_entities[:limit]:
                if data['score'] >= self.min_score_threshold:
                    results.append({
                        'match_score': data['score'],
                        **data['payload']
                    })
            
            logger.info(f"Found {len(results)} results from {collection_name} (filtered from {len(seen_entities)} unique entities)")
            return results
            
        except KeyError as e:
            logger.error(f"Collection {collection_name} key error: {e}", exc_info=True)
            return []
        except AttributeError as e:
            logger.error(f"Collection {collection_name} attribute error: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Failed to search collection {collection_name}: {e}", exc_info=True)
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
        # Validate inputs
        if not query or not isinstance(query, str) or not query.strip():
            logger.warning("Empty or invalid query provided for job search")
            return []
        
        if limit <= 0:
            logger.warning(f"Invalid limit {limit} for job search, using default")
            limit = self.search_limit
        
        query = query.strip()
        
        # Refine query to extract key terms
        refined_query = self._refine_search_query(query)
        
        logger.info(f"Searching jobs with query: '{query[:100]}...' (refined: '{refined_query[:100]}...', limit: {limit})")
        
        if not self.openai_available or not self.embeddings:
            logger.warning("OpenAI not available, cannot generate embeddings for job search")
            return []
        
        try:
            # Generate query embedding using refined query
            logger.debug("Generating embedding for job search query")
            query_embedding = self.embeddings.embed_query(refined_query)
            
            if not query_embedding or len(query_embedding) == 0:
                logger.error("Failed to generate embedding for job search")
                return []
            
            # Search jobs collection
            results = self._search_collection(
                collection_name=self.collections['jobs'],
                query_embedding=query_embedding,
                limit=limit
            )
            
            logger.info(f"Job search completed: {len(results)} results for query: '{query[:50]}...'")
            return results
            
        except ValueError as e:
            logger.error(f"Invalid input for job search: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to search jobs: {e}", exc_info=True)
            return []
    
    def _expand_abbreviations(self, query: str) -> str:
        """
        Expand common tech/career abbreviations to full terms for better semantic matching
        
        Args:
            query: Query string with potential abbreviations
            
        Returns:
            Query with abbreviations expanded
        """
        # Dictionary of common abbreviations and their expansions
        abbreviations = {
            # Tech roles
            'swe': 'software engineer software engineering',
            'sw eng': 'software engineer software engineering',
            'dev': 'developer development',
            'sde': 'software development engineer',
            'sre': 'site reliability engineer',
            'qa': 'quality assurance tester testing',
            'qe': 'quality engineer',
            'pm': 'product manager project manager',
            'em': 'engineering manager',
            'tpm': 'technical program manager',
            'po': 'product owner',
            'ba': 'business analyst',
            'da': 'data analyst',
            'ds': 'data scientist',
            'ml eng': 'machine learning engineer',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'de': 'data engineer',
            'devops': 'development operations',
            'sdet': 'software development engineer in test',
            
            # Design roles
            'ui/ux': 'user interface user experience',
            'ui': 'user interface',
            'ux': 'user experience',
            'designer': 'ui ux designer',
            
            # Other common terms
            'hr': 'human resources',
            'recruiter': 'talent acquisition hr',
            'sales': 'sales representative account executive',
            'marketing': 'digital marketing content marketing',
            'finance': 'financial analyst accountant',
            'legal': 'attorney lawyer',
            'ops': 'operations',
            'it': 'information technology',
            'infra': 'infrastructure',
            'sec': 'security cybersecurity',
            'cyber': 'cybersecurity',
            
            # Technologies
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'java': 'java programming',
            'cpp': 'c++',
            'c#': 'csharp',
            'sql': 'database sql',
            'nosql': 'mongodb cassandra',
            'aws': 'amazon web services cloud',
            'gcp': 'google cloud platform',
            'azure': 'microsoft azure cloud',
            'k8s': 'kubernetes',
            'docker': 'containerization',
            'kafka': 'apache kafka messaging',
            'react': 'react.js frontend',
            'vue': 'vue.js frontend',
            'angular': 'angular.js frontend',
            'node': 'node.js backend',
            'spring': 'spring framework java',
            'django': 'django python',
            'flask': 'flask python',
        }
        
        query_lower = query.lower()
        expanded_query = query_lower
        
        # Expand abbreviations (case-insensitive, whole word matching)
        for abbrev, expansion in abbreviations.items():
            # Match whole word abbreviations (with word boundaries)
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            if re.search(pattern, expanded_query, re.IGNORECASE):
                # Replace abbreviation with both original and expansion
                expanded_query = re.sub(pattern, f'{abbrev} {expansion}', expanded_query, flags=re.IGNORECASE)
                logger.debug(f"Expanded abbreviation '{abbrev}' to '{abbrev} {expansion}'")
        
        # Also handle common word concatenation issues (e.g., "expertisein" -> "expertise in")
        # Split common compound words that might be missing spaces
        word_splits = {
            'expertisein': 'expertise in',
            'expertisewith': 'expertise with',
            'skillin': 'skill in',
            'skillwith': 'skill with',
            'experiencein': 'experience in',
            'experiencewith': 'experience with',
        }
        for compound, split in word_splits.items():
            if compound in expanded_query.lower():
                expanded_query = re.sub(re.escape(compound), split, expanded_query, flags=re.IGNORECASE)
                logger.debug(f"Split compound word '{compound}' to '{split}'")
        
        return expanded_query
    
    def _enhance_query_with_llm(self, query: str) -> str:
        """
        Use LLM to enhance query for better semantic search understanding
        
        Args:
            query: Original user query
            
        Returns:
            Enhanced query optimized for semantic search
        """
        if not self.openai_available or not self.llm:
            return query
        
        try:
            enhancement_prompt = f"""You are a search query optimizer. Your task is to rewrite the user's search query to maximize semantic search effectiveness while preserving the original intent.

Original query: "{query}"

Rewrite the query to:
1. Keep all important technical terms, skills, and keywords
2. Expand abbreviations naturally (e.g., "SWE" -> "software engineer", "Java" -> "Java programming")
3. Add synonyms for better matching (e.g., "expertise" -> "expertise skills experience")
4. Preserve the search intent (finding profiles/jobs/posts with specific skills/expertise)
5. Make it more search-friendly while keeping it natural

Return ONLY the enhanced query text, nothing else. Do not add explanations or JSON formatting."""

            messages = [
                SystemMessage(content="You are a search query optimizer. Return only the enhanced query text."),
                HumanMessage(content=enhancement_prompt)
            ]
            
            response = self.llm.invoke(messages)
            enhanced_query = response.content.strip()
            
            # Clean up any markdown formatting if present
            if "```" in enhanced_query:
                enhanced_query = enhanced_query.split("```")[1].split("```")[0].strip()
            
            logger.debug(f"LLM enhanced query: '{query}' -> '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            logger.warning(f"Failed to enhance query with LLM: {e}, using original query")
            return query
    
    def _refine_search_query(self, query: str, use_llm_enhancement: bool = True) -> str:
        """
        Refine search query by extracting key terms and removing conversational phrases
        
        Args:
            query: Original user query
            use_llm_enhancement: Whether to use LLM to enhance the query for better semantic matching
            
        Returns:
            Refined query string with key terms
        """
        query_lower = query.lower().strip()
        
        # First, expand abbreviations
        expanded = self._expand_abbreviations(query_lower)
        
        # Use LLM to enhance query for better semantic understanding
        if use_llm_enhancement:
            enhanced = self._enhance_query_with_llm(expanded)
        else:
            enhanced = expanded
        
        # Remove only the most common conversational phrases (be less aggressive)
        # Keep important words like "expertise", "with", "in", "skills", etc.
        phrases_to_remove = [
            'can you find me',
            'can you search for',
            'can you show me',
            'i want to find',
            'i need',
            'i am looking for',
            'find me',
            'show me',
            'search for',
            'a profile',
            'profiles',
            'a job',
            'jobs',
            'a post',
            'posts'
        ]
        
        refined = enhanced.lower()
        for phrase in phrases_to_remove:
            refined = refined.replace(phrase, ' ').strip()
        
        # Clean up multiple spaces but preserve important words
        refined = ' '.join(refined.split())
        
        # If query becomes too short or empty, use enhanced version or original
        if len(refined) < 2:
            refined = enhanced if len(enhanced) >= 2 else query.strip()
        
        logger.debug(f"Refined query: '{query}' -> '{refined}'")
        return refined
    
    def search_profiles(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for user profiles matching the query
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of profile results with match scores
        """
        # Validate inputs
        if not query or not isinstance(query, str) or not query.strip():
            logger.warning("Empty or invalid query provided for profile search")
            return []
        
        if limit <= 0:
            logger.warning(f"Invalid limit {limit} for profile search, using default")
            limit = self.search_limit
        
        query = query.strip()
        
        # Refine query to extract key terms
        refined_query = self._refine_search_query(query)
        
        logger.info(f"Searching profiles with query: '{query[:100]}...' (refined: '{refined_query[:100]}...', limit: {limit})")
        
        if not self.openai_available or not self.embeddings:
            logger.warning("OpenAI not available, cannot generate embeddings for profile search")
            return []
        
        try:
            # Generate query embedding using refined query
            logger.debug("Generating embedding for profile search query")
            query_embedding = self.embeddings.embed_query(refined_query)
            
            if not query_embedding or len(query_embedding) == 0:
                logger.error("Failed to generate embedding for profile search")
                return []
            
            # Search users collection
            results = self._search_collection(
                collection_name=self.collections['users'],
                query_embedding=query_embedding,
                limit=limit
            )
            
            logger.info(f"Profile search completed: {len(results)} results for query: '{query[:50]}...'")
            return results
            
        except ValueError as e:
            logger.error(f"Invalid input for profile search: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to search profiles: {e}", exc_info=True)
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
        # Validate inputs
        if not query or not isinstance(query, str) or not query.strip():
            logger.warning("Empty or invalid query provided for post search")
            return []
        
        if limit <= 0:
            logger.warning(f"Invalid limit {limit} for post search, using default")
            limit = self.search_limit
        
        query = query.strip()
        
        # Refine query to extract key terms
        refined_query = self._refine_search_query(query)
        
        logger.info(f"Searching posts with query: '{query[:100]}...' (refined: '{refined_query[:100]}...', limit: {limit})")
        
        if not self.openai_available or not self.embeddings:
            logger.warning("OpenAI not available, cannot generate embeddings for post search")
            return []
        
        try:
            # Generate query embedding using refined query
            logger.debug("Generating embedding for post search query")
            query_embedding = self.embeddings.embed_query(refined_query)
            
            if not query_embedding or len(query_embedding) == 0:
                logger.error("Failed to generate embedding for post search")
                return []
            
            # Search posts collection
            results = self._search_collection(
                collection_name=self.collections['posts'],
                query_embedding=query_embedding,
                limit=limit
            )
            
            logger.info(f"Post search completed: {len(results)} results for query: '{query[:50]}...'")
            return results
            
        except ValueError as e:
            logger.error(f"Invalid input for post search: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to search posts: {e}", exc_info=True)
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
        # Validate inputs
        if not user_query or not isinstance(user_query, str) or not user_query.strip():
            logger.warning("Empty or invalid user_query provided to process_query")
            return {
                'query': user_query or '',
                'search_type': search_type or 'all',
                'jobs': [],
                'profiles': [],
                'posts': [],
                'total_results': 0,
                'error': 'Invalid query provided'
            }
        
        user_query = user_query.strip()
        
        if limit <= 0:
            logger.warning(f"Invalid limit {limit}, using default {self.search_limit}")
            limit = self.search_limit
        
        # Validate search_type if provided
        if search_type and search_type not in ['jobs', 'profiles', 'posts', 'all']:
            logger.warning(f"Invalid search_type '{search_type}', will auto-detect")
            search_type = None
        
        logger.info(f"Processing query: '{user_query[:100]}...' (type: {search_type or 'auto'}, limit: {limit})")
        
        if not search_type:
            # Determine intent from query
            intent = self._determine_query_intent(user_query)
            search_type = intent.get('search_type', 'all')
            logger.debug(f"Auto-detected search_type: {search_type}")
        
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
        
        if not search_types:
            logger.warning(f"No valid search types determined for query: {user_query}")
            return results
        
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
    
    def _get_zed_context(self, user_id: int) -> Optional[str]:
        """
        Retrieve Zed context from database for the logged-in user
        
        Args:
            user_id: User ID to retrieve context for
            
        Returns:
            Zed context text or None if not found
        """
        try:
            from config.database_orm import get_db
            from models.orm.users_context import UsersContext
            from sqlalchemy.orm import Session
            
            # Use ORM for database access
            db: Session = next(get_db())
            try:
                users_context = db.query(UsersContext).filter(
                    UsersContext.user_id == user_id
                ).first()
                
                if users_context and users_context.zed:
                    context_length = len(users_context.zed)
                    logger.info(f"Retrieved Zed context for user_id={user_id} ({context_length} chars)")
                    return users_context.zed
                
                logger.debug(f"No Zed context found for user_id={user_id}")
                return None
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Failed to retrieve Zed context for user_id={user_id}: {e}", exc_info=True)
            return None
    
    def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Have a conversational chat with the user. The LLM decides when to use search.
        
        Args:
            user_message: User's message
            conversation_history: Optional list of previous messages in format [{"role": "user/assistant", "content": "..."}]
            user_id: Optional user ID to fetch Zed context (only used if user is logged in)
            
        Returns:
            Dictionary with:
            - response: The conversational response
            - should_search: Boolean indicating if search should be performed
            - search_type: If should_search is True, the type of search ("jobs", "profiles", "posts", "all")
            - search_query: If should_search is True, the search query to use
        """
        if not self.openai_available or not self.llm:
            return {
                "response": "I'm currently unavailable. Please check the system configuration.",
                "should_search": False,
                "search_type": None,
                "search_query": None
            }
        
        try:
            # Get Zed context if user is logged in
            zed_context = None
            if user_id:
                zed_context = self._get_zed_context(user_id)
            
            # Build system prompt with user context if available
            system_prompt = NEMZ_CONVERSATIONAL_PROMPT
            if zed_context:
                # Append user context to system prompt
                # This context is only available when user is logged in
                system_prompt += f"""

## User Context (from Zed Agent):
{zed_context}

IMPORTANT: Use this context to provide personalized responses. You have access to the user's profile, skills, interests, preferences, and activity history. Reference this information naturally in your responses when relevant. For example:
- If asked "what do you know about me?", summarize relevant information from the context
- When suggesting jobs or courses, consider their skills and interests
- When providing career advice, reference their experience and goals
- Only use this context while the user is logged in (which they are, since you're receiving it)
"""
            
            # Build conversation history
            messages = [SystemMessage(content=system_prompt)]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))
            
            # Add current user message
            messages.append(HumanMessage(content=user_message))
            
            # Get LLM response
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Check if response contains search command
            should_search = False
            search_type = None
            search_query = None
            
            if response_text.startswith("SEARCH:"):
                # Parse search command: "SEARCH: [type] [query]"
                parts = response_text[7:].strip().split(" ", 1)  # Remove "SEARCH:" and split
                if len(parts) >= 1:
                    search_type = parts[0].lower()
                    search_query = parts[1] if len(parts) > 1 else user_message
                    
                    # Validate search type
                    if search_type not in ["jobs", "profiles", "posts", "all"]:
                        search_type = "all"
                    
                    should_search = True
                    # Return conversational response that will be followed by search results
                    response_text = f"I'll search for {search_type} matching '{search_query}'..."
                else:
                    # Invalid search format, treat as normal response
                    logger.warning(f"Invalid search format in response: {response_text}")
            
            return {
                "response": response_text,
                "should_search": should_search,
                "search_type": search_type,
                "search_query": search_query or user_message
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "should_search": False,
                "search_type": None,
                "search_query": None
            }


# Global agent instance (lazy initialization)
_agent_instance: Optional[NemzAgent] = None


def get_nemz_agent() -> NemzAgent:
    """Get or create global Nemz agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = NemzAgent()
    
    return _agent_instance
