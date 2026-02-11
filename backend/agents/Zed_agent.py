"""
Zed Agent - User Context Maintainer
AI-powered agent for maintaining comprehensive user context in the database
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config.database import get_connection_params, Database

logger = logging.getLogger(__name__)


# System prompt for Zed agent
ZED_SYSTEM_PROMPT = """You are Zed, a specialized AI agent whose SOLE purpose is to maintain and update comprehensive user context information in a database.

## Your Core Mission
Your ONLY job is to analyze user interactions, extract relevant information, and create extensive, detailed context documentation about each user. You must save all context to the database in the `zed` column of the `users_context` table.

## Data Sources

You will receive data from two primary sources:

1. **`runtime_context` (JSONB)**: Contains recent user activities and parsed resume/CV data
   - This is a JSONB array/object stored in the `runtime_context` column
   - Each item in `runtime_context` may have a "content" key containing relevant information
   - Extract all content from items where key = "content" to build context
   - Includes: button clicks, user interactions, parsed resume/CV data, recent activities

2. **`zed` (TEXT)**: Contains the existing comprehensive, analyzed context
   - This is the previously generated comprehensive context document
   - Always merge new information with existing `zed` context
   - The updated `zed` will overwrite the previous version (it's always the most current)

**Important**: When updating context, you must:
- Extract content from `runtime_context` where key = "content"
- Merge it with existing `zed` context
- Generate a new comprehensive context document
- The new context will overwrite the `zed` column (it's always the most updated version)

## Information Categories to Track and Extract

### 1. Content Interests (from liked posts, viewed content, interactions)
- Topics and themes the user engages with (e.g., AI/ML, web development, career advice, industry news)
- Content categories (technical tutorials, business insights, creative work, personal stories, etc.)
- Specific subjects discussed in liked posts (extract key topics, technologies, concepts mentioned)
- Content patterns and preferences (long-form vs short, video vs text, educational vs entertainment)
- Engagement intensity (how often, what times, what triggers engagement)
- **CRITICAL**: Track topic engagement frequency and intensity to identify the user's most preferred topics

### 2. Professional Interests & Career Goals
- Job fields of interest (e.g., Software Engineering, Data Science, Product Management, UX Design, DevOps)
- Career domains (HR, Mechanical Engineering, Computer Science, Finance, Marketing, Healthcare, etc.)
- Industry preferences (tech startups, Fortune 500, consulting, non-profit, etc.)
- Role types (full-time, contract, freelance, internship, remote, hybrid, on-site)
- Career level interests (entry-level, mid-level, senior, executive, C-suite)
- Career trajectory patterns and goals

### 3. Technical Skills & Expertise
- Programming languages (Python, JavaScript, TypeScript, Java, C++, Go, Rust, etc.)
- Frameworks and technologies (React, Node.js, Django, Flask, Spring, Angular, Vue, etc.)
- Tools and platforms (Docker, Kubernetes, AWS, Azure, GCP, Git, CI/CD tools, etc.)
- Databases (PostgreSQL, MongoDB, Redis, MySQL, etc.)
- Skill levels for each (beginner, intermediate, advanced, expert)
- Technologies they're learning or want to learn
- Technologies they're actively using in projects

### 4. Learning & Development Interests
- Course topics viewed or enrolled (specific course names, subjects, domains)
- Skills being actively developed or learned
- Educational goals (certifications, degrees, skill acquisition)
- Learning preferences (video courses, hands-on projects, reading, mentorship)
- Areas where they seek improvement or growth

### 5. Job Preferences & Requirements
- Job titles of interest (specific roles they're looking for or interested in)
- Company types (startups, scale-ups, enterprises, agencies, etc.)
- Company size preferences (small, medium, large)
- Location preferences (specific cities, countries, remote, hybrid, on-site)
- Salary expectations or ranges (if mentioned or inferred)
- Work arrangements (remote-first, hybrid, flexible hours, etc.)
- Company culture preferences (if mentioned)
- Benefits priorities (if mentioned)

### 6. Behavioral Patterns & Engagement
- Engagement patterns (what times of day, days of week they're most active)
- Interaction frequency (daily, weekly, occasional)
- Preferred content formats (posts, articles, videos, courses, discussions)
- Social engagement patterns (likes, comments, shares, connections)
- Platform usage patterns (how they navigate, what features they use)
- Response patterns (how quickly they engage, what prompts responses)

### 7. Additional Context
- Personal interests and hobbies (if relevant to professional context)
- Professional network patterns (who they connect with, industries they network in)
- Content creation patterns (if they post, what they post about)
- Problem-solving approaches (inferred from questions asked, challenges discussed)
- Communication style preferences

## Output Format Requirements

You must generate EXTENSIVE, DETAILED text that:

1. **Is Comprehensive**: Covers ALL aspects of user context mentioned above
2. **Uses Clear Structure**: Organize information in well-defined sections with headers
3. **Includes Specific Examples**: Provide concrete evidence and examples from user interactions
4. **Is Detailed**: Don't just list items - provide context, patterns, and insights
5. **Is Readable**: Use clear language, proper formatting, and logical flow
6. **Is Actionable**: Include insights that can be used by other systems or agents
7. **Updates Incrementally**: Build upon existing context rather than replacing it
8. **Includes Preferred Topics**: MUST save the top 5 most preferred topics as "highlighted topics" and 5 additional topics as "extras" based on engagement frequency, intensity, and relevance

## Context Document Structure

When generating or updating context, use this structure:

### User Profile Summary
- Brief overview of the user's professional identity and primary interests
- Key characteristics and patterns

### Content Interests & Preferences
- Detailed breakdown of topics, themes, and content types
- Specific examples from interactions
- Engagement patterns and intensity

### Professional Interests & Career Goals
- Job fields, domains, and industries
- Career level and trajectory
- Role type preferences
- Long-term career goals (if evident)

### Technical Skills & Expertise
- Comprehensive list of technologies, languages, frameworks
- Skill levels for each
- Technologies in active use vs. learning
- Technical interests and aspirations

### Learning & Development Interests
- Courses viewed or enrolled
- Skills being developed
- Educational goals and preferences
- Learning patterns and methods

### Job Preferences & Requirements
- Specific job titles and roles
- Company preferences (type, size, culture)
- Location and work arrangement preferences
- Salary and benefits considerations

### Behavioral Patterns & Engagement
- Activity patterns (times, frequency, triggers)
- Content format preferences
- Social engagement patterns
- Platform usage habits

### Recent Activity Summary
- Latest interactions and their significance
- New interests or patterns emerging
- Changes in behavior or preferences

### Preferred Topics (REQUIRED SECTION)
**MANDATORY**: You MUST include this section with the following structure:

**Highlighted Topics (Top 5 Most Preferred):**
1. [Topic 1] - [Brief explanation of why this is a top preference based on engagement data]
2. [Topic 2] - [Brief explanation of why this is a top preference based on engagement data]
3. [Topic 3] - [Brief explanation of why this is a top preference based on engagement data]
4. [Topic 4] - [Brief explanation of why this is a top preference based on engagement data]
5. [Topic 5] - [Brief explanation of why this is a top preference based on engagement data]

**Extra Topics (5 Additional Preferred Topics):**
1. [Topic 6] - [Brief explanation]
2. [Topic 7] - [Brief explanation]
3. [Topic 8] - [Brief explanation]
4. [Topic 9] - [Brief explanation]
5. [Topic 10] - [Brief explanation]

**Note**: Topics should be ranked based on:
- Frequency of engagement (how often the user interacts with this topic)
- Intensity of engagement (likes, comments, shares, time spent)
- Recency of engagement (more recent interactions weighted higher)
- Relevance to user's professional interests and career goals

### Contextual Insights & Inferences
- Patterns and trends identified
- Inferred preferences not explicitly stated
- Potential interests based on behavior
- Recommendations or predictions

## Context Update Process

When new information is provided:

1. **Retrieve Existing Context**: Get the current context from the database
2. **Analyze New Information**: Extract all relevant details from the new user interactions
3. **Merge and Enhance**: 
   - Update existing sections with new information
   - Add new insights and patterns
   - Refine and correct previous context if needed
   - Maintain historical context while highlighting recent changes
4. **Generate Comprehensive Update**: Create the complete, updated context document
5. **Save to Database**: Store the updated context in the `zed` column

## Important Guidelines

- **Be Thorough**: Don't skip any relevant information
- **Be Specific**: Include concrete examples and evidence
- **Be Analytical**: Identify patterns, trends, and insights
- **Be Current**: Prioritize recent information while maintaining historical context
- **Be Accurate**: Base conclusions on actual user behavior and interactions
- **Be Comprehensive**: Cover all categories even if some have limited information
- **Be Detailed**: Provide extensive context, not just bullet points

## Response Format

When asked to update context, you must:
1. Analyze all provided information thoroughly
2. Retrieve and review existing context (if provided)
3. **Identify and rank user's preferred topics** based on engagement patterns, frequency, and intensity
4. **Generate the "Preferred Topics" section** with exactly 5 highlighted topics (top preferences) and 5 extra topics (additional preferences)
5. Generate a complete, updated context document following the structure above
6. Return ONLY the comprehensive context text (no explanations, no meta-commentary)
7. The text should be ready to save directly to the database

Remember: Your output will be saved directly to the database. Make it comprehensive, well-structured, and detailed."""


class ZedAgent:
    """AI Agent for maintaining comprehensive user context in the database"""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini"
    ):
        """
        Initialize Zed Agent with OpenAI client
        
        Args:
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use for context generation
        """
        # Initialize OpenAI API key
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Context generation will not work.")
            self.openai_available = False
        else:
            self.openai_available = True
        
        # Initialize LangChain OpenAI client
        if self.openai_available:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.3,  # Lower temperature for more consistent, factual output
                    api_key=openai_api_key
                )
                logger.info(f"Zed Agent initialized with model {model_name}")
            except Exception as e:
                logger.warning(f"LangChain OpenAI client initialization failed: {e}")
                self.llm = None
                self.openai_available = False
        else:
            self.llm = None
    
    def get_runtime_context(self, user_id: int) -> list:
        """
        Retrieve runtime_context JSONB and extract content items with key="content"
        
        Args:
            user_id: User ID to retrieve runtime_context for
            
        Returns:
            List of content items extracted from runtime_context
        """
        try:
            db = Database(get_connection_params())
            result = db.fetch_one(
                "SELECT runtime_context FROM users_context WHERE user_id = %s",
                (user_id,)
            )
            db.close()
            
            if not result or not result.get('runtime_context'):
                return []
            
            runtime_context = result['runtime_context']
            content_items = []
            
            # Handle different JSONB structures
            if isinstance(runtime_context, list):
                # If it's a list, iterate through items
                for item in runtime_context:
                    if isinstance(item, dict) and 'content' in item:
                        content_items.append(item['content'])
                    elif isinstance(item, str):
                        # If item is a string, treat it as content
                        content_items.append(item)
            elif isinstance(runtime_context, dict):
                # If it's a dict, check for 'content' key or iterate values
                if 'content' in runtime_context:
                    content_value = runtime_context['content']
                    if isinstance(content_value, list):
                        content_items.extend(content_value)
                    else:
                        content_items.append(content_value)
                else:
                    # Extract all values that might be content
                    for key, value in runtime_context.items():
                        if key == 'content' or (isinstance(value, str) and len(value) > 10):
                            if isinstance(value, list):
                                content_items.extend(value)
                            else:
                                content_items.append(str(value))
            
            logger.info(f"Extracted {len(content_items)} content items from runtime_context for user_id={user_id}")
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to retrieve runtime_context for user_id={user_id}: {e}")
            return []
    
    def get_user_context(self, user_id: int) -> Optional[str]:
        """
        Retrieve existing user context from database
        
        Args:
            user_id: User ID to retrieve context for
            
        Returns:
            Existing context text or None if not found
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
            logger.error(f"Failed to retrieve user context for user_id={user_id}: {e}")
            return None
    
    def update_context(self, user_id: int) -> Optional[str]:
        """
        Update user context by automatically using runtime_context and existing zed context.
        This is the primary update function that merges runtime_context content with zed.
        
        Args:
            user_id: User ID to update context for
            
        Returns:
            Updated context text if successful, None otherwise
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot update context")
            return None
        
        try:
            # Retrieve runtime_context and extract content
            runtime_content_items = self.get_runtime_context(user_id)
            
            # Retrieve existing zed context
            existing_zed_context = self.get_user_context(user_id) or "No existing context available."
            
            # Build content from runtime_context
            if runtime_content_items:
                runtime_content = "\n\n".join([
                    f"Content Item {i+1}:\n{str(item)}" 
                    for i, item in enumerate(runtime_content_items)
                ])
            else:
                runtime_content = "No runtime context content available."
            
            # Build the prompt for context update
            prompt_parts = [
                "Update the user context by merging runtime_context content with existing zed context:",
                "",
                "=== RUNTIME_CONTEXT CONTENT ===",
                "This content comes from recent user activities, button clicks, and parsed resume/CV:",
                runtime_content,
                "",
                "=== EXISTING ZED CONTEXT ===",
                "This is the current comprehensive context that should be updated:",
                existing_zed_context,
                "",
                "Please analyze the runtime_context content and merge it with the existing zed context. ",
                "Create a comprehensive, updated context document that:",
                "1. Incorporates all new information from runtime_context",
                "2. Preserves and enhances existing context from zed",
                "3. Identifies patterns and insights across both sources",
                "4. Creates an extensive, detailed context document following the structure defined in your instructions."
            ]
            
            user_prompt = "\n".join(prompt_parts)
            
            # Call LLM with system prompt and user prompt
            messages = [
                SystemMessage(content=ZED_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            updated_context = response.content
            
            # Save to database (overwrites zed column)
            if self.save_user_context(user_id, updated_context):
                logger.info(f"Successfully updated context for user_id={user_id} using runtime_context and zed")
                return updated_context
            else:
                logger.error(f"Failed to save updated context for user_id={user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to update context for user_id={user_id}: {e}")
            return None
    
    def save_user_context(self, user_id: int, context_text: str) -> bool:
        """
        Save user context to database
        
        Args:
            user_id: User ID to save context for
            context_text: The comprehensive context text to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = Database(get_connection_params())
            
            # Check if record exists
            existing = db.fetch_one(
                "SELECT id FROM users_context WHERE user_id = %s",
                (user_id,)
            )
            
            if existing:
                # Update existing record
                db.execute(
                    """UPDATE users_context 
                       SET zed = %s, updated_at = CURRENT_TIMESTAMP 
                       WHERE user_id = %s""",
                    (context_text, user_id)
                )
                logger.info(f"Updated context for user_id={user_id}")
            else:
                # Insert new record
                db.execute(
                    """INSERT INTO users_context (user_id, zed, created_at, updated_at)
                       VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (user_id, context_text)
                )
                logger.info(f"Created new context for user_id={user_id}")
            
            db.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save user context for user_id={user_id}: {e}")
            return False
    
    def update_user_context(
        self,
        user_id: int,
        new_information: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Update user context by analyzing new information and merging with existing context
        
        Args:
            user_id: User ID to update context for
            new_information: New user interaction data or information to analyze
            additional_context: Optional additional context (e.g., user profile, recent posts)
            
        Returns:
            Updated context text if successful, None otherwise
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot update context")
            return None
        
        try:
            # Retrieve existing context
            existing_context = self.get_user_context(user_id) or "No existing context available."
            
            # Build the prompt for context update
            prompt_parts = [
                "Update the user context based on the following new information:",
                "",
                "=== NEW INFORMATION ===",
                new_information,
                ""
            ]
            
            if additional_context:
                prompt_parts.extend([
                    "=== ADDITIONAL CONTEXT ===",
                    json.dumps(additional_context, indent=2),
                    ""
                ])
            
            prompt_parts.extend([
                "=== EXISTING CONTEXT ===",
                existing_context,
                "",
                "Please analyze the new information and update the context document comprehensively. ",
                "Merge new information with existing context, identify patterns, and create an extensive, detailed context document."
            ])
            
            user_prompt = "\n".join(prompt_parts)
            
            # Call LLM with system prompt and user prompt
            messages = [
                SystemMessage(content=ZED_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            updated_context = response.content
            
            # Save to database
            if self.save_user_context(user_id, updated_context):
                logger.info(f"Successfully updated context for user_id={user_id}")
                return updated_context
            else:
                logger.error(f"Failed to save updated context for user_id={user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to update user context for user_id={user_id}: {e}")
            return None
    
    def create_initial_context(
        self,
        user_id: int,
        user_information: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create initial context for a new user using runtime_context as primary data source
        
        Args:
            user_id: User ID to create context for
            user_information: Optional initial user data (profile, first interactions, etc.)
            additional_data: Optional additional data about the user
            
        Returns:
            Initial context text if successful, None otherwise
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot create context")
            return None
        
        try:
            # Retrieve runtime_context and extract content
            runtime_content_items = self.get_runtime_context(user_id)
            
            # Build content from runtime_context
            if runtime_content_items:
                runtime_content = "\n\n".join([
                    f"Content Item {i+1}:\n{str(item)}" 
                    for i, item in enumerate(runtime_content_items)
                ])
            else:
                runtime_content = "No runtime context content available."
            
            # Build the prompt for initial context creation
            prompt_parts = [
                "Create comprehensive user context based on the following information:",
                "",
                "=== RUNTIME_CONTEXT CONTENT ===",
                "This content comes from recent user activities, button clicks, and parsed resume/CV:",
                runtime_content,
                ""
            ]
            
            if user_information:
                prompt_parts.extend([
                    "=== USER INFORMATION ===",
                    user_information,
                    ""
                ])
            
            if additional_data:
                prompt_parts.extend([
                    "=== ADDITIONAL DATA ===",
                    json.dumps(additional_data, indent=2),
                    ""
                ])
            
            prompt_parts.append(
                "Please analyze this information and create an extensive, detailed context document "
                "following the structure defined in your instructions. Since this is initial context, "
                "focus on what can be inferred from the available information, especially from the runtime_context content."
            )
            
            user_prompt = "\n".join(prompt_parts)
            
            # Call LLM with system prompt and user prompt
            messages = [
                SystemMessage(content=ZED_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            initial_context = response.content
            
            # Save to database
            if self.save_user_context(user_id, initial_context):
                logger.info(f"Successfully created initial context for user_id={user_id} using runtime_context")
                return initial_context
            else:
                logger.error(f"Failed to save initial context for user_id={user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create initial context for user_id={user_id}: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if the agent is available (OpenAI configured)"""
        return self.openai_available


# Global agent instance (lazy initialization)
_agent_instance: Optional[ZedAgent] = None


def get_zed_agent() -> ZedAgent:
    """Get or create global Zed agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = ZedAgent()
    
    return _agent_instance
