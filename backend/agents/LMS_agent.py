"""  LMS Agent - AI-powered question generation using LangGraph, Qdrant and OpenAI  """
"""   Helper agent for Lemzy  """
import os
import logging
from typing import Optional, List, Dict, Any, TypedDict, Annotated, Literal
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State schema for the LMS question generation agent"""
    # Input parameters
    course_id: int
    course_title: str
    course_content: Optional[str]
    search_query: Optional[str]
    difficulty: str
    question_type: str
    
    # Intermediate state
    relevant_content: Annotated[List[Dict[str, Any]], lambda x, y: x + y]  # Accumulated content
    context: Optional[str]
    question_data: Optional[Dict[str, Any]]
    
    # Control flow
    needs_search: bool
    should_continue: bool
    error: Optional[str]


class LMSAgent:
    """AI Agent for generating questions for LMS courses using LangGraph, Qdrant and OpenAI"""
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini"
    ):
        """
        Initialize LMS Agent with Qdrant and OpenAI clients
        
        Args:
            qdrant_url: Qdrant server URL (default: from env or localhost)
            qdrant_api_key: Qdrant API key (optional)
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use for question generation
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
            logger.warning(f"Qdrant not available, question generation will be limited: {e}")
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
        
        # Collection name for course content embeddings
        self.collection_name = "lms_course_content"
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small dimension
        
        # Initialize collection if Qdrant is available
        if self.qdrant_available:
            self._ensure_collection_exists()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _ensure_collection_exists(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            self.qdrant_available = False
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding vector for text using LangChain OpenAI embeddings
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if unavailable
        """
        if not self.openai_available or not self.embeddings:
            return None
        
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    def _search_content(self, state: AgentState) -> AgentState:
        """
        Search node: Find relevant course content using semantic search
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with relevant_content
        """
        if not self.qdrant_available or not self.qdrant_client:
            logger.warning("Qdrant not available, skipping content search")
            state["relevant_content"] = []
            state["context"] = ""
            return state
        
        if not self.openai_available:
            logger.warning("OpenAI not available, skipping content search")
            state["relevant_content"] = []
            state["context"] = ""
            return state
        
        search_query = state.get("search_query", "")
        course_id = state.get("course_id")
        
        if not search_query:
            state["relevant_content"] = []
            state["context"] = ""
            return state
        
        # Get query embedding
        query_embedding = self._get_embedding(search_query)
        if not query_embedding:
            state["relevant_content"] = []
            state["context"] = ""
            return state
        
        # Prepare filter
        filter_condition = None
        if course_id:
            filter_condition = {
                "must": [
                    {"key": "course_id", "match": {"value": course_id}}
                ]
            }
        
        try:
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=filter_condition,
                limit=5
            )
            
            results = []
            for result in search_results:
                results.append({
                    "score": result.score,
                    "course_id": result.payload.get("course_id"),
                    "content_type": result.payload.get("content_type"),
                    "content": result.payload.get("content", ""),
                    "metadata": {k: v for k, v in result.payload.items() 
                               if k not in ["course_id", "content_type", "content"]}
                })
            
            state["relevant_content"] = results
            
            # Combine relevant content for context
            if results:
                context_parts = [item["content"] for item in results]
                state["context"] = "\n\n".join(context_parts)
            else:
                state["context"] = ""
            
            logger.info(f"Found {len(results)} relevant content items for course_id={course_id}")
            
        except Exception as e:
            logger.error(f"Failed to search similar content: {e}")
            state["relevant_content"] = []
            state["context"] = ""
        
        return state
    
    def _generate_question(self, state: AgentState) -> AgentState:
        """
        Generate node: Create question using LLM
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with question_data
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot generate questions")
            state["error"] = "OpenAI not available"
            state["should_continue"] = False
            return state
        
        course_id = state.get("course_id")
        course_title = state.get("course_title", f"Course {course_id}")
        context = state.get("context", "")
        difficulty = state.get("difficulty", "intermediate")
        question_type = state.get("question_type", "multiple_choice")
        
        if not context:
            logger.warning("No context available for question generation")
            state["error"] = "No context available"
            state["should_continue"] = False
            return state
        
        # Build prompt for question generation
        prompt = f"""Generate a {difficulty} level {question_type} question for the following course.

Course Title: {course_title}
Course Content: {context[:2000]}

Please generate a question that:
1. Tests understanding of key concepts from the course
2. Is appropriate for {difficulty} level
3. Is clear and unambiguous
4. Has a single correct answer

For multiple choice questions, provide:
- The question text
- 4 options (A, B, C, D)
- The correct answer (A, B, C, or D)
- A brief explanation

For true/false questions, provide:
- The question statement
- The correct answer (True or False)
- A brief explanation

For text questions, provide:
- The question text
- A sample correct answer
- Key points that should be included

Return the response in JSON format with the following structure:
{{
    "question_text": "...",
    "question_type": "{question_type}",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}} (only for multiple_choice),
    "correct_answer": "...",
    "explanation": "...",
    "points": 1
}}"""

        try:
            messages = [
                SystemMessage(
                    content="You are an expert educational content creator. Generate high-quality questions that test understanding and knowledge retention. Always return valid JSON."
                ),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content
            
            # Try to extract JSON from response
            # Sometimes LLM wraps JSON in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            question_data = json.loads(content)
            
            # Add metadata
            question_data["course_id"] = course_id
            question_data["difficulty"] = difficulty
            question_data["generated_at"] = str(datetime.now())
            
            state["question_data"] = question_data
            state["should_continue"] = True
            state["error"] = None
            
            logger.info(f"Generated question for course_id={course_id}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")
            state["error"] = f"Failed to parse JSON: {str(e)}"
            state["should_continue"] = False
        except Exception as e:
            logger.error(f"Failed to generate question: {e}")
            state["error"] = str(e)
            state["should_continue"] = False
        
        return state
    
    def _validate_question(self, state: AgentState) -> AgentState:
        """
        Validate node: Validate generated question
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        question_data = state.get("question_data")
        
        if not question_data:
            state["error"] = "No question data to validate"
            state["should_continue"] = False
            return state
        
        # Basic validation
        required_fields = ["question_text", "question_type", "correct_answer"]
        missing_fields = [field for field in required_fields if field not in question_data]
        
        if missing_fields:
            state["error"] = f"Missing required fields: {missing_fields}"
            state["should_continue"] = False
            return state
        
        # Validate question type specific fields
        question_type = question_data.get("question_type")
        if question_type == "multiple_choice":
            if "options" not in question_data:
                state["error"] = "Multiple choice questions require options"
                state["should_continue"] = False
                return state
        
        state["should_continue"] = True
        state["error"] = None
        
        logger.info("Question validation passed")
        return state
    
    def _decide_search_node(self, state: AgentState) -> AgentState:
        """
        Decision node: Determine if we need to search for content
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        # If we have course_content, skip search
        if state.get("course_content"):
            state["needs_search"] = False
            state["context"] = state["course_content"]
            return state
        
        # If we have search_query, do search
        if state.get("search_query"):
            state["needs_search"] = True
            return state
        
        # Default: skip search if no search query
        state["needs_search"] = False
        state["context"] = state.get("course_content", "")
        return state
    
    def _route_after_decide(self, state: AgentState) -> Literal["search_content", "generate_question"]:
        """
        Route function: Determine next node after decide_search
        
        Args:
            state: Current agent state
            
        Returns:
            Next node to execute
        """
        if state.get("needs_search"):
            return "search_content"
        return "generate_question"
    
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow for question generation
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("decide_search", self._decide_search_node)
        workflow.add_node("search_content", self._search_content)
        workflow.add_node("generate_question", self._generate_question)
        workflow.add_node("validate_question", self._validate_question)
        
        # Set entry point
        workflow.set_entry_point("decide_search")
        
        # Add conditional edge for search decision
        workflow.add_conditional_edges(
            "decide_search",
            self._route_after_decide,
            {
                "search_content": "search_content",
                "generate_question": "generate_question"
            }
        )
        
        # Add edges
        workflow.add_edge("search_content", "generate_question")
        workflow.add_edge("generate_question", "validate_question")
        workflow.add_edge("validate_question", END)
        
        # Compile workflow
        return workflow.compile()
    
    def store_course_content(
        self,
        course_id: int,
        content: str,
        content_type: str = "course_description",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store course content in Qdrant for semantic search
        
        Args:
            course_id: Course ID
            content: Course content text (description, section content, etc.)
            content_type: Type of content (course_description, section_content, etc.)
            metadata: Additional metadata to store
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.qdrant_available or not self.qdrant_client:
            logger.warning("Qdrant not available, cannot store course content")
            return False
        
        if not self.openai_available:
            logger.warning("OpenAI not available, cannot generate embeddings")
            return False
        
        # Get embedding
        embedding = self._get_embedding(content)
        if not embedding:
            return False
        
        # Prepare metadata
        point_metadata = {
            "course_id": course_id,
            "content_type": content_type,
            "content": content[:500],  # Store first 500 chars for reference
            **(metadata or {})
        }
        
        # Create point ID (course_id + content_type hash)
        point_id = hash(f"{course_id}_{content_type}_{content[:100]}")
        
        try:
            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=abs(point_id),  # Ensure positive ID
                        vector=embedding,
                        payload=point_metadata
                    )
                ]
            )
            logger.info(f"Stored course content for course_id={course_id}, type={content_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to store course content in Qdrant: {e}")
            return False
    
    def generate_question(
        self,
        course_id: int,
        course_title: str,
        course_content: Optional[str] = None,
        search_query: Optional[str] = None,
        difficulty: str = "intermediate",
        question_type: str = "multiple_choice"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a question for a course using LangGraph workflow
        
        Args:
            course_id: Course ID
            course_title: Course title
            course_content: Course content/description (optional if using search_query)
            search_query: Query to search for relevant content (optional if using course_content)
            difficulty: Question difficulty (beginner, intermediate, advanced)
            question_type: Type of question (multiple_choice, true_false, text)
            
        Returns:
            Generated question dictionary or None if generation fails
        """
        if not self.openai_available:
            logger.warning("OpenAI not available, cannot generate questions")
            return None
        
        # Initialize state
        initial_state: AgentState = {
            "course_id": course_id,
            "course_title": course_title,
            "course_content": course_content,
            "search_query": search_query,
            "difficulty": difficulty,
            "question_type": question_type,
            "relevant_content": [],
            "context": None,
            "question_data": None,
            "needs_search": False,
            "should_continue": True,
            "error": None
        }
        
        try:
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Check for errors
            if final_state.get("error"):
                logger.error(f"Question generation failed: {final_state['error']}")
                return None
            
            if not final_state.get("should_continue"):
                logger.warning("Question generation was stopped")
                return None
            
            question_data = final_state.get("question_data")
            if not question_data:
                logger.warning("No question data generated")
                return None
            
            return question_data
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if agent is available (both Qdrant and OpenAI working)"""
        return self.qdrant_available and self.openai_available


# Global agent instance (lazy initialization)
_agent_instance: Optional[LMSAgent] = None


def get_lms_agent() -> LMSAgent:
    """Get or create global LMS agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = LMSAgent()
    
    return _agent_instance
