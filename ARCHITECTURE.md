# Architecture Documentation

## System Architecture

### Overview

The Medical AI Assistant implements a multi-agent architecture with the following components:

1. **Frontend (Streamlit)**: User interface for patient interactions
2. **Backend API (FastAPI)**: RESTful API for agent coordination
3. **Agent Coordinator**: Manages agent handoffs and routing
4. **Receptionist Agent**: Patient identification and basic queries
5. **Clinical Agent**: Medical guidance with RAG and web search
6. **RAG System**: Vector database for nephrology knowledge
7. **Database**: SQLite for patient discharge reports
8. **Logging System**: Comprehensive interaction tracking

## Data Flow

```
User Input (Streamlit)
    ↓
FastAPI Endpoint (/chat)
    ↓
Agent Coordinator
    ↓
    ├─→ Receptionist Agent
    │       ├─→ Patient Data Retrieval Tool
    │       └─→ SQLite Database
    │
    └─→ Clinical Agent (on handoff)
            ├─→ RAG System
            │   ├─→ ChromaDB (Vector Search)
            │   └─→ PDF Reference Materials
            │
            └─→ Web Search Tool (fallback)
```

## Agent Specifications

### Receptionist Agent

**Purpose**: Patient identification and basic query handling

**Capabilities**:
- Greets patients and requests name
- Retrieves discharge reports from database
- Answers basic questions about discharge information
- Routes medical queries to Clinical Agent

**Tools**:
- `patient_data_retrieval`: Retrieves patient discharge reports

**Decision Logic**:
- If medical keywords detected → Route to Clinical Agent
- If basic discharge question → Answer using LLM with patient context

### Clinical Agent

**Purpose**: Medical guidance using RAG and web search

**Capabilities**:
- Processes medical queries
- Retrieves relevant information from nephrology reference materials (RAG)
- Falls back to web search for latest research
- Provides citations and sources

**Tools**:
- RAG System (implicit through coordinator)
- `web_search`: Web search for queries outside reference materials

**Decision Logic**:
- If query contains "latest", "research", "study" → Use web search
- Otherwise → Try RAG first, then web search if needed

## RAG Implementation Details

### PDF Processing
1. Extract text from PDF using pdfplumber
2. Split into chunks (1000 chars, 200 char overlap)
3. Generate embeddings using Sentence-Transformers
4. Store in ChromaDB with metadata

### Retrieval Process
1. Generate query embedding
2. Search ChromaDB for top-K similar chunks (K=5)
3. Format chunks with source citations
4. Provide context to Clinical Agent LLM

### Embeddings
- Model: `all-MiniLM-L6-v2`
- Dimensions: 384
- Performance: Balanced speed and accuracy

## Database Schema

### Patients Table (SQLite)

```sql
CREATE TABLE patients (
    patient_id TEXT PRIMARY KEY,
    patient_name TEXT NOT NULL,
    discharge_date TEXT NOT NULL,
    primary_diagnosis TEXT NOT NULL,
    medications TEXT NOT NULL,
    dietary_restrictions TEXT,
    follow_up TEXT,
    warning_signs TEXT,
    discharge_instructions TEXT,
    age INTEGER,
    gender TEXT,
    contact_phone TEXT,
    blood_pressure TEXT,
    serum_creatinine REAL,
    egfr INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Logging Architecture

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General system events
- **ERROR**: Error conditions

### Logged Events
- User-agent interactions
- Agent handoffs
- Database access attempts
- RAG retrieval operations
- Web search queries
- Agent decisions
- Errors and exceptions

### Log Format
```
TIMESTAMP - LEVEL - [AGENT] - MESSAGE
```

## Error Handling

### Receptionist Agent
- Patient not found → Inform user, request name correction
- Database error → Log error, return user-friendly message
- LLM error → Fallback message with error logging

### Clinical Agent
- RAG retrieval fails → Fallback to web search
- Web search fails → Inform user, recommend consulting professional
- LLM error → Error message with logging

### Agent Coordinator
- Agent initialization fails → Return error, log failure
- Session errors → Reset session, log error

## Security Considerations

### Current Implementation (POC)
- No authentication (for POC simplicity)
- No encryption (local deployment)
- Dummy data only

### Production Recommendations
1. Add user authentication (JWT tokens)
2. Implement API rate limiting
3. Encrypt sensitive data
4. Add input validation and sanitization
5. Implement HIPAA compliance measures
6. Add audit logging
7. Secure API endpoints

## Performance Considerations

### Optimization Strategies
1. **RAG Caching**: Cache frequently accessed chunks
2. **Embedding Caching**: Cache query embeddings
3. **Database Indexing**: Index patient_name column
4. **Async Operations**: Use async for API calls
5. **Batch Processing**: Batch database operations

### Current Performance
- API Response Time: ~2-5 seconds per query
- RAG Retrieval: ~200-500ms
- Database Query: ~10-50ms
- Web Search: ~1-3 seconds

## Scalability

### Current Limitations
- Single-threaded agent processing
- Local file-based storage
- No distributed architecture

### Scaling Options
1. **Horizontal Scaling**: Multiple API instances behind load balancer
2. **Database**: Migrate to PostgreSQL for production
3. **Vector DB**: Use distributed ChromaDB or Qdrant
4. **Caching**: Redis for session and retrieval caching
5. **Queue System**: Celery for async task processing

## Testing Strategy

### Unit Tests
- Agent message processing
- Database operations
- RAG retrieval
- Tool functionality

### Integration Tests
- Agent handoff flow
- End-to-end chat flow
- API endpoint testing

### Manual Testing
- Patient identification flow
- Medical query routing
- RAG citation accuracy
- Web search fallback

## Future Enhancements

1. **Multiple Specialists**: Add more specialized agents (cardiologist, etc.)
2. **Multilingual Support**: Support for multiple languages
3. **Voice Interface**: Speech-to-text and text-to-speech
4. **Patient History**: Long-term conversation history
5. **Prescription Reminders**: Medication adherence tracking
6. **Telemedicine Integration**: Connect with healthcare providers
7. **Analytics Dashboard**: Patient interaction analytics

