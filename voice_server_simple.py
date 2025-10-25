"""
SIMPLE VOICE SERVER - No dependencies on OpenAI Whisper
Uses browser speech recognition + ElevenLabs TTS only
"""
from fastapi import FastAPI, Request
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

@app.get("/")
async def root():
    return {"status": "Voice server running", "elevenlabs_configured": bool(ELEVENLABS_API_KEY)}

@app.get("/voice-test")
async def serve_test_page():
    """Serve voice test page"""
    return FileResponse("voice_test.html")

@app.post("/api/voice/chat")
async def chat(request: Request):
    """Simple chat endpoint - just echoes back"""
    data = await request.json()
    text = data.get("text", "")

    # Simple response
    response = f"You said: {text}"

    return {"response": response}

@app.post("/api/voice/tts")
async def text_to_speech(request: Request):
    """Convert text to speech using ElevenLabs"""
    try:
        data = await request.json()
        text = data.get("text", "")

        if not ELEVENLABS_API_KEY:
            return JSONResponse({"error": "ElevenLabs API key not configured"}, status_code=500)

        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        # Call ElevenLabs API
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return Response(content=response.content, media_type="audio/mpeg")
            else:
                error_text = response.text
                return JSONResponse({"error": f"ElevenLabs error: {error_text}"}, status_code=500)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("🎤 Starting Simple Voice Server on http://localhost:8002")
    print(f"✅ ElevenLabs API Key: {'Configured' if ELEVENLABS_API_KEY else 'NOT CONFIGURED'}")
    uvicorn.run(app, host="0.0.0.0", port=8002)
