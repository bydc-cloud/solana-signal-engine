# Helix Trading Bot - Lovable Control Center Specification

## Overview
A real-time web dashboard for monitoring and controlling the Helix cryptocurrency trading bot. Built with Lovable AI to provide an intuitive interface for managing paper and live trading operations.

## API Backend
- **Base URL**: `http://localhost:8000` (local) or your deployed URL
- **Documentation**: Available at `/docs` (FastAPI auto-generated)
- **CORS**: Enabled for Lovable frontend

## Core Features to Implement

### 1. Dashboard Home Page
**Route**: `/`

**Layout**:
- Header with "Helix Trading Bot Control Center" title
- Status card showing:
  - Scanner status (Running/Stopped) with colored indicator (green/red)
  - Current mode badge (PAPER/LIVE)
  - Scanner PID if running
  - Last updated timestamp with auto-refresh every 10 seconds

- Equity card displaying:
  - Total equity in USD (large, prominent)
  - Realized P&L with color coding (green if positive, red if negative)
  - Unrealized P&L with color coding
  - Progress bar showing % change from starting equity

- 24h Stats card:
  - Total trades executed
  - Total alerts generated
  - Average graduation score
  - Trade success rate

- Quick action buttons:
  - Start Scanner (primary button, green)
  - Stop Scanner (danger button, red)
  - Restart Scanner (secondary button, orange)

**API Calls**:
- `GET /status` - Poll every 10 seconds for real-time updates

---

### 2. Live Trading View
**Route**: `/trades`

**Components**:
- Time filter tabs: Last 1h | 6h | 24h | 7 days
- Mode filter pills: All | Paper | Live
- Real-time trade table with columns:
  - Timestamp (formatted: "2h ago", "just now")
  - Token Symbol (clickable link to Solscan)
  - Token Address (truncated with copy button)
  - Graduation Score (GS) with color gradient (red <40, yellow 40-70, green >70)
  - Size (% of portfolio)
  - Mode badge (PAPER/LIVE)
  - Route (Jupiter/Raydium)
  - Status indicator
- Pagination (50 trades per page)
- Export button (CSV download)

**API Calls**:
- `GET /trades?hours={hours}&mode={mode}&limit=50`

**Styling**:
- Use a dark theme with neon accents (cyan, purple, green)
- Monospace font for addresses and numbers
- Smooth animations for new trades appearing

---

### 3. Alerts & Signals
**Route**: `/alerts`

**Components**:
- Filter section:
  - Time range slider (1-168 hours)
  - Minimum GS slider (0-100)
  - Gate status filter (All | Passed | Failed)

- Alert cards grid (3 columns on desktop):
  - Token symbol and address
  - Graduation Score (large, colored)
  - Gate result badges (green checkmarks for passed gates)
  - Timestamp
  - "Traded" badge if resulted in trade
  - Click to expand full details

- Live alert counter showing total matching alerts

**API Calls**:
- `GET /alerts?hours={hours}&min_gs={min_gs}&limit=100`

---

### 4. Performance Analytics
**Route**: `/analytics`

**Components**:
- Equity Chart (line chart):
  - Time series of portfolio equity
  - Dual Y-axis for equity and P&L
  - Zoom and pan controls
  - Toggle between 24h, 7d, 30d views

- Daily Statistics Table:
  - Date column
  - Paper trades count
  - Live trades count
  - Total alerts
  - Average GS
  - Color coding for trends (up/down arrows)

- Performance Metrics cards:
  - Total return %
  - Sharpe ratio (if calculable)
  - Max drawdown
  - Win rate
  - Average trade size

**API Calls**:
- `GET /analytics/performance`
- `GET /analytics/daily`

---

### 5. Configuration Panel
**Route**: `/config`

**Components**:
- Warning banner: "Configuration changes require scanner restart"

- Mode Selector (prominent):
  - Radio buttons: PAPER | LIVE
  - Large warning for LIVE mode

- Trading Parameters form:
  - GRAD_MIN_SCORE (slider 0-100, current: 35)
  - GRAD_PER_TRADE_CAP (slider 0.001-0.10, current: 0.02)
  - GRAD_GLOBAL_EXPOSURE_CAP (slider 0.1-1.0, current: 0.90)
  - GRAD_MAX_CONCURRENT (number input 1-50, current: 20)

- Each parameter shows:
  - Current value
  - Description tooltip
  - Recommended range

- Save button (primary)
- Reset to defaults button (secondary)
- Restart scanner button (appears after save)

**API Calls**:
- `GET /config`
- `POST /config/update` (for each parameter)
- `POST /scanner/restart`

---

### 6. System Logs
**Route**: `/logs`

**Components**:
- Log viewer with:
  - Dark terminal-style background
  - Monospace font
  - Color coding for log levels:
    - ERROR: red
    - WARNING: yellow
    - INFO: white
    - DEBUG: gray
  - Auto-scroll toggle
  - Search/filter input
  - Lines count selector (100, 500, 1000)
  - Refresh button
  - Auto-refresh toggle (every 5s)

- Download logs button

**API Calls**:
- `GET /logs?lines={lines}`

---

## Design System

### Colors (Dark Theme)
- Background: `#0a0a0f`
- Surface: `#1a1a2e`
- Border: `#2a2a3e`
- Text Primary: `#ffffff`
- Text Secondary: `#a0a0b0`
- Accent Cyan: `#00f5ff`
- Accent Purple: `#b537f2`
- Accent Green: `#00ff88`
- Success: `#10b981`
- Warning: `#f59e0b`
- Danger: `#ef4444`

### Typography
- Headers: Inter or Outfit (bold)
- Body: Inter
- Mono: JetBrains Mono or Fira Code

### Components
- Cards: Rounded corners, subtle shadow, hover effects
- Buttons: Rounded, gradient on hover for primary
- Status indicators: Pulsing animation when active
- Charts: Gradient fills, smooth animations

---

## Mobile Responsive
- Stack cards vertically on mobile
- Hamburger menu for navigation
- Touch-friendly button sizes
- Simplified charts on small screens

---

## Real-time Updates
- Use React hooks for polling
- Visual indicators when data is loading
- Toast notifications for important events (scanner stopped, trade executed)
- Error handling with user-friendly messages

---

## To Build in Lovable

1. **Start the API server first**:
   ```bash
   cd /Users/johncox/Projects/helix/helix_production
   pip install -r api_requirements.txt
   python3 api_server.py
   ```

2. **In Lovable, create a new project and prompt**:
   ```
   Create a dark-themed crypto trading bot control center dashboard with these pages:

   1. Dashboard home showing bot status, equity, and 24h stats
   2. Live trades table with filters
   3. Alerts grid with filtering
   4. Analytics page with charts
   5. Configuration panel
   6. System logs viewer

   Use the API at http://localhost:8000 with these endpoints:
   - GET /status (poll every 10s)
   - GET /trades?hours=24&mode=PAPER
   - GET /alerts?hours=24&min_gs=35
   - GET /analytics/performance
   - GET /analytics/daily
   - GET /config
   - POST /config/update (body: {key: string, value: string})
   - POST /scanner/start
   - POST /scanner/stop
   - POST /scanner/restart
   - GET /logs?lines=100

   Use shadcn/ui components, dark theme with neon cyan/purple/green accents.
   Add real-time polling, toast notifications, and smooth animations.
   Make it mobile responsive with a sidebar navigation.
   ```

3. **Lovable will generate the full frontend with**:
   - React components
   - Routing (React Router)
   - API integration (fetch or axios)
   - State management
   - Styling (Tailwind CSS)
   - Deployment-ready code

4. **Customize and iterate**: Tell Lovable to adjust colors, add features, or modify layouts using natural language.

---

## Deployment

### API Server
Deploy to:
- Railway.app (free tier, easy Python deployment)
- Fly.io (free tier)
- Your own VPS (runs alongside scanner)

### Lovable Frontend
- Deploys automatically to Lovable Cloud
- Get shareable link
- Can export code to deploy elsewhere (Vercel, Netlify)

---

## Security Notes
- In production, replace `allow_origins=["*"]` with your Lovable domain
- Use environment variables for sensitive config
- Consider adding API authentication for live mode
- Keep API server on localhost or behind VPN for safety

---

## Future Enhancements
- WebSocket support for real-time trade notifications
- Backtesting interface
- Strategy comparison
- Mobile app (Lovable can generate React Native)
- Telegram bot integration interface
- Alert rule builder
