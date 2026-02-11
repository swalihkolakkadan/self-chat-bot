import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try getting it from the app settings if env is not straightforward
    try:
        from app.config import get_settings
        settings = get_settings()
        api_key = settings.google_api_key
    except:
        print("Could not find API key")
        exit(1)

genai.configure(api_key=api_key)

print("Available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (generateContent)")
        if 'embedContent' in m.supported_generation_methods:
            print(f"- {m.name} (embedContent)")
except Exception as e:
    print(f"Error listing models: {e}")
