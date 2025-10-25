#!/usr/bin/env python3
"""
AURA Conversation Manager
Handles multi-conversation tabs with memory and learning
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, db_path="aura.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize conversation tables"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Conversations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # Messages table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tool_calls TEXT,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Conversation insights/learnings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                insight_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # User preferences learned from conversations
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                learned_from_conversation TEXT,
                confidence_score REAL DEFAULT 1.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.info("✅ Conversation database initialized")

    def create_conversation(self, title: str = None) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        if not title:
            title = f"Conversation {datetime.now().strftime('%b %d, %I:%M %p')}"

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO conversations (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, title, datetime.now(), datetime.now()))
        conn.commit()
        conn.close()

        logger.info(f"📝 Created conversation: {conversation_id} - {title}")
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str,
                   tool_calls: List[Dict] = None, metadata: Dict = None):
        """Add a message to conversation"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO conversation_messages
            (conversation_id, role, content, tool_calls, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conversation_id,
            role,
            content,
            json.dumps(tool_calls) if tool_calls else None,
            json.dumps(metadata) if metadata else None
        ))

        # Update conversation
        cur.execute("""
            UPDATE conversations
            SET updated_at = ?, message_count = message_count + 1
            WHERE id = ?
        """, (datetime.now(), conversation_id))

        conn.commit()
        conn.close()

    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation message history"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT role, content, timestamp, tool_calls, metadata
            FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """, (conversation_id, limit))

        messages = []
        for row in cur.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "tool_calls": json.loads(row[3]) if row[3] else [],
                "metadata": json.loads(row[4]) if row[4] else {}
            })

        conn.close()
        return messages

    def list_conversations(self, active_only: bool = True, limit: int = 20) -> List[Dict]:
        """List all conversations"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = """
            SELECT id, title, created_at, updated_at, message_count
            FROM conversations
        """
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY updated_at DESC LIMIT ?"

        cur.execute(query, (limit,))

        conversations = []
        for row in cur.fetchall():
            conversations.append({
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "message_count": row[4]
            })

        conn.close()
        return conversations

    def update_conversation_title(self, conversation_id: str, title: str):
        """Update conversation title"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            UPDATE conversations SET title = ?, updated_at = ?
            WHERE id = ?
        """, (title, datetime.now(), conversation_id))
        conn.commit()
        conn.close()

    def delete_conversation(self, conversation_id: str):
        """Mark conversation as inactive"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            UPDATE conversations SET is_active = 0
            WHERE id = ?
        """, (conversation_id,))
        conn.commit()
        conn.close()

    def add_insight(self, conversation_id: str, insight_type: str, insight_data: Dict):
        """Store learned insight from conversation"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO conversation_insights
            (conversation_id, insight_type, insight_data)
            VALUES (?, ?, ?)
        """, (conversation_id, insight_type, json.dumps(insight_data)))
        conn.commit()
        conn.close()
        logger.info(f"💡 Learned insight: {insight_type}")

    def set_preference(self, key: str, value: str, conversation_id: str = None, confidence: float = 1.0):
        """Store user preference learned from conversation"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO user_preferences
            (key, value, learned_from_conversation, confidence_score, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (key, value, conversation_id, confidence, datetime.now()))
        conn.commit()
        conn.close()
        logger.info(f"📌 Learned preference: {key} = {value}")

    def get_preferences(self) -> Dict[str, str]:
        """Get all user preferences"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM user_preferences WHERE confidence_score >= 0.5")
        prefs = {row[0]: row[1] for row in cur.fetchall()}
        conn.close()
        return prefs

    def get_context_summary(self, conversation_id: str) -> str:
        """Get context summary for continuing conversation"""
        messages = self.get_conversation_history(conversation_id, limit=10)

        if not messages:
            return ""

        # Build context from recent messages
        context_parts = []
        for msg in messages[-5:]:  # Last 5 messages
            role = "User" if msg["role"] == "user" else "AURA"
            context_parts.append(f"{role}: {msg['content'][:100]}")

        return "\n".join(context_parts)

# Global instance
conversation_manager = ConversationManager()
