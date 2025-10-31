"""
Multi-Agent Coordinator: Manages handoffs between Receptionist and Clinical agents
"""
from typing import Dict, Optional
from agents import ReceptionistAgent, ClinicalAgent
from tools import PatientDataRetrievalTool, WebSearchTool
from rag_system import RAGSystem
from database import PatientDatabase
from logger import system_logger
import os


class AgentCoordinator:
    """Coordinates interactions between Receptionist and Clinical agents"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is required. Please set it in your .env file.")
        
        self.groq_api_key = groq_api_key
        
        # Initialize database and tools
        self.db = PatientDatabase()
        self.patient_tool = PatientDataRetrievalTool(self.db)
        self.web_search_tool = WebSearchTool()
        
        # Initialize RAG system
        pdf_path = "data/comprehensive-clinical-nephrology.pdf"
        if os.path.exists(pdf_path):
            self.rag_system = RAGSystem(pdf_path)
        else:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Initialize agents
        self.receptionist = ReceptionistAgent(self.patient_tool, groq_api_key)
        self.clinical_agent = ClinicalAgent(self.rag_system, self.web_search_tool, groq_api_key)
        
        # Session state
        self.current_agent = "receptionist"
        self.session_id = None
    
    def process_message(self, user_message: str, session_id: Optional[str] = None) -> Dict:
        """Process user message through appropriate agent"""
        self.session_id = session_id or "default"
        
        try:
            # Route to appropriate agent
            if self.current_agent == "receptionist":
                result = self.receptionist.process_message(user_message)
                
                # Check if routing to clinical agent is needed
                if result.get("route_to_clinical", False):
                    self.current_agent = "clinical"
                    system_logger.log_agent_handoff(
                        "ReceptionistAgent",
                        "ClinicalAgent",
                        f"User query: {result.get('original_query', user_message)}"
                    )
                    
                    # Forward query to clinical agent
                    original_query = result.get("original_query", user_message)
                    clinical_result = self.clinical_agent.process_message(
                        original_query,
                        patient_data=result.get("patient_data")
                    )
                    
                    return {
                        "agent": "clinical",
                        "response": clinical_result["response"],
                        "patient_data": result.get("patient_data"),
                        "sources": clinical_result.get("sources", []),
                        "handoff": True
                    }
                
                return result
            
            elif self.current_agent == "clinical":
                # Get current patient data if available
                patient_data = self.receptionist.current_patient
                result = self.clinical_agent.process_message(user_message, patient_data)
                return result
            
            else:
                return {
                    "agent": "system",
                    "response": "Error: Unknown agent state",
                    "error": "Invalid agent state"
                }
        
        except Exception as e:
            system_logger.log_error("AgentCoordinator", e, f"Processing message: {user_message}")
            return {
                "agent": "system",
                "response": "I'm sorry, I encountered a system error. Please try again.",
                "error": str(e)
            }
    
    def reset_session(self):
        """Reset session state"""
        self.current_agent = "receptionist"
        self.receptionist.reset()
        self.clinical_agent.reset()
        system_logger.logger.info("Session reset")


if __name__ == "__main__":
    # Test coordinator
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Please set GROQ_API_KEY environment variable")
    else:
        coordinator = AgentCoordinator(api_key)
        print("Agent Coordinator initialized successfully!")

