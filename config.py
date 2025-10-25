"""
Production Configuration Management
Centralized config loading with validation
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load .env file from project root
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class Config:
    """Application configuration"""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

    # Voice Configuration
    ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

    # Server Configuration
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8001))

    # Database
    DATABASE_PATH = "aura.db"

    # Feature Flags
    VOICE_ENABLED = bool(ELEVENLABS_API_KEY)
    OPENAI_WHISPER_ENABLED = bool(OPENAI_API_KEY)

    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        issues = []

        if not cls.ELEVENLABS_API_KEY:
            issues.append("⚠️  ELEVENLABS_API_KEY not set - voice output disabled")

        if not cls.ANTHROPIC_API_KEY:
            issues.append("❌ ANTHROPIC_API_KEY not set - AI chat will fail")

        if issues:
            logger.warning("Configuration issues:")
            for issue in issues:
                logger.warning(f"  {issue}")

        return len([i for i in issues if i.startswith("❌")]) == 0

    @classmethod
    def print_status(cls):
        """Print configuration status"""
        print("\n" + "="*60)
        print("🚀 AURA CONFIGURATION")
        print("="*60)
        print(f"✅ OpenAI API:      {'Configured' if cls.OPENAI_API_KEY else '❌ NOT SET'}")
        print(f"✅ Anthropic API:   {'Configured' if cls.ANTHROPIC_API_KEY else '❌ NOT SET'}")
        print(f"✅ ElevenLabs API:  {'Configured' if cls.ELEVENLABS_API_KEY else '❌ NOT SET'}")
        print(f"✅ Helius API:      {'Configured' if cls.HELIUS_API_KEY else '❌ NOT SET'}")
        print(f"\n🎤 Voice Features:  {'Enabled' if cls.VOICE_ENABLED else 'Disabled'}")
        print(f"🎙️  Whisper STT:     {'Enabled' if cls.OPENAI_WHISPER_ENABLED else 'Disabled (using browser)'}")
        print(f"\n🌐 Server:          http://localhost:{cls.PORT}")
        print("="*60 + "\n")

# Validate on import
Config.validate()
