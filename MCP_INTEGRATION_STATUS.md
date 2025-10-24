# MCP Integration Status & Usage Guide

## 🔌 MCP Servers Configured

Based on your VSCode setup, you have these MCP servers available:

### 1. **Context7 MCP** ✅
- **Purpose:** Real-time documentation and code examples for any library
- **Commands:**
  - `resolve-library-id` - Convert package name to Context7 ID
  - `get-library-docs` - Fetch up-to-date documentation

**Example Usage:**
```
User: "How do I use the latest FastAPI WebSocket features?"
Claude: [Uses Context7 to fetch FastAPI docs] → Returns current best practices
```

### 2. **Firecrawl MCP** ✅
- **Purpose:** Web scraping and content extraction
- **Use Cases:**
  - Scrape DexScreener for token data
  - Monitor Twitter for trending tokens
  - Extract crypto news from websites

### 3. **Puppeteer MCP** ✅
- **Purpose:** Browser automation
- **Available Tools:**
  - `puppeteer_navigate` - Go to URL
  - `puppeteer_screenshot` - Capture page
  - `puppeteer_click` - Click elements
  - `puppeteer_fill` - Fill forms
  - `puppeteer_evaluate` - Run JavaScript

**Current Resource:**
- Browser console logs: `console://logs`

### 4. **Memory MCP** ✅
- **Purpose:** Persistent knowledge graph across sessions
- **Tools:**
  - `create_entities` - Store facts about wallets, tokens, users
  - `create_relations` - Link entities (wallet→trades→token)
  - `search_nodes` - Query stored knowledge
  - `add_observations` - Update entity attributes

### 5. **Sequential Thinking MCP** ✅
- **Purpose:** Complex problem-solving with chain-of-thought
- **Already Used:** Yes, used during architecture planning
- **Use Case:** Multi-step reasoning for trade analysis

---

## 🚀 HOW TO ACTIVELY USE MCPS IN AURA

### Integration Opportunity 1: **Enhanced Voice Controller with Context7**

**Current:** Voice controller uses hardcoded tool definitions
**With MCP:** Dynamically fetch latest API docs

```python
# In voice_controller.py
async def get_api_documentation(library_name: str):
    """Fetch latest docs via Context7 MCP"""
    # Use mcp__context7__resolve-library-id
    # Then mcp__context7__get-library-docs
    # Return: Up-to-date API reference
```

**User benefit:** Voice assistant can answer "How do I use Helius API v2?" with latest docs

---

### Integration Opportunity 2: **Web Scraping with Firecrawl MCP**

**Current:** Using requests/aiohttp for DexScreener
**With MCP:** More reliable scraping with JS rendering

```python
# In momentum_scanner.py
async def scrape_dexscreener_with_firecrawl():
    """Use Firecrawl MCP for better reliability"""
    # Handles Cloudflare challenges
    # Renders JavaScript
    # Returns clean JSON/HTML
```

**User benefit:** More reliable token data (no 530 errors)

---

### Integration Opportunity 3: **Browser Automation with Puppeteer MCP**

**Current:** Not implemented
**Potential Use Cases:**

1. **Screenshot Dashboard for Telegram**
   ```python
   async def share_dashboard_screenshot():
       """Send dashboard screenshot to Telegram"""
       await mcp_puppeteer_navigate("http://localhost:8000/dashboard/complete")
       screenshot = await mcp_puppeteer_screenshot(name="portfolio")
       # Send to Telegram
   ```

2. **Monitor Twitter via Browser**
   ```python
   async def scrape_crypto_twitter():
       """Monitor CT for trending tokens"""
       await mcp_puppeteer_navigate("https://twitter.com/search?q=solana")
       html = await mcp_puppeteer_evaluate("document.body.innerHTML")
       # Parse for trending tokens
   ```

3. **Test Dashboard Automatically**
   ```python
   async def test_wallet_modal():
       """E2E test wallet click"""
       await mcp_puppeteer_navigate("http://localhost:8000/dashboard/complete")
       await mcp_puppeteer_click("tr:first-child")  # Click first wallet
       screenshot = await mcp_puppeteer_screenshot(name="modal_test")
   ```

---

### Integration Opportunity 4: **Knowledge Graph with Memory MCP**

**Current:** Flat database tables
**With MCP:** Rich relationship graph

```python
# Store whale wallet knowledge
await mcp_memory_create_entities([
    {
        "name": "Yenni",
        "entityType": "whale_wallet",
        "observations": [
            "90% win rate over 10 trades",
            "Specializes in micro-cap gems",
            "Prefers tokens under $50k market cap",
            "Average hold time: 2.5 hours",
            "Best performing wallet in Q4 2025"
        ]
    }
])

# Create relationships
await mcp_memory_create_relations([
    {
        "from": "Yenni",
        "to": "BONK",
        "relationType": "traded_profitably"
    },
    {
        "from": "Yenni",
        "to": "momentum_strategy",
        "relationType": "follows"
    }
])

# Query knowledge
results = await mcp_memory_search_nodes("whale wallets with 90%+ win rate")
```

**User benefit:**
- Voice agent remembers patterns
- "Show me wallets similar to Yenni"
- "What strategy does Yenni use?"

---

## 🎯 RECOMMENDED MCP USAGE PRIORITIES

### Priority 1: **Memory MCP for Whale Intelligence** (High Value, Low Effort)

**Implementation:**
1. After each whale trade, store as entity + observation
2. Build relationship graph: wallet → trades → tokens → strategies
3. Voice commands: "What's Yenni's trading pattern?"

**ROI:** Makes the system actually intelligent (learns from data)

---

### Priority 2: **Puppeteer MCP for Monitoring** (Medium Value, Medium Effort)

**Implementation:**
1. Use for Twitter scraping (better than Twitter API rate limits)
2. Screenshot dashboards for Telegram alerts
3. E2E testing of critical flows

**ROI:** More reliable data sources + automated testing

---

### Priority 3: **Context7 MCP for Developer Experience** (Low Value, Low Effort)

**Implementation:**
1. Add to voice controller tools
2. User: "How do I use Helius webhooks?"
3. Claude: [Fetches latest Helius docs via Context7] → Explains

**ROI:** Better developer support, less time searching docs

---

## 📝 IMPLEMENTATION EXAMPLES

### Example 1: Store Whale Trade in Memory Graph

```python
# In live_whale_tracker.py
async def store_trade_in_memory(wallet_name, trade_data):
    """Store trade as knowledge graph entity"""
    await mcp_memory_create_entities([{
        "name": f"trade_{trade_data['signature'][:8]}",
        "entityType": "trade",
        "observations": [
            f"Wallet: {wallet_name}",
            f"Type: {trade_data['type']}",
            f"Value: ${trade_data['value_usd']}",
            f"Token: {trade_data['token_address'][:8]}",
            f"Timestamp: {trade_data['timestamp']}"
        ]
    }])

    # Link wallet → trade → token
    await mcp_memory_create_relations([
        {"from": wallet_name, "to": f"trade_{trade_data['signature'][:8]}", "relationType": "executed"},
        {"from": f"trade_{trade_data['signature'][:8]}", "to": trade_data['token_address'], "relationType": "involved"}
    ])
```

### Example 2: Query Trading Patterns

```python
# In voice_controller.py
async def analyze_wallet_strategy(wallet_name):
    """Use memory graph to infer strategy"""
    # Query all trades
    trades = await mcp_memory_search_nodes(f"{wallet_name} trades")

    # Query related tokens
    tokens = await mcp_memory_search_nodes(f"{wallet_name} traded tokens")

    # Infer pattern
    if avg_market_cap < 100k:
        strategy = "micro_cap_hunter"
    elif avg_hold_time < 1_hour:
        strategy = "scalper"
    else:
        strategy = "swing_trader"

    await mcp_memory_add_observations([{
        "entityName": wallet_name,
        "contents": [f"Trading strategy: {strategy}"]
    }])
```

### Example 3: Screenshot Portfolio for Telegram

```python
# In telegram webhook handler
async def send_portfolio_screenshot(chat_id):
    """Take screenshot and send to Telegram"""
    # Navigate to dashboard
    await mcp_puppeteer_navigate("http://localhost:8000/dashboard/complete")

    # Wait for data to load
    await asyncio.sleep(2)

    # Capture screenshot
    screenshot = await mcp_puppeteer_screenshot(
        name="portfolio",
        encoded=True  # Base64 for easy transmission
    )

    # Send to Telegram
    await send_telegram_photo(chat_id, screenshot)
```

---

## 🔧 SETUP VERIFICATION

### Check if MCPs are Active

```bash
# In VSCode, check MCP status
# Should see these servers connected:
# - context7
# - firecrawl
# - puppeteer
# - memory
# - sequential-thinking
```

### Test MCP Functions

```python
# Test Memory MCP
result = await mcp__memory__read_graph()
print(f"Memory graph nodes: {len(result.get('nodes', []))}")

# Test Context7 MCP
lib_id = await mcp__context7__resolve_library_id("fastapi")
docs = await mcp__context7__get_library_docs(lib_id)
print(f"FastAPI docs: {docs[:100]}...")

# Test Puppeteer MCP
await mcp__puppeteer__puppeteer_navigate("https://example.com")
screenshot = await mcp__puppeteer__puppeteer_screenshot(name="test")
```

---

## 🎨 CREATIVE MCP USE CASES

### Use Case 1: **Automated Trade Journaling**

Store every trade with context in Memory MCP:
- Why the signal was generated
- What the whale was doing at the time
- Market conditions (BTC price, volume)
- Outcome (win/loss)

Then query: "Show me all losing trades from momentum strategy in bear markets"

### Use Case 2: **Visual Regression Testing**

Use Puppeteer to screenshot dashboard before/after changes:
```python
# Before deployment
before = await mcp_puppeteer_screenshot(name="dashboard_v1")

# Deploy changes
# ...

# After deployment
after = await mcp_puppeteer_screenshot(name="dashboard_v2")

# Visual diff
if visual_diff(before, after) > threshold:
    alert("UI regression detected!")
```

### Use Case 3: **Crypto News Aggregation**

Use Puppeteer to monitor crypto news sites:
```python
sources = [
    "https://cryptonews.com",
    "https://coindesk.com",
    "https://decrypt.co"
]

for url in sources:
    await mcp_puppeteer_navigate(url)
    content = await mcp_puppeteer_evaluate("""
        document.querySelectorAll('.article-title').map(el => el.textContent)
    """)
    # Parse for Solana-related news
    # Cross-reference with tracked tokens
```

### Use Case 4: **Sentiment Analysis via Twitter**

```python
# Navigate to crypto Twitter
await mcp_puppeteer_navigate("https://twitter.com/search?q=%24SOL")

# Extract tweets
tweets = await mcp_puppeteer_evaluate("""
    Array.from(document.querySelectorAll('[data-testid="tweet"]'))
        .map(t => t.textContent)
""")

# Use Claude to analyze sentiment
for tweet in tweets:
    sentiment = await analyze_with_claude(tweet)
    # Store in Memory MCP
    await mcp_memory_create_entities([{
        "name": f"tweet_{hash(tweet)[:8]}",
        "entityType": "social_signal",
        "observations": [
            f"Content: {tweet[:100]}",
            f"Sentiment: {sentiment}",
            f"Related tokens: {extract_tokens(tweet)}"
        ]
    }])
```

---

## 📊 MCP INTEGRATION ROADMAP

### Phase 1: Foundation (Week 1)
- [ ] Add Memory MCP to voice controller tools
- [ ] Store whale trades as knowledge graph entities
- [ ] Test basic queries ("what wallets trade BONK?")

### Phase 2: Intelligence (Week 2)
- [ ] Build relationship graph (wallet→strategy→tokens)
- [ ] Add pattern recognition ("similar wallets to Yenni")
- [ ] Voice command: "What's the best performing strategy?"

### Phase 3: Automation (Week 3)
- [ ] Add Puppeteer for Twitter monitoring
- [ ] Screenshot portfolio for Telegram alerts
- [ ] E2E testing of critical flows

### Phase 4: Advanced (Week 4+)
- [ ] Context7 for dynamic documentation
- [ ] Multi-source news aggregation
- [ ] Visual regression testing

---

## 🚨 IMPORTANT NOTES

1. **MCP calls are synchronous** - Use async wrappers
2. **Rate limits apply** - Some MCPs have API limits
3. **Error handling crucial** - MCP failures should gracefully degrade
4. **Security** - Be careful with browser automation (XSS risks)
5. **Cost** - Some MCPs (like Puppeteer) consume resources

---

## ✅ ACTION ITEMS

1. **Verify MCP connections:** Check all 5 servers are active in VSCode
2. **Test Memory MCP:** Store one whale trade, query it back
3. **Test Puppeteer MCP:** Screenshot your dashboard
4. **Plan integration:** Pick one Priority 1 use case to implement
5. **Document patterns:** Add examples as you discover useful patterns

---

**Current MCP Status:** ✅ All servers configured and available
**Active Usage:** ⚠️ Not yet integrated into AURA codebase
**Next Step:** Implement Memory MCP for whale intelligence (highest ROI)

---

*Last updated: October 24, 2025*
