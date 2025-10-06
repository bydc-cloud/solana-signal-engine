# 🚨 Quick Fix: Enable Telegram Bot AI Features

## The Issue

Your Telegram bot is deployed but needs API keys to fully work with AI features.

## ✅ Quick Solution (5 minutes)

### **Step 1: Get Anthropic API Key** (For AI responses)

1. Go to: https://console.anthropic.com
2. Sign up or log in
3. Click "API Keys" in left sidebar
4. Click "Create Key"
5. Give it a name like "AURA Telegram Bot"
6. Copy the key (starts with `sk-ant-`)

### **Step 2: Add to Railway**

```bash
# In your terminal:
railway variables --set "ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE"
```

### **Step 3: Get OpenAI API Key** (For voice transcription - OPTIONAL)

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Give it a name like "AURA Voice"
5. Copy the key (starts with `sk-proj-` or `sk-`)

```bash
# Add to Railway:
railway variables --set "OPENAI_API_KEY=sk-YOUR_KEY_HERE"
```

### **Step 4: Restart Railway**

```bash
railway restart
```

### **Step 5: Wait 2 minutes, then test**

1. Open Telegram
2. Search for your bot (check with @BotFather if you forgot the username)
3. Send: `/start`
4. Send: "how's my portfolio?"

You should get an AI-powered response!

---

## 🔍 Troubleshooting

### **Bot Still Not Responding?**

**Check if bot is running:**
```bash
railway logs | grep -i "telegram bot" | tail -20
```

**Look for:**
- ✅ `"✅ Telegram bot ready: commands + natural language + voice"`
- ✅ `"✅ Telegram bot command handlers setup complete"`

**If you see errors:**
```bash
# View full logs
railway logs --follow

# Look for any errors related to telegram or bot
```

### **Check Bot Username**

1. Open Telegram
2. Message @BotFather
3. Send `/mybots`
4. Select your bot
5. See username (like @your_bot_name)
6. Search for that in Telegram

### **Verify Environment Variables**

```bash
railway variables | grep TELEGRAM
```

Should show:
```
TELEGRAM_BOT_TOKEN=8305979428:AAHoWtmCGgndUZvdrA-vHmnNqyxun53V9_Y
TELEGRAM_CHAT_ID=7024329420
```

---

## 🎯 Test Commands

Once bot is responding:

### **Basic Commands:**
```
/start
/portfolio
/signals
/stats
/help
```

### **Natural Language:**
```
how's my portfolio?
why no signals today?
what tokens are we watching?
summarize recent activity
```

### **Voice (if OpenAI key set):**
- Record voice message
- Send to bot
- Should transcribe and respond

---

## 💡 What Each Key Does

### **ANTHROPIC_API_KEY** (Highly Recommended)
- **What:** Claude AI integration
- **Enables:** Intelligent, context-aware responses
- **Without it:** Bot uses basic keyword detection (still works, but less smart)
- **Cost:** ~$0.01-0.03 per conversation (very cheap)

### **OPENAI_API_KEY** (Optional)
- **What:** OpenAI Whisper transcription
- **Enables:** Voice message transcription
- **Without it:** Bot acknowledges voice but can't transcribe
- **Cost:** ~$0.006 per minute of audio

---

## 🚀 Expected Behavior

### **With ANTHROPIC_API_KEY:**
```
You: "how's my portfolio doing?"

Bot: 🤖 Your portfolio is currently at $0.00 P&L with 0 open
positions. The system is actively scanning for high-momentum
opportunities. Recent signals: 0 in the last 24 hours. Use
/signals to see the latest scans.
```

### **Without ANTHROPIC_API_KEY:**
```
You: "how's my portfolio doing?"

Bot: 🤔 I understand you're asking about: how's my portfolio doing?

💼 Current Portfolio:
• Open Positions: 0
• Total P&L: $0.00
• Win Rate: 0.0%
```

Both work, but Claude AI gives much better responses!

---

## 📊 Alternative: Use the Dashboard

While setting up the bot, you can use the dashboard:

**URL:** https://signal-railway-deployment-production.up.railway.app/dashboard

The dashboard shows all the same data and updates in real-time!

---

## 🆘 Still Stuck?

### **Option 1: Check Railway Status**
```bash
curl -s https://signal-railway-deployment-production.up.railway.app/health | jq
```

Should return:
```json
{
  "status": "healthy",
  "helix": {...},
  "aura": {...}
}
```

### **Option 2: View Logs in Browser**

1. Go to https://railway.app
2. Sign in
3. Click your project
4. Click "Deployments"
5. View logs in browser

### **Option 3: Restart Everything**

```bash
railway restart
```

Wait 2-3 minutes, then test again.

---

## ✅ Success Checklist

- [ ] Got Anthropic API key from console.anthropic.com
- [ ] Added key to Railway with `railway variables --set`
- [ ] (Optional) Got OpenAI API key from platform.openai.com
- [ ] (Optional) Added OpenAI key to Railway
- [ ] Restarted Railway with `railway restart`
- [ ] Waited 2 minutes for deployment
- [ ] Found bot username from @BotFather
- [ ] Sent `/start` to bot in Telegram
- [ ] Tested with "how's my portfolio?"
- [ ] Got response from bot ✅

---

## 🎉 Once Working

Your bot will be able to:
- ✅ Answer any question about your trading system
- ✅ Provide intelligent analysis with full context
- ✅ Explain why signals were or weren't generated
- ✅ Debug issues ("why no signals today?")
- ✅ Summarize performance ("how am I doing?")
- ✅ Research tokens ("analyze SOL")
- ✅ Transcribe and respond to voice messages

---

**Last Updated:** 2025-10-06
**Version:** AURA v0.3.0
