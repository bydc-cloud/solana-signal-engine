"""
AURA MCP-Powered Telegram Handler
Integrates all MCP tools with Telegram bot for advanced capabilities
"""
import os
import logging
import json
import asyncio
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional Anthropic import
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("⚠️  anthropic module not installed - MCP features will be limited")

class MCPTelegramHandler:
    """
    MCP-powered Telegram bot handler
    Uses Claude with MCP tools for advanced intelligence
    """

    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if ANTHROPIC_AVAILABLE and self.anthropic_key:
            self.client = Anthropic(api_key=self.anthropic_key)
            logger.info("✅ MCP Telegram Handler initialized with Claude")
        else:
            if not ANTHROPIC_AVAILABLE:
                logger.warning("⚠️  Anthropic SDK not available")
            elif not self.anthropic_key:
                logger.warning("⚠️  No ANTHROPIC_API_KEY - MCP features disabled")

    async def handle_message(
        self,
        message: str,
        context: Dict,
        username: str = "User"
    ) -> str:
        """
        Handle telegram message with full MCP tool access

        Args:
            message: User's message
            context: System context (portfolio, signals, watchlist)
            username: User's name

        Returns:
            AI-generated response using MCP tools
        """
        if not self.client:
            return "🤖 AI features not available (missing ANTHROPIC_API_KEY)"

        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt(context, username)

            # Prepare conversation with MCP tool definitions
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message}
                ],
                tools=self._get_mcp_tools()
            )

            # Process tool calls if any
            if response.stop_reason == "tool_use":
                return await self._process_tool_calls(response, message, context)

            # Extract text response
            text_blocks = [block for block in response.content if block.type == "text"]
            if text_blocks:
                return text_blocks[0].text

            return "🤖 Processed your request"

        except Exception as e:
            logger.error(f"MCP handler error: {e}")
            return f"⚠️ AI processing error: {str(e)[:100]}"

    def _build_system_prompt(self, context: Dict, username: str) -> str:
        """Build system prompt with current context"""
        portfolio = context.get('portfolio', {})
        signals = context.get('signals', [])
        watchlist = context.get('watchlist', [])

        return f"""You are AURA, an autonomous trading intelligence AI with full access to MCP tools.

Current Context:
- User: {username}
- Portfolio: {portfolio.get('open_positions', 0)} positions, ${portfolio.get('total_pnl_usd', 0):.2f} P&L
- Recent Signals: {len(signals)} in last 24h
- Watchlist: {len(watchlist)} tokens tracked

You have access to these MCP tools:
- memory: Store/retrieve knowledge graph data
- puppeteer: Browse websites and scrape data
- context7: Look up library documentation
- sequential-thinking: Chain-of-thought reasoning
- coingecko: Cryptocurrency market data
- helius: Solana blockchain data
- birdeye: DEX price and liquidity data
- defillama: DeFi protocol TVL data
- firecrawl: Web scraping
- viz: Generate charts

Respond naturally and concisely. Use tools when needed to provide accurate, real-time data.
Format responses for Telegram Markdown (bold with *, italic with _, `code`)."""

    def _get_mcp_tools(self) -> List[Dict]:
        """Define available MCP tools for Claude"""
        return [
            {
                "name": "memory_search",
                "description": "Search the knowledge graph for entities and relationships",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "memory_store",
                "description": "Store information in the knowledge graph",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "entity": {"type": "string", "description": "Entity name"},
                        "entity_type": {"type": "string", "description": "Entity type"},
                        "observations": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["entity", "entity_type", "observations"]
                }
            },
            {
                "name": "web_browse",
                "description": "Browse a website and extract content",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to browse"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "token_search",
                "description": "Search for token data on CoinGecko",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Token name or symbol"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "solana_wallet_analyze",
                "description": "Analyze Solana wallet transactions",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string", "description": "Wallet address"}
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "token_price",
                "description": "Get real-time token price from Birdeye",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string", "description": "Token contract address"}
                    },
                    "required": ["address"]
                }
            }
        ]

    async def _process_tool_calls(
        self,
        response,
        original_message: str,
        context: Dict
    ) -> str:
        """Process tool calls and generate final response"""
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                logger.info(f"🔧 Tool call: {tool_name}({json.dumps(tool_input)[:100]})")

                # Execute tool (mock for now - would integrate with actual MCP servers)
                result = await self._execute_tool(tool_name, tool_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Continue conversation with tool results
        try:
            final_response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=self._build_system_prompt(context, "User"),
                messages=[
                    {"role": "user", "content": original_message},
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results}
                ]
            )

            text_blocks = [block for block in final_response.content if block.type == "text"]
            if text_blocks:
                return text_blocks[0].text
        except Exception as e:
            logger.error(f"Tool processing error: {e}")

        return "🤖 Processed with tools"

    async def _execute_tool(self, tool_name: str, tool_input: Dict) -> str:
        """Execute MCP tool (would integrate with actual MCP servers)"""
        # Mock responses for now - would integrate with real MCP servers
        if tool_name == "memory_search":
            return json.dumps({"results": [], "message": "No results found"})
        elif tool_name == "token_search":
            return json.dumps({"name": "Unknown Token", "price": 0, "market_cap": 0})
        elif tool_name == "web_browse":
            return "Website content would appear here"
        else:
            return f"Tool {tool_name} executed successfully"


# Global handler instance
mcp_handler = MCPTelegramHandler()
