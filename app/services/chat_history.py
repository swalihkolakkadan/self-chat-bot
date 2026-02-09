from typing import List, Dict, Tuple
from collections import deque
import time

# Global in-memory storage for chat history
# Format: {session_id: deque([(role, message), ...])}
_chat_histories: Dict[str, deque] = {}

# Maximum number of exchange pairs to keep (user + assistant = 1 pair)
MAX_HISTORY_LENGTH = 10 

# Session timeout in seconds (e.g., 30 minutes)
SESSION_TIMEOUT = 1800
_session_timestamps: Dict[str, float] = {}

class ChatHistoryManager:
    """
    Manages chat history for different sessions in-memory.
    """
    
    @staticmethod
    def _get_history_deque(session_id: str) -> deque:
        """Get or create history deque for a session."""
        current_time = time.time()
        
        # Clean up old session if it exists but timed out
        if session_id in _session_timestamps:
            if current_time - _session_timestamps[session_id] > SESSION_TIMEOUT:
                if session_id in _chat_histories:
                    del _chat_histories[session_id]
        
        # Create new if doesn't exist
        if session_id not in _chat_histories:
            _chat_histories[session_id] = deque(maxlen=MAX_HISTORY_LENGTH * 2)
            
        _session_timestamps[session_id] = current_time
        return _chat_histories[session_id]

    @classmethod
    def add_user_message(cls, session_id: str, message: str):
        """Add a user message to history."""
        if not session_id:
            return
        history = cls._get_history_deque(session_id)
        history.append(("user", message))

    @classmethod
    def add_ai_message(cls, session_id: str, message: str):
        """Add an AI message to history."""
        if not session_id:
            return
        history = cls._get_history_deque(session_id)
        history.append(("assistant", message))

    @classmethod
    def get_history(cls, session_id: str) -> List[Tuple[str, str]]:
        """Get complete history for a session."""
        if not session_id or session_id not in _chat_histories:
            return []
        
        # Update timestamp on access
        _session_timestamps[session_id] = time.time()
        return list(_chat_histories[session_id])

    @classmethod
    def get_formatted_history(cls, session_id: str) -> str:
        """Get history formatted as a string for LLM context."""
        history = cls.get_history(session_id)
        if not history:
            return ""
            
        formatted = []
        for role, content in history:
            if role == "user":
                formatted.append(f"User: {content}")
            else:
                formatted.append(f"Swalih: {content}")
                
        return "\n".join(formatted)
