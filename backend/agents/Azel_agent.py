"""
Azel Agent - Question Generation from User Context
AI-powered agent that uses Zed's context to generate course questions via Google search and Qdrant knowledge base
"""

import os
import logging
import hashlib
import uuid
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import time

from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PointIdsList
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config.database import get_connection_params, Database
from config.database_orm import get_db
from models.orm.azel_search_url import AzelSearchUrl
from models.orm.lms_question import LMSQuestion
from utils.api_security import normalize_env_secret

logger = logging.getLogger(__name__)


# System prompt for extracting highlighted topics
EXTRACT_TOPICS_PROMPT = """You are an AI assistant that extracts highlighted topics of interest from user context.

The context provided contains information about a user's interests, with specific topics that are highlighted or emphasized. Your task is to:

1. Identify the topics that are most highlighted or emphasized in the context
2. Extract these topics as a list of searchable keywords/phrases
3. Focus on topics that are relevant to educational content and course material
4. Return a JSON array of topic strings

Example output format:
["Python programming", "Machine Learning basics", "Data structures", "Web development"]

Return ONLY the JSON array, no additional text."""


# System prompt for question generation
QUESTION_GENERATION_PROMPT = """You are an expert educational content creator. Generate high-quality questions that test understanding and knowledge retention.

CRITICAL RULE: Every question you generate MUST be directly about the COURSE SUBJECT specified in the prompt. The user's highlighted topics are provided only to personalise questions within the course scope — they must NEVER cause you to generate questions about unrelated subjects.

Based on the course subject, the user's relevant topics, and the knowledge base content, create questions that:
1. Are strictly about the course subject
2. Use the user's interests to personalise examples (only when relevant to the course)
3. Test understanding of key concepts within the course scope
4. Are clear and unambiguous
5. Have detailed, comprehensive answers
6. Match the specified difficulty level (Basic, Intermediate, or Expert)

Difficulty guidelines:
- **Basic**: Definitions, recall, simple true/false, straightforward multiple choice.
- **Intermediate**: Application of concepts, compare/contrast, scenario-based questions.
- **Expert**: Analysis, synthesis, multi-step reasoning, open-ended expert-level problems.

For each question, provide:
- question_text: The question itself
- question_type: "multiple_choice", "text", or "true_false"
- options: For multiple_choice, provide {"A": "...", "B": "...", "C": "...", "D": "..."}
- correct_answer: The correct answer (for multiple_choice: "A", "B", "C", or "D"; for text: a detailed answer; for true_false: "True" or "False")
- explanation: A detailed explanation of why the answer is correct
- points: Points value (default: 1)

Return a JSON array of question objects. Generate 3-5 questions focusing on the highlighted topics."""


class AzelAgent:
    """AI Agent for generating questions from Zed context using web search (DuckDuckGo) and Qdrant knowledge base"""
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini"
    ):
        """
        Initialize Azel Agent with Qdrant and OpenAI clients
        
        Args:
            qdrant_url: Qdrant server URL (default: from env or localhost)
            qdrant_api_key: Qdrant API key (optional)
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use
        """
        # Initialize Qdrant client
        qdrant_url = qdrant_url or os.environ.get('QDRANT_URL')
        qdrant_api_key = qdrant_api_key or os.environ.get('QDRANT_API_KEY')
        
        try:
            # Get timeout from environment or default to 150 seconds
            qdrant_timeout = float(os.environ.get('QDRANT_TIMEOUT', 150.0))
            
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
            logger.info(f"Qdrant client connected to {qdrant_url}")
            self.qdrant_available = True
        except Exception as e:
            logger.warning(f"Qdrant not available: {e}")
            self.qdrant_client = None
            self.qdrant_available = False
        
        # Initialize OpenAI API key (normalize: hosting UIs often add whitespace/quotes)
        openai_api_key = openai_api_key or normalize_env_secret(os.environ.get("OPENAI_API_KEY"))
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Question generation will not work.")
            self.openai_available = False
        else:
            self.openai_available = True
        
        # Initialize LangChain OpenAI clients
        if self.openai_available:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.7,
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
        self.kb_ttl_minutes = 30  # Fixed 30-minute TTL
        self.max_search_results = int(os.environ.get('AZEL_MAX_SEARCH_RESULTS', 10))
        self.questions_per_course = int(os.environ.get('AZEL_QUESTIONS_PER_COURSE', 20))
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small dimension
    
    def _get_zed_context(self, user_id: int) -> Optional[str]:
        """
        Retrieve Zed context from database
        
        Args:
            user_id: User ID to retrieve context for
            
        Returns:
            Zed context text or None if not found
        """
        try:
            db = Database(get_connection_params())
            result = db.fetch_one(
                "SELECT zed FROM users_context WHERE user_id = %s",
                (user_id,)
            )
            db.close()
            
            if result and result.get('zed'):
                return result['zed']
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve Zed context for user_id={user_id}: {e}")
            return None
    
    def _extract_highlighted_topics(self, context: str, course_id: int, course_title: Optional[str] = None) -> List[str]:
        """
        Extract highlighted topics of interest from Zed context, filtered to
        be relevant to the given course subject.

        First tries to parse the structured "Preferred Topics" section,
        then falls back to LLM extraction if structured format not found.
        When a course_title is provided the LLM is asked to return only
        topics that are relevant to that course.
        
        Args:
            context: Zed context text containing highlighted topics
            course_id: Course ID for context
            course_title: Optional course title to scope topics
            
        Returns:
            List of highlighted topics (top 5 from "Highlighted Topics" section)
        """
        # Try to parse structured "Preferred Topics" section first
        topics = self._parse_structured_topics(context)
        
        if topics:
            logger.info(f"Extracted {len(topics)} highlighted topics from structured section for course_id={course_id}")
            # If we have a course title, filter topics to only those relevant
            if course_title and self.openai_available and self.llm:
                topics = self._filter_topics_for_course(topics, course_title)
            return topics
        
        # Fallback to LLM extraction if structured format not found
        logger.info(f"Structured topics not found, falling back to LLM extraction for course_id={course_id}")
        return self._extract_topics_with_llm(context, course_id, course_title=course_title)
    
    def _parse_structured_topics(self, context: str) -> List[str]:
        """
        Parse the structured "Preferred Topics" section from zed context.
        Looks for "**Highlighted Topics (Top 5 Most Preferred):**" section.
        
        Args:
            context: Zed context text
            
        Returns:
            List of topic names extracted from the structured section, or empty list if not found
        """
        try:
            # Find the "Preferred Topics" section
            # Look for "### Preferred Topics" or "**Highlighted Topics (Top 5 Most Preferred):**"
            preferred_topics_pattern = r'(?:###\s*Preferred\s+Topics|Preferred\s+Topics\s*\(REQUIRED\s+SECTION\)|Highlighted\s+Topics\s*\(Top\s+5\s+Most\s+Preferred\))'
            
            # Find the section
            section_match = re.search(preferred_topics_pattern, context, re.IGNORECASE)
            if not section_match:
                return []
            
            # Extract text after the section header
            section_start = section_match.end()
            section_text = context[section_start:]
            
            # Look for "Highlighted Topics (Top 5 Most Preferred):" specifically
            highlighted_pattern = r'\*\*Highlighted\s+Topics\s*\(Top\s+5\s+Most\s+Preferred\):\*\*'
            highlighted_match = re.search(highlighted_pattern, section_text, re.IGNORECASE)
            
            if not highlighted_match:
                return []
            
            # Extract the highlighted topics section
            highlighted_start = highlighted_match.end()
            # Find where "Extra Topics" section starts (or end of document)
            extra_pattern = r'\*\*Extra\s+Topics|###\s*[A-Z]'
            extra_match = re.search(extra_pattern, section_text[highlighted_start:], re.IGNORECASE)
            
            if extra_match:
                highlighted_section = section_text[highlighted_start:highlighted_start + extra_match.start()]
            else:
                # Take next 2000 characters if no extra section found
                highlighted_section = section_text[highlighted_start:highlighted_start + 2000]
            
            # Extract topic names from numbered list items
            # Pattern: "1. **Topic Name** - description" or "1. Topic Name - description"
            topics = []
            for line in highlighted_section.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Match lines starting with number and period (e.g., "1. **Topic** -" or "1. Topic -")
                numbered_item_match = re.match(r'^\d+\.\s*(.+?)(?:\s*-\s*|$)', line)
                if numbered_item_match:
                    topic_text = numbered_item_match.group(1).strip()
                    
                    # Extract bold text if present (format: **Topic Name**)
                    bold_match = re.match(r'\*\*([^*]+)\*\*', topic_text)
                    if bold_match:
                        topic = bold_match.group(1).strip()
                    else:
                        # If no bold, take text before dash or first part
                        topic = topic_text.split('-')[0].strip() if '-' in topic_text else topic_text.strip()
                    
                    # Clean up any remaining markdown
                    topic = re.sub(r'\*\*', '', topic)
                    topic = topic.strip()
                    
                    if topic and len(topic) > 2:  # Filter out very short matches
                        topics.append(topic)
            
            # Return top 5 topics (or all if less than 5)
            return topics[:5] if topics else []
            
        except Exception as e:
            logger.warning(f"Failed to parse structured topics: {e}")
            return []
    
    def _filter_topics_for_course(self, topics: List[str], course_title: str) -> List[str]:
        """Filter a list of user-interest topics to only those relevant to the course.

        If none of the user's topics match the course subject at all, the LLM
        generates course-specific sub-topics instead so that the pipeline always
        has something relevant to search for.
        """
        try:
            prompt = (
                f"Course title: \"{course_title}\"\n\n"
                f"User's highlighted topics: {json.dumps(topics)}\n\n"
                f"Return a JSON array containing ONLY the topics from the list above "
                f"that are directly relevant to the course \"{course_title}\".\n"
                f"If NONE of the topics are relevant, generate 3-5 sub-topics that "
                f"ARE relevant to \"{course_title}\" and return those instead.\n"
                f"Return ONLY the JSON array, no additional text."
            )
            messages = [
                SystemMessage(content="You filter topic lists to keep only those relevant to a given course subject."),
                HumanMessage(content=prompt),
            ]
            response = self.llm.invoke(messages)
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            filtered = json.loads(content)
            if isinstance(filtered, list) and filtered:
                logger.info(f"[AZEL-AGENT] Filtered topics for '{course_title}': {filtered}")
                return filtered[:5]
        except Exception as e:
            logger.warning(f"[AZEL-AGENT] Topic filtering failed, using originals: {e}")
        return topics

    def _extract_topics_with_llm(self, context: str, course_id: int, course_title: Optional[str] = None) -> List[str]:
        """
        Fallback method: Extract highlighted topics using LLM when structured format not found.
        When course_title is provided, topics are scoped to that course subject.
        
        Args:
            context: Zed context text
            course_id: Course ID for context
            course_title: Optional course title to scope topic extraction
            
        Returns:
            List of highlighted topics
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot extract topics")
            return []
        
        try:
            course_scope = ""
            if course_title:
                course_scope = (
                    f"\nIMPORTANT: The user is studying the course \"{course_title}\".\n"
                    f"Only extract topics that are relevant to \"{course_title}\".\n"
                    f"If the user context does not mention topics related to "
                    f"\"{course_title}\", generate 3-5 sub-topics that are core to "
                    f"\"{course_title}\" instead.\n"
                )

            prompt = f"""Extract the highlighted topics of interest from the following user context.
{course_scope}
Context:
{context[:3000]}

Focus on topics that are:
- Highlighted or emphasized in the context
- Relevant to the course "{course_title or 'educational content'}"
- Suitable for course material and questions

Return a JSON array of topic strings."""
            
            messages = [
                SystemMessage(content=EXTRACT_TOPICS_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            topics = json.loads(content)
            if isinstance(topics, list):
                logger.info(f"Extracted {len(topics)} highlighted topics via LLM for course_id={course_id}")
                return topics[:5]  # Return top 5
            else:
                logger.warning(f"Unexpected topics format: {type(topics)}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse topics JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return []
        except Exception as e:
            logger.error(f"Failed to extract highlighted topics with LLM: {e}")
            return []
    
    def _perform_google_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform web search (DuckDuckGo via ddgs) and return URLs with metadata
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of dictionaries with url, title, snippet
        """
        try:
            results: List[Dict[str, Any]] = []

            # Primary web search via DuckDuckGo (ddgs)
            try:
                ddgs = DDGS()
                # ddgs.text returns an iterator of result dicts
                for item in ddgs.text(query, max_results=num_results):
                    url = item.get("href") or item.get("url")
                    if not url:
                        continue

                    title_text = item.get("title") or url
                    snippet = item.get("body") or item.get("snippet") or ""

                    results.append(
                        {
                            "url": url,
                            "title": title_text[:500] if title_text else url,
                            "snippet": snippet[:500] if snippet else "",
                        }
                    )

                logger.info(f"DDG search returned {len(results)} results for query: {query}")
            except Exception as e:
                logger.error(f"DuckDuckGo search failed for query '{query}': {e}")

            # Fallback: fetch HTML metadata for any URLs we have (or if DDG failed but results list is empty)
            enriched_results: List[Dict[str, Any]] = []
            for result in results:
                url = result.get("url")
                if not url:
                    continue
                try:
                    response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                    soup = BeautifulSoup(response.content, "html.parser")

                    title_tag = soup.find("title")
                    title_text = title_tag.string if title_tag else result.get("title") or url

                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    snippet = meta_desc.get("content", "") if meta_desc else result.get("snippet") or ""

                    if not snippet:
                        first_p = soup.find("p")
                        snippet = first_p.get_text()[:200] if first_p else ""

                    enriched_results.append(
                        {
                            "url": url,
                            "title": title_text[:500] if title_text else url,
                            "snippet": snippet[:500] if snippet else "",
                        }
                    )

                    # Simple pacing to avoid hammering sites
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"Failed to fetch metadata for {url}: {e}")
                    enriched_results.append(
                        {
                            "url": url,
                            "title": result.get("title") or url,
                            "snippet": result.get("snippet") or "",
                        }
                    )

            logger.info(f"Finalized {len(enriched_results)} search results for query: {query}")
            return enriched_results

        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            return []
    
    def _save_search_urls(self, user_id: int, course_id: int, urls: List[Dict[str, Any]], search_query: str) -> bool:
        """
        Save search URLs to database
        
        Args:
            user_id: User ID
            course_id: Course ID
            urls: List of URL dictionaries with url, title, snippet
            search_query: The search query used
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = Database(get_connection_params())
            
            for url_data in urls:
                url = url_data.get('url', '')
                # Generate unique URL ID
                url_id = hashlib.md5(f"{user_id}_{course_id}_{url}".encode()).hexdigest()
                
                # Check if URL already exists
                existing = db.fetch_one(
                    """SELECT id FROM azel_search_urls 
                       WHERE user_id = %s AND course_id = %s AND url_id = %s""",
                    (user_id, course_id, url_id)
                )
                
                if not existing:
                    db.execute(
                        """INSERT INTO azel_search_urls 
                           (user_id, course_id, url_id, url, title, snippet, search_query, created_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)""",
                        (
                            user_id,
                            course_id,
                            url_id,
                            url,
                            url_data.get('title', ''),
                            url_data.get('snippet', ''),
                            search_query
                        )
                    )
            
            db.close()
            logger.info(f"Saved {len(urls)} URLs to database for user_id={user_id}, course_id={course_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save search URLs: {e}")
            return False
    
    def _get_collection_name(self, user_id: int, course_id: int) -> str:
        """
        Generate secure collection name for user and course using hash with salt
        
        Args:
            user_id: User ID
            course_id: Course ID
            
        Returns:
            Hashed collection name to prevent guessing and data leakage
        """
        salt = os.environ.get("AZEL_COLLECTION_SALT", "").strip()
        if not salt:
            try:
                from config.settings import settings
                is_production = not getattr(settings, "DEBUG", True)
            except Exception:
                is_production = os.environ.get("ENV", "").lower() == "production"
            if is_production:
                logger.error("AZEL_COLLECTION_SALT is not set. Set it in production for Azel knowledge base collections.")
                raise ValueError(
                    "AZEL_COLLECTION_SALT is required in production. "
                    "Set the AZEL_COLLECTION_SALT environment variable."
                )
            salt = "default_salt_change_in_prod"
            logger.warning("Using default AZEL_COLLECTION_SALT (dev only). Set AZEL_COLLECTION_SALT in production.")
        user_hash = hashlib.sha256(f"{user_id}_{salt}".encode()).hexdigest()[:16]
        course_hash = hashlib.sha256(f"{course_id}_{salt}".encode()).hexdigest()[:16]
        return f"azel_kb_{user_hash}_{course_hash}"
    
    def _create_knowledge_base(self, user_id: int, course_id: int, urls: List[Dict[str, Any]]) -> bool:
        """
        Create Qdrant knowledge base with 30-minute TTL
        
        Args:
            user_id: User ID
            course_id: Course ID
            urls: List of URL dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.qdrant_available or not self.qdrant_client:
            logger.warning("Qdrant not available, cannot create knowledge base")
            return False
        
        if not self.openai_available or not self.embeddings:
            logger.warning("OpenAI not available, cannot create embeddings")
            return False
        
        try:
            collection_name = self._get_collection_name(user_id, course_id)
            
            # Check if collection exists, delete it first (for fresh start)
            try:
                collections = self.qdrant_client.get_collections()
                if collection_name in [col.name for col in collections.collections]:
                    self.qdrant_client.delete_collection(collection_name)
                    logger.info(f"Deleted existing collection: {collection_name}")
            except Exception:
                pass
            
            # Create new collection
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
            
            # Extract content from URLs and store embeddings
            points = []
            for idx, url_data in enumerate(urls):
                try:
                    url = url_data.get('url', '')
                    content = self._extract_content_from_url(url)
                    
                    if content:
                        # Create embedding
                        embedding = self.embeddings.embed_query(content[:2000])  # Limit content length
                        
                        # Create point with TTL metadata
                        point_id = abs(hash(f"{user_id}_{course_id}_{url}_{idx}"))
                        points.append(
                            PointStruct(
                                id=point_id,
                                vector=embedding,
                                payload={
                                    "user_id": user_id,
                                    "course_id": course_id,
                                    "url": url,
                                    "title": url_data.get('title', ''),
                                    "content": content[:1000],  # Store first 1000 chars
                                    "created_at": datetime.now().isoformat(),
                                    "expires_at": (datetime.now() + timedelta(minutes=self.kb_ttl_minutes)).isoformat()
                                }
                            )
                        )
                except Exception as e:
                    logger.warning(f"Failed to process URL {url_data.get('url', '')}: {e}")
                    continue
            
            if points:
                self.qdrant_client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                logger.info(f"Stored {len(points)} points in knowledge base: {collection_name}")
            
            # Schedule cleanup after TTL (we'll implement a cleanup job separately)
            # For now, we rely on Qdrant's built-in TTL or manual cleanup
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create knowledge base: {e}")
            return False
    
    def _extract_content_from_url(self, url: str) -> Optional[str]:
        """
        Extract text content from a URL
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limit to 5000 characters
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None
    
    def _extract_content_from_urls(self, urls: List[Dict[str, Any]]) -> str:
        """
        Extract content from multiple URLs and combine (parallelized)
        
        Args:
            urls: List of URL dictionaries
            
        Returns:
            Combined text content
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from utils.api_security import sanitize_url
        import threading
        
        if not urls:
            return ""
        
        contents = []
        lock = threading.Lock()
        max_workers = int(os.environ.get('AZEL_WEB_MAX_WORKERS', 3))
        
        def extract_single_url(url_data):
            """Extract content from a single URL with error handling"""
            url = url_data.get('url', '')
            if not url:
                return None
            
            try:
                # Sanitize URL
                sanitized_url = sanitize_url(url)
                content = self._extract_content_from_url(sanitized_url)
                return content
            except Exception as e:
                logger.warning(f"Failed to extract content from URL {url[:50]}: {e}")
                return None
        
        # Extract content from URLs in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(extract_single_url, url_data): url_data
                for url_data in urls
            }
            
            for future in as_completed(future_to_url):
                url_data = future_to_url[future]
                try:
                    content = future.result()
                    if content:
                        with lock:
                            contents.append(content)
                except Exception as e:
                    logger.error(f"Error extracting content from URL: {e}")
        
        return "\n\n".join(contents)
    
    def _generate_questions(
        self,
        user_id: int,
        course_id: int,
        highlighted_topics: List[str],
        context: str,
        knowledge_base_content: str,
        level: Optional[str] = None,
        course_title: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate questions with detailed answers based on highlighted topics,
        strictly scoped to the course subject.
        
        Args:
            user_id: User ID
            course_id: Course ID
            highlighted_topics: List of highlighted topics
            context: Zed context
            knowledge_base_content: Content from knowledge base
            level: Difficulty level (e.g. "Basic", "Intermediate", "Expert")
            course_title: Course title — ALL questions must be about this subject
            
        Returns:
            List of question dictionaries
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot generate questions")
            return []
        
        try:
            topics_str = ", ".join(highlighted_topics[:5])  # Limit to top 5 topics
            kb_content_preview = knowledge_base_content[:2000] if knowledge_base_content else "No knowledge base content available."
            
            level_instruction = ""
            if level:
                level_instruction = f"\nDifficulty Level: {level}\nAll questions MUST be at the {level} difficulty level.\n"
            
            course_instruction = ""
            if course_title:
                course_instruction = (
                    f"\n*** COURSE SUBJECT: {course_title} ***\n"
                    f"CRITICAL: Every question MUST be directly about \"{course_title}\".\n"
                    f"The user's highlighted topics below are meant to personalise the "
                    f"questions within the scope of \"{course_title}\" — they must NOT "
                    f"cause questions to drift to unrelated subjects.\n"
                    f"If a highlighted topic does not relate to \"{course_title}\", ignore it.\n"
                )
            
            prompt = f"""Generate educational questions based on the following information:
{course_instruction}
User's Highlighted Topics of Interest (use ONLY those relevant to the course):
{topics_str}
{level_instruction}
Zed Context (User Interests — for personalisation only, NOT as primary subject):
{context[:1500]}

Knowledge Base Content:
{kb_content_preview}

Generate {self.questions_per_course} questions that:
1. Are STRICTLY about the course subject "{course_title or 'General'}"
2. Use the user's relevant interests to personalise examples/scenarios
3. Test understanding of key concepts within the course scope
4. Include detailed, comprehensive answers
5. Match the {level or 'Basic'} difficulty level

Return a JSON array of question objects."""
            
            messages = [
                SystemMessage(content=QUESTION_GENERATION_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            questions = json.loads(content)
            if isinstance(questions, list):
                logger.info(f"Generated {len(questions)} questions for course_id={course_id}")
                return questions
            else:
                logger.warning(f"Unexpected questions format: {type(questions)}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return []
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            return []
    
    def _save_questions(self, course_id: int, questions: List[Dict[str, Any]], section_id: Optional[int] = None) -> bool:
        """
        Save questions to lms_questions table using the SQLAlchemy ORM session pool.

        Before inserting new questions, any existing questions for the same
        course + section are deleted so that "Generate Questions" always
        produces a fresh set.  Associated user answers are cascade-deleted
        by the database FK constraint (ondelete='CASCADE').
        
        Args:
            course_id: Course ID
            questions: List of question dictionaries
            section_id: Optional section ID to scope questions to a level
            
        Returns:
            True if successful, False otherwise
        """
        from config.database_orm import SessionLocal
        from sqlalchemy import func
        
        db = SessionLocal()
        try:
            # ---- Delete previous questions for this course + section ----
            delete_filter = [LMSQuestion.course_id == course_id]
            if section_id:
                delete_filter.append(LMSQuestion.section_id == section_id)
            else:
                delete_filter.append(LMSQuestion.section_id.is_(None))

            deleted = (
                db.query(LMSQuestion)
                .filter(*delete_filter)
                .delete(synchronize_session="fetch")
            )
            if deleted:
                logger.info(f"[AZEL-AGENT] Deleted {deleted} old questions for course_id={course_id}, section_id={section_id}")

            # New questions always start at order_index 0 since old ones are gone
            start_index = 0
            
            for idx, question_data in enumerate(questions):
                # Store detailed answer in correct_answer field
                correct_answer = question_data.get('correct_answer', '')
                explanation = question_data.get('explanation', '')
                
                # Combine answer and explanation for detailed answer
                detailed_answer = f"{correct_answer}\n\nExplanation: {explanation}" if explanation else correct_answer
                
                db.add(LMSQuestion(
                    course_id=course_id,
                    section_id=section_id,
                    question_text=question_data.get('question_text', ''),
                    question_type=question_data.get('question_type', 'text'),
                    options=question_data.get('options') if question_data.get('options') else None,
                    correct_answer=detailed_answer,
                    points=question_data.get('points', 1),
                    order_index=start_index + idx,
                ))
            
            db.commit()
            logger.info(f"Saved {len(questions)} questions to database for course_id={course_id}, section_id={section_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save questions: {e}")
            return False
        finally:
            db.close()
    
    def process_course_context(
        self,
        user_id: int,
        course_id: int,
        section_id: Optional[int] = None,
        level: Optional[str] = None,
        course_title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Main pipeline method: Process course context and generate questions
        scoped to a specific section / difficulty level.
        
        Args:
            user_id: User ID
            course_id: Course ID
            section_id: Optional section ID (questions will be saved with this)
            level: Difficulty level label (e.g. "Basic", "Intermediate", "Expert")
            course_title: The course title — questions MUST be relevant to this subject
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'success': False,
            'user_id': user_id,
            'course_id': course_id,
            'section_id': section_id,
            'level': level,
            'topics_extracted': [],
            'urls_found': 0,
            'urls_saved': 0,
            'knowledge_base_created': False,
            'questions_generated': 0,
            'questions_saved': 0,
            'error': None
        }
        
        import time
        pipeline_start = time.time()
        
        try:
            # Step 1: Get Zed context
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 1: Getting Zed context for user_id={user_id}")
            context = self._get_zed_context(user_id)
            step_elapsed = time.time() - step_start
            
            if not context:
                # Production users often have profile/resume but no merged `zed` yet (Zed runs on logout).
                try:
                    from agents.Zed_agent import get_zed_agent
                    profile_text = get_zed_agent()._get_user_profile(user_id)
                    if profile_text and len(profile_text.strip()) > 20:
                        context = profile_text.strip()
                        logger.info(
                            f"[AZEL-AGENT] Step 1: No users_context.zed; using user profile fallback "
                            f"({len(context)} chars) for user_id={user_id}"
                        )
                except Exception as fb_e:
                    logger.warning(f"[AZEL-AGENT] Profile context fallback failed: {fb_e}")
            
            if not context:
                result['error'] = (
                    "No career context found. Add profile/resume in Settings, use the app for a bit, "
                    "or sign out once to refresh your context — then try again."
                )
                logger.warning(f"[AZEL-AGENT] Step 1 FAILED: No Zed context found for user_id={user_id} (took {step_elapsed:.2f}s)")
                return result
            
            step_elapsed = time.time() - step_start
            context_length = len(context) if context else 0
            logger.info(f"[AZEL-AGENT] Step 1 SUCCESS: Context ready ({context_length} chars) in {step_elapsed:.2f}s")
            
            # Step 2: Extract highlighted topics (scoped to course subject)
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 2: Extracting highlighted topics (course_title='{course_title}')")
            highlighted_topics = self._extract_highlighted_topics(context, course_id, course_title=course_title)
            result['topics_extracted'] = highlighted_topics
            step_elapsed = time.time() - step_start
            
            if not highlighted_topics and course_title:
                highlighted_topics = [course_title.strip()]
                result['topics_extracted'] = highlighted_topics
                logger.warning(
                    f"[AZEL-AGENT] Step 2: No topics from context; using course title as search seed: {highlighted_topics}"
                )
            
            if not highlighted_topics:
                result['error'] = "No highlighted topics extracted and no course title to fall back on"
                logger.warning(f"[AZEL-AGENT] Step 2 FAILED: No highlighted topics for user_id={user_id}, course_id={course_id} (took {step_elapsed:.2f}s)")
                return result
            
            logger.info(f"[AZEL-AGENT] Step 2 SUCCESS: Using {len(highlighted_topics)} topics: {highlighted_topics} (took {step_elapsed:.2f}s)")
            
            # Step 3: Perform Google searches for each topic (parallelized)
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 3: Starting web searches for topics")
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from utils.rate_limiter import get_google_search_limiter
            from utils.api_retry import retry_with_backoff
            from utils.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenError
            from utils.api_security import sanitize_search_query
            
            all_urls = []
            topics_to_search = highlighted_topics[:3]  # Limit to top 3 topics
            logger.info(f"[AZEL-AGENT] Step 3: Searching for {len(topics_to_search)} topics: {topics_to_search}")
            
            # Get rate limiter and circuit breaker
            rate_limiter = get_google_search_limiter()
            circuit_breaker = get_circuit_breaker('google_search')
            max_workers = int(os.environ.get('AZEL_WEB_MAX_WORKERS', 3))
            logger.info(f"[AZEL-AGENT] Step 3: Using {max_workers} workers for parallel searches")
            
            def perform_search_with_protection(topic):
                """Perform Google search with rate limiting and error handling"""
                # Include the course title in the search query so results are course-relevant
                course_scope = sanitize_search_query(course_title) if course_title else ""
                search_query = f"{course_scope} {sanitize_search_query(topic)} tutorial course educational"
                
                try:
                    with rate_limiter.acquire():
                        @retry_with_backoff(max_retries=int(os.environ.get('GOOGLE_SEARCH_MAX_RETRIES', 3)))
                        def search():
                            return circuit_breaker.call(
                                self._perform_google_search,
                                search_query,
                                num_results=self.max_search_results
                            )
                        
                        urls = search()
                        for url_data in urls:
                            url_data['search_query'] = search_query
                        return urls
                
                except CircuitBreakerOpenError as e:
                    logger.error(f"Circuit breaker open for Google search '{topic}': {e}")
                    return []
                except Exception as e:
                    logger.error(f"Failed to search for topic '{topic}': {e}")
                    return []
            
            # Perform searches in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_topic = {
                    executor.submit(perform_search_with_protection, topic): topic
                    for topic in topics_to_search
                }
                
                completed_searches = 0
                for future in as_completed(future_to_topic):
                    topic = future_to_topic[future]
                    try:
                        urls = future.result()
                        all_urls.extend(urls)
                        completed_searches += 1
                        logger.info(f"[AZEL-AGENT] Step 3: Completed search for topic '{topic}': {len(urls)} URLs found ({completed_searches}/{len(topics_to_search)} searches done)")
                    except Exception as e:
                        completed_searches += 1
                        logger.error(f"[AZEL-AGENT] Step 3: Error processing search for topic '{topic}': {e} ({completed_searches}/{len(topics_to_search)} searches done)")
            
            step_elapsed = time.time() - step_start
            result['urls_found'] = len(all_urls)
            logger.info(f"[AZEL-AGENT] Step 3 SUCCESS: Found {len(all_urls)} total URLs in {step_elapsed:.2f}s")
            
            # Step 4: Save URLs to database
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 4: Saving {len(all_urls)} URLs to database")
            if all_urls:
                # Save all URLs
                for url_data in all_urls:
                    self._save_search_urls(
                        user_id,
                        course_id,
                        [url_data],
                        url_data.get('search_query', '')
                    )
                result['urls_saved'] = len(all_urls)
            step_elapsed = time.time() - step_start
            logger.info(f"[AZEL-AGENT] Step 4 SUCCESS: Saved {result['urls_saved']} URLs to database in {step_elapsed:.2f}s")
            
            # Step 5: Create Qdrant knowledge base with TTL
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 5: Creating Qdrant knowledge base with {len(all_urls)} URLs")
            if all_urls:
                kb_created = self._create_knowledge_base(user_id, course_id, all_urls)
                result['knowledge_base_created'] = kb_created
                step_elapsed = time.time() - step_start
                if kb_created:
                    logger.info(f"[AZEL-AGENT] Step 5 SUCCESS: Knowledge base created in {step_elapsed:.2f}s")
                else:
                    logger.warning(f"[AZEL-AGENT] Step 5 FAILED: Knowledge base creation failed (took {step_elapsed:.2f}s)")
            else:
                logger.warning(f"[AZEL-AGENT] Step 5 SKIPPED: No URLs to create knowledge base from")
            
            # Step 6: Extract content from URLs
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 6: Extracting content from {len(all_urls)} URLs")
            knowledge_base_content = self._extract_content_from_urls(all_urls)
            step_elapsed = time.time() - step_start
            content_length = len(knowledge_base_content) if knowledge_base_content else 0
            logger.info(f"[AZEL-AGENT] Step 6 SUCCESS: Extracted {content_length} chars of content in {step_elapsed:.2f}s")
            
            # Step 7: Generate questions (with level + course title context)
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 7: Generating questions using LLM (level={level}, course='{course_title}')")
            questions = self._generate_questions(
                user_id,
                course_id,
                highlighted_topics,
                context,
                knowledge_base_content,
                level=level,
                course_title=course_title,
            )
            result['questions_generated'] = len(questions)
            step_elapsed = time.time() - step_start
            logger.info(f"[AZEL-AGENT] Step 7 SUCCESS: Generated {len(questions)} questions in {step_elapsed:.2f}s")
            
            # Step 8: Save questions (with section_id)
            step_start = time.time()
            logger.info(f"[AZEL-AGENT] Step 8: Saving {len(questions)} questions to database (section_id={section_id})")
            if questions:
                saved = self._save_questions(course_id, questions, section_id=section_id)
                if saved:
                    result['questions_saved'] = len(questions)
                    step_elapsed = time.time() - step_start
                    logger.info(f"[AZEL-AGENT] Step 8 SUCCESS: Saved {result['questions_saved']} questions to database in {step_elapsed:.2f}s")
                else:
                    step_elapsed = time.time() - step_start
                    logger.error(f"[AZEL-AGENT] Step 8 FAILED: Failed to save questions (took {step_elapsed:.2f}s)")
            else:
                logger.warning(f"[AZEL-AGENT] Step 8 SKIPPED: No questions to save")
            
            total_elapsed = time.time() - pipeline_start
            if result['questions_saved'] > 0:
                result['success'] = True
                logger.info(
                    f"[AZEL-AGENT] ===== PIPELINE COMPLETE: Saved {result['questions_saved']} questions "
                    f"for user_id={user_id}, course_id={course_id} in {total_elapsed:.2f}s ====="
                )
            else:
                result['success'] = False
                if not result.get('error'):
                    if result['questions_generated'] > 0:
                        result['error'] = "Questions were generated but could not be saved to the database"
                    else:
                        result['error'] = (
                            "No questions were produced. Check OpenAI responses, web search results, "
                            "and Render logs for [AZEL-AGENT]. Ensure QDRANT_URL points to a reachable Qdrant."
                        )
                logger.warning(
                    f"[AZEL-AGENT] ===== PIPELINE FINISHED WITH NO SAVED QUESTIONS: user_id={user_id}, "
                    f"course_id={course_id} in {total_elapsed:.2f}s — {result.get('error')} ====="
                )
            
        except Exception as e:
            total_elapsed = time.time() - pipeline_start
            result['error'] = str(e)
            logger.error(f"[AZEL-AGENT] ===== PIPELINE FAILED: Error processing course context after {total_elapsed:.2f}s: {e}", exc_info=True)
        
        return result
    
    def cleanup_expired_collections(self) -> Dict[str, Any]:
        """
        Clean up expired Azel knowledge base collections
        
        Scans all collections matching azel_kb_* pattern and:
        - Deletes collections where all points are expired (30+ minutes old)
        - Deletes expired points from collections with mixed expiration
        
        Returns:
            Dictionary with cleanup statistics
        """
        if not self.qdrant_available or not self.qdrant_client:
            logger.warning("Qdrant not available, cannot cleanup collections")
            return {
                'success': False,
                'collections_deleted': 0,
                'points_deleted': 0,
                'collections_checked': 0,
                'error': 'Qdrant not available'
            }
        
        # Check if cleanup is enabled
        cleanup_enabled = os.environ.get('AZEL_CLEANUP_ENABLED', 'true').lower() == 'true'
        if not cleanup_enabled:
            logger.debug("Azel cleanup is disabled via AZEL_CLEANUP_ENABLED")
            return {
                'success': True,
                'collections_deleted': 0,
                'points_deleted': 0,
                'collections_checked': 0,
                'message': 'Cleanup disabled'
            }
        
        stats = {
            'collections_deleted': 0,
            'points_deleted': 0,
            'collections_checked': 0,
            'errors': []
        }
        
        try:
            # Get all collections
            collections = self.qdrant_client.get_collections()
            current_time = datetime.now()
            
            # Filter to only azel_kb_* collections
            azel_collections = [
                col.name for col in collections.collections 
                if col.name.startswith('azel_kb_')
            ]
            
            logger.info(f"Found {len(azel_collections)} Azel collections to check for cleanup")
            
            for collection_name in azel_collections:
                try:
                    stats['collections_checked'] += 1
                    
                    # Scroll through all points in collection
                    offset = None
                    expired_point_ids = []
                    active_point_count = 0
                    batch_size = 100
                    
                    while True:
                        result, next_offset = self.qdrant_client.scroll(
                            collection_name=collection_name,
                            limit=batch_size,
                            offset=offset,
                            with_payload=True,
                            with_vectors=False  # Don't need vectors for cleanup
                        )
                        
                        if not result:
                            break
                        
                        # Check each point's expires_at metadata
                        for point in result:
                            payload = point.payload or {}
                            expires_at_str = payload.get('expires_at')
                            
                            if expires_at_str:
                                try:
                                    expires_at = datetime.fromisoformat(expires_at_str)
                                    if expires_at < current_time:
                                        expired_point_ids.append(point.id)
                                    else:
                                        active_point_count += 1
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"Invalid expires_at format in collection {collection_name}, point {point.id}: {e}")
                                    # Treat invalid dates as expired for safety
                                    expired_point_ids.append(point.id)
                            else:
                                # No expires_at metadata - treat as expired for safety
                                expired_point_ids.append(point.id)
                        
                        if next_offset is None:
                            break
                        offset = next_offset
                    
                    # If all points are expired, delete the entire collection
                    if active_point_count == 0 and expired_point_ids:
                        try:
                            self.qdrant_client.delete_collection(collection_name)
                            stats['collections_deleted'] += 1
                            stats['points_deleted'] += len(expired_point_ids)
                            logger.info(f"Deleted expired collection: {collection_name} ({len(expired_point_ids)} points)")
                        except Exception as e:
                            error_msg = f"Failed to delete collection {collection_name}: {e}"
                            logger.error(error_msg)
                            stats['errors'].append(error_msg)
                    
                    # If some points are expired but collection has active points, delete only expired points
                    elif expired_point_ids and active_point_count > 0:
                        try:
                            # Delete expired points in batches
                            for i in range(0, len(expired_point_ids), batch_size):
                                batch_ids = expired_point_ids[i:i + batch_size]
                                # Qdrant delete accepts PointIdsList or list of IDs
                                self.qdrant_client.delete(
                                    collection_name=collection_name,
                                    points_selector=PointIdsList(points=batch_ids)
                                )
                            stats['points_deleted'] += len(expired_point_ids)
                            logger.info(f"Deleted {len(expired_point_ids)} expired points from collection: {collection_name}")
                        except Exception as e:
                            error_msg = f"Failed to delete expired points from {collection_name}: {e}"
                            logger.error(error_msg)
                            stats['errors'].append(error_msg)
                    
                except Exception as e:
                    error_msg = f"Error processing collection {collection_name}: {e}"
                    logger.error(error_msg, exc_info=True)
                    stats['errors'].append(error_msg)
                    continue
            
            logger.info(
                f"Azel cleanup completed: {stats['collections_deleted']} collections deleted, "
                f"{stats['points_deleted']} points deleted, {stats['collections_checked']} collections checked"
            )
            
            return {
                'success': len(stats['errors']) == 0,
                'collections_deleted': stats['collections_deleted'],
                'points_deleted': stats['points_deleted'],
                'collections_checked': stats['collections_checked'],
                'errors': stats['errors'] if stats['errors'] else None
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup Azel collections: {e}", exc_info=True)
            return {
                'success': False,
                'collections_deleted': stats['collections_deleted'],
                'points_deleted': stats['points_deleted'],
                'collections_checked': stats['collections_checked'],
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Check if agent is available (both Qdrant and OpenAI working)"""
        return self.qdrant_available and self.openai_available


# Global agent instance (lazy initialization)
_agent_instance: Optional[AzelAgent] = None


def get_azel_agent() -> AzelAgent:
    """Get or create global Azel agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = AzelAgent()
    
    return _agent_instance
