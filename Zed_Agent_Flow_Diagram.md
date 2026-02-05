# Zed Agent - Complete Flow Diagram

## Overview Flow

```mermaid
flowchart TD
    Start([User Action/Trigger]) --> Check{Context Exists?}
    
    Check -->|No| CreateInitial[create_initial_context]
    Check -->|Yes| UpdateContext[update_context]
    
    CreateInitial --> GetRuntime1[get_runtime_context]
    GetRuntime1 --> ParseJSON1[Parse JSONB<br/>Extract content items]
    ParseJSON1 --> BuildPrompt1[Build Initial Prompt]
    BuildPrompt1 --> LLM1[LLM Processing<br/>Generate Initial Context]
    LLM1 --> Save1[save_user_context<br/>INSERT new record]
    Save1 --> End1([Initial Context Created])
    
    UpdateContext --> GetRuntime2[get_runtime_context]
    UpdateContext --> GetZed[get_user_context<br/>Get existing zed]
    
    GetRuntime2 --> ParseJSON2[Parse JSONB<br/>Extract content items]
    ParseJSON2 --> FormatContent[Format Runtime Content]
    GetZed --> FormatZed[Format Existing Zed Context]
    
    FormatContent --> MergePrompt[Build Merge Prompt<br/>runtime_context + zed]
    FormatZed --> MergePrompt
    
    MergePrompt --> LLM2[LLM Processing<br/>Merge & Generate Updated Context]
    LLM2 --> Save2[save_user_context<br/>UPDATE zed column]
    Save2 --> End2([Context Updated])
    
    style Start fill:#e1f5ff
    style End1 fill:#c8e6c9
    style End2 fill:#c8e6c9
    style LLM1 fill:#fff9c4
    style LLM2 fill:#fff9c4
    style Save1 fill:#f3e5f5
    style Save2 fill:#f3e5f5
```

## Detailed Update Context Flow

```mermaid
flowchart TD
    Start([update_context called]) --> CheckOpenAI{OpenAI Available?}
    CheckOpenAI -->|No| Error1[Return None<br/>Log Warning]
    CheckOpenAI -->|Yes| GetRuntime[get_runtime_context user_id]
    
    GetRuntime --> Query1[SELECT runtime_context<br/>WHERE user_id = %s]
    Query1 --> CheckNull{Result Exists?}
    CheckNull -->|No| EmptyList[Return Empty List]
    CheckNull -->|Yes| ParseJSON[Parse JSONB Structure]
    
    ParseJSON --> CheckType{JSONB Type?}
    CheckType -->|List| ParseList[Iterate List<br/>Extract content key]
    CheckType -->|Dict| ParseDict[Check content key<br/>Extract values]
    CheckType -->|String| AddString[Add as content item]
    
    ParseList --> ExtractContent[Extract All Content Items]
    ParseDict --> ExtractContent
    AddString --> ExtractContent
    EmptyList --> ExtractContent
    
    ExtractContent --> GetZed[get_user_context user_id]
    GetZed --> Query2[SELECT zed<br/>WHERE user_id = %s]
    Query2 --> CheckZed{Context Exists?}
    CheckZed -->|No| DefaultZed[Use Default Message]
    CheckZed -->|Yes| UseZed[Use Existing Context]
    
    DefaultZed --> FormatPrompt[Format Content Items]
    UseZed --> FormatPrompt
    
    FormatPrompt --> BuildPrompt[Build Comprehensive Prompt<br/>- Runtime Context Content<br/>- Existing Zed Context<br/>- Merge Instructions]
    
    BuildPrompt --> CreateMessages[Create LLM Messages<br/>SystemMessage + HumanMessage]
    CreateMessages --> InvokeLLM[llm.invoke messages]
    InvokeLLM --> GetResponse[Get Updated Context Text]
    
    GetResponse --> SaveContext[save_user_context]
    SaveContext --> CheckExists{Record Exists?}
    CheckExists -->|Yes| UpdateSQL[UPDATE users_context<br/>SET zed = %s<br/>WHERE user_id = %s]
    CheckExists -->|No| InsertSQL[INSERT INTO users_context<br/>user_id, zed, timestamps]
    
    UpdateSQL --> Success[Return Updated Context]
    InsertSQL --> Success
    Success --> End([Context Saved Successfully])
    
    Error1 --> End
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style InvokeLLM fill:#fff9c4
    style UpdateSQL fill:#f3e5f5
    style InsertSQL fill:#f3e5f5
    style Error1 fill:#ffcdd2
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph UserActions[User Activities]
        A1[Button Clicks]
        A2[Post Likes]
        A3[Resume Upload]
        A4[CV Upload]
        A5[Content Views]
    end
    
    subgraph Database[PostgreSQL Database]
        DB1[(users_context table)]
        DB2[runtime_context<br/>JSONB Column]
        DB3[zed<br/>TEXT Column]
    end
    
    subgraph ZedAgent[Zed Agent Process]
        Z1[get_runtime_context]
        Z2[Parse JSONB]
        Z3[Extract Content]
        Z4[get_user_context]
        Z5[Build Prompt]
        Z6[LLM Processing]
        Z7[save_user_context]
    end
    
    subgraph Output[Generated Context]
        O1[User Profile Summary]
        O2[Content Interests]
        O3[Professional Interests]
        O4[Technical Skills]
        O5[Learning Interests]
        O6[Job Preferences]
        O7[Behavioral Patterns]
        O8[Recent Activity]
        O9[Contextual Insights]
    end
    
    A1 --> DB2
    A2 --> DB2
    A3 --> DB2
    A4 --> DB2
    A5 --> DB2
    
    DB2 --> Z1
    Z1 --> Z2
    Z2 --> Z3
    DB3 --> Z4
    Z3 --> Z5
    Z4 --> Z5
    Z5 --> Z6
    Z6 --> Z7
    Z7 --> DB3
    
    Z6 --> O1
    Z6 --> O2
    Z6 --> O3
    Z6 --> O4
    Z6 --> O5
    Z6 --> O6
    Z6 --> O7
    Z6 --> O8
    Z6 --> O9
    
    style DB1 fill:#e3f2fd
    style Z6 fill:#fff9c4
    style O1 fill:#c8e6c9
    style O2 fill:#c8e6c9
    style O3 fill:#c8e6c9
    style O4 fill:#c8e6c9
    style O5 fill:#c8e6c9
    style O6 fill:#c8e6c9
    style O7 fill:#c8e6c9
    style O8 fill:#c8e6c9
    style O9 fill:#c8e6c9
```

## Method Call Sequence

```mermaid
sequenceDiagram
    participant User
    participant API
    participant ZedAgent
    participant Database
    participant OpenAI
    
    User->>API: Trigger Context Update
    API->>ZedAgent: update_context(user_id)
    
    ZedAgent->>ZedAgent: Check OpenAI Availability
    alt OpenAI Available
        ZedAgent->>Database: get_runtime_context(user_id)
        Database-->>ZedAgent: runtime_context JSONB
        ZedAgent->>ZedAgent: Parse JSONB & Extract Content
        
        ZedAgent->>Database: get_user_context(user_id)
        Database-->>ZedAgent: Existing zed context (or None)
        
        ZedAgent->>ZedAgent: Build Merge Prompt
        Note over ZedAgent: Format runtime_context content<br/>+ existing zed context<br/>+ merge instructions
        
        ZedAgent->>OpenAI: LLM Invocation
        Note over OpenAI: System Prompt:<br/>ZED_SYSTEM_PROMPT<br/><br/>User Prompt:<br/>Runtime Context + Zed Context
        OpenAI-->>ZedAgent: Updated Context Text
        
        ZedAgent->>Database: save_user_context(user_id, context)
        Database->>Database: Check if record exists
        alt Record Exists
            Database->>Database: UPDATE users_context<br/>SET zed = context<br/>WHERE user_id = user_id
        else New Record
            Database->>Database: INSERT INTO users_context<br/>(user_id, zed, timestamps)
        end
        Database-->>ZedAgent: Success
        ZedAgent-->>API: Updated Context Text
        API-->>User: Context Updated
    else OpenAI Not Available
        ZedAgent-->>API: None (Error)
        API-->>User: Update Failed
    end
```

## JSONB Parsing Logic Flow

```mermaid
flowchart TD
    Start([get_runtime_context]) --> Query[SELECT runtime_context<br/>WHERE user_id = %s]
    Query --> CheckResult{Result Exists?}
    CheckResult -->|No| ReturnEmpty[Return Empty List]
    CheckResult -->|Yes| GetJSONB[Get runtime_context JSONB]
    
    GetJSONB --> CheckType{JSONB Type?}
    
    CheckType -->|List| ProcessList[Process as List]
    ProcessList --> IterateList[Iterate Each Item]
    IterateList --> ItemType{Item Type?}
    ItemType -->|Dict with content| ExtractContentKey[Extract item['content']]
    ItemType -->|String| AddString[Add String as Content]
    ExtractContentKey --> AddToList
    AddString --> AddToList[Add to Content Items List]
    
    CheckType -->|Dict| ProcessDict[Process as Dict]
    ProcessDict --> CheckContentKey{Has 'content' key?}
    CheckContentKey -->|Yes| GetContentValue[Get content value]
    GetContentValue --> ContentType{Content Type?}
    ContentType -->|List| ExtendList[Extend with List Items]
    ContentType -->|String| AddSingle[Add Single Value]
    ExtendList --> AddToList
    AddSingle --> AddToList
    
    CheckContentKey -->|No| IterateValues[Iterate All Values]
    IterateValues --> CheckValue{Value Type?}
    CheckValue -->|String > 10 chars| AddValue[Add as Content]
    CheckValue -->|List| ExtendList2[Extend with List]
    AddValue --> AddToList
    ExtendList2 --> AddToList
    
    AddToList --> LogResult[Log Extraction Count]
    LogResult --> ReturnList[Return Content Items List]
    ReturnEmpty --> ReturnList
    ReturnList --> End([End])
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style ExtractContentKey fill:#fff9c4
    style GetContentValue fill:#fff9c4
```

## Complete System Architecture

```mermaid
graph TB
    subgraph External[External Systems]
        User[User Actions]
        Resume[Resume/CV Parser]
    end
    
    subgraph DataLayer[Data Layer]
        DB[(PostgreSQL<br/>users_context)]
        RT[runtime_context<br/>JSONB]
        ZED[zed<br/>TEXT]
    end
    
    subgraph AgentLayer[Zed Agent Layer]
        Init[ZedAgent.__init__<br/>Initialize OpenAI]
        GetRT[get_runtime_context<br/>Extract Content]
        GetZED[get_user_context<br/>Retrieve Context]
        Update[update_context<br/>Primary Update]
        Create[create_initial_context<br/>Initial Creation]
        Save[save_user_context<br/>Save to DB]
    end
    
    subgraph AILayer[AI Processing Layer]
        Prompt[Build Prompt<br/>System + User]
        LLM[OpenAI GPT-4o-mini<br/>Temperature: 0.3]
        Analyze[Context Analysis<br/>7 Categories]
        Generate[Generate Context<br/>9 Sections]
    end
    
    User -->|Activities| RT
    Resume -->|Parsed Data| RT
    RT -->|JSONB Data| GetRT
    GetRT -->|Content Items| Update
    ZED -->|Existing Context| GetZED
    GetZED -->|Context Text| Update
    Update -->|Formatted Data| Prompt
    Prompt -->|Messages| LLM
    LLM -->|Analysis| Analyze
    Analyze -->|Insights| Generate
    Generate -->|Updated Context| Save
    Save -->|INSERT/UPDATE| ZED
    Create -->|Initial Context| Save
    
    Init -.->|Initializes| GetRT
    Init -.->|Initializes| GetZED
    Init -.->|Initializes| Update
    Init -.->|Initializes| Create
    
    style User fill:#e1f5ff
    style LLM fill:#fff9c4
    style ZED fill:#c8e6c9
    style Update fill:#f3e5f5
    style Save fill:#f3e5f5
```

## Error Handling Flow

```mermaid
flowchart TD
    Start([Method Call]) --> Try[Try Block]
    Try --> Operation[Database/LLM Operation]
    Operation --> CheckSuccess{Success?}
    
    CheckSuccess -->|Yes| ReturnSuccess[Return Result]
    CheckSuccess -->|No| Catch[Catch Exception]
    
    Catch --> LogError[Log Error with Context<br/>- user_id<br/>- operation type<br/>- error message]
    LogError --> ReturnSafe[Return Safe Default<br/>None or Empty List]
    
    ReturnSuccess --> End1([Success Path])
    ReturnSafe --> End2([Error Path])
    
    style Start fill:#e1f5ff
    style End1 fill:#c8e6c9
    style End2 fill:#ffcdd2
    style LogError fill:#fff9c4
```
