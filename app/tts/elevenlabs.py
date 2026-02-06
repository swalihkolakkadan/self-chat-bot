"""
ElevenLabs Text-to-Speech integration with phoneme alignment.
"""
import base64
from typing import Optional, Tuple
from app.config import get_settings
from app.api.schemas import PhonemeAlignment

settings = get_settings()

# Initialize ElevenLabs client only if API key is configured
client = None
if settings.elevenlabs_api_key:
    try:
        from elevenlabs import ElevenLabs
        client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    except Exception as e:
        print(f"Failed to initialize ElevenLabs client: {e}")


def estimate_character_timings(text: str, audio_duration: float = None) -> PhonemeAlignment:
    """
    Estimate character timings based on text length.
    This is a fallback when actual phoneme data isn't available.
    
    Since ElevenLabs free tier doesn't provide phoneme timing,
    we estimate based on average speaking rate.
    """
    characters = list(text)
    
    # Estimate ~12 characters per second for natural speech
    chars_per_second = 12
    total_duration = audio_duration or (len(text) / chars_per_second)
    
    # Calculate timing for each character
    time_per_char = total_duration / max(len(characters), 1)
    timings = [i * time_per_char for i in range(len(characters))]
    
    return PhonemeAlignment(
        characters=characters,
        character_start_times_seconds=timings
    )


async def generate_speech_with_alignment(
    text: str
) -> Tuple[Optional[str], Optional[PhonemeAlignment]]:
    """
    Generate speech audio and phoneme alignment for lip-sync.
    
    Returns:
        Tuple of (base64_audio, alignment) or (None, None) on error
    """
    if not client:
        # Return empty if no API key configured
        return None, None
    
    try:
        # Generate audio using ElevenLabs v2 API
        audio_generator = client.text_to_speech.convert(
            voice_id=settings.elevenlabs_voice_id,
            text=text,
            model_id="eleven_monolingual_v1"
        )
        
        # Collect all audio bytes
        audio_bytes = b"".join(audio_generator)
        
        # Convert to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Estimate character timings (free tier doesn't provide actual phonemes)
        # Estimate audio duration: ~24kB per second at default quality
        estimated_duration = len(audio_bytes) / 24000
        alignment = estimate_character_timings(text, estimated_duration)
        
        return audio_base64, alignment
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None, None
