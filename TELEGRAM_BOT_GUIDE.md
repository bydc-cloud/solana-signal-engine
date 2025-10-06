# 📱 AURA Telegram Bot - Complete Guide

## 🎉 Features

Your AURA Telegram bot now supports:

### ✅ **1. Slash Commands**
- `/start` - Initialize and see welcome message
- `/portfolio` - Portfolio summary with P&L
- `/watchlist` - View watched tokens
- `/signals` - Recent trading signals (24h)
- `/stats` - System statistics
- `/strategies` - Active trading strategies
- `/help` - Full command list

### ✅ **2. Natural Language Text**
Send ANY text message and AURA will:
- Understand your question
- Fetch relevant system data
- Provide context-aware responses
- Use Claude API for intelligent analysis (if key set)

**Examples:**
- "How's my portfolio doing?"
- "Why aren't there signals today?"
- "What tokens are we watching?"
- "Summarize recent activity"

### ✅ **3. Voice Messages**
Send voice messages and AURA will:
- Download and transcribe (requires OpenAI API key)
- Process as text message
- Respond with full context

---

## 🔧 Setup & Configuration

### **1. Find Your Bot**

Your bot token: `8305979428:AAHoWtmCGgndUZvdrA-vHmnNqyxun53V9_Y`

**To find your bot in Telegram:**
1. Open Telegram
2. Search for `@YOUR_BOT_USERNAME` (use @BotFather to get username)
3. Or use this direct link: `https://t.me/YOUR_BOT_USERNAME`

**To get your bot username:**
1. Message @BotFather in Telegram
2. Send `/mybots`
3. Select your bot
4. Click "Bot Settings" → "Username"

---

### **2. Enable AI-Powered Responses (Optional)**

For intelligent Claude-powered responses, add your Anthropic API key:

```bash
railway variables --set "ANTHROPIC_API_KEY=sk-ant-..."
```

**How to get an API key:**
1. Go to https://console.anthropic.com
2. Create an account / Sign in
3. Go to API Keys section
4. Create a new API key
5. Copy and add to Railway

**Without API key:**
- Bot still works with keyword detection
- Shows relevant data based on message content
- Falls back to smart contextual responses

---

### **3. Enable Voice Transcription (Optional)**

For voice message support, add your OpenAI API key:

```bash
railway variables --set "OPENAI_API_KEY=sk-proj-..."
```

**How to get an API key:**
1. Go to https://platform.openai.com
2. Sign in / Create account
3. Go to API Keys section
4. Create new secret key
5. Copy and add to Railway

**Without API key:**
- Bot acknowledges voice messages
- Tells you how to enable transcription
- Text messages work perfectly

---

## 🔍 Troubleshooting

### **Issue: Bot Not Responding**

**Check if bot is running:**
```bash
# Check Railway logs
railway logs | grep -i telegram

# Look for:
"✅ Telegram bot ready: commands + natural language + voice"
```

**Verify bot token is set:**
```bash
railway variables | grep TELEGRAM
```

**Restart the service:**
```bash
railway restart
```

---

### **Issue: Voice Messages Not Transcribed**

**Cause:** OpenAI API key not set

**Solution:**
```bash
railway variables --set "OPENAI_API_KEY=sk-proj-..."
```

---

### **Issue: No AI Responses**

**Cause:** Anthropic API key not set (bot uses fallback)

**Solution:**
```bash
railway variables --set "ANTHROPIC_API_KEY=sk-ant-..."
```

**Check if it's working:**
- Bot should respond with "🤖 [AI response]"
- Railway logs should show: "✅ Claude API response: ..."

---

## 📊 How It Works

### **Message Flow:**

```
User sends message
    ↓
Telegram API receives
    ↓
Bot handler processes
    ↓
┌─────────────────────┐
│ Is it a /command?   │
└─────────────────────┘
    ↓ YES              ↓ NO
Command handler    Text handler
    ↓                  ↓
Execute command    Fetch context:
                   - Portfolio
                   - Watchlist
                   - Signals
                   - Strategies
                       ↓
                   Check for Claude API
                       ↓ YES        ↓ NO
                   AI response   Keyword detection:
                                 - "portfolio"
                                 - "signal"
                                 - "token"
                       ↓              ↓
                   Send response ←────┘
```

---

## 🎯 Example Conversations

### **With Claude API Enabled:**

```
You: "hey how's my portfolio?"

AURA: 🤖 Your portfolio is currently showing 0 open positions
with no P&L yet. The system is actively scanning for high-momentum
opportunities. Check /signals to see what tokens are being tracked.
```

### **Without Claude API (Keyword Detection):**

```
You: "how's my portfolio?"

AURA: 🤔 I understand you're asking about: how's my portfolio?

💼 Current Portfolio:
• Open Positions: 0
• Total P&L: $0.00
• Win Rate: 0.0%
```

### **Voice Message:**

```
You: [voice] "what signals did we get today?"

AURA: 🎤 Transcribed: what signals did we get today?

📡 Recent Signals: 0 in last 24h
```

---

## 🚀 Advanced Usage

### **Config Management via Telegram:**

```
/panel edit momentum_threshold 30
→ 📝 Patch 42 created. Use /approve 42 to apply.

/approve 42
→ ✅ Patch 42 applied! momentum_threshold: 25 → 30
```

### **Performance Reports:**

```
/report today
→ Shows today's trading activity

/report week
→ Shows weekly performance digest
```

### **Manual Scan:**

```
/scan
→ Triggers manual signal scan
```

---

## 📈 Integration with Dashboard

The bot and dashboard share the same database, so:
- Actions taken in Telegram reflect on dashboard
- Dashboard updates show in Telegram (if alerts configured)
- Real-time sync across all interfaces

**Access dashboard:**
https://signal-railway-deployment-production.up.railway.app/dashboard

---

## 🔐 Security Notes

- ✅ Bot token is securely stored in Railway environment variables
- ✅ Only responds to your chat ID: `7024329420`
- ✅ API keys are never exposed in logs
- ✅ All communication encrypted via Telegram

---

## 📞 Support

**Check Bot Status:**
```bash
curl https://signal-railway-deployment-production.up.railway.app/health
```

**View Logs:**
```bash
railway logs --follow | grep -i telegram
```

**Restart Bot:**
```bash
railway restart
```

---

## 🎉 Summary

**Your bot is configured with:**
- ✅ Bot Token: Set
- ✅ Chat ID: `7024329420`
- ⚠️ Claude API: Not set (optional - adds AI)
- ⚠️ OpenAI API: Not set (optional - adds voice)

**To enable AI features:**
```bash
# For AI-powered responses
railway variables --set "ANTHROPIC_API_KEY=sk-ant-..."

# For voice transcription
railway variables --set "OPENAI_API_KEY=sk-proj-..."

# Restart to apply
railway restart
```

**Test it:**
1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Send "how's my portfolio?"
5. Should get a response!

---

**Last Updated:** 2025-10-06
**AURA Version:** v0.3.0
