# URGENT: Voice Transcription Not Working - Agent Handoff

## Current Situation
We've been stuck for days/weeks trying to get voice transcription working. Despite multiple attempts at fixing, the user still sees "could not transcribe audio, please try again" error.

## What We've Built (But Isn't Working)
1. **Voice widget** at http://localhost:8001/dashboard/aura-complete.html
   - Green blinking dot in bottom-right corner
   - Click once → panel opens
   - Click again → should start voice input
   - **PROBLEM**: Gets "could not transcribe audio" error

2. **Backend endpoints**:
   - `/api/aura/voice` - Uses OpenAI Whisper (requires audio file upload)
   - `/api/aura/voice/elevenlabs` - Text-to-speech (WORKING - confirmed with curl test)
   - `/api/aura/chat` - Chat endpoint for text input

3. **Config system** ([config.py](config.py)):
   - Centralized configuration loading from .env
   - All API keys present: ELEVENLABS_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY

## Root Cause Analysis
The voice widget uses **browser-based speech recognition** (webkitSpeechRecognition), NOT the server's OpenAI Whisper endpoint. So the "could not transcribe audio" error is coming from somewhere else.

**Multiple server processes running** (see system reminders):
- Background Bash 463a7e - uvicorn on port 8001
- Background Bash 017e92 - live_whale_tracker
- Background Bash 5f73f6 - live_whale_tracker
- Background Bash b76cf1 - live_whale_tracker
- Background Bash edffed - uvicorn on port 8001
- Background Bash f960c0 - uvicorn on port 8001
- Background Bash 399d2b - uvicorn on port 8001
- Background Bash 31f39d - start_local.sh
- Background Bash 6edcd9 - start_aura.sh

**This is the real problem**: Multiple conflicting server instances, process chaos, unclear which server is actually responding.

## Files Involved
- `/Users/johncox/Projects/helix/helix_production/dashboard/aura-complete.html` (lines 1382-1531) - Voice widget JavaScript
- `/Users/johncox/Projects/helix/helix_production/aura_server.py` - Main server
- `/Users/johncox/Projects/helix/helix_production/config.py` - Config management
- `/Users/johncox/Projects/helix/helix_production/.env` - Environment variables

## What Needs To Happen

### Step 1: KILL EVERYTHING
```bash
# Kill ALL Python processes
pkill -9 python3

# Verify nothing is running
ps aux | grep -E "uvicorn|python3|live_whale" | grep -v grep
```

### Step 2: Start ONE Clean Server
```bash
cd /Users/johncox/Projects/helix/helix_production
python3 -m uvicorn aura_server:app --host 0.0.0.0 --port 8001 --reload
```

### Step 3: Test Voice Flow in Browser
1. Open http://localhost:8001/dashboard/aura-complete.html
2. Open browser console (F12 → Console tab)
3. Click green dot → Check for JavaScript errors
4. Click dot again → Check if voice recognition starts
5. Speak → Check console for transcription results

### Step 4: Debug the Actual Error
Look at browser console when clicking voice dot. The error is likely:
- Browser doesn't support webkitSpeechRecognition
- Microphone permissions denied
- JavaScript error preventing voice from starting
- Wrong endpoint being called

## API Key Status
✅ ElevenLabs: Working (tested with curl - returns MP3 audio)
✅ OpenAI: Present in .env
✅ Anthropic: Present in .env

## Expected Behavior
1. Click dot → Panel opens
2. Click dot again → Browser asks for microphone permission (first time only)
3. See "🎤 Listening..." status
4. Speak → Text appears in input box
5. AURA responds in chat panel
6. ElevenLabs voice plays response

## Testing Commands
```bash
# Test ElevenLabs TTS (should return audio data)
curl -X POST http://localhost:8001/api/aura/voice/elevenlabs \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello this is a test"}'

# Test chat endpoint
curl -X POST http://localhost:8001/api/aura/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"show top wallets"}'

# Check server health
curl http://localhost:8001/health
```

## Critical Question to Answer
Where is the "could not transcribe audio" error actually coming from?
- Browser console log?
- Network request failure?
- Server endpoint error?
- JavaScript exception?

## Success Criteria
- User clicks voice dot
- Microphone activates
- User speaks
- Text appears in chat
- AURA responds with voice

---

## Instructions for Next Agent
1. Kill ALL background processes first
2. Start ONE clean server
3. Open browser console and test voice flow
4. Find the ACTUAL source of the transcription error
5. Fix it properly with root cause solution, not workarounds
6. Verify end-to-end: voice input → AI response → voice output

**Don't add more code unless you've identified the real problem first.**
