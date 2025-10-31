"""
FastAPI backend for Multi-Agent Medical AI Assistant
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from dotenv import load_dotenv
from agent_coordinator import AgentCoordinator
from logger import system_logger
import uuid

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Medical AI Assistant API",
    description="Multi-Agent Post-Discharge Care Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global coordinator instance
coordinator: Optional[AgentCoordinator] = None
sessions: Dict[str, AgentCoordinator] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    agent: str
    patient_data: Optional[Dict] = None
    sources: Optional[List[str]] = None
    handoff: Optional[bool] = False
    session_id: str


class HealthResponse(BaseModel):
    status: str
    message: str


@app.on_event("startup")
async def startup_event():
    """Initialize coordinator on startup"""
    global coordinator
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            system_logger.logger.warning("GROQ_API_KEY not found in environment variables")
        
        coordinator = AgentCoordinator(api_key)
        system_logger.logger.info("FastAPI server started successfully")
    except Exception as e:
        system_logger.log_error("FastAPI", e, "Startup")
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Medical AI Assistant API is running"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    if coordinator is None:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    return HealthResponse(
        status="healthy",
        message="Medical AI Assistant API is running"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message through multi-agent system
    """
    try:
        if coordinator is None:
            raise HTTPException(
                status_code=503,
                detail="Agent coordinator not initialized"
            )
        
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Use session-specific coordinator if needed (for multi-user support)
        # For simplicity, using global coordinator for now
        # In production, create session-specific coordinators
        
        # Process message
        result = coordinator.process_message(request.message, session_id)
        
        system_logger.log_interaction(
            result.get("agent", "unknown"),
            request.message,
            result.get("response", ""),
            {"session_id": session_id}
        )
        
        return ChatResponse(
            response=result.get("response", "No response generated"),
            agent=result.get("agent", "unknown"),
            patient_data=result.get("patient_data"),
            sources=result.get("sources"),
            handoff=result.get("handoff", False),
            session_id=session_id
        )
    
    except Exception as e:
        system_logger.log_error("FastAPI", e, f"Chat endpoint: {request.message}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/reset")
async def reset_session(session_id: Optional[str] = None):
    """Reset agent session"""
    try:
        if coordinator is None:
            raise HTTPException(
                status_code=503,
                detail="Agent coordinator not initialized"
            )
        
        coordinator.reset_session()
        
        return {"status": "success", "message": "Session reset"}
    
    except Exception as e:
        system_logger.log_error("FastAPI", e, "Reset endpoint")
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting session: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

