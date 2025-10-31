# Medical AI Assistant - Multi-Agent Post-Discharge Care System

A comprehensive chatbot system with multi-agent architecture for managing post-discharge patient reports and providing medical guidance using RAG (Retrieval Augmented Generation).

## 🏥 System Overview

This system implements a **multi-agent architecture** with specialized AI agents:
- **Receptionist Agent**: Handles patient identification and basic queries
- **Clinical AI Agent**: Provides medical guidance using RAG and web search

### Key Features

✅ **25+ Dummy Patient Reports** - Comprehensive discharge data management  
✅ **RAG Implementation** - Semantic search over nephrology reference materials  
✅ **Multi-Agent System** - Specialized agents with clear workflows  
✅ **Vector Database** - ChromaDB for efficient knowledge retrieval  
✅ **Web Search Integration** - Fallback for queries outside reference materials  
✅ **Comprehensive Logging** - Full system interaction tracking  
✅ **Simple Web Interface** - Streamlit-based user interface  

## 📋 Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [System Workflow](#system-workflow)
- [Project Structure](#project-structure)
- [Architecture Justification](#architecture-justification)
- [Medical Disclaimers](#medical-disclaimers)

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │
┌────────▼────────┐
│   FastAPI API   │
└────────┬────────┘
         │
┌────────▼──────────────┐
│ Agent Coordinator     │
├───────────────────────┤
│ Receptionist Agent    │◄──┐
│ Clinical Agent        │   │
└────────┬──────────────┘   │
         │                  │
    ┌────┴────┐             │
    │         │             │
┌───▼───┐ ┌──▼─────┐       │
│SQLite │ │ ChromaDB│      │
│  DB   │ │Vector DB│      │
└───────┘ └─────────┘      │
         │                  │
    ┌────▼────┐             │
    │  PDF   │             │
    │  RAG   │             │
    └────────┘             │
                           │
                   Agent Handoff
```

### Agent Workflow

1. **Receptionist Agent**
   - Greets patient and asks for name
   - Retrieves discharge report from SQLite database
   - Answers basic questions about discharge report
   - Routes medical queries to Clinical Agent

2. **Clinical Agent**
   - Receives medical queries from Receptionist
   - Uses RAG to search nephrology reference materials
   - Falls back to web search for latest research
   - Provides citations and sources
   - Logs all interactions

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Simple, interactive web interface

### Backend
- **FastAPI** - High-performance API framework
- **Uvicorn** - ASGI server

### LLM & Agents
- **LangChain** - Agent framework
- **LangChain-Groq** - Groq LLM integration (Llama 3.1 70B)
- **Custom Multi-Agent System** - Specialized agent coordination

### Vector Database & Embeddings
- **ChromaDB** - Vector database for RAG
- **Sentence-Transformers** - Embeddings (all-MiniLM-L6-v2)

### Data Storage
- **SQLite** - Patient discharge reports database
- **JSON Files** - Patient data source

### PDF Processing
- **pdfplumber** - Text extraction from PDF

### Logging
- **Python Logging** - Comprehensive system logging

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com/))

### Step 1: Clone Repository

```bash
cd "Medical AI Assistant"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Step 4: Run Setup Script

```bash
python setup.py
```

This will:
- Generate 30 dummy patient reports
- Initialize SQLite database
- Check system configuration

## 🚀 Usage

### Start the Backend (FastAPI)

```bash
python api.py
```

The API will run on `http://localhost:8000`

### Start the Frontend (Streamlit)

In a new terminal:

```bash
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501`

### API Endpoints

- `GET /` - Health check
- `GET /health` - System health status
- `POST /chat` - Process chat message
- `POST /reset` - Reset agent session

## 🔄 System Workflow

### Initial Interaction

```
System: "Hello! I'm your post-discharge care assistant. What's your name?"
Patient: "John Smith"
Receptionist Agent: [Retrieves discharge report from database]
Receptionist Agent: "Hi John! I found your discharge report from January 15th 
                      for Chronic Kidney Disease. How are you feeling today?"
```

### Medical Query Routing

```
Patient: "I'm having swelling in my legs. Should I be worried?"
Receptionist Agent: "This sounds like a medical concern. Let me connect you 
                      with our Clinical AI Agent."
Clinical Agent: "Based on your CKD diagnosis and nephrology guidelines, 
                 leg swelling can indicate fluid retention... [RAG response 
                 with citations]"
```

### Web Search Fallback

```
Patient: "What's the latest research on SGLT2 inhibitors for kidney disease?"
Clinical Agent: "This requires recent information. Let me search for you... 
                 According to recent medical literature [Web search results]..."
```

## 📁 Project Structure

```
Medical AI Assistant/
├── data/
│   ├── comprehensive-clinical-nephrology.pdf  # Knowledge base
│   └── patient_reports.json                    # Generated patient data
├── logs/                                        # System logs
├── chroma_db/                                   # Vector database
├── patient_database.db                          # SQLite database
├── api.py                                       # FastAPI backend
├── app.py                                       # Streamlit frontend
├── agents.py                                    # Agent implementations
├── agent_coordinator.py                         # Multi-agent coordinator
├── database.py                                  # Database operations
├── tools.py                                     # Agent tools (retrieval, search)
├── rag_system.py                                # RAG implementation
├── logger.py                                    # Logging system
├── create_patient_data.py                       # Patient data generator
├── setup.py                                     # Setup script
├── requirements.txt                             # Dependencies
├── .env                                         # Environment variables
└── README.md                                    # This file
```

## 🎓 Architecture Justification

### LLM Selection: Groq (Llama 3.1 70B)

**Rationale:**
- **Fast Inference**: Groq's hardware acceleration provides low-latency responses
- **High Quality**: Llama 3.1 70B offers excellent reasoning capabilities
- **Cost-Effective**: Competitive pricing for API usage
- **Medical Context**: Large model size enables better understanding of medical terminology

### Vector Database: ChromaDB

**Rationale:**
- **Simplicity**: Easy to set up and use locally
- **Persistence**: Built-in persistence for production use
- **Performance**: Efficient similarity search
- **Integration**: Seamless integration with LangChain and Sentence-Transformers

### RAG Implementation

**Rationale:**
- **Chunking Strategy**: 1000-character chunks with 200-character overlap for context preservation
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2) - Balanced performance and accuracy
- **Retrieval**: Top-K retrieval (default: 5 chunks) for comprehensive context
- **Citations**: Source tracking for medical transparency

### Multi-Agent Framework

**Rationale:**
- **Specialization**: Each agent has clear, focused responsibilities
- **Modularity**: Easy to extend or modify individual agents
- **Workflow Clarity**: Explicit handoff mechanism for medical queries
- **LangChain Integration**: Leverages LangChain's agent framework

### Web Search Integration

**Rationale:**
- **Fallback Mechanism**: Handles queries outside reference materials
- **Latest Information**: Access to recent research and developments
- **Transparency**: Clear indication of web vs. reference material sources

### Patient Data Retrieval

**Rationale:**
- **Explicit Tool**: Dedicated tool with clear interface
- **Error Handling**: Handles not found, multiple matches, and database errors
- **Logging**: All database accesses are logged for audit trail

### Logging Implementation

**Rationale:**
- **Comprehensive**: Logs all interactions, handoffs, and decisions
- **Structured**: Consistent format with timestamps and agent identification
- **File-Based**: Persistent logging for audit and debugging
- **Metadata**: Includes context for each logged event

## ⚠️ Medical Disclaimers

**This is an AI assistant for educational purposes only.**

- This system uses dummy data and is NOT intended for real patient care
- All information provided by the AI should be verified by healthcare professionals
- Always consult qualified medical professionals for medical advice
- Do not use this system for diagnosis or treatment decisions
- The AI responses may contain inaccuracies and should not replace professional medical consultation

## 📝 Sample Patient Report Structure

```json
{
  "patient_id": "PT0001",
  "patient_name": "John Smith",
  "discharge_date": "2024-01-15",
  "primary_diagnosis": "Chronic Kidney Disease Stage 3",
  "medications": ["Lisinopril 10mg daily", "Furosemide 20mg twice daily"],
  "dietary_restrictions": "Low sodium (2g/day), fluid restriction (1.5L/day)",
  "follow_up": "Nephrology clinic in 2 weeks",
  "warning_signs": "Swelling, shortness of breath, decreased urine output",
  "discharge_instructions": "Monitor blood pressure daily, weigh yourself daily",
  "age": 65,
  "gender": "Male"
}
```

## 🔍 Features Checklist

- ✅ 25+ dummy patient reports created
- ✅ Nephrology reference materials processed
- ✅ Receptionist Agent implemented
- ✅ Clinical AI Agent with RAG implemented
- ✅ Patient data retrieval tool implemented
- ✅ Web search tool integration
- ✅ Comprehensive logging system
- ✅ Simple web interface working
- ✅ Agent handoff mechanism functional
- ✅ Medical disclaimers included
- ✅ All code commented and documented

## 🤝 Contributing

This is an educational project. For production use:
1. Add proper authentication and authorization
2. Implement HIPAA compliance measures
3. Add input validation and sanitization
4. Enhance error handling
5. Add comprehensive testing
6. Implement proper security measures

## 📄 License

This project is for educational purposes only.

## 🙏 Acknowledgments

- LangChain community for the agent framework
- Groq for fast LLM inference
- ChromaDB for vector database
- Sentence-Transformers for embeddings

---

**Remember**: This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.

