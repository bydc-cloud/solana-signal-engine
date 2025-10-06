#!/bin/bash
# Set API Keys for AURA

echo "🔑 Setting API Keys in Railway..."

# Firecrawl API Key
railway variables --set "FIRECRAWL_API_KEY=fc-6323d77bc1ec4b5d87779dfb1156f8fa"

echo "✅ Firecrawl API key set!"
echo ""
echo "Optional: Set these for AI features:"
echo "railway variables --set \"ANTHROPIC_API_KEY=sk-ant-YOUR_KEY\""
echo "railway variables --set \"OPENAI_API_KEY=sk-proj-YOUR_KEY\""
echo ""
echo "🔄 Restarting Railway..."
railway restart

echo ""
echo "✅ Done! API keys configured."
echo ""
echo "🧪 Test your bot now:"
echo "   Open Telegram → @money3printerbot"
echo "   Send: /start"
echo "   Send: how's my portfolio?"
