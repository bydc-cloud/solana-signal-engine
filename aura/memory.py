"""
AURA Memory System Integration
Uses MCP memory server for knowledge graph operations
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class AuraMemory:
    """
    Memory system using MCP memory server
    Stores entities (tokens, strategies, patterns) and observations
    """

    def __init__(self):
        # Will use MCP memory tools when available
        # For now, fallback to local database
        from .database import db
        self.db = db

    # ═══════════════════════════════════════════════════════════
    # ENTITY MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def create_entity(self, name: str, entity_type: str, observations: List[str]) -> None:
        """
        Create or update an entity in memory
        Uses MCP memory if available, falls back to local DB
        """
        try:
            # Store in local DB
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json
                from datetime import datetime

                # Check if exists
                cur.execute("""
                    SELECT id, observations FROM aura_memories
                    WHERE entity_name = ? AND entity_type = ?
                """, (name, entity_type))

                row = cur.fetchone()
                if row:
                    # Update existing
                    existing_obs = json.loads(row[1])
                    existing_obs.extend(observations)
                    cur.execute("""
                        UPDATE aura_memories
                        SET observations = ?, updated_at = ?, access_count = access_count + 1
                        WHERE id = ?
                    """, (json.dumps(existing_obs), datetime.now().isoformat(), row[0]))
                else:
                    # Create new
                    cur.execute("""
                        INSERT INTO aura_memories (entity_name, entity_type, observations)
                        VALUES (?, ?, ?)
                    """, (name, entity_type, json.dumps(observations)))

                conn.commit()
                logger.info(f"Memory: Stored entity {name} ({entity_type}) with {len(observations)} observations")

        except Exception as e:
            logger.error(f"Memory create entity error: {e}")

    def get_entity(self, name: str, entity_type: Optional[str] = None) -> Optional[Dict]:
        """Get entity from memory"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json
                from datetime import datetime

                if entity_type:
                    cur.execute("""
                        SELECT entity_name, entity_type, observations, created_at, updated_at, access_count
                        FROM aura_memories
                        WHERE entity_name = ? AND entity_type = ?
                    """, (name, entity_type))
                else:
                    cur.execute("""
                        SELECT entity_name, entity_type, observations, created_at, updated_at, access_count
                        FROM aura_memories
                        WHERE entity_name = ?
                    """, (name,))

                row = cur.fetchone()
                if not row:
                    return None

                # Update access count
                cur.execute("""
                    UPDATE aura_memories
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE entity_name = ?
                """, (datetime.now().isoformat(), name))
                conn.commit()

                return {
                    "entity_name": row[0],
                    "entity_type": row[1],
                    "observations": json.loads(row[2]),
                    "created_at": row[3],
                    "updated_at": row[4],
                    "access_count": row[5] + 1,
                }

        except Exception as e:
            logger.error(f"Memory get entity error: {e}")
            return None

    def search_entities(self, query: str, entity_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search entities by query"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json

                if entity_type:
                    cur.execute("""
                        SELECT entity_name, entity_type, observations, access_count
                        FROM aura_memories
                        WHERE entity_type = ? AND (entity_name LIKE ? OR observations LIKE ?)
                        ORDER BY access_count DESC
                        LIMIT ?
                    """, (entity_type, f"%{query}%", f"%{query}%", limit))
                else:
                    cur.execute("""
                        SELECT entity_name, entity_type, observations, access_count
                        FROM aura_memories
                        WHERE entity_name LIKE ? OR observations LIKE ?
                        ORDER BY access_count DESC
                        LIMIT ?
                    """, (f"%{query}%", f"%{query}%", limit))

                results = []
                for row in cur.fetchall():
                    results.append({
                        "entity_name": row[0],
                        "entity_type": row[1],
                        "observations": json.loads(row[2]),
                        "access_count": row[3],
                    })

                return results

        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # TOKEN MEMORY
    # ═══════════════════════════════════════════════════════════

    def remember_token(self, address: str, observations: List[str]) -> None:
        """Store token observations in memory"""
        self.create_entity(address, "token", observations)

    def recall_token(self, address: str) -> Optional[Dict]:
        """Recall token from memory"""
        return self.get_entity(address, "token")

    # ═══════════════════════════════════════════════════════════
    # STRATEGY MEMORY
    # ═══════════════════════════════════════════════════════════

    def remember_strategy_result(self, strategy_name: str, observations: List[str]) -> None:
        """Store strategy performance observations"""
        self.create_entity(strategy_name, "strategy", observations)

    def recall_strategy(self, strategy_name: str) -> Optional[Dict]:
        """Recall strategy learnings"""
        return self.get_entity(strategy_name, "strategy")

    # ═══════════════════════════════════════════════════════════
    # PATTERN MEMORY
    # ═══════════════════════════════════════════════════════════

    def remember_pattern(self, pattern_name: str, observations: List[str]) -> None:
        """Store discovered patterns"""
        self.create_entity(pattern_name, "pattern", observations)

    def find_patterns(self, query: str) -> List[Dict]:
        """Search for patterns"""
        return self.search_entities(query, "pattern")


# Singleton instance
memory = AuraMemory()
