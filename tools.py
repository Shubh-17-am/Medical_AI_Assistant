"""
Tools for agents: Patient data retrieval and web search
"""
import requests
from typing import Dict, List, Optional
from database import PatientDatabase
from logger import system_logger


class PatientDataRetrievalTool:
    """Tool for retrieving patient discharge reports from database"""
    
    def __init__(self, db: PatientDatabase):
        self.db = db
        self.tool_name = "patient_data_retrieval"
    
    def retrieve_patient(self, patient_name: str) -> Dict:
        """
        Retrieve patient discharge report by name.
        
        Args:
            patient_name: Full name of the patient
            
        Returns:
            Dictionary containing patient discharge report or error message
        """
        try:
            # Try exact match first
            patient = self.db.get_patient_by_name(patient_name)
            
            if patient:
                system_logger.log_database_access(
                    "SELECT",
                    f"patient_name = '{patient_name}'",
                    f"Found patient: {patient.get('patient_id')}",
                    success=True
                )
                return {
                    "success": True,
                    "patient": patient,
                    "message": f"Found discharge report for {patient_name}"
                }
            
            # Try partial match
            patients = self.db.search_patients_by_name(patient_name)
            
            if len(patients) == 0:
                system_logger.log_database_access(
                    "SELECT",
                    f"patient_name LIKE '%{patient_name}%'",
                    "No patients found",
                    success=False
                )
                return {
                    "success": False,
                    "patient": None,
                    "message": f"No patient found with name: {patient_name}"
                }
            elif len(patients) == 1:
                system_logger.log_database_access(
                    "SELECT",
                    f"patient_name LIKE '%{patient_name}%'",
                    f"Found patient: {patients[0].get('patient_id')}",
                    success=True
                )
                return {
                    "success": True,
                    "patient": patients[0],
                    "message": f"Found discharge report for {patients[0]['patient_name']}"
                }
            else:
                # Multiple matches
                system_logger.log_database_access(
                    "SELECT",
                    f"patient_name LIKE '%{patient_name}%'",
                    f"Found {len(patients)} matching patients",
                    success=False
                )
                names = [p["patient_name"] for p in patients]
                return {
                    "success": False,
                    "patient": None,
                    "message": f"Multiple patients found. Please specify full name. Found: {', '.join(names[:5])}"
                }
        
        except Exception as e:
            system_logger.log_error("PatientDataRetrievalTool", e, f"Retrieving patient: {patient_name}")
            return {
                "success": False,
                "patient": None,
                "message": f"Error retrieving patient data: {str(e)}"
            }


class WebSearchTool:
    """Tool for web search when information is not in reference materials"""
    
    def __init__(self):
        self.tool_name = "web_search"
        self.base_url = "https://api.duckduckgo.com/"
    
    def search(self, query: str, max_results: int = 5) -> Dict:
        """
        Perform web search using DuckDuckGo (fallback to simple requests)
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            # Using DuckDuckGo Instant Answer API
            # For better results, could use SerpAPI or Google Custom Search API
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            # Simple web scraping approach (for POC)
            # In production, use proper search API
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            try:
                response = requests.get(search_url, headers=headers, timeout=5)
                system_logger.log_web_search(query, len(response.text) if response.ok else 0, True)
                
                # For POC, return structured response
                # In production, parse actual results
                return {
                    "success": True,
                    "query": query,
                    "results": [
                        {
                            "title": f"Search result for: {query}",
                            "snippet": f"Information related to {query}. This is a simplified web search result. In production, actual search results would be parsed and returned here.",
                            "source": "Web Search",
                            "url": search_url
                        }
                    ],
                    "message": f"Found web search results for: {query}",
                    "note": "This is web search information. Always verify with healthcare professionals."
                }
            except requests.RequestException as e:
                system_logger.log_web_search(query, 0, False)
                return {
                    "success": False,
                    "query": query,
                    "results": [],
                    "message": f"Web search failed: {str(e)}",
                    "note": "Please consult with healthcare professionals for medical information."
                }
        
        except Exception as e:
            system_logger.log_error("WebSearchTool", e, f"Searching: {query}")
            return {
                "success": False,
                "query": query,
                "results": [],
                "message": f"Error performing web search: {str(e)}"
            }
    
    def format_results(self, search_result: Dict) -> str:
        """Format search results for display"""
        if not search_result.get("success"):
            return search_result.get("message", "Web search unavailable")
        
        formatted = f"Web Search Results for: {search_result['query']}\n\n"
        
        for i, result in enumerate(search_result.get("results", [])[:3], 1):
            formatted += f"{i}. {result.get('title', 'Result')}\n"
            formatted += f"   {result.get('snippet', '')}\n"
            formatted += f"   Source: {result.get('source', 'Web')}\n\n"
        
        formatted += f"\n{search_result.get('note', '')}\n"
        return formatted

