#!/usr/bin/env python3
"""
AURA Master Voice Controller
Handles all voice command processing with Claude function calling
Provides natural language control over entire trading system
"""

import os
import logging
import sqlite3
import asyncio
import subprocess
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic
import json

logger = logging.getLogger(__name__)

# Tool definitions for Claude
TOOLS = [
    {
        "name": "get_whale_wallets",
        "description": "Get list of tracked whale wallets with performance stats. Returns wallet addresses, nicknames, win rates, P&L, and recent activity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "active", "profitable", "high_win_rate"],
                    "description": "Filter wallets by type: 'all' (all wallets), 'active' (recently traded), 'profitable' (positive P&L), 'high_win_rate' (>60% win rate)"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["win_rate", "trades", "pnl", "recent"],
                    "description": "Sort by: 'win_rate', 'trades' (total trades), 'pnl' (profit/loss), 'recent' (last trade)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of wallets to return (default 10, max 50)"
                }
            }
        }
    },
    {
        "name": "track_whale_wallet",
        "description": "Add a new whale wallet to tracking system. Wallet will be monitored 24/7 for trades.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Solana wallet address (base58 encoded, 32-44 characters)"
                },
                "nickname": {
                    "type": "string",
                    "description": "Friendly name for the wallet (optional)"
                },
                "min_tx_value": {
                    "type": "number",
                    "description": "Minimum transaction value in USD to alert on (default 10000)"
                }
            },
            "required": ["address"]
        }
    },
    {
        "name": "untrack_whale_wallet",
        "description": "Remove a whale wallet from tracking system",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Wallet address or nickname to stop tracking"
                }
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_recent_signals",
        "description": "Get recent token signals from momentum scanner. Shows tokens with high momentum scores and good fundamentals.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hours": {
                    "type": "integer",
                    "description": "Hours to look back (default 24)"
                },
                "min_score": {
                    "type": "number",
                    "description": "Minimum momentum score (0-100, default 60)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max signals to return (default 20)"
                }
            }
        }
    },
    {
        "name": "trigger_whale_tracking",
        "description": "Manually trigger whale tracking for all wallets. Fetches latest trades from Helius API and updates stats.",
        "input_schema": {
            "type": "object",
            "properties": {
                "batch_size": {
                    "type": "integer",
                    "description": "Number of wallets to track in parallel (default 10)"
                }
            }
        }
    },
    {
        "name": "get_wallet_details",
        "description": "Get detailed stats and recent trades for a specific whale wallet",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Wallet address or nickname"
                }
            },
            "required": ["address"]
        }
    },
    {
        "name": "search_wallets",
        "description": "Search for wallets by nickname or partial address",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term (nickname or address fragment)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_portfolio",
        "description": "Get user's current portfolio with open positions and P&L summary",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_system_status",
        "description": "Get system status including scanner health, database stats, and recent activity",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


class VoiceController:
    """Master AI Voice Controller for AURA Trading System"""

    def __init__(self, db_path: str = 'aura.db'):
        self.db_path = db_path
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=anthropic_key)

        self.system_prompt = """You're a sharp Solana trader sharing alpha. Never mention being AI.

RULES:
- 10-15 words max, super casual
- Skip "I am", "simply", "certainly" - talk like texting
- Never introduce yourself or explain what you do
- Sound hyped about wins, chill about everything else

COPY THIS STYLE:
"Show top wallets" → "Raydiance at 75% win rate. Clukz crushing 8 trades."
"Good signals?" → "Yeah, 3 hot ones. BONK up 45%."
"Track xyz wallet" → "Added. Watching it."
"What's this?" → "Tracks whales and finds Solana gems."

NO AI TALK. Just straight fire.
""" + datetime.now().strftime("%I:%M %p")

    async def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process voice command using Claude with tools
        Returns: {
            "response": str,  # Text response to user
            "tool_results": List[Dict],  # Results from tool calls
            "success": bool
        }
        """
        try:
            # Check for quick commands first (bypass AI for speed)
            quick_result = await self._check_quick_commands(text)
            if quick_result:
                return quick_result

            # Use Claude with tools for complex queries
            return await self._claude_with_tools(text)

        except Exception as e:
            logger.error(f"Voice command error: {e}")
            return {
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "tool_results": [],
                "success": False
            }

    async def _check_quick_commands(self, text: str) -> Optional[Dict]:
        """Check for simple commands that don't need AI"""
        text_lower = text.lower()

        # Quick wallet list
        if any(phrase in text_lower for phrase in ["show whales", "list whales", "show wallets"]):
            if "top" in text_lower or "best" in text_lower:
                result = await self._handle_tool("get_whale_wallets", {
                    "filter": "high_win_rate",
                    "sort_by": "win_rate",
                    "limit": 5
                })
                response = self._format_wallet_list(result, "Top 5 Whale Wallets by Win Rate")
                return {
                    "response": response,
                    "tool_results": [result],
                    "success": True
                }

        # Quick signals
        if "signal" in text_lower and ("today" in text_lower or "recent" in text_lower):
            result = await self._handle_tool("get_recent_signals", {"hours": 24})
            response = self._format_signals(result)
            return {
                "response": response,
                "tool_results": [result],
                "success": True
            }

        # System status
        if "status" in text_lower:
            result = await self._handle_tool("get_system_status", {})
            response = self._format_system_status(result)
            return {
                "response": response,
                "tool_results": [result],
                "success": True
            }

        return None

    async def _claude_with_tools(self, text: str) -> Dict[str, Any]:
        """Use Claude with function calling to process command"""
        try:
            # Initial Claude request with tools
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,  # SHORT responses for voice
                tools=TOOLS,
                system=self.system_prompt,
                messages=[{"role": "user", "content": text}]
            )

            tool_results = []

            # Process tool calls iteratively
            while message.stop_reason == "tool_use":
                # Extract tool calls
                tool_calls = [block for block in message.content if block.type == "tool_use"]

                if not tool_calls:
                    break

                # Execute each tool
                tool_result_content = []
                for tool_use in tool_calls:
                    tool_name = tool_use.name
                    tool_input = tool_use.input

                    logger.info(f"🔧 Executing tool: {tool_name} with input: {tool_input}")

                    # Execute tool
                    result = await self._handle_tool(tool_name, tool_input)
                    tool_results.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result
                    })

                    # Add tool result for next Claude call
                    tool_result_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(result)
                    })

                # Continue conversation with tool results
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=150,  # SHORT responses for voice
                    tools=TOOLS,
                    system=self.system_prompt,
                    messages=[
                        {"role": "user", "content": text},
                        {"role": "assistant", "content": message.content},
                        {"role": "user", "content": tool_result_content}
                    ]
                )

            # Extract final text response
            response_text = ""
            for block in message.content:
                if hasattr(block, "text"):
                    response_text += block.text

            return {
                "response": response_text or "Done!",
                "tool_results": tool_results,
                "success": True
            }

        except Exception as e:
            logger.error(f"Claude tool execution error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"I had trouble processing that: {str(e)}",
                "tool_results": [],
                "success": False
            }

    async def _handle_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute tool calls from Claude"""
        try:
            if tool_name == "get_whale_wallets":
                return await self._get_whale_wallets(
                    filter_type=tool_input.get("filter", "all"),
                    sort_by=tool_input.get("sort_by", "win_rate"),
                    limit=tool_input.get("limit", 10)
                )

            elif tool_name == "track_whale_wallet":
                return await self._track_whale_wallet(
                    address=tool_input["address"],
                    nickname=tool_input.get("nickname", "Unknown Whale"),
                    min_tx_value=tool_input.get("min_tx_value", 10000)
                )

            elif tool_name == "untrack_whale_wallet":
                return await self._untrack_whale_wallet(
                    address=tool_input["address"]
                )

            elif tool_name == "get_recent_signals":
                return await self._get_recent_signals(
                    hours=tool_input.get("hours", 24),
                    min_score=tool_input.get("min_score", 0),
                    limit=tool_input.get("limit", 20)
                )

            elif tool_name == "trigger_whale_tracking":
                return await self._trigger_whale_tracking(
                    batch_size=tool_input.get("batch_size", 10)
                )

            elif tool_name == "get_wallet_details":
                return await self._get_wallet_details(
                    address=tool_input["address"]
                )

            elif tool_name == "search_wallets":
                return await self._search_wallets(
                    query=tool_input["query"]
                )

            elif tool_name == "get_portfolio":
                return await self._get_portfolio()

            elif tool_name == "get_system_status":
                return await self._get_system_status()

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Tool handler error for {tool_name}: {e}")
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # TOOL IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════

    async def _get_whale_wallets(self, filter_type: str = "all", sort_by: str = "win_rate", limit: int = 10) -> Dict:
        """Get whale wallets from database"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cur = conn.cursor()

            # Build query based on filter
            where_clause = ""
            if filter_type == "active":
                where_clause = "WHERE s.total_trades > 0 AND s.last_trade_timestamp > datetime('now', '-7 days')"
            elif filter_type == "profitable":
                where_clause = "WHERE s.total_pnl_usd > 0"
            elif filter_type == "high_win_rate":
                where_clause = "WHERE s.win_rate > 60 AND s.total_trades >= 5"

            # Build sort clause
            sort_map = {
                "win_rate": "s.win_rate DESC",
                "trades": "s.total_trades DESC",
                "pnl": "s.total_pnl_usd DESC",
                "recent": "s.last_trade_timestamp DESC"
            }
            order_clause = f"ORDER BY {sort_map.get(sort_by, 's.win_rate DESC')}"

            query = f"""
                SELECT
                    w.wallet_address,
                    w.nickname,
                    w.min_tx_value_usd,
                    COALESCE(s.total_trades, 0) as total_trades,
                    COALESCE(s.win_rate, 0) as win_rate,
                    COALESCE(s.total_pnl_usd, 0) as total_pnl,
                    s.last_trade_timestamp
                FROM live_whale_wallets w
                LEFT JOIN whale_stats s ON w.wallet_address = s.wallet_address
                {where_clause}
                {order_clause}
                LIMIT ?
            """

            cur.execute(query, (limit,))

            wallets = []
            for row in cur.fetchall():
                wallets.append({
                    "address": row[0],
                    "nickname": row[1] or "Unknown Whale",
                    "min_tx": row[2] or 10000,
                    "total_trades": row[3],
                    "win_rate": round(row[4], 1),
                    "total_pnl": round(row[5], 2),
                    "last_trade": row[6],
                    "solscan": f"https://solscan.io/account/{row[0]}"
                })

            conn.close()
            return {
                "wallets": wallets,
                "count": len(wallets),
                "filter": filter_type,
                "sort": sort_by
            }

        except Exception as e:
            logger.error(f"Get wallets error: {e}")
            return {"error": str(e), "wallets": []}

    async def _track_whale_wallet(self, address: str, nickname: str, min_tx_value: float) -> Dict:
        """Add new wallet to tracking"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cur = conn.cursor()

            cur.execute("""
                INSERT OR REPLACE INTO live_whale_wallets
                (wallet_address, nickname, min_tx_value_usd, added_at)
                VALUES (?, ?, ?, ?)
            """, (address, nickname, min_tx_value, datetime.now().isoformat()))

            conn.commit()
            conn.close()

            return {
                "success": True,
                "message": f"Added {nickname} ({address[:8]}...) to tracking",
                "address": address,
                "nickname": nickname,
                "min_tx_value": min_tx_value
            }

        except Exception as e:
            logger.error(f"Track wallet error: {e}")
            return {"success": False, "error": str(e)}

    async def _untrack_whale_wallet(self, address: str) -> Dict:
        """Remove wallet from tracking"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cur = conn.cursor()

            # Try by address or nickname
            cur.execute("""
                DELETE FROM live_whale_wallets
                WHERE wallet_address = ? OR nickname = ?
            """, (address, address))

            deleted = cur.rowcount
            conn.commit()
            conn.close()

            if deleted > 0:
                return {
                    "success": True,
                    "message": f"Removed wallet from tracking",
                    "deleted_count": deleted
                }
            else:
                return {
                    "success": False,
                    "error": "Wallet not found"
                }

        except Exception as e:
            logger.error(f"Untrack wallet error: {e}")
            return {"success": False, "error": str(e)}

    async def _get_recent_signals(self, hours: int = 24, min_score: float = 0, limit: int = 20) -> Dict:
        """Get recent signals from helix_signals table"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cur = conn.cursor()

            cur.execute("""
                SELECT token_address, symbol, momentum_score, market_cap,
                       liquidity, volume_24h, price, timestamp, metadata
                FROM helix_signals
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
                  AND momentum_score >= ?
                ORDER BY momentum_score DESC
                LIMIT ?
            """, (hours, min_score, limit))

            signals = []
            for row in cur.fetchall():
                metadata = json.loads(row[8]) if row[8] else {}
                signals.append({
                    "address": row[0],
                    "symbol": row[1],
                    "momentum": row[2],
                    "mcap": row[3],
                    "liquidity": row[4],
                    "volume": row[5],
                    "price": row[6],
                    "timestamp": row[7],
                    "risk_score": metadata.get("risk_score", 0),
                    "narrative": metadata.get("narrative", ""),
                    "dexscreener": f"https://dexscreener.com/solana/{row[0]}"
                })

            conn.close()
            return {
                "signals": signals,
                "count": len(signals),
                "hours": hours,
                "min_score": min_score
            }

        except Exception as e:
            logger.error(f"Get signals error: {e}")
            return {"error": str(e), "signals": []}

    async def _trigger_whale_tracking(self, batch_size: int = 10) -> Dict:
        """Trigger live whale tracking"""
        try:
            logger.info(f"🚀 Triggering whale tracking (batch_size={batch_size})")

            # Run tracking script in background
            process = subprocess.Popen(
                [sys.executable, "live_whale_tracker.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            return {
                "success": True,
                "message": "Whale tracking started in background",
                "pid": process.pid,
                "batch_size": batch_size
            }

        except Exception as e:
            logger.error(f"Trigger tracking error: {e}")
            return {"success": False, "error": str(e)}

    async def _get_wallet_details(self, address: str) -> Dict:
        """Get detailed info for specific wallet"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cur = conn.cursor()

            # Try to find by address or nickname
            cur.execute("""
                SELECT w.wallet_address, w.nickname, w.min_tx_value_usd, w.added_at,
                       s.total_trades, s.winning_trades, s.win_rate, s.total_pnl_usd, s.last_trade_timestamp
                FROM live_whale_wallets w
                LEFT JOIN whale_stats s ON w.wallet_address = s.wallet_address
                WHERE w.wallet_address = ? OR w.nickname = ?
            """, (address, address))

            wallet_row = cur.fetchone()
            if not wallet_row:
                conn.close()
                return {"error": "Wallet not found"}

            wallet_address = wallet_row[0]

            # Get recent trades
            cur.execute("""
                SELECT token_address, type, value_usd, timestamp, signature
                FROM whale_transactions
                WHERE wallet_address = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (wallet_address,))

            trades = []
            for row in cur.fetchall():
                trades.append({
                    "token": row[0],
                    "type": row[1],
                    "value_usd": row[2],
                    "timestamp": row[3],
                    "tx": f"https://solscan.io/tx/{row[4]}"
                })

            conn.close()

            return {
                "wallet": {
                    "address": wallet_row[0],
                    "nickname": wallet_row[1],
                    "min_tx": wallet_row[2],
                    "added": wallet_row[3],
                    "solscan": f"https://solscan.io/account/{wallet_row[0]}"
                },
                "stats": {
                    "total_trades": wallet_row[4] or 0,
                    "winning_trades": wallet_row[5] or 0,
                    "win_rate": wallet_row[6] or 0,
                    "total_pnl": wallet_row[7] or 0,
                    "last_trade": wallet_row[8]
                },
                "recent_trades": trades
            }

        except Exception as e:
            logger.error(f"Get wallet details error: {e}")
            return {"error": str(e)}

    async def _search_wallets(self, query: str) -> Dict:
        """Search wallets by nickname or address"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cur = conn.cursor()

            cur.execute("""
                SELECT w.wallet_address, w.nickname, w.min_tx_value_usd,
                       COALESCE(s.total_trades, 0), COALESCE(s.win_rate, 0)
                FROM live_whale_wallets w
                LEFT JOIN whale_stats s ON w.wallet_address = s.wallet_address
                WHERE w.wallet_address LIKE ? OR w.nickname LIKE ?
                LIMIT 20
            """, (f"%{query}%", f"%{query}%"))

            results = []
            for row in cur.fetchall():
                results.append({
                    "address": row[0],
                    "nickname": row[1],
                    "min_tx": row[2],
                    "total_trades": row[3],
                    "win_rate": row[4]
                })

            conn.close()
            return {
                "results": results,
                "count": len(results),
                "query": query
            }

        except Exception as e:
            logger.error(f"Search wallets error: {e}")
            return {"error": str(e), "results": []}

    async def _get_portfolio(self) -> Dict:
        """Get portfolio summary"""
        try:
            from aura.database import db
            portfolio = db.get_portfolio_summary()
            positions = db.get_open_positions()

            return {
                "summary": portfolio,
                "positions": positions,
                "count": len(positions)
            }

        except Exception as e:
            logger.error(f"Get portfolio error: {e}")
            return {"error": str(e)}

    async def _get_system_status(self) -> Dict:
        """Get system status"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cur = conn.cursor()

            # Count wallets
            cur.execute("SELECT COUNT(*) FROM live_whale_wallets")
            wallet_count = cur.fetchone()[0]

            # Count signals (last 24h)
            cur.execute("""
                SELECT COUNT(*) FROM helix_signals
                WHERE datetime(timestamp) > datetime('now', '-24 hours')
            """)
            signal_count = cur.fetchone()[0]

            # Count recent trades
            cur.execute("""
                SELECT COUNT(*) FROM whale_transactions
                WHERE datetime(timestamp) > datetime('now', '-24 hours')
            """)
            trade_count = cur.fetchone()[0]

            conn.close()

            return {
                "status": "healthy",
                "wallets_tracked": wallet_count,
                "signals_24h": signal_count,
                "trades_24h": trade_count,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Get system status error: {e}")
            return {"error": str(e), "status": "error"}

    # ═══════════════════════════════════════════════════════════
    # RESPONSE FORMATTERS
    # ═══════════════════════════════════════════════════════════

    def _format_wallet_list(self, result: Dict, title: str) -> str:
        """Format wallet list for display"""
        if "error" in result:
            return f"Error: {result['error']}"

        wallets = result.get("wallets", [])
        if not wallets:
            return "No wallets found."

        response = f"{title}\n\n"
        for i, w in enumerate(wallets, 1):
            response += f"{i}. {w['nickname']} - {w['win_rate']}% WR, "
            response += f"{w['total_trades']} trades, ${w['total_pnl']:.2f} P&L\n"

        return response.strip()

    def _format_signals(self, result: Dict) -> str:
        """Format signals for display"""
        if "error" in result:
            return f"Error: {result['error']}"

        signals = result.get("signals", [])
        if not signals:
            return f"No signals found in last {result.get('hours', 24)} hours."

        response = f"Recent Signals ({len(signals)} found)\n\n"
        for i, s in enumerate(signals[:5], 1):
            response += f"{i}. {s['symbol']} - Momentum: {s['momentum']:.1f}, "
            response += f"Volume: ${s['volume']:,.0f}\n"

        if len(signals) > 5:
            response += f"\n... and {len(signals) - 5} more"

        return response.strip()

    def _format_system_status(self, result: Dict) -> str:
        """Format system status for display"""
        if "error" in result:
            return f"Error: {result['error']}"

        response = "System Status\n\n"
        response += f"Wallets Tracked: {result.get('wallets_tracked', 0)}\n"
        response += f"Signals (24h): {result.get('signals_24h', 0)}\n"
        response += f"Trades (24h): {result.get('trades_24h', 0)}\n"
        response += f"Status: {result.get('status', 'unknown').upper()}"

        return response


# Singleton instance
voice_controller = VoiceController()
