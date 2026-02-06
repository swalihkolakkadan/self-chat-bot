import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.api.schemas import ChatRequest, ChatResponse
from app.rag.pipeline import get_rag_response, stream_rag_response
from app.tts.elevenlabs import generate_speech_with_alignment
from app.utils.rate_limiter import check_rate_limit

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint.
    Returns complete response with audio.
    """
    # Check rate limit (simplified - would use IP in production)
    if not check_rate_limit(request.session_id or "anonymous"):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again tomorrow!"
        )
    
    try:
        # Get AI response
        text_response = await get_rag_response(request.message)
        
        # Generate speech with alignment
        audio_base64, alignment = await generate_speech_with_alignment(text_response)
        
        return ChatResponse(
            text=text_response,
            audio_base64=audio_base64,
            alignment=alignment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming chat endpoint.
    Streams text chunks, then sends audio at the end.
    """
    # Check rate limit
    if not check_rate_limit(request.session_id or "anonymous"):
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'error': 'Rate limit exceeded'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    async def generate():
        full_text = ""
        
        try:
            # Stream text chunks from RAG
            async for chunk in stream_rag_response(request.message):
                full_text += chunk
                yield f"data: {json.dumps({'type': 'text', 'text': chunk})}\n\n"
            
            # Generate audio after text is complete
            audio_base64, alignment = await generate_speech_with_alignment(full_text)
            
            yield f"data: {json.dumps({'type': 'audio', 'audio_base64': audio_base64, 'alignment': {'characters': alignment.characters, 'character_start_times_seconds': alignment.character_start_times_seconds} if alignment else None})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


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
