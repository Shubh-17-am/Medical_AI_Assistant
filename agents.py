"""
Multi-Agent System: Receptionist Agent and Clinical AI Agent
"""
import os
from typing import Dict, Optional, List
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from tools import PatientDataRetrievalTool, WebSearchTool
from rag_system import RAGSystem
from logger import system_logger


class ReceptionistAgent:
    """Receptionist Agent: Handles patient identification and basic queries"""
    
    def __init__(self, patient_tool: PatientDataRetrievalTool, api_key: str):
        self.tool = patient_tool
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.1-8b-instant",
            groq_api_key=api_key
        )
        self.current_patient = None
        self.conversation_history = []
        
        self.system_prompt = """You are a friendly and professional receptionist for a post-discharge care assistant system.

Your primary responsibilities:
1. Greet patients warmly and ask for their name
2. Retrieve their discharge report using the patient data retrieval tool
3. Provide information about their discharge (date, diagnosis, medications, follow-up)
4. Answer basic questions about their discharge report
5. Recognize medical concerns and route them to the Clinical AI Agent

When a patient provides their name:
- Use the patient_data_retrieval tool to fetch their discharge report
- Confirm the information you found
- Ask how they're feeling and if they have any questions

When a patient asks medical questions:
- If it's a basic question about their discharge report, answer it
- If it's a medical concern or clinical question, route to Clinical AI Agent by saying: "This sounds like a medical concern. Let me connect you with our Clinical AI Agent."

Always be empathetic, professional, and helpful.
Medical Disclaimer: This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.
"""
    
    def process_message(self, user_message: str) -> Dict:
        """Process user message and return agent response"""
        try:
            # Check if this is initial greeting or name request
            message_lower = user_message.lower().strip()
            
            # Check if user is providing a name (likely first interaction)
            if not self.current_patient:
                # Try to extract name or retrieve patient
                if any(word in message_lower for word in ["hi", "hello", "hey"]):
                    response_text = "Hello! I'm your post-discharge care assistant. What's your name?"
                    self.conversation_history.append(HumanMessage(content=user_message))
                    self.conversation_history.append(AIMessage(content=response_text))
                    system_logger.log_interaction("ReceptionistAgent", user_message, response_text)
                    return {
                        "agent": "receptionist",
                        "response": response_text,
                        "patient_data": None,
                        "route_to_clinical": False
                    }
                
                # User likely provided name
                result = self.tool.retrieve_patient(user_message.strip())
                
                if result["success"]:
                    self.current_patient = result["patient"]
                    patient = self.current_patient
                    
                    # Create contextual response
                    response_text = (
                        f"Hi {patient['patient_name']}! I found your discharge report from "
                        f"{patient['discharge_date']} for {patient['primary_diagnosis']}. "
                        f"How are you feeling today? Are you following your medication schedule?"
                    )
                    
                    self.conversation_history.append(HumanMessage(content=user_message))
                    self.conversation_history.append(AIMessage(content=response_text))
                    
                    system_logger.log_interaction(
                        "ReceptionistAgent",
                        user_message,
                        response_text,
                        {"patient_id": patient.get("patient_id")}
                    )
                    
                    return {
                        "agent": "receptionist",
                        "response": response_text,
                        "patient_data": patient,
                        "route_to_clinical": False
                    }
                else:
                    response_text = (
                        f"I couldn't find a discharge report for '{user_message}'. "
                        f"Please check the spelling of your name or contact support."
                    )
                    
                    self.conversation_history.append(HumanMessage(content=user_message))
                    self.conversation_history.append(AIMessage(content=response_text))
                    
                    system_logger.log_interaction("ReceptionistAgent", user_message, response_text)
                    
                    return {
                        "agent": "receptionist",
                        "response": response_text,
                        "patient_data": None,
                        "route_to_clinical": False
                    }
            
            # Patient already identified - handle follow-up questions
            # Check if this is a medical question that should be routed
            medical_keywords = [
                "symptom", "pain", "swelling", "worried", "concern", "should i",
                "is it normal", "what does", "why", "medication", "side effect",
                "research", "latest", "treatment", "therapy", "diagnosis"
            ]
            
            is_medical_query = any(keyword in message_lower for keyword in medical_keywords)
            
            if is_medical_query:
                # Route to Clinical Agent
                system_logger.log_decision(
                    "ReceptionistAgent",
                    "Route to Clinical Agent",
                    f"Detected medical query: {user_message}"
                )
                system_logger.log_agent_handoff(
                    "ReceptionistAgent",
                    "ClinicalAgent",
                    "Medical query detected"
                )
                
                response_text = (
                    "This sounds like a medical concern. Let me connect you with our Clinical AI Agent."
                )
                
                return {
                    "agent": "receptionist",
                    "response": response_text,
                    "patient_data": self.current_patient,
                    "route_to_clinical": True,
                    "original_query": user_message
                }
            
            # Basic question about discharge report - answer using LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                *self.conversation_history[-6:],  # Last 3 exchanges
                HumanMessage(content=user_message)
            ]
            
            # Add patient context
            patient_context = f"\n\nCurrent Patient Information:\n"
            if self.current_patient:
                patient_context += f"Name: {self.current_patient['patient_name']}\n"
                patient_context += f"Diagnosis: {self.current_patient['primary_diagnosis']}\n"
                patient_context += f"Discharge Date: {self.current_patient['discharge_date']}\n"
                patient_context += f"Medications: {', '.join(self.current_patient['medications'])}\n"
                patient_context += f"Follow-up: {self.current_patient['follow_up']}\n"
            
            full_context = self.system_prompt + patient_context
            messages[0] = SystemMessage(content=full_context)
            
            response = self.llm(messages)
            response_text = response.content
            
            self.conversation_history.append(HumanMessage(content=user_message))
            self.conversation_history.append(AIMessage(content=response_text))
            
            system_logger.log_interaction("ReceptionistAgent", user_message, response_text)
            
            return {
                "agent": "receptionist",
                "response": response_text,
                "patient_data": self.current_patient,
                "route_to_clinical": False
            }
        
        except Exception as e:
            system_logger.log_error("ReceptionistAgent", e, f"Processing message: {user_message}")
            return {
                "agent": "receptionist",
                "response": "I'm sorry, I encountered an error. Please try again or contact support.",
                "patient_data": self.current_patient,
                "route_to_clinical": False,
                "error": str(e)
            }
    
    def reset(self):
        """Reset agent state"""
        self.current_patient = None
        self.conversation_history = []


class ClinicalAgent:
    """Clinical AI Agent: Handles medical questions using RAG and web search"""
    
    def __init__(self, rag_system: RAGSystem, web_search_tool: WebSearchTool, api_key: str):
        self.rag = rag_system
        self.web_search = web_search_tool
        # Allow faster configurable model via env var while keeping quality default
        model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.llm = ChatGroq(
            temperature=0.2,
            model_name=model_name,
            groq_api_key=api_key
        )
        self.conversation_history = []
        
        self.system_prompt = """You are a Clinical AI Agent specializing in nephrology (kidney medicine).

STRICT GROUNDEDNESS POLICY (must follow exactly):
- You MUST answer ONLY using the provided context sections:
  1) Reference Material Information (RAG results), and
  2) Web Search Results (if present).
- Do NOT use prior knowledge or general world knowledge outside the provided context.
- If the context does not contain the needed information, explicitly say you do not have enough information in the reference materials and suggest consulting a healthcare professional. Only use web search when asked for latest/recent research or when RAG provides no relevant information.
- Always include citations: reference chunks as [source: <filename> chunk <id>] and list web URLs when used.
- Be concise, clinically safe, and clearly separate sections: Assessment, Guidance, Red flags, Next steps, and Sources.

Safety and Style:
- Never provide definitive diagnoses.
- Always include the medical disclaimer.
- Use patient context if provided.
- Prefer bullet points for clarity.

Medical Disclaimer: This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.
"""
    
    def process_message(self, user_message: str, patient_data: Optional[Dict] = None) -> Dict:
        """Process medical query using RAG and web search with explicit citations"""
        try:
            # Determine if we need web search (latest research, very specific queries)
            search_keywords = ["latest", "recent", "research", "study", "new", "2024", "2025"]
            message_lower = user_message.lower()
            needs_web_search = any(keyword in message_lower for keyword in search_keywords)
            
            # Build context
            context_parts = []
            sources = []
            
            # Try RAG first (slightly larger n for better coverage) and collect explicit citations
            retrieved_chunks = self.rag.retrieve_relevant_chunks(user_message, n_results=5)
            if retrieved_chunks:
                rag_context = self.rag.format_context_for_llm(retrieved_chunks)
                context_parts.append(f"Reference Material Information:\n{rag_context}")
                for chunk in retrieved_chunks:
                    src = chunk.get("source", "Nephrology Reference")
                    cid = chunk.get("chunk_id", "-")
                    sources.append(f"Reference: {src} [chunk {cid}]")
            
            # Add web search only if needed (latest research query) OR RAG provided no context
            web_result = None
            if needs_web_search or len(context_parts) == 0:
                web_result = self.web_search.search(user_message)
                if web_result.get("success"):
                    # Include formatted web search results as context
                    formatted_web = self.web_search.format_results(web_result)
                    context_parts.append(formatted_web)
                    for r in web_result.get("results", [])[:3]:
                        title = r.get("title", "Web Result")
                        url = r.get("url")
                        if url:
                            sources.append(f"Web: {title} ({url})")
                        else:
                            sources.append(f"Web: {title}")
            
            # Prepare messages for LLM
            full_context = "\n\n".join(context_parts) if context_parts else "No specific information available in reference materials."
            
            patient_info = ""
            if patient_data:
                patient_info = f"\n\nPatient Context:\nName: {patient_data.get('patient_name')}\n"
                patient_info += f"Diagnosis: {patient_data.get('primary_diagnosis')}\n"
                patient_info += f"Medications: {', '.join(patient_data.get('medications', []))}\n"
            
            prompt = f"""{self.system_prompt}

{patient_info}

User Question: {user_message}

Available Information:
{full_context}

Answer strictly and only from the Available Information above. If the information is insufficient, explicitly say so and recommend consulting a healthcare professional. Provide:
- Assessment (based only on context)
- Guidance (based only on context)
- Red flags and when to seek urgent care
- Next steps
- Short summary
Include exact citations as [source: <filename> chunk <id>] and web URLs when applicable.
"""
            
            messages = [
                SystemMessage(content=prompt),
                *self.conversation_history[-4:],  # Last 2 exchanges
                HumanMessage(content=user_message)
            ]
            
            response = self.llm(messages)
            response_text = response.content

            # If there was no RAG context and web also failed, enforce grounded failure response
            if len(context_parts) == 0:
                response_text = (
                    "I don't have enough information in the available reference materials to answer this. "
                    "Please consider refining the question or consulting a healthcare professional."
                )
            
            # Enhance response with source citations
            if sources:
                response_text += "\n\n---\n"
                response_text += "Sources:\n" + "\n".join([f"- {s}" for s in sources])
                if web_result and web_result.get("success"):
                    response_text += "\nNote: Web search information should be verified with healthcare professionals."
            
            # Add disclaimer
            response_text += "\n\n⚠️ Medical Disclaimer: This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice."
            
            self.conversation_history.append(HumanMessage(content=user_message))
            self.conversation_history.append(AIMessage(content=response_text))
            
            system_logger.log_interaction(
                "ClinicalAgent",
                user_message,
                response_text,
                {"sources": sources, "used_web_search": needs_web_search}
            )
            
            return {
                "agent": "clinical",
                "response": response_text,
                "sources": sources,
                "used_rag": bool(retrieved_chunks),
                "used_web_search": needs_web_search or (web_result and web_result.get("success"))
            }
        
        except Exception as e:
            system_logger.log_error("ClinicalAgent", e, f"Processing query: {user_message}")
            return {
                "agent": "clinical",
                "response": "I'm sorry, I encountered an error processing your medical query. Please try again or consult with a healthcare professional.",
                "sources": [],
                "error": str(e)
            }
    
    def reset(self):
        """Reset agent state"""
        self.conversation_history = []

