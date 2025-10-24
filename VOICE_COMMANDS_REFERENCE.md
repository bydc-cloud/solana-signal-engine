# AURA Voice Commands - Quick Reference

## Getting Started

1. **Add API Key to .env:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

2. **Start Server:**
   ```bash
   python3 aura_server.py
   ```

3. **Open Voice Dashboard:**
   ```
   http://localhost:8000/jarvis
   ```

## Voice Commands

### 🐋 Whale Wallets

| Command | What It Does |
|---------|-------------|
| "Show me the top 5 whale wallets" | Lists best performing wallets |
| "Show whales with win rate above 70%" | Filters by win rate |
| "Show profitable whales" | Shows wallets with positive P&L |
| "Show active whales" | Shows recently traded wallets |
| "Search for wallet latuche" | Find wallet by nickname |
| "Track wallet [address]" | Add new wallet to tracking |
| "Stop tracking [wallet]" | Remove wallet from tracking |
| "What's the win rate of Yenni?" | Get specific wallet details |

### 📊 Signals & Opportunities

| Command | What It Does |
|---------|-------------|
| "What signals came in today?" | Recent 24h signals |
| "Show signals with momentum above 70" | High-quality signals only |
| "What are the latest token opportunities?" | Recent trading signals |
| "Show me signals from the last 6 hours" | Time-filtered signals |

### 🔄 System Control

| Command | What It Does |
|---------|-------------|
| "Run whale tracking now" | Start tracking job |
| "What's the system status?" | Check system health |
| "Show scanner status" | Check scanner operation |

### 💼 Portfolio

| Command | What It Does |
|---------|-------------|
| "Show my portfolio" | Open positions & P&L |
| "What's my P&L?" | Profit/loss summary |

## Quick Command Buttons

Click these for instant actions:

1. **🐋 Top Whales** - Best performing wallets
2. **📊 Latest Signals** - Recent token signals
3. **🔄 Track All** - Run whale tracking
4. **⚙️ System Status** - System health check
5. **💼 Portfolio** - Portfolio summary

## Advanced Usage

### Natural Language Works!

All these work the same:
- "Show me the best whales"
- "Display top whale wallets"
- "What are the highest performing wallets?"
- "List the whales with best win rates"

### Combine Filters:

- "Show me 10 profitable wallets sorted by trades"
- "Find whales with more than 50 trades and 60% win rate"
- "Show recent signals with momentum over 80"

### Multi-Step Commands:

- "Track this wallet and show me its details"
- "Run tracking and show me the system status"

## Response Format

### Wallet Cards Show:
- ✓ Nickname
- ✓ Address (shortened)
- ✓ Win Rate (color-coded)
- ✓ Total Trades
- ✓ P&L (green if positive, red if negative)

### Signal Cards Show:
- ✓ Token Symbol
- ✓ Address
- ✓ Momentum Score
- ✓ 24h Volume
- ✓ Market Cap

### Status Shows:
- ✓ Wallets Tracked
- ✓ Signals (24h)
- ✓ Trades (24h)
- ✓ System Health

## Testing Commands

Try these to verify it works:

```bash
# Test 1: Basic wallet query
"Show me the top 3 whale wallets"

# Test 2: Signal check
"What signals came in today?"

# Test 3: System check
"What's the system status?"

# Test 4: Search
"Search for wallet with address starting with 7Ytt"

# Test 5: Filtered query
"Show wallets with win rate above 65%"
```

## Tips & Tricks

### Speed Optimization:
- Use quick command buttons for instant results
- Simple queries like "show whales" bypass AI (< 1s)
- Complex queries use full AI reasoning (1-3s)

### Voice Input:
1. Click microphone button
2. Wait for "Listening..."
3. Speak clearly
4. Command auto-transcribes
5. AI responds with voice

### Best Practices:
- Be specific: "top 5" instead of "some"
- Use filters: "profitable", "active", "high win rate"
- Try natural language - it understands context
- Check quick buttons first for common tasks

## Troubleshooting

### "I'm having trouble accessing my AI capabilities"
→ ANTHROPIC_API_KEY not set in .env

### No wallets showing up:
→ Database might be empty. Run: `/api/aura/seed_whale_stats`

### Voice not working:
→ OPENAI_API_KEY needed for Whisper transcription

### TTS not working:
→ ELEVENLABS_API_KEY needed for voice responses

## API Usage (Programmatic)

```bash
curl -X POST http://localhost:8000/api/aura/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Show top 5 whales"}'
```

Response includes:
- `message`: Human-readable response
- `tool_results`: Raw data from tools
- `success`: Boolean status

## Examples by Scenario

### Scenario 1: Finding Good Wallets
```
"Show me wallets with win rate above 70% and at least 10 trades"
→ Returns filtered list
→ Click wallet card for details
→ "Track wallet [address]" to add it
```

### Scenario 2: Daily Check-In
```
"What's the system status?"
→ See wallets, signals, trades count

"Show me today's signals"
→ Review new opportunities

"Show top 5 whales"
→ Check best performers
```

### Scenario 3: Deep Dive
```
"Search for wallet Yenni"
→ Find specific wallet

"What's the win rate of Yenni?"
→ Get detailed stats

"Show me Yenni's recent trades"
→ See trade history
```

## Command Categories

### Query Commands (Read Only):
- Show, display, list, what, get
- These only read data, no changes

### Action Commands (Write):
- Track, add, start, run, trigger
- These modify data or start processes

### Status Commands:
- Status, health, check
- System diagnostics

## Performance Guide

| Command Type | Response Time |
|--------------|---------------|
| Quick Commands | < 1 second |
| Simple Queries | 1-3 seconds |
| Complex Queries | 3-5 seconds |
| With Voice | +2-4 seconds |

## Security Notes

- Commands validate inputs
- Database uses parameterized queries
- No command can delete critical data
- Tool execution is logged

## Need Help?

1. Try quick command buttons first
2. Check this reference guide
3. Read `VOICE_CONTROLLER_SETUP.md`
4. Review `VOICE_CONTROLLER_SUMMARY.md`
5. Run test suite: `python3 test_voice_controller.py`

---

**Remember**: The AI actually EXECUTES commands, it doesn't just respond!

When you say "Track wallet X", it ADDS it to the database.
When you say "Run tracking", it STARTS the background job.
When you say "Show whales", it QUERIES live data.

This is a **MASTER CONTROLLER**, not just a chatbot!
