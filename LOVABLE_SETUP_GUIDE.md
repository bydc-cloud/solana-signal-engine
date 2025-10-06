# 🎨 Helix Trading Bot - Lovable Control Center Setup Guide

## Quick Start (5 minutes)

### Step 1: Start the API Server

```bash
cd /Users/johncox/Projects/helix/helix_production
./START_API_SERVER.sh
```

The API will be running at `http://localhost:8000`
- API Docs: http://localhost:8000/docs (FastAPI auto-generated)
- Health Check: http://localhost:8000/

### Step 2: Create Lovable Account

1. Go to https://lovable.dev/
2. Sign up with Google or email
3. Click "Create New Project"

### Step 3: Build the Dashboard

Copy and paste this prompt into Lovable:

```
Create a professional dark-themed cryptocurrency trading bot control center dashboard called "Helix Control Center".

BACKEND API:
Base URL: http://localhost:8000

PAGES TO CREATE:

1. DASHBOARD HOME (/)
- Header with "Helix Trading Bot" title and logo
- Auto-refreshing status card (poll /status every 10 seconds):
  * Scanner status badge (green "Running" or red "Stopped")
  * Current mode badge (PAPER/LIVE)
  * Scanner PID
  * Last updated timestamp
- Large equity display card:
  * Total equity in USD (prominent, large font)
  * Realized P&L (green if positive, red if negative)
  * Unrealized P&L (colored)
  * Percentage change from start
- 24h statistics grid:
  * Total trades
  * Total alerts
  * Active positions
- Action buttons:
  * Start Scanner (green, primary)
  * Stop Scanner (red, danger)
  * Restart Scanner (orange, secondary)
  * All call POST endpoints with success toasts

2. TRADES TABLE (/trades)
- Time range tabs: 1h, 6h, 24h, 7 days
- Mode filter: All, Paper, Live
- Sortable table with columns:
  * Time (relative: "2h ago")
  * Symbol (clickable to Solscan)
  * Address (truncated, copy button)
  * GS Score (colored: <40 red, 40-70 yellow, >70 green)
  * Size %
  * Mode badge
  * Route
- Pagination (50 per page)
- GET /trades?hours={hours}&mode={mode}

3. ALERTS GRID (/alerts)
- Filters:
  * Time range slider
  * Minimum GS slider
- Grid of alert cards (3 columns):
  * Symbol and address
  * Large GS score (colored)
  * Gate result badges
  * Timestamp
  * "Traded" indicator
- GET /alerts?hours={hours}&min_gs={min_gs}

4. ANALYTICS (/analytics)
- Equity chart (line chart using Recharts):
  * Time series of equity over time
  * Toggle 24h, 7d, 30d
  * Responsive
- Daily stats table:
  * Date, Paper trades, Live trades, Alerts, Avg GS
- Performance metrics cards:
  * Total return %
  * Trends with up/down arrows
- GET /analytics/performance
- GET /analytics/daily

5. CONFIGURATION (/config)
- Warning banner about restart requirement
- Mode toggle: PAPER / LIVE (large, prominent)
- Parameter form with sliders:
  * GRAD_MIN_SCORE (0-100)
  * GRAD_PER_TRADE_CAP (0.001-0.10)
  * GRAD_GLOBAL_EXPOSURE_CAP (0.1-1.0)
  * GRAD_MAX_CONCURRENT (1-50)
- Each shows current value and description
- Save button → POST /config/update for each param
- Restart button → POST /scanner/restart

6. SYSTEM LOGS (/logs)
- Terminal-style dark viewer
- Color-coded log levels (ERROR red, WARNING yellow, INFO white)
- Search/filter input
- Auto-scroll toggle
- Refresh button
- Lines selector (100, 500, 1000)
- GET /logs?lines={lines}

DESIGN SYSTEM:
- Dark theme: background #0a0a0f, surface #1a1a2e
- Neon accents: cyan #00f5ff, purple #b537f2, green #00ff88
- Use shadcn/ui components
- Smooth animations and transitions
- Mobile responsive with sidebar navigation
- Toast notifications for actions
- Loading states for all API calls

TECHNICAL:
- Use React with TypeScript
- React Query for API calls
- React Router for navigation
- Tailwind CSS for styling
- Recharts for charts
- Add error handling with friendly messages
- Auto-refresh dashboard every 10 seconds
```

### Step 4: Iterate and Customize

After Lovable generates the initial app, you can refine it:

```
"Make the equity card bigger and add a gradient background"
"Add a confetti animation when a trade is successful"
"Make the sidebar collapsible on mobile"
"Add a dark mode toggle (even darker)"
"Change the accent color to blue"
"Add export to CSV button on trades page"
"Make the GS score display as a circular progress indicator"
```

### Step 5: Deploy

Lovable automatically deploys your app to Lovable Cloud. You'll get:
- Live URL: `https://your-app.lovable.app`
- Auto-deployment on changes
- Free SSL certificate
- CDN hosting

## API Endpoint Reference

### Scanner Control
```bash
# Get status
curl http://localhost:8000/status

# Start scanner
curl -X POST http://localhost:8000/scanner/start

# Stop scanner
curl -X POST http://localhost:8000/scanner/stop

# Restart scanner
curl -X POST http://localhost:8000/scanner/restart
```

### Trading Data
```bash
# Get recent trades
curl "http://localhost:8000/trades?hours=24&mode=PAPER&limit=50"

# Get alerts
curl "http://localhost:8000/alerts?hours=24&min_gs=35&limit=100"

# Daily analytics
curl http://localhost:8000/analytics/daily

# Performance metrics
curl http://localhost:8000/analytics/performance
```

### Configuration
```bash
# Get config
curl http://localhost:8000/config

# Update config
curl -X POST http://localhost:8000/config/update \
  -H "Content-Type: application/json" \
  -d '{"key": "GRAD_MIN_SCORE", "value": "40"}'
```

### Logs
```bash
# Get logs
curl "http://localhost:8000/logs?lines=100"
```

## Troubleshooting

### API Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -f api_server.py

# Restart
./START_API_SERVER.sh
```

### CORS Issues
If Lovable can't connect to localhost:
1. Deploy API server to a cloud service (Railway, Fly.io)
2. Update API base URL in Lovable app
3. Or use ngrok for temporary tunnel:
   ```bash
   ngrok http 8000
   ```

### Database Not Found
Make sure `final_nuclear.db` exists:
```bash
ls -lh final_nuclear.db
```

If missing, the scanner will create it on first run.

## Advanced Features

### Add WebSocket Support (Future)
For real-time trade notifications without polling:

1. Update `api_server.py` to add WebSocket endpoint
2. In Lovable, prompt: "Add WebSocket connection to /ws for real-time trade updates"

### Add Authentication
For production deployment:

1. Add API key to `.env`:
   ```bash
   API_SECRET_KEY=your-random-secret-key
   ```

2. Update `api_server.py` to check API key header
3. In Lovable, add header to all API calls

### Custom Domain
1. Deploy API to your VPS or cloud service
2. Point subdomain: `api.yourdomain.com` → API server
3. Update Lovable app base URL
4. Deploy Lovable app to custom domain (Pro plan)

## Support

- Lovable Docs: https://docs.lovable.dev/
- Lovable Discord: https://lovable.dev/discord
- API Docs: http://localhost:8000/docs

## Next Steps

1. **Test the API**: Open http://localhost:8000/docs and try the endpoints
2. **Start Lovable**: Go to lovable.dev and paste the prompt
3. **Iterate**: Keep refining the UI using natural language
4. **Share**: Get your dashboard link and access from anywhere
5. **Deploy**: Move API to cloud for 24/7 access

---

**Pro Tip**: Take screenshots of your ideal dashboard design and tell Lovable "Make it look like this" - it can understand images!
