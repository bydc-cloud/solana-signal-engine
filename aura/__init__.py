"""
AURA - Autonomous Crypto Intelligence Assistant
"""

__version__ = "0.1.0"
__author__ = "Claude Code"

from pathlib import Path

AURA_ROOT = Path(__file__).parent.parent
AURA_DB_PATH = AURA_ROOT / "aura.db"
HELIX_DB_PATH = AURA_ROOT / "final_nuclear.db"
