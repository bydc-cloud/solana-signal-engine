#!/bin/bash
# Enable AI Features for AURA Telegram Bot

echo "🤖 AURA AI Features Setup"
echo "========================="
echo ""

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

echo "📋 Current Setup:"
echo ""
echo "✅ Telegram Bot Token: Set"
echo "✅ Telegram Chat ID: Set"
echo "✅ Birdeye API Key: Set"
echo "✅ Helius API Key: Set"
echo ""

# Check current variables
echo "⚙️  Checking Railway environment variables..."
railway variables | grep -E "ANTHROPIC|OPENAI" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Some AI keys are already set"
    railway variables | grep -E "ANTHROPIC|OPENAI"
else
    echo "⚠️  No AI keys found"
fi
echo ""

echo "🔑 To enable AI features, you need:"
echo ""
echo "1. ANTHROPIC_API_KEY (for Claude AI responses)"
echo "   - Get it from: https://console.anthropic.com"
echo "   - Sign up / Login"
echo "   - Go to API Keys section"
echo "   - Create new key"
echo "   - Copy the key (starts with 'sk-ant-')"
echo ""
echo "2. OPENAI_API_KEY (for voice transcription)"
echo "   - Get it from: https://platform.openai.com"
echo "   - Sign up / Login"
echo "   - Go to API Keys section"
echo "   - Create new key"
echo "   - Copy the key (starts with 'sk-proj-' or 'sk-')"
echo ""

read -p "Do you want to set ANTHROPIC_API_KEY now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your Anthropic API key (sk-ant-...): " anthropic_key
    if [[ $anthropic_key == sk-ant-* ]]; then
        echo "Setting ANTHROPIC_API_KEY..."
        railway variables --set "ANTHROPIC_API_KEY=$anthropic_key"
        echo "✅ ANTHROPIC_API_KEY set!"
    else
        echo "❌ Invalid key format. Should start with 'sk-ant-'"
    fi
fi

echo ""
read -p "Do you want to set OPENAI_API_KEY now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your OpenAI API key (sk-...): " openai_key
    if [[ $openai_key == sk-* ]]; then
        echo "Setting OPENAI_API_KEY..."
        railway variables --set "OPENAI_API_KEY=$openai_key"
        echo "✅ OPENAI_API_KEY set!"
    else
        echo "❌ Invalid key format. Should start with 'sk-'"
    fi
fi

echo ""
echo "🔄 Restarting Railway service..."
railway restart

echo ""
echo "✅ Done! Your bot now has:"
railway variables | grep -E "ANTHROPIC|OPENAI" && echo "" || echo "⚠️  No AI keys set yet"

echo ""
echo "📱 Test your bot:"
echo "1. Open Telegram"
echo "2. Find your bot"
echo "3. Send: how's my portfolio?"
echo "4. If ANTHROPIC_API_KEY is set, you'll get AI responses!"
echo "5. If OPENAI_API_KEY is set, voice messages will be transcribed!"
echo ""
echo "🎉 All done!"
