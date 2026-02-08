from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None


class VisemeMark(BaseModel):
    """A single viseme mark for lip-sync animation."""
    time: float  # Time in seconds from audio start
    viseme: str  # Viseme ID (p, t, k, f, S, T, etc.)


class WordMark(BaseModel):
    """A single word mark with timing."""
    time: float  # Time in seconds from audio start
    value: str   # The word


class SpeechAlignment(BaseModel):
    """Speech alignment data for lip-sync animation using Amazon Polly."""
    visemes: List[VisemeMark]  # Viseme timing for mouth shapes
    words: List[WordMark]      # Word timing for text highlighting


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    text: str
    audio_base64: Optional[str] = None
    alignment: Optional[SpeechAlignment] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
