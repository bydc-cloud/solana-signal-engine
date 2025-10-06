// API configuration for Railway backend
const API_BASE_URL = "https://signal-railway-deployment-production.up.railway.app";

export const api = {
  // Status endpoint
  getStatus: () => fetch(`${API_BASE_URL}/status`).then(res => res.json()),
  
  // Scanner endpoints
  getTiers: () => fetch(`${API_BASE_URL}/scanner/tiers`).then(res => res.json()),
  getRecentSignals: (limit = 20, signalType?: string) => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (signalType) params.append('signal_type', signalType);
    return fetch(`${API_BASE_URL}/scanner/recent_signals?${params}`).then(res => res.json());
  },
  getMetrics: () => fetch(`${API_BASE_URL}/scanner/metrics`).then(res => res.json()),
  
  // Control endpoints
  startScanner: () => fetch(`${API_BASE_URL}/scanner/start`, { method: 'POST' }).then(res => res.json()),
  stopScanner: () => fetch(`${API_BASE_URL}/scanner/stop`, { method: 'POST' }).then(res => res.json()),
  restartScanner: () => fetch(`${API_BASE_URL}/scanner/restart`, { method: 'POST' }).then(res => res.json()),
  
  // Analytics endpoints
  getPerformance: () => fetch(`${API_BASE_URL}/analytics/performance`).then(res => res.json()),
  
  // Trades endpoint
  getTrades: (hours = 24, mode = 'PAPER') => fetch(`${API_BASE_URL}/trades?hours=${hours}&mode=${mode}`).then(res => res.json()),
  
  // Alerts endpoint
  getAlerts: (hours = 24, minGs = 35) => fetch(`${API_BASE_URL}/alerts?hours=${hours}&min_gs=${minGs}`).then(res => res.json()),
  
  // Logs endpoint
  getLogs: (lines = 500) => fetch(`${API_BASE_URL}/logs?lines=${lines}`).then(res => res.json()),
  
  // Wallet tracking endpoints
  getTrackedWallets: () => fetch(`${API_BASE_URL}/wallets/tracked`).then(res => res.json()),
  getWalletTrades: (hours = 24) => fetch(`${API_BASE_URL}/wallets/trades?hours=${hours}`).then(res => res.json()),
  getMirrorTrades: () => fetch(`${API_BASE_URL}/wallets/mirror_trades`).then(res => res.json()),
  getWalletPerformance: (timeframe = '1d', limit = 20) => 
    fetch(`${API_BASE_URL}/wallets/performance?timeframe=${timeframe}&limit=${limit}`).then(res => res.json()),
  
  // Trading metrics endpoints
  getActivePositions: () => fetch(`${API_BASE_URL}/trading/active_positions`).then(res => res.json()),
  getClosedTrades: (hours = 168, limit = 100) => 
    fetch(`${API_BASE_URL}/trading/closed_trades?hours=${hours}&limit=${limit}`).then(res => res.json()),
  getPnlSummary: () => fetch(`${API_BASE_URL}/trading/pnl_summary`).then(res => res.json()),
  getTradingSignals: (hours = 24, limit = 50, signalType?: string) => {
    const params = new URLSearchParams({ 
      hours: hours.toString(),
      limit: limit.toString() 
    });
    if (signalType) params.append('signal_type', signalType);
    return fetch(`${API_BASE_URL}/trading/signals?${params}`).then(res => res.json());
  },
  
  // Health check
  getHealth: () => fetch(`${API_BASE_URL}/health`).then(res => res.json()),
  
  // Smart money exits
  getRecentExits: (hours = 24, limit = 50) => 
    fetch(`${API_BASE_URL}/exits/recent?hours=${hours}&limit=${limit}`).then(res => res.json()),
  
  // Twitter endpoints
  getTwitterAccounts: () => fetch(`${API_BASE_URL}/twitter/accounts`).then(res => res.json()),
  getTwitterSignals: (hours = 24, minStrength = 50, tier?: string, sentiment?: string) => {
    const params = new URLSearchParams({ 
      hours: hours.toString(),
      min_strength: minStrength.toString()
    });
    if (tier) params.append('tier', tier);
    if (sentiment) params.append('sentiment', sentiment);
    return fetch(`${API_BASE_URL}/twitter/signals?${params}`).then(res => res.json());
  },
  getTwitterTrending: (hours = 24) => fetch(`${API_BASE_URL}/twitter/trending?hours=${hours}`).then(res => res.json()),
  getTwitterSentiment: (hours = 24) => fetch(`${API_BASE_URL}/twitter/sentiment?hours=${hours}`).then(res => res.json()),
};
