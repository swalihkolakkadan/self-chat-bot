from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None


class PhonemeAlignment(BaseModel):
    """Phoneme alignment data for lip-sync."""
    characters: List[str]
    character_start_times_seconds: List[float]


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    text: str
    audio_base64: Optional[str] = None
    alignment: Optional[PhonemeAlignment] = None


class SSEMessage(BaseModel):
    """Server-Sent Event message."""
    type: str  # "text", "audio", "error", "done"
    text: Optional[str] = None
    audio_base64: Optional[str] = None
    alignment: Optional[PhonemeAlignment] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
