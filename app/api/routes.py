from fastapi import APIRouter, HTTPException
from app.api.schemas import ChatRequest, ChatResponse
from app.rag.pipeline import get_rag_response
from app.tts.polly import generate_speech_with_alignment
from app.utils.rate_limiter import check_rate_limit

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - returns complete response with optional audio.
    """
    # Check rate limit (simplified - would use IP in production)
    if not check_rate_limit(request.session_id or "anonymous"):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again tomorrow!"
        )
    
    try:
        # Get AI response
        text_response = await get_rag_response(request.message, request.session_id)
        
        # Generate speech with alignment (if AWS Polly is configured)
        audio_base64, alignment = await generate_speech_with_alignment(text_response)
        
        return ChatResponse(
            text=text_response,
            audio_base64=audio_base64,
            alignment=alignment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest_knowledge():
    """
    Trigger knowledge base re-ingestion.
    Call this after adding new markdown files.
    """
    from app.rag.ingest import ingest_knowledge_base
    
    try:
        count = await ingest_knowledge_base()
        return {"status": "success", "documents_ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

