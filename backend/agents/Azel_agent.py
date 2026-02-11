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

Based on the user's highlighted topics of interest and the knowledge base content, create questions that:
1. Focus on the user's highlighted topics
2. Test understanding of key concepts
3. Are clear and unambiguous
4. Have detailed, comprehensive answers

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
        self.questions_per_course = int(os.environ.get('AZEL_QUESTIONS_PER_COURSE', 5))
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
    
    def _extract_highlighted_topics(self, context: str, course_id: int) -> List[str]:
        """
        Extract highlighted topics of interest from Zed context.
        First tries to parse the structured "Preferred Topics" section,
        then falls back to LLM extraction if structured format not found.
        
        Args:
            context: Zed context text containing highlighted topics
            course_id: Course ID for context
            
        Returns:
            List of highlighted topics (top 5 from "Highlighted Topics" section)
        """
        # Try to parse structured "Preferred Topics" section first
        topics = self._parse_structured_topics(context)
        
        if topics:
            logger.info(f"Extracted {len(topics)} highlighted topics from structured section for course_id={course_id}")
            return topics
        
        # Fallback to LLM extraction if structured format not found
        logger.info(f"Structured topics not found, falling back to LLM extraction for course_id={course_id}")
        return self._extract_topics_with_llm(context, course_id)
    
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
    
    def _extract_topics_with_llm(self, context: str, course_id: int) -> List[str]:
        """
        Fallback method: Extract highlighted topics using LLM when structured format not found.
        
        Args:
            context: Zed context text
            course_id: Course ID for context
            
        Returns:
            List of highlighted topics
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot extract topics")
            return []
        
        try:
            prompt = f"""Extract the highlighted topics of interest from the following user context.

Context:
{context[:3000]}

Focus on topics that are:
- Highlighted or emphasized in the context
- Relevant to educational content
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
        # Use hash with salt to prevent guessing collection names
        salt = os.environ.get('AZEL_COLLECTION_SALT', 'default_salt_change_in_prod')
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
        knowledge_base_content: str
    ) -> List[Dict[str, Any]]:
        """
        Generate questions with detailed answers based on highlighted topics
        
        Args:
            user_id: User ID
            course_id: Course ID
            highlighted_topics: List of highlighted topics
            context: Zed context
            knowledge_base_content: Content from knowledge base
            
        Returns:
            List of question dictionaries
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot generate questions")
            return []
        
        try:
            topics_str = ", ".join(highlighted_topics[:5])  # Limit to top 5 topics
            kb_content_preview = knowledge_base_content[:2000] if knowledge_base_content else "No knowledge base content available."
            
            prompt = f"""Generate educational questions based on the following information:

User's Highlighted Topics of Interest:
{topics_str}

Zed Context (User Interests):
{context[:1500]}

Knowledge Base Content:
{kb_content_preview}

Generate {self.questions_per_course} questions that:
1. Focus on the highlighted topics of interest
2. Test understanding of key concepts
3. Include detailed, comprehensive answers
4. Are appropriate for course material

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
    
    def _save_questions(self, course_id: int, questions: List[Dict[str, Any]]) -> bool:
        """
        Save questions to lms_questions table
        
        Args:
            course_id: Course ID
            questions: List of question dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = Database(get_connection_params())
            
            for idx, question_data in enumerate(questions):
                # Store detailed answer in correct_answer field
                correct_answer = question_data.get('correct_answer', '')
                explanation = question_data.get('explanation', '')
                
                # Combine answer and explanation for detailed answer
                detailed_answer = f"{correct_answer}\n\nExplanation: {explanation}" if explanation else correct_answer
                
                db.execute(
                    """INSERT INTO lms_questions 
                       (course_id, question_text, question_type, options, correct_answer, points, order_index, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)""",
                    (
                        course_id,
                        question_data.get('question_text', ''),
                        question_data.get('question_type', 'text'),
                        json.dumps(question_data.get('options', {})) if question_data.get('options') else None,
                        detailed_answer,  # Store detailed answer in correct_answer field
                        question_data.get('points', 1),
                        idx
                    )
                )
            
            db.close()
            logger.info(f"Saved {len(questions)} questions to database for course_id={course_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save questions: {e}")
            return False
    
    def process_course_context(self, user_id: int, course_id: int) -> Dict[str, Any]:
        """
        Main pipeline method: Process course context and generate questions
        
        Args:
            user_id: User ID
            course_id: Course ID
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'success': False,
            'user_id': user_id,
            'course_id': course_id,
            'topics_extracted': [],
            'urls_found': 0,
            'urls_saved': 0,
            'knowledge_base_created': False,
            'questions_generated': 0,
            'questions_saved': 0,
            'error': None
        }
        
        try:
            # Step 1: Get Zed context
            logger.info(f"Processing course context for user_id={user_id}, course_id={course_id}")
            context = self._get_zed_context(user_id)
            
            if not context:
                result['error'] = "No Zed context found for user"
                logger.warning(f"No Zed context found for user_id={user_id}")
                return result
            
            # Step 2: Extract highlighted topics
            highlighted_topics = self._extract_highlighted_topics(context, course_id)
            result['topics_extracted'] = highlighted_topics
            
            if not highlighted_topics:
                result['error'] = "No highlighted topics extracted"
                logger.warning(f"No highlighted topics extracted for user_id={user_id}, course_id={course_id}")
                return result
            
            # Step 3: Perform Google searches for each topic (parallelized)
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from utils.rate_limiter import get_google_search_limiter
            from utils.api_retry import retry_with_backoff
            from utils.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenError
            from utils.api_security import sanitize_search_query
            
            all_urls = []
            topics_to_search = highlighted_topics[:3]  # Limit to top 3 topics
            
            # Get rate limiter and circuit breaker
            rate_limiter = get_google_search_limiter()
            circuit_breaker = get_circuit_breaker('google_search')
            max_workers = int(os.environ.get('AZEL_WEB_MAX_WORKERS', 3))
            
            def perform_search_with_protection(topic):
                """Perform Google search with rate limiting and error handling"""
                search_query = f"{sanitize_search_query(topic)} tutorial course educational"
                
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
                
                for future in as_completed(future_to_topic):
                    topic = future_to_topic[future]
                    try:
                        urls = future.result()
                        all_urls.extend(urls)
                        logger.debug(f"Completed search for topic '{topic}': {len(urls)} URLs found")
                    except Exception as e:
                        logger.error(f"Error processing search for topic '{topic}': {e}")
            
            result['urls_found'] = len(all_urls)
            
            # Step 4: Save URLs to database
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
            
            # Step 5: Create Qdrant knowledge base with TTL
            if all_urls:
                kb_created = self._create_knowledge_base(user_id, course_id, all_urls)
                result['knowledge_base_created'] = kb_created
            
            # Step 6: Extract content from URLs
            knowledge_base_content = self._extract_content_from_urls(all_urls)
            
            # Step 7: Generate questions
            questions = self._generate_questions(
                user_id,
                course_id,
                highlighted_topics,
                context,
                knowledge_base_content
            )
            result['questions_generated'] = len(questions)
            
            # Step 8: Save questions
            if questions:
                saved = self._save_questions(course_id, questions)
                if saved:
                    result['questions_saved'] = len(questions)
            
            result['success'] = True
            logger.info(f"Successfully processed course context for user_id={user_id}, course_id={course_id}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to process course context: {e}")
        
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
