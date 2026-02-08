"""
Amazon Polly Text-to-Speech integration with viseme alignment.

Uses Amazon Polly's speech marks feature to get precise viseme timing
for lip-sync animation in the Rive character.
"""
import base64
import json
from typing import Optional, Tuple, List
from app.config import get_settings
from app.api.schemas import SpeechAlignment, VisemeMark, WordMark

settings = get_settings()

# Initialize Polly client only if AWS credentials are configured
polly_client = None
if settings.aws_access_key_id and settings.aws_secret_access_key:
    try:
        import boto3
        polly_client = boto3.client(
            'polly',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        print(f"Amazon Polly client initialized (region: {settings.aws_region})")
    except Exception as e:
        print(f"Failed to initialize Amazon Polly client: {e}")


def parse_speech_marks(speech_marks_data: str) -> Tuple[List[VisemeMark], List[WordMark]]:
    """
    Parse the line-delimited JSON speech marks from Polly.
    
    Returns:
        Tuple of (visemes, words)
    """
    visemes = []
    words = []
    
    for line in speech_marks_data.strip().split('\n'):
        if not line:
            continue
        try:
            mark = json.loads(line)
            # Convert time from milliseconds to seconds
            time_seconds = mark['time'] / 1000.0
            
            if mark['type'] == 'viseme':
                visemes.append(VisemeMark(
                    time=time_seconds,
                    viseme=mark['value']
                ))
            elif mark['type'] == 'word':
                words.append(WordMark(
                    time=time_seconds,
                    value=mark['value']
                ))
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing speech mark: {e}")
            continue
    
    return visemes, words


async def generate_speech_with_alignment(
    text: str
) -> Tuple[Optional[str], Optional[SpeechAlignment]]:
    """
    Generate speech audio with viseme alignment for lip-sync.
    
    Amazon Polly requires two separate API calls:
    1. One for the audio stream
    2. One for the speech marks (visemes + words)
    
    Returns:
        Tuple of (base64_audio, alignment) or (None, None) on error
    """
    if not polly_client:
        # Return empty if no AWS credentials configured
        return None, None
    
    try:
        # Request 1: Get the audio stream
        audio_response = polly_client.synthesize_speech(
            Engine=settings.polly_engine,
            OutputFormat='mp3',
            SampleRate='24000',
            Text=text,
            TextType='text',
            VoiceId=settings.polly_voice_id
        )
        
        # Read audio stream and convert to base64
        audio_stream = audio_response['AudioStream'].read()
        audio_base64 = base64.b64encode(audio_stream).decode('utf-8')
        
        # Request 2: Get speech marks (visemes and words)
        marks_response = polly_client.synthesize_speech(
            Engine=settings.polly_engine,
            OutputFormat='json',
            Text=text,
            TextType='text',
            VoiceId=settings.polly_voice_id,
            SpeechMarkTypes=['viseme', 'word']
        )
        
        # Parse the speech marks
        speech_marks_data = marks_response['AudioStream'].read().decode('utf-8')
        visemes, words = parse_speech_marks(speech_marks_data)
        
        alignment = SpeechAlignment(
            visemes=visemes,
            words=words
        )
        
        return audio_base64, alignment
        
    except Exception as e:
        print(f"Polly TTS Error: {e}")
        return None, None


# List of available neural voices for reference
NEURAL_VOICES = {
    'en-US': ['Danielle', 'Gregory', 'Ivy', 'Joanna', 'Kendra', 'Kimberly', 
              'Matthew', 'Ruth', 'Salli', 'Stephen'],
    'en-GB': ['Amy', 'Arthur', 'Brian', 'Emma'],
    'en-AU': ['Olivia'],
    'en-IN': ['Kajal'],
}
