"""
Streamlit frontend for Multi-Agent Medical AI Assistant
"""
import streamlit as st
import requests
import os
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Medical disclaimer (always visible)
MEDICAL_DISCLAIMER = """
⚠️ **Medical Disclaimer**: This is an AI assistant for educational purposes only. 
Always consult healthcare professionals for medical advice.
"""

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = "receptionist"
    if "patient_data" not in st.session_state:
        st.session_state.patient_data = None


def send_message(message: str) -> Optional[dict]:
    """Send message to API and get response"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None


def reset_session():
    """Reset chat session"""
    try:
        if st.session_state.session_id:
            requests.post(f"{API_BASE_URL}/reset", json={"session_id": st.session_state.session_id})
        st.session_state.messages = []
        st.session_state.session_id = None
        st.session_state.current_agent = "receptionist"
        st.session_state.patient_data = None
        st.rerun()
    except Exception as e:
        st.error(f"Error resetting session: {str(e)}")


def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🏥 Medical AI Assistant")
        st.markdown("---")
        
        st.markdown("### System Information")
        st.info(
            "This system uses a multi-agent architecture:\n\n"
            "• **Receptionist Agent**: Handles patient identification\n"
            "• **Clinical Agent**: Provides medical guidance using RAG\n\n"
            "Powered by LangChain-Groq, ChromaDB, and RAG."
        )
        
        st.markdown("---")
        
        if st.button("🔄 Reset Conversation", use_container_width=True):
            reset_session()
        
        st.markdown("---")
        st.markdown(MEDICAL_DISCLAIMER)
        
        # Show patient data if available
        if st.session_state.patient_data:
            st.markdown("### Patient Information")
            patient = st.session_state.patient_data
            st.write(f"**Name:** {patient.get('patient_name', 'N/A')}")
            st.write(f"**Diagnosis:** {patient.get('primary_diagnosis', 'N/A')}")
            st.write(f"**Discharge Date:** {patient.get('discharge_date', 'N/A')}")
    
    # Main content area
    st.title("🏥 Post-Discharge Care Assistant")
    st.markdown("Multi-Agent AI System with RAG")
    st.markdown("---")
    
    # Display medical disclaimer at top
    st.warning(MEDICAL_DISCLAIMER)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show agent info if available
                if "agent" in message:
                    agent_badge = "🔷 Receptionist" if message["agent"] == "receptionist" else "🔶 Clinical"
                    st.caption(f"Agent: {agent_badge}")
                
                # Show sources if available
                if "sources" in message and message["sources"]:
                    sources_text = " | ".join(message["sources"])
                    st.caption(f"Sources: {sources_text}")
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from API
            with st.chat_message("assistant"):
                with st.spinner("Processing your message..."):
                    response_data = send_message(prompt)
                
                if response_data:
                    response_text = response_data.get("response", "No response received")
                    agent = response_data.get("agent", "unknown")
                    sources = response_data.get("sources", [])
                    
                    # Update session state
                    if response_data.get("session_id"):
                        st.session_state.session_id = response_data["session_id"]
                    
                    if response_data.get("patient_data"):
                        st.session_state.patient_data = response_data["patient_data"]
                    
                    st.session_state.current_agent = agent
                    
                    # Display response
                    st.markdown(response_text)
                    
                    # Show agent badge
                    agent_badge = "🔷 Receptionist Agent" if agent == "receptionist" else "🔶 Clinical Agent"
                    st.caption(agent_badge)
                    
                    # Show sources
                    if sources:
                        sources_text = " | ".join(sources)
                        st.caption(f"📚 Sources: {sources_text}")
                    
                    # Show handoff indicator
                    if response_data.get("handoff"):
                        st.info("🔄 Routed to Clinical Agent")
                    
                    # Add assistant message to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "agent": agent,
                        "sources": sources
                    })
                    
                    st.rerun()
                else:
                    st.error("Failed to get response from the API. Please check if the backend server is running.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        <p>Multi-Agent Medical AI Assistant | Powered by LangChain-Groq, ChromaDB, and RAG</p>
        <p>This system is for educational purposes only. Always consult healthcare professionals.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

