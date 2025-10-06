# Lovable: Advanced Trading Dashboard Prompt

Build on top of my existing Helix dashboard to create an **in-depth, institutional-grade trading analytics platform** comparable to Axiom and GMGN, with the following comprehensive features:

---

## 🎯 Core Requirements

### 1. **Live Wallet Activity Stream** (Real-Time)
- Display **20 smart money wallets** with live transaction feeds
- Show wallet-level PnL: **1d / 7d / 30d / All-Time**
- Filter by:
  - Tier (S / A / B)
  - Category (DeFi, NFT, Meme, Infrastructure)
  - Win rate (>70%, 50-70%, <50%)
  - Activity (Active last 1h / 6h / 24h)
- Each wallet card shows:
  - **Label** (e.g., "Nansen Alpha Whale #3")
  - **Live balance** (SOL + USD value)
  - **Recent trades** (last 5 trades with entry/exit, PnL, duration)
  - **Win rate** sparkline chart
  - **Volume** (24h / 7d / 30d bar chart)

**API Endpoint:** `GET /wallets/activity?tier=S&hours=24`

---

### 2. **Token Discovery Dashboard** (Axiom-Style)
- **4-panel layout:**
  1. **High Momentum** (momentum_score ≥ 50)
  2. **Smart Money Inflow** (3+ wallets bought in last 1h)
  3. **Volume Surge** (24h volume >300% of 7d avg)
  4. **New Listings** (created <24h ago)

- Each token card shows:
  - Symbol, address (truncated), market cap, liquidity
  - **Price chart** (1h / 6h / 24h line chart with TradingView-style candlesticks)
  - **Holder distribution pie chart** (top 10 holders vs rest)
  - **Buy/Sell pressure gauge** (buyer_dominance %)
  - **Risk score** (LOW / MEDIUM / HIGH with color coding)
  - **Graduation Score (GS)** with component breakdown tooltip:
    - Volume: 25%
    - Liquidity: 20%
    - Holders: 15%
    - Price momentum: 20%
    - Smart money: 20%

**API Endpoints:**
- `GET /tokens/trending?sort=momentum&limit=20`
- `GET /tokens/smartmoney?min_wallets=3&hours=1`
- `GET /tokens/new?hours=24&min_mc=10000`

---

### 3. **Bubble Map Visualization** (GMGN-Style)
- **Interactive bubble chart** where:
  - **X-axis:** Market Cap ($10k - $100k log scale)
  - **Y-axis:** 24h Volume
  - **Bubble size:** Number of holders
  - **Bubble color:** Graduation Score (gradient: red <30, yellow 30-60, green >60)
  - **Hover tooltip:** Full token details + mini price chart
  - **Click action:** Open detailed token modal

- **Filters:**
  - Market cap range slider ($10k - $1M)
  - Min GS threshold (0-100)
  - Smart money activity (0-10+ wallets)
  - Time range (1h / 6h / 24h)

**Implementation:** Use D3.js or Recharts for bubble chart

---

### 4. **Holder Analysis** (Deep Dive)
For each token, show:
- **Top 20 holders table:**
  - Wallet address (with Solscan link)
  - Holdings (% of supply)
  - Entry date
  - Current PnL
  - Classification (Smart Money / Retail / Bot / Dev)
  - Recent activity (Buy / Sell / Hold)

- **Holder distribution charts:**
  - **Pie chart:** Top 10 vs rest
  - **Histogram:** Holdings distribution buckets (<0.1%, 0.1-1%, 1-5%, >5%)
  - **Timeline:** Holder count over time (24h)

**API Endpoint:** `GET /tokens/{address}/holders?limit=20`

---

### 5. **Trading Activity Heatmap**
- **24-hour heatmap** showing:
  - Rows: 20 smart money wallets
  - Columns: Hour of day (0-23)
  - Cell color: Trade volume ($0 = white, $10k+ = dark green)
  - Hover: List of trades in that hour

- **Filters:**
  - Token filter (show activity for specific token)
  - Wallet tier filter (S / A / B)
  - Min trade size ($100 - $10k+)

**API Endpoint:** `GET /wallets/heatmap?hours=24&token={address}`

---

### 6. **Signal Performance Analytics**
- **Signal history table:**
  - Timestamp, symbol, entry price, current price, PnL, duration
  - Signal strength (0-100)
  - Status (Active / Closed / Stopped Out)
  - Win rate by signal strength bucket (<50, 50-70, >70)

- **Charts:**
  - **Win rate by hour** (bar chart showing which hours have best signals)
  - **Avg return by GS** (scatter plot: GS vs return %)
  - **Cumulative PnL** (line chart over time)

**API Endpoints:**
- `GET /signals/performance?hours=168` (7 days)
- `GET /signals/stats?group_by=hour`

---

### 7. **Live Scanner Status Panel**
- **Top status bar:**
  - Scanner status (Running / Stopped) with green/red indicator
  - Current cycle progress (e.g., "Scanning: 45/300 tokens")
  - Last signal: 2m ago
  - Signals today: 7

- **Metrics cards:**
  - **Cycles completed:** 42
  - **Signals sent:** 7 (avg: 12.3s/cycle)
  - **Empty cycles:** 12
  - **Guard rejection breakdown** (pie chart):
    - low_momentum: 35%
    - holder_count: 20%
    - stale_trade: 15%
    - Other: 30%

**API Endpoint:** `GET /scanner/metrics`

---

### 8. **Advanced Filtering & Search**
- **Global search bar:**
  - Search by token symbol, address, wallet address
  - Auto-complete suggestions
  - Recent searches dropdown

- **Multi-filter sidebar:**
  - Market cap range (slider)
  - Liquidity range (slider)
  - Holder count range (slider)
  - GS range (slider)
  - Smart money count (0-10+)
  - Risk level (Low / Medium / High checkboxes)
  - Time range (1h / 6h / 24h / 7d / 30d)

---

### 9. **Customizable Layouts**
- **Dashboard presets:**
  - "Overview" - 4-grid layout (Signals, Wallets, Trending, Scanner Status)
  - "Token Focus" - Large bubble map + holder analysis
  - "Wallet Deep Dive" - Wallet activity stream + heatmap + PnL charts
  - "Performance" - Signal analytics + cumulative PnL + win rate charts

- **Drag-and-drop panels** to rearrange
- **Save custom layouts** to localStorage

---

### 10. **Dark Mode & Responsive Design**
- **Dark theme** (default) with neon accents (green for wins, red for losses)
- **Light theme** option
- **Responsive breakpoints:**
  - Desktop: 4-column grid
  - Tablet: 2-column grid
  - Mobile: Single column stack

---

## 📊 Chart Library Recommendations

Use **Recharts** (React-native charts) for:
- Line charts (price, PnL)
- Bar charts (volume, holder distribution)
- Pie charts (holder breakdown)
- Area charts (cumulative PnL)
- Scatter plots (GS vs return)

Use **D3.js** for:
- Bubble map (custom interactivity)
- Heatmap (trading activity)
- Force-directed graph (wallet network analysis - bonus feature)

---

## 🎨 Design References

**Axiom-style:**
- Clean, dark background (#0a0a0f)
- Neon accents (green #00ff88, red #ff3366, blue #0088ff)
- Glass-morphism cards (backdrop-blur, rgba borders)
- Hover effects on all interactive elements
- Smooth transitions (300ms ease-in-out)

**GMGN-style:**
- Dense information layout
- Monospace fonts for numbers
- Color-coded metrics (green = good, red = bad, yellow = neutral)
- Tooltips everywhere (on hover, show full details)

---

## 🔗 API Integration

All endpoints are available at: `https://signal-railway-deployment-production.up.railway.app`

**Key endpoints:**
- `/status` - Scanner status + equity
- `/scanner/metrics` - Detailed scanner metrics
- `/wallets` - Smart money wallet list
- `/wallets/{address}` - Single wallet details
- `/wallets/activity` - Live activity stream
- `/tokens/trending` - Trending tokens
- `/signals/all` - Signal history
- `/positions/active` - Active positions

**Authentication:** None required (public API)

---

## 🚀 Implementation Priority

1. **Phase 1 (MVP):** Live wallet activity + trending tokens + scanner status
2. **Phase 2:** Bubble map + holder analysis + signal performance
3. **Phase 3:** Heatmap + advanced filtering + custom layouts
4. **Phase 4:** Dark mode toggle + responsive design + animations

---

## 📱 Responsive Behavior

- **Desktop (>1200px):** 4-column grid, side-by-side panels
- **Tablet (768-1199px):** 2-column grid, collapsible sidebar
- **Mobile (<768px):** Single column, bottom nav bar, swipeable cards

---

## 🔔 Real-Time Updates

Use **polling** (every 10 seconds) for:
- Scanner status
- Wallet activity
- Signal updates

Use **WebSocket** (if available) for:
- Live price updates
- New signal alerts
- Wallet transaction notifications

---

## 🎯 Success Metrics

Dashboard should display:
- **20 smart money wallets** with live data
- **40-60 tokens** in trending/discovery panels
- **3-5 signals** generated per hour (when scanner running)
- **<500ms** API response times
- **<2s** page load time

---

## 📝 Notes

- Use **TailwindCSS** for styling (utility-first)
- Use **Shadcn UI** for components (buttons, cards, modals)
- Use **Tanstack Query** for API data fetching (caching, refetching)
- Use **Zustand** for state management (lightweight)
- Deploy to **Lovable** platform (one-click deploy)

---

Build this dashboard incrementally, starting with Phase 1. Focus on **dense information display** and **fast interactions** - users should be able to scan 100+ tokens in <30 seconds.

Make it **visually stunning** and **data-rich** like Axiom/GMGN, not sparse like typical crypto dashboards.
