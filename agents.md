# AI Agents Flow Diagrams

This document contains all Mermaid flow diagrams for the ZedRec AI agents. These diagrams illustrate the complete workflows and data flows for each agent in the system.

## Table of Contents

1. [Zed Agent - Context Update Flow](#zed-agent-context-update-flow)
2. [Azel Agent - Question Generation Flow](#azel-agent-question-generation-flow)
3. [Seez Agent - Answer Evaluation Flow](#seez-agent-answer-evaluation-flow)
4. [Vec Agent - Vector Database Population Flow](#vec-agent-vector-database-population-flow)
5. [Nemz Agent - Career Assistant Search Flow](#nemz-agent-career-assistant-search-flow)
6. [Riz Agent - Interview Flow (Flowchart)](#riz-agent-interview-flow-flowchart)
7. [Riz Agent - Interview Sequence (Sequence Diagram)](#riz-agent-interview-sequence-sequence-diagram)
8. [Complete Agent Ecosystem Overview](#complete-agent-ecosystem-overview)

---

## Zed Agent - Context Update Flow

**Purpose:** Shows how Zed Agent maintains and updates user context from runtime activities.

```mermaid
flowchart TD
    Start([User Clicks Button<br/>e.g., Like Post, View Job, Upload Resume]) --> Store[Store Activity in<br/>runtime_context JSONB<br/>users_context table]
    
    Store --> Trigger[Trigger Context Update<br/>update_context user_id]
    
    Trigger --> GetRT[get_runtime_context<br/>Extract content from JSONB<br/>WHERE user_id = user_id]
    
    GetRT --> Parse[Parse JSONB Structure<br/>Extract items with key='content'<br/>Handle: List, Dict, Nested]
    
    Parse --> GetZed[get_user_context<br/>Retrieve existing zed context<br/>WHERE user_id = user_id]
    
    GetZed --> Format[Format Content<br/>Runtime Context Items<br/>+ Existing Zed Context]
    
    Format --> BuildPrompt[Build Comprehensive Prompt<br/>System Prompt: ZED_SYSTEM_PROMPT<br/>User Prompt: Runtime + Zed + Instructions]
    
    BuildPrompt --> LLM[OpenAI GPT-4o-mini<br/>Analyze & Merge Context<br/>Generate Updated Context]
    
    LLM --> Analyze[AI Analysis<br/>7 Information Categories<br/>9 Section Document Structure]
    
    Analyze --> Generate[Generate Comprehensive Context<br/>User Profile, Interests, Skills,<br/>Preferences, Patterns, Insights]
    
    Generate --> Save[save_user_context<br/>UPDATE users_context<br/>SET zed = new_context<br/>WHERE user_id = user_id]
    
    Save --> End([Context Updated in zed Column<br/>Ready for Next Update])
    
    style Start fill:#e1f5ff
    style Store fill:#fff9c4
    style GetRT fill:#e3f2fd
    style GetZed fill:#e3f2fd
    style LLM fill:#fff9c4
    style Analyze fill:#c8e6c9
    style Save fill:#f3e5f5
    style End fill:#c8e6c9
```

---

## Azel Agent - Question Generation Flow

**Purpose:** Illustrates the complete process of generating personalized course questions using user context, web search, and knowledge bases.

```mermaid
flowchart TD
    Start(["Manual Trigger<br/>API Endpoint"]) --> Validate["Validate Course Exists<br/>Check User Authentication"]
    Validate --> GetContext["Get Zed Context<br/>SELECT zed FROM users_context<br/>WHERE user_id"]
    GetContext --> CheckContext{"Context Exists?"}
    CheckContext -->|No| Error1["Return Error<br/>No Zed context found"]
    CheckContext -->|Yes| ExtractTopics["Extract Highlighted Topics<br/>LLM: Extract topics from context<br/>Return JSON array of topics"]
    ExtractTopics --> CheckTopics{"Topics Found?"}
    CheckTopics -->|No| Error2["Return Error<br/>No topics extracted"]
    CheckTopics -->|Yes| GoogleSearch["DuckDuckGo Search<br/>For each topic top 3<br/>Search with tutorial course educational<br/>Extract URL title snippet"]
    GoogleSearch --> SaveURLs["Save URLs to Database<br/>INSERT INTO azel_search_urls<br/>user_id course_id url_id url title snippet search_query"]
    SaveURLs --> CreateKB["Create Qdrant KB<br/>Collection azel_kb_userid_courseid<br/>TTL 30 minutes"]
    CreateKB --> ExtractContent["Extract Content from URLs<br/>BeautifulSoup Parse HTML<br/>Extract text content<br/>Limit 5000 chars per URL"]
    ExtractContent --> GenerateEmbeddings["Generate Embeddings<br/>OpenAI text-embedding-3-small<br/>Store in Qdrant with metadata"]
    GenerateEmbeddings --> GenerateQuestions["Generate Questions<br/>LLM: Use highlighted topics<br/>Zed context Knowledge base content<br/>Generate 3-5 questions with detailed answers"]
    GenerateQuestions --> SaveQuestions["Save Questions<br/>INSERT INTO lms_questions<br/>Store detailed answer in correct_answer field"]
    SaveQuestions --> ReturnResult["Return Result<br/>success topics URLs questions counts"]
    ReturnResult --> End(["Complete"])
    
    style Start fill:#e1f5ff
    style GetContext fill:#e3f2fd
    style ExtractTopics fill:#fff9c4
    style GoogleSearch fill:#fff9c4
    style SaveURLs fill:#f3e5f5
    style CreateKB fill:#c8e6c9
    style GenerateQuestions fill:#fff9c4
    style SaveQuestions fill:#f3e5f5
    style End fill:#c8e6c9
```

---

## Seez Agent - Answer Evaluation Flow

**Purpose:** Shows the sequence of answer evaluation, scoring, and performance updates.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as LMS API
    participant SeezAgent as Seez Agent
    participant LLM as OpenAI LLM
    participant Service as LMSService
    participant DB as Database

    Note over User,DB: Answer Evaluation Flow

    User->>Frontend: Submit Answers
    Frontend->>API: POST /api/lms/questions/id/answer
    API->>Service: submit_answer(user_id, question_id, answer_text)
    Service->>DB: INSERT INTO lms_user_answers
    DB-->>Service: Answer Created
    Service-->>API: Answer Response
    API-->>Frontend: Answer Submitted

    Note over User,DB: Seez Agent Evaluation Flow

    User->>Frontend: Trigger Evaluation
    Frontend->>API: POST /api/lms/seez/evaluate-course/course_id
    API->>SeezAgent: evaluate_course_answers(user_id, course_id)
    
    SeezAgent->>DB: SELECT ua.*, q.* FROM lms_user_answers ua<br/>JOIN lms_questions q ON ua.question_id = q.id<br/>WHERE ua.user_id = ? AND q.course_id = ?<br/>AND ua.evaluated_at IS NULL
    
    DB-->>SeezAgent: List of Unevaluated Answers
    
    loop For Each Answer
        SeezAgent->>SeezAgent: _evaluate_single_answer(question, answer_text)
        SeezAgent->>LLM: Evaluate Answer (System Prompt + Question + Correct Answer + User Answer)
        LLM-->>SeezAgent: JSON: {score, is_correct, feedback, improvement_suggestions, points_earned}
        
        SeezAgent->>SeezAgent: Validate Score (0-10)<br/>Calculate: points_earned = (score/10) * question_points<br/>Determine: is_correct = score >= 7<br/>Format: feedback + improvement_suggestions
        
        SeezAgent->>Service: evaluate_answer(answer_id, is_correct, points_earned, feedback)
        Service->>DB: UPDATE lms_user_answers<br/>SET is_correct, points_earned, feedback, evaluated_at
        Service->>DB: Update lms_user_course_performance<br/>(incremental update)
        Service->>DB: Update lms_dashboard stats
        Service->>DB: Update lms_user_domain_performance
        Service->>DB: Update lms_weekly_performance
    end
    
    SeezAgent->>SeezAgent: Calculate Average Score<br/>average = sum(scores) / count(answers)
    
    SeezAgent-->>API: Result: {success, evaluated_count, average_score, evaluations}
    API-->>Frontend: Evaluation Results
    Frontend-->>User: Display Scores & Feedback
```

---

## Vec Agent - Vector Database Population Flow

**Purpose:** Shows how Vec Agent indexes jobs, users, and posts into Qdrant vector database.

```mermaid
flowchart TD
    Start([Scheduled Job Trigger<br/>Every 24 Hours]) --> CheckForce{Force Sync?}
    CheckForce -->|Yes| GetAll[Get All Entities<br/>No Time Filter]
    CheckForce -->|No| GetRecent[Get Entities<br/>Created/Updated<br/>Last 24 Hours]
    
    GetAll --> Parallel[Parallel Processing<br/>ThreadPoolExecutor<br/>3 Workers]
    GetRecent --> Parallel
    
    Parallel --> IndexJobs[index_jobs<br/>Batch Process Jobs]
    Parallel --> IndexUsers[index_users<br/>Batch Process Users]
    Parallel --> IndexPosts[index_posts<br/>Batch Process Posts]
    
    IndexJobs --> FetchJobs[Fetch Jobs from DB<br/>Pagination: 50 per batch]
    IndexUsers --> FetchUsers[Fetch Users from DB<br/>Pagination: 50 per batch]
    IndexPosts --> FetchPosts[Fetch Posts from DB<br/>Pagination: 50 per batch]
    
    FetchJobs --> FormatJobs[Format Job Text<br/>Title + Description +<br/>Company + Location + Skills]
    FetchUsers --> FormatUsers[Format User Text<br/>Name + About + Skills +<br/>Status + Interests]
    FetchPosts --> FormatPosts[Format Post Text<br/>Post Description]
    
    FormatJobs --> ChunkJobs{Text > 6000 chars?}
    FormatUsers --> ChunkUsers{Text > 6000 chars?}
    FormatPosts --> ChunkPosts{Text > 6000 chars?}
    
    ChunkJobs -->|Yes| ChunkJobText[Split into Chunks<br/>6000 chars, 200 overlap]
    ChunkJobs -->|No| EmbedJobs[Generate Embeddings<br/>Batch: 100 per API call]
    ChunkJobText --> EmbedJobs
    
    ChunkUsers -->|Yes| ChunkUserText[Split into Chunks<br/>6000 chars, 200 overlap]
    ChunkUsers -->|No| EmbedUsers[Generate Embeddings<br/>Batch: 100 per API call]
    ChunkUserText --> EmbedUsers
    
    ChunkPosts -->|Yes| ChunkPostText[Split into Chunks<br/>6000 chars, 200 overlap]
    ChunkPosts -->|No| EmbedPosts[Generate Embeddings<br/>Batch: 100 per API call]
    ChunkPostText --> EmbedPosts
    
    EmbedJobs --> StoreJobs[Store in Qdrant<br/>Collection: nemz_jobs<br/>With Metadata]
    EmbedUsers --> StoreUsers[Store in Qdrant<br/>Collection: nemz_users<br/>With Metadata]
    EmbedPosts --> StorePosts[Store in Qdrant<br/>Collection: nemz_posts<br/>With Metadata]
    
    StoreJobs --> LogProgress[Log Progress<br/>Every 500 entities]
    StoreUsers --> LogProgress
    StorePosts --> LogProgress
    
    LogProgress --> CheckMore{More Entities?}
    CheckMore -->|Yes| FetchJobs
    CheckMore -->|No| Complete([Sync Complete<br/>Collections Updated])
    
    style Start fill:#e1f5ff
    style Parallel fill:#fff9c4
    style EmbedJobs fill:#c8e6c9
    style EmbedUsers fill:#c8e6c9
    style EmbedPosts fill:#c8e6c9
    style StoreJobs fill:#f3e5f5
    style StoreUsers fill:#f3e5f5
    style StorePosts fill:#f3e5f5
    style Complete fill:#c8e6c9
```

---

## Nemz Agent - Career Assistant Search Flow

**Purpose:** Illustrates how Nemz Agent detects query intent and searches across jobs, profiles, and posts.

```mermaid
flowchart TD
    Start([User Query<br/>Frontend Request]) --> CheckType{search_type<br/>Provided?}
    
    CheckType -->|No| DetectIntent[Determine Query Intent<br/>LLM: QUERY_INTENT_PROMPT<br/>Analyze Natural Language]
    CheckType -->|Yes| UseType[Use Provided Type]
    
    DetectIntent --> ParseIntent[Parse LLM Response<br/>Extract search_type<br/>jobs/profiles/posts/all]
    ParseIntent --> UseType
    
    UseType --> CheckIntent{search_type?}
    
    CheckIntent -->|jobs| SearchJobs[Search Jobs Collection<br/>nemz_jobs]
    CheckIntent -->|profiles| SearchProfiles[Search Profiles Collection<br/>nemz_users]
    CheckIntent -->|posts| SearchPosts[Search Posts Collection<br/>nemz_posts]
    CheckIntent -->|all| ParallelSearch[Parallel Search<br/>All Three Collections<br/>ThreadPoolExecutor]
    
    ParallelSearch --> SearchJobs
    ParallelSearch --> SearchProfiles
    ParallelSearch --> SearchPosts
    
    SearchJobs --> EmbedQuery1[Generate Query Embedding<br/>OpenAI text-embedding-3-small]
    SearchProfiles --> EmbedQuery2[Generate Query Embedding<br/>OpenAI text-embedding-3-small]
    SearchPosts --> EmbedQuery3[Generate Query Embedding<br/>OpenAI text-embedding-3-small]
    
    EmbedQuery1 --> VectorSearch1[Vector Similarity Search<br/>Qdrant: Cosine Distance<br/>Top K Results]
    EmbedQuery2 --> VectorSearch2[Vector Similarity Search<br/>Qdrant: Cosine Distance<br/>Top K Results]
    EmbedQuery3 --> VectorSearch3[Vector Similarity Search<br/>Qdrant: Cosine Distance<br/>Top K Results]
    
    VectorSearch1 --> DedupeJobs[Deduplicate by job_id<br/>Keep Best Match Score<br/>Per Entity]
    VectorSearch2 --> DedupeProfiles[Deduplicate by user_id<br/>Keep Best Match Score<br/>Per Entity]
    VectorSearch3 --> DedupePosts[Deduplicate by post_id<br/>Keep Best Match Score<br/>Per Entity]
    
    DedupeJobs --> RankJobs[Rank by Match Score<br/>Descending Order]
    DedupeProfiles --> RankProfiles[Rank by Match Score<br/>Descending Order]
    DedupePosts --> RankPosts[Rank by Match Score<br/>Descending Order]
    
    RankJobs --> Combine[Combine Results<br/>jobs + profiles + posts]
    RankProfiles --> Combine
    RankPosts --> Combine
    
    Combine --> FormatResponse[Format Response<br/>query, search_type,<br/>jobs[], profiles[], posts[],<br/>total_results]
    
    FormatResponse --> Return([Return to Frontend<br/>Display Results])
    
    style Start fill:#e1f5ff
    style DetectIntent fill:#fff9c4
    style ParallelSearch fill:#fff9c4
    style EmbedQuery1 fill:#c8e6c9
    style EmbedQuery2 fill:#c8e6c9
    style EmbedQuery3 fill:#c8e6c9
    style VectorSearch1 fill:#e3f2fd
    style VectorSearch2 fill:#e3f2fd
    style VectorSearch3 fill:#e3f2fd
    style Combine fill:#f3e5f5
    style Return fill:#c8e6c9
```

---

## Riz Agent - Interview Flow (Flowchart)

**Purpose:** Complete flowchart showing the interview process from start to completion with RizAgent coaching feedback, including file access and database operations.

```mermaid
flowchart TD
    Start([User Starts Interview<br/>POST /api/interviews/start]) --> GetJob[Get Job Details<br/>File: backend/services/interview_service.py<br/>DB: SELECT FROM job_postings<br/>WHERE job_id<br/>Columns: title, description, company_name,<br/>location, job_type, skills_required]
    
    GetJob --> CalcAttempt[Calculate Attempt Number<br/>File: backend/services/interview_service.py<br/>DB: SELECT COUNT FROM live_interviews<br/>WHERE user_id AND job_id<br/>Returns: attempt_number]
    
    CalcAttempt --> GenQuestions[Generate Interview Questions<br/>File: backend/services/interview_question_service.py<br/>LLM: OpenAI GPT-4o-mini<br/>Input: Job description from job_postings<br/>Output: 5-7 questions JSON array<br/>with question_text, question_type,<br/>answer_criteria, expected_key_points,<br/>difficulty_level]
    
    GenQuestions --> GenPrompt[Generate System Prompt<br/>File: backend/services/interview_question_service.py<br/>Method: generate_system_prompt<br/>Includes: Job context + Questions<br/>+ Interview instructions]
    
    GenPrompt --> CreateTavus[Create Tavus Conversation<br/>File: backend/services/tavus_service.py<br/>External: POST /v2/conversations<br/>Params: replica_id, system_prompt<br/>Response: conversation_id, status]
    
    CreateTavus --> GetConvId[Get conversation_id<br/>File: backend/services/tavus_service.py<br/>Extract from Tavus API response]
    
    GetConvId --> SaveInterview[Save Interview Record<br/>File: backend/services/interview_service.py<br/>DB: INSERT INTO live_interviews<br/>Columns Saved:<br/>- user_id<br/>- job_id<br/>- tavus_conversation_id<br/>- tavus_response JSONB<br/>- questions JSONB<br/>- attempt_number<br/>- status: 'in_progress'<br/>- started_at TIMESTAMP]
    
    SaveInterview --> ReturnStart([Return Interview Details<br/>interview_id, conversation_id<br/>Questions to Frontend])
    
    ReturnStart --> UserCompletes([User Completes<br/>Video Interview<br/>via Tavus])
    
    UserCompletes --> CompleteAPI([User Calls<br/>POST /api/interviews/id/complete])
    
    CompleteAPI --> GetInterview[Get Interview Record<br/>File: backend/services/interview_service.py<br/>DB: SELECT FROM live_interviews<br/>WHERE interview_id<br/>Load: questions, tavus_conversation_id]
    
    GetInterview --> GetTranscript[Get Interview Transcript<br/>File: backend/services/tavus_service.py<br/>External: GET /v2/conversations/id/transcript<br/>Returns: Full transcript with<br/>questions and responses]
    
    GetTranscript --> ExtractResponses[Extract User Responses<br/>File: backend/services/interview_service.py<br/>Method: _extract_user_responses<br/>Parse transcript and map<br/>responses to questions]
    
    ExtractResponses --> GetJobDetails[Get Job Details for Context<br/>File: backend/services/interview_service.py<br/>DB: SELECT FROM job_postings<br/>WHERE job_id<br/>Load: title, description, company_name]
    
    GetJobDetails --> TavCheck[Tav_check_agent Analysis<br/>File: backend/agents/Tav_check_agent.py<br/>LLM: OpenAI GPT-4o-mini<br/>Input: questions, user_responses,<br/>job_context<br/>Output: Analysis JSON with scores<br/>and feedback]
    
    TavCheck --> CalcScores[Calculate Scores<br/>File: backend/agents/Tav_check_agent.py<br/>Calculates:<br/>- overall_score 0-100<br/>- technical_score<br/>- communication_score<br/>- problem_solving_score<br/>- domain_knowledge_score]
    
    CalcScores --> GenFeedback[Generate Feedback<br/>File: backend/agents/Tav_check_agent.py<br/>Generates:<br/>- detailed_feedback TEXT<br/>- strengths array<br/>- weaknesses array<br/>- improvement_suggestions array]
    
    GenFeedback --> CheckRiz{RizAgent<br/>Available?}
    
    CheckRiz -->|Yes| RizFeedback[RizAgent Feedback<br/>File: backend/agents/Riz_agent.py<br/>LLM: OpenAI GPT-4o-mini<br/>Method: generate_feedback<br/>Input: job_context, questions,<br/>user_responses, Tav_check analysis<br/>Output: JSON with:<br/>- summary<br/>- strengths array<br/>- weaknesses array<br/>- recommendations array<br/>- next_steps array]
    CheckRiz -->|No| SkipRiz[Skip Riz Feedback<br/>Log warning]
    
    RizFeedback --> SaveResults[Save All Results<br/>File: backend/services/interview_service.py<br/>DB: UPDATE live_interviews<br/>WHERE interview_id<br/>Columns Updated:<br/>- user_responses JSONB<br/>- overall_score INTEGER<br/>- score_breakdown JSONB<br/>- feedback TEXT<br/>- riz_feedback JSONB<br/>- status: 'completed'<br/>- completed_at TIMESTAMP]
    SkipRiz --> SaveResults
    
    SaveResults --> ReturnComplete([Return Complete Results<br/>Scores, Feedback,<br/>Riz Coaching to Frontend])
    
    style Start fill:#e1f5ff
    style GenQuestions fill:#fff9c4
    style CreateTavus fill:#fff9c4
    style TavCheck fill:#fff9c4
    style RizFeedback fill:#c8e6c9
    style SaveResults fill:#f3e5f5
    style ReturnComplete fill:#c8e6c9
```

### File Access Details

**Backend Files Accessed:**
- `backend/routers/interviews.py` - API endpoint handlers
- `backend/services/interview_service.py` - Main orchestration service
- `backend/services/interview_question_service.py` - Question generation
- `backend/services/tavus_service.py` - Tavus AI integration
- `backend/agents/Tav_check_agent.py` - Response analysis
- `backend/agents/Riz_agent.py` - Coaching feedback generation
- `backend/models/orm/live_interview.py` - Database model
- `backend/models/orm/job_posting.py` - Job model

**External Services:**
- Tavus AI API (`/v2/conversations`)
- OpenAI API (LLM for questions, analysis, feedback)

### Database Operations

**Table: `live_interviews`**

**On Interview Start (INSERT):**
- `user_id` (INTEGER, FK to users.uid)
- `job_id` (INTEGER, FK to job_postings.job_id)
- `tavus_conversation_id` (VARCHAR(255))
- `tavus_response` (JSONB) - Full Tavus API response
- `questions` (JSONB) - Generated questions array
- `attempt_number` (INTEGER) - Calculated attempt count
- `status` (VARCHAR(20)) - Set to 'in_progress'
- `started_at` (TIMESTAMP) - Current timestamp

**On Interview Complete (UPDATE):**
- `user_responses` (JSONB) - Extracted from transcript
- `overall_score` (INTEGER) - 0-100 score from Tav_check
- `score_breakdown` (JSONB) - Category scores:
  - `technical_score`
  - `communication_score`
  - `problem_solving_score`
  - `domain_knowledge_score`
- `feedback` (TEXT) - Detailed feedback from Tav_check
- `riz_feedback` (JSONB) - Coaching feedback structure:
  - `summary` (TEXT)
  - `strengths` (array)
  - `weaknesses` (array)
  - `recommendations` (array)
  - `next_steps` (array)
- `status` (VARCHAR(20)) - Updated to 'completed'
- `completed_at` (TIMESTAMP) - Completion timestamp

**Table: `job_postings` (READ ONLY)**
- Used to get job context for question generation and analysis
- Columns accessed: `job_id`, `title`, `description`, `company_name`, `location`, `job_type`, `skills_required`

---

## Riz Agent - Interview Sequence (Sequence Diagram)

**Purpose:** Sequence diagram showing the interaction between components during the interview process.

```mermaid
sequenceDiagram
    participant User
    participant API
    participant InterviewService
    participant QuestionService
    participant TavusService
    participant TavusAI
    participant TavCheckAgent
    participant Database

    User->>API: POST /api/interviews/start job_id
    API->>InterviewService: start_interview(user_id, job_id)
    InterviewService->>Database: Get job details
    InterviewService->>InterviewService: Calculate attempt_number
    InterviewService->>QuestionService: generate_interview_questions(job)
    QuestionService->>LLM: Generate questions from job description
    LLM-->>QuestionService: 5-7 questions with criteria
    QuestionService->>QuestionService: generate_system_prompt(job, questions)
    QuestionService-->>InterviewService: questions + system_prompt
    InterviewService->>TavusService: create_conversation(replica_id, prompt)
    TavusService->>TavusAI: POST /v2/conversations
    TavusAI-->>TavusService: conversation_id
    TavusService-->>InterviewService: conversation details
    InterviewService->>Database: Create LiveInterview record
    InterviewService-->>API: interview_id, conversation_id, questions
    API-->>User: Interview started
    
    User->>TavusAI: Complete video interview
    TavusAI-->>User: Interview completed
    
    User->>API: POST /api/interviews/id/complete
    API->>InterviewService: complete_interview(interview_id)
    InterviewService->>TavusService: get_conversation_transcript()
    TavusService->>TavusAI: GET transcript
    TavusAI-->>TavusService: Full transcript with responses
    TavusService-->>InterviewService: user_responses
    InterviewService->>TavCheckAgent: analyze_interview_responses()
    TavCheckAgent->>LLM: Analyze responses vs criteria
    LLM-->>TavCheckAgent: Scores + feedback
    TavCheckAgent-->>InterviewService: Analysis results
    InterviewService->>Database: Update interview with scores
    InterviewService-->>API: Complete results
    API-->>User: Scores, feedback, suggestions
```

---

## Complete Agent Ecosystem Overview

**Purpose:** High-level overview showing how all agents interact with frontend, backend services, data stores, and external services.

```mermaid
flowchart TB
    subgraph Frontend["Frontend Pages"]
        LMS[LMS Page]
        AIMode[AI Mode Page]
        Eval[Evaluation Page]
        Interviews[AI Interviews Page]
    end
    
    subgraph Backend["Backend Services"]
        LMSService[LMS Service]
        InterviewService[Interview Service]
    end
    
    subgraph Agents["AI Agents"]
        Zed[Zed Agent<br/>Context Maintainer]
        Azel[Azel Agent<br/>Question Generator]
        Seez[Seez Agent<br/>Answer Evaluator]
        Nemz[Nemz Agent<br/>Career Assistant]
        Vec[Vec Agent<br/>Vector Indexer]
        Riz[Riz Agent<br/>Interview Coach]
        TavCheck[Tav_check Agent<br/>Interview Analyzer]
    end
    
    subgraph DataStores["Data Stores"]
        PostgreSQL[(PostgreSQL<br/>Database)]
        Qdrant[(Qdrant<br/>Vector DB)]
    end
    
    subgraph External["External Services"]
        DuckDuckGo[DuckDuckGo<br/>Web Search]
        OpenAI[OpenAI API<br/>LLM + Embeddings]
        Tavus[Tavus AI<br/>Video Interviews]
    end
    
    %% User Interactions
    LMS -->|Trigger Question Gen| LMSService
    Eval -->|Trigger Evaluation| LMSService
    AIMode -->|Search Query| Nemz
    Interviews -->|Start/Complete| InterviewService
    
    %% LMS Flow
    LMSService -->|Get User Context| Zed
    LMSService -->|Generate Questions| Azel
    LMSService -->|Evaluate Answers| Seez
    
    %% Azel Agent Flow
    Azel -->|Get Context| Zed
    Azel -->|Web Search| DuckDuckGo
    Azel -->|Store URLs| PostgreSQL
    Azel -->|Create KB| Qdrant
    Azel -->|Generate Questions| OpenAI
    Azel -->|Save Questions| PostgreSQL
    
    %% Seez Agent Flow
    Seez -->|Evaluate Answers| OpenAI
    Seez -->|Update Scores| PostgreSQL
    Seez -->|Update Performance| LMSService
    
    %% Nemz Agent Flow
    Nemz -->|Detect Intent| OpenAI
    Nemz -->|Search Vectors| Qdrant
    Nemz -->|Return Results| AIMode
    
    %% Vec Agent Flow
    Vec -->|Index Jobs/Users/Posts| PostgreSQL
    Vec -->|Generate Embeddings| OpenAI
    Vec -->|Store Vectors| Qdrant
    Vec -.->|Scheduled<br/>Every 24h| Vec
    
    %% Interview Flow
    InterviewService -->|Generate Questions| OpenAI
    InterviewService -->|Create Interview| Tavus
    InterviewService -->|Analyze Responses| TavCheck
    InterviewService -->|Coaching Feedback| Riz
    TavCheck -->|Analysis| OpenAI
    Riz -->|Feedback| OpenAI
    InterviewService -->|Save Results| PostgreSQL
    
    %% Zed Agent Flow
    Zed -->|Update Context| PostgreSQL
    Zed -->|Analyze Data| OpenAI
    
    %% Data Flow
    PostgreSQL -->|Read Data| LMSService
    PostgreSQL -->|Read Data| InterviewService
    PostgreSQL -->|Read Data| Vec
    PostgreSQL -->|Read Data| Zed
    
    Qdrant -->|Vector Search| Nemz
    Qdrant -->|Store Vectors| Vec
    Qdrant -->|Store KB| Azel
    
    style Frontend fill:#e1f5ff
    style Backend fill:#fff9c4
    style Agents fill:#c8e6c9
    style DataStores fill:#f3e5f5
    style External fill:#ffecb3
```

---

## Notes

- All diagrams use Mermaid syntax and can be rendered in any Markdown viewer that supports Mermaid (GitHub, GitLab, VS Code with Mermaid extension, etc.)
- The diagrams show the complete data flow and decision points for each agent
- Color coding:
  - **Blue (#e1f5ff)**: Start/Entry points
  - **Yellow (#fff9c4)**: LLM/AI processing steps
  - **Green (#c8e6c9)**: Success/completion states
  - **Purple (#f3e5f5)**: Data storage operations
  - **Light Blue (#e3f2fd)**: Data retrieval operations
