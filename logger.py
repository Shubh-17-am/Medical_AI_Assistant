"""
Comprehensive logging system for the multi-agent chatbot
"""
import logging
import os
from datetime import datetime
from typing import Optional


class SystemLogger:
    """Centralized logging system for all agents and interactions"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("MedicalAIAssistant")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        # Ensure every record has an 'agent' attribute to avoid KeyError in formatters
        class DefaultAgentFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                if not hasattr(record, 'agent'):
                    record.agent = 'SYSTEM'
                return True
        default_agent_filter = DefaultAgentFilter()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(agent)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for detailed logs
        log_file = os.path.join(log_dir, f"system_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        file_handler.addFilter(default_agent_filter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        console_handler.addFilter(default_agent_filter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_interaction(self, agent: str, user_input: str, agent_response: str, 
                       metadata: Optional[dict] = None):
        """Log user-agent interaction"""
        extra = {'agent': agent}
        self.logger.info(f"User Input: {user_input}", extra=extra)
        self.logger.info(f"Agent Response: {agent_response}", extra=extra)
        if metadata:
            self.logger.debug(f"Metadata: {metadata}", extra=extra)
    
    def log_agent_handoff(self, from_agent: str, to_agent: str, reason: str):
        """Log agent handoff"""
        extra = {'agent': 'SYSTEM'}
        self.logger.info(f"Agent Handoff: {from_agent} -> {to_agent} | Reason: {reason}", 
                        extra=extra)
    
    def log_database_access(self, operation: str, query: str, result: str, 
                           success: bool = True):
        """Log database access attempts"""
        extra = {'agent': 'DATABASE'}
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"DB {operation} | Query: {query} | Result: {result} | Status: {status}",
                        extra=extra)
    
    def log_rag_retrieval(self, query: str, num_results: int, sources: list):
        """Log RAG retrieval operations"""
        extra = {'agent': 'RAG'}
        self.logger.info(f"RAG Query: {query} | Retrieved {num_results} results", extra=extra)
        self.logger.debug(f"Sources: {sources}", extra=extra)
    
    def log_web_search(self, query: str, results_count: int, used: bool = True):
        """Log web search operations"""
        extra = {'agent': 'WEB_SEARCH'}
        status = "USED" if used else "NOT_USED"
        self.logger.info(f"Web Search: {query} | Results: {results_count} | Status: {status}",
                        extra=extra)
    
    def log_error(self, agent: str, error: Exception, context: str = ""):
        """Log errors"""
        extra = {'agent': agent}
        error_msg = f"ERROR in {agent}: {str(error)}"
        if context:
            error_msg += f" | Context: {context}"
        self.logger.error(error_msg, extra=extra, exc_info=True)
    
    def log_decision(self, agent: str, decision: str, reasoning: str):
        """Log agent decision-making process"""
        extra = {'agent': agent}
        self.logger.debug(f"Decision: {decision} | Reasoning: {reasoning}", extra=extra)


# Global logger instance
system_logger = SystemLogger()

