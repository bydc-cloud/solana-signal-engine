"""
AURA MCP-Powered Chat
Uses Anthropic Claude with full MCP tool access
"""
import os
import logging
from typing import Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class MCPChat:
    """
    Chat interface that uses Claude with MCP tools
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"
        self.conversation_history = []

        logger.info("🧠 MCP Chat initialized with Claude 3.5 Sonnet")

    async def process_query(self, query: str, context: Dict = None) -> Dict:
        """
        Process query using Claude with MCP tools
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(context)

            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })

            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=self.conversation_history
            )

            # Extract response
            assistant_message = response.content[0].text

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return {
                "type": "mcp_response",
                "message": assistant_message,
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"MCP Chat error: {e}")
            return {
                "type": "error",
                "message": f"I encountered an error: {str(e)}",
                "error": str(e)
            }

    def _build_system_prompt(self, context: Dict = None) -> str:
        """
        Build system prompt with AURA context
        """
        prompt = """You are AURA - an Autonomous Unified Research Assistant for cryptocurrency trading.

You have access to:
- Real-time token data from Solana
- Signal generation algorithms
- Wallet tracking capabilities
- Portfolio management
- Market analysis tools

Your role is to:
1. Answer questions about crypto trading and signals
2. Provide insights on tokens and market trends
3. Help manage portfolios and watchlists
4. Explain signal generation and momentum scoring
5. Track whale wallets and their activity

Be concise, professional, and data-driven. Always cite sources when providing market data.
"""

        if context:
            prompt += "\n\nCurrent Context:\n"
            if "recent_signals" in context:
                prompt += f"- Recent signals: {len(context['recent_signals'])}\n"
            if "portfolio_summary" in context:
                summary = context['portfolio_summary']
                prompt += f"- Portfolio: {summary.get('open_positions', 0)} positions, ${summary.get('total_value', 0):.2f} value\n"
            if "tracked_wallets" in context:
                prompt += f"- Tracked wallets: {len(context['tracked_wallets'])}\n"

        return prompt

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("🔄 Conversation history cleared")


# Global instance
mcp_chat = MCPChat()
