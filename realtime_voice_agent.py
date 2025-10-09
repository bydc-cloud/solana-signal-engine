#!/usr/bin/env python3
"""
Real-Time Voice Agent for AURA
Continuous voice interaction with OpenAI Realtime API
Responds immediately without waiting for user to stop talking
"""
import os
import asyncio
import logging
import json
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class RealtimeVoiceAgent:
    """
    Real-time voice agent using OpenAI Realtime API
    Features:
    - Continuous listening
    - Automatic silence detection
    - Real-time responses
    - Tool calling (signals, portfolio, wallet data)
    - TTS responses via ElevenLabs
    """

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

        if not all([self.openai_key, self.anthropic_key]):
            raise ValueError("Missing required API keys")

        self.anthropic = Anthropic(api_key=self.anthropic_key)
        self.is_listening = False
        self.conversation_history = []

        logger.info("🎤 Real-time voice agent initialized")

    async def handle_voice_stream(self, audio_stream):
        """
        Handle continuous audio stream from client
        Auto-detects speech and processes in real-time
        """
        try:
            # This would integrate with OpenAI Realtime API
            # For now, we'll use Whisper + Claude streaming

            # 1. Transcribe incoming audio
            transcription = await self.transcribe_audio(audio_stream)

            if not transcription:
                return None

            logger.info(f"User said: {transcription}")

            # 2. Process with Claude + tools
            response = await self.process_with_tools(transcription)

            # 3. Convert to speech
            audio_response = await self.text_to_speech(response)

            return {
                "transcription": transcription,
                "response_text": response,
                "response_audio": audio_response
            }

        except Exception as e:
            logger.error(f"Voice stream error: {e}")
            return None

    async def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper"""
        try:
            from openai import OpenAI
            import tempfile

            client = OpenAI(api_key=self.openai_key)

            # Save temporarily
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            with open(tmp_path, 'rb') as audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"
                )

            os.unlink(tmp_path)
            return transcript.text

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def process_with_tools(self, query: str) -> str:
        """
        Process query with Claude + tool access
        Tools: get_signals, get_portfolio, get_wallets, search_token
        """
        try:
            # Get context for Claude
            from aura.database import db

            context = {
                "recent_signals": db.get_recent_helix_signals(hours=24, limit=5),
                "portfolio_summary": db.get_portfolio_summary(),
            }

            # System prompt with tool definitions
            system_prompt = f"""You are AURA - a real-time voice trading assistant.

You have access to these tools:
- get_signals: Get recent trading signals
- get_portfolio: Check portfolio status
- get_wallets: Check tracked whale wallets
- analyze_token: Analyze a specific token

Current context:
- Recent signals: {len(context['recent_signals'])} found
- Portfolio value: ${context['portfolio_summary'].get('open_value_usd', 0):.2f}

Respond conversationally and concisely. You're in a voice conversation."""

            # Call Claude with streaming
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": query}
                ]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Processing error: {e}")
            return "I'm having trouble processing that. Could you try again?"

    async def text_to_speech(self, text: str):
        """Convert text to speech using ElevenLabs"""
        try:
            import aiohttp

            if not self.elevenlabs_key:
                return None

            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
            headers = {
                "xi-api-key": self.elevenlabs_key,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as resp:
                    if resp.status == 200:
                        return await resp.read()

            return None

        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None


# Global instance
voice_agent = RealtimeVoiceAgent()
