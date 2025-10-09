# Final Integration Tasks - AURA v0.3.0

## 🎯 User Requirements

1. **Voice Agent**: Continuous listening, auto-detects silence, responds in real-time
2. **Telegram → Signals**: Store all Telegram signals in database → display on dashboard
3. **Wallets Tab**: Show tracked whale wallets from database
4. **Logs Tab**: Display system logs in real-time
5. **Twitter/X Momentum Tab**: Social sentiment tracking

---

## ✅ What's Already Working

- [dashboard/aura-complete.html](dashboard/aura-complete.html:1) - Jarvis-style UI with voice button
- [aura_server.py](aura_server.py:171) - Voice transcription endpoint
- [seed_wallets.py](seed_wallets.py:1) - Wallet seeding script
- [unified_scanner.py](unified_scanner.py:1) - Dual scanner system
- [aura/mcp_chat.py](aura/mcp_chat.py:1) - Claude-powered chat

---

## 🔧 Tasks Needed

### 1. **Continuous Voice with Auto-Silence Detection**

**File**: `dashboard/aura-complete.html`

**Changes Needed**:
```javascript
// Add silence detection variables
let silenceTimeout = null;
let lastSoundTime = 0;
const SILENCE_THRESHOLD = 30; // Volume threshold
const SILENCE_DURATION = 1500; // 1.5s silence = auto-stop

// In toggleVoice(), add VAD logic:
function startSilenceDetection() {
    function checkSilence() {
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((sum, val) => sum + val, 0) / dataArray.length;

        if (average > SILENCE_THRESHOLD) {
            lastSoundTime = Date.now();
        } else if (Date.now() - lastSoundTime > SILENCE_DURATION) {
            // Auto-stop
            mediaRecorder.stop();
            return;
        }

        silenceTimeout = setTimeout(checkSilence, 100);
    }
    checkSilence();
}
```

**Why**: Enables hands-free voice interaction like Jarvis/Alexa

---

### 2. **Store Telegram Signals in Database**

**File**: `REALITY_MOMENTUM_SCANNER.py` ([Line 1266](REALITY_MOMENTUM_SCANNER.py:1266))

**Changes Needed**:
```python
async def send_enhanced_signal(self, token: dict, signal_strength: float, validation: dict):
    # ... existing Telegram send logic ...

    # NEW: Store in AURA database
    try:
        import sqlite3
        conn = sqlite3.connect('aura.db')
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO helix_signals
            (token_address, symbol, momentum_score, market_cap, liquidity, volume_24h, price, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            address,
            symbol,
            signal_strength,
            mcap,
            token.get('liquidity', 0),
            volume,
            price,
            datetime.now().isoformat(),
            json.dumps({
                'risk_score': validation['risk_score'],
                'buyer_dominance': validation.get('buyer_dominance', 0),
                'narrative': narrative
            })
        ))

        conn.commit()
        conn.close()
        logger.info(f"Stored signal in AURA database: {symbol}")
    except Exception as e:
        logger.error(f"Failed to store signal: {e}")

    return True
```

**Why**: Dashboard can display same signals that go to Telegram

---

### 3. **Verify Wallets Display**

**Current Status**: Wallets are seeded locally but may not be on Railway

**Fix**: The [start.sh](start.sh:19) already includes wallet seeding. Just need to verify it runs.

**Test**:
```bash
curl https://signal-railway-deployment-production.up.railway.app/api/aura/wallets
```

Should return 5 wallets. If empty, seed script didn't run.

---

### 4. **Add Logs Tab**

**File**: `dashboard/aura-complete.html`

**Changes Needed**:

**HTML** (add tab):
```html
<button class="tab" onclick="switchTab('logs')">Logs</button>

<!-- Logs Tab -->
<div class="tab-content" id="logs-tab">
    <div class="live-header">
        <div class="live-title">System Logs</div>
        <div class="live-indicator"><div class="live-dot"></div><span>LIVE</span></div>
    </div>
    <div class="logs-container" id="logsContainer">
        <div class="log-entry"><span class="log-time">18:30:45</span> <span class="log-level info">INFO</span> Scanner started</div>
    </div>
</div>
```

**CSS**:
```css
.logs-container {
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 12px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    max-height: 600px;
    overflow-y: auto;
}

.log-entry {
    padding: 0.5rem;
    border-bottom: 1px solid #1a1a1a;
}

.log-time {
    color: #666;
    margin-right: 0.5rem;
}

.log-level {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: 600;
    margin-right: 0.5rem;
}

.log-level.info { background: rgba(0, 136, 255, 0.1); color: #0088ff; }
.log-level.error { background: rgba(255, 68, 68, 0.1); color: #ff4444; }
.log-level.success { background: rgba(0, 255, 136, 0.1); color: #00ff88; }
```

**JavaScript**:
```javascript
async function loadLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/aura/logs?limit=100`);
        const data = await response.json();
        const logs = data.logs || [];

        const container = document.getElementById('logsContainer');
        container.innerHTML = logs.map(log => `
            <div class="log-entry">
                <span class="log-time">${log.timestamp}</span>
                <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
                ${log.message}
            </div>
        `).join('');
    } catch (error) {
        console.error('Logs error:', error);
    }
}
```

**API Endpoint** (`aura_server.py`):
```python
@app.get("/api/aura/logs")
async def get_logs(limit: int = 100):
    """Get recent system logs"""
    try:
        log_file = "momentum_scanner.log"
        if not os.path.exists(log_file):
            return {"logs": []}

        with open(log_file, 'r') as f:
            lines = f.readlines()[-limit:]

        logs = []
        for line in lines:
            # Parse log format: 2025-10-06 18:30:45 - INFO - Message
            parts = line.split(' - ', 2)
            if len(parts) >= 3:
                timestamp = parts[0]
                level = parts[1].lower()
                message = parts[2].strip()
                logs.append({
                    'timestamp': timestamp,
                    'level': level,
                    'message': message
                })

        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        return {"error": str(e), "logs": []}
```

---

### 5. **Add Twitter/X Momentum Tab**

**File**: `dashboard/aura-complete.html`

**Changes Needed**:

**HTML**:
```html
<button class="tab" onclick="switchTab('twitter')">Twitter/X</button>

<!-- Twitter Tab -->
<div class="tab-content" id="twitter-tab">
    <div class="live-header">
        <div class="live-title">Social Momentum</div>
        <div class="live-indicator"><div class="live-dot"></div><span>LIVE</span></div>
    </div>
    <div class="feed" id="twitterFeed">
        <div class="empty-state"><div class="empty-text">Monitoring social sentiment...</div></div>
    </div>
</div>
```

**JavaScript**:
```javascript
async function loadTwitter() {
    try {
        const response = await fetch(`${API_BASE}/api/aura/social/momentum`);
        const data = await response.json();
        const trends = data.trends || [];

        const feedEl = document.getElementById('twitterFeed');
        if (trends.length === 0) {
            feedEl.innerHTML = '<div class="empty-state"><div class="empty-text">No trending tokens</div></div>';
        } else {
            let html = '';
            trends.forEach(trend => {
                html += `<div class="card">
                    <div class="card-header">
                        <div class="card-title">$${trend.symbol}</div>
                        <div class="card-badge">${trend.mentions} mentions</div>
                    </div>
                    <div class="card-meta">
                        <div class="meta-item">
                            <div class="meta-label">Sentiment</div>
                            <div class="meta-value ${trend.sentiment > 0 ? 'positive' : 'negative'}">
                                ${(trend.sentiment * 100).toFixed(0)}%
                            </div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">24h Change</div>
                            <div class="meta-value">${trend.change_24h}%</div>
                        </div>
                    </div>
                    <div class="card-actions">
                        <a href="https://twitter.com/search?q=%24${trend.symbol}" target="_blank" class="card-link">View Tweets</a>
                    </div>
                </div>`;
            });
            feedEl.innerHTML = html;
        }
    } catch (error) {
        console.error('Twitter error:', error);
    }
}
```

**API Endpoint** (would need Twitter API integration):
```python
@app.get("/api/aura/social/momentum")
async def get_social_momentum():
    """Get trending tokens from Twitter/X"""
    # Would integrate with Twitter API or social sentiment service
    # For now, return mock data
    return {
        "trends": [
            {
                "symbol": "BONK",
                "mentions": 1234,
                "sentiment": 0.75,
                "change_24h": 15.3
            },
            {
                "symbol": "WIF",
                "mentions": 987,
                "sentiment": 0.82,
                "change_24h": 22.1
            }
        ]
    }
```

---

## 📊 Complete Dashboard Structure

```
┌─────────────────────────────────────────┐
│  AURA                        [●] Online │
│  Chat | Signals | Wallets | Watchlist  │
│  Portfolio | Logs | Twitter/X           │
├─────────────────────────────────────────┤
│                                         │
│  [Chat/Signals/etc content here]        │
│                                         │
│  🎤 Voice Button (with auto-silence)   │
└─────────────────────────────────────────┘
```

---

## 🚀 Deployment Steps

1. **Update dashboard with new tabs**:
   ```bash
   # Edit dashboard/aura-complete.html
   # Add Logs and Twitter tabs
   ```

2. **Update scanner to store signals**:
   ```bash
   # Edit REALITY_MOMENTUM_SCANNER.py
   # Add database insert in send_enhanced_signal()
   ```

3. **Add API endpoints**:
   ```bash
   # Edit aura_server.py
   # Add /api/aura/logs
   # Add /api/aura/social/momentum
   ```

4. **Update voice with VAD**:
   ```bash
   # Edit dashboard/aura-complete.html
   # Add startSilenceDetection()
   ```

5. **Commit and deploy**:
   ```bash
   git add -A
   git commit -m "feat: Complete integration - Logs, Twitter, Auto-Voice"
   git push origin main
   railway up --detach
   ```

---

## ✅ Testing Checklist

- [ ] Voice: Click mic, speak, stops automatically after 1.5s silence
- [ ] Signals: New Telegram signals appear on Signals tab
- [ ] Wallets: 5 whale wallets displayed with win rates
- [ ] Logs: System logs streaming in real-time
- [ ] Twitter: Social momentum trends displayed
- [ ] Chat: Claude responds with context
- [ ] All tabs switch correctly

---

**Status**: Ready to implement
**Est. Time**: 2-3 hours
**Priority**: HIGH
