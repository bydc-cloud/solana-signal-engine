import { useState, useEffect } from 'react';

const API_BASE = 'https://signal-railway-deployment-production.up.railway.app';

interface BotStatus {
  scanner_running: boolean;
  scanner_pid: string | number | null;
  scanner_status: string;
  database_initialized: boolean;
  mode: string;
  timestamp: string;
  paper_equity: {
    total_usd: number;
    realized_pnl: number;
    unrealized_pnl: number;
  };
  stats_24h: {
    trades: number;
    alerts: number;
  };
}

interface PnLSummary {
  total_equity: number;
  total_pnl: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_roi_percent: number;
  win_rate: number;
  total_trades: number;
  wins: number;
  losses: number;
}

interface Position {
  symbol: string;
  entry_price: number;
  current_price: number;
  unrealized_pnl_usd: number;
  unrealized_pnl_percent: number;
  holding_time_minutes: number;
  solscan_link: string;
  birdeye_link: string;
  dexscreener_link: string;
  size_usd?: number;
  entry_time?: string;
}

interface Signal {
  symbol: string;
  graduation_score: number;
  signal_type: string;
  tier: number;
  metadata: {
    market_cap: number;
    volume_24h: number;
    momentum_score: number;
    risk_score: number;
  };
  solscan_link: string;
  birdeye_link: string;
  dexscreener_link: string;
  created_at: string;
}

interface Sentiment {
  overall_sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  bullish_percentage: number;
  bullish_score: number;
  bearish_score: number;
}

interface HelixBotData {
  status: BotStatus | null;
  pnl: PnLSummary | null;
  positions: Position[];
  signals: Signal[];
  sentiment: Sentiment | null;
  loading: boolean;
  error: string | null;
}

export const useHelixBot = () => {
  const [data, setData] = useState<HelixBotData>({
    status: null,
    pnl: null,
    positions: [],
    signals: [],
    sentiment: null,
    loading: true,
    error: null,
  });

  const fetchData = async () => {
    try {
      const [statusRes, pnlRes, positionsRes, signalsRes, sentimentRes] =
        await Promise.all([
          fetch(`${API_BASE}/status`),
          fetch(`${API_BASE}/trading/pnl_summary`),
          fetch(`${API_BASE}/trading/active_positions`),
          fetch(`${API_BASE}/trading/signals?hours=24&limit=20`),
          fetch(`${API_BASE}/twitter/sentiment`)
        ]);

      const [status, pnlData, positionsData, signalsData, sentiment] = await Promise.all([
        statusRes.json(),
        pnlRes.json(),
        positionsRes.json(),
        signalsRes.json(),
        sentimentRes.json()
      ]);

      // Transform PnL data to include calculated fields
      const transformedPnl = {
        total_equity: pnlData.paper_equity?.total_usd || 100000,
        total_pnl: (pnlData.realized?.total_pnl_usd || 0) + (pnlData.unrealized?.total_pnl_usd || 0),
        realized_pnl: pnlData.realized?.total_pnl_usd || 0,
        unrealized_pnl: pnlData.unrealized?.total_pnl_usd || 0,
        total_roi_percent: ((((pnlData.realized?.total_pnl_usd || 0) + (pnlData.unrealized?.total_pnl_usd || 0)) / 100000) * 100),
        win_rate: pnlData.realized?.win_rate || 0,
        total_trades: pnlData.realized?.total_trades || 0,
        wins: pnlData.realized?.wins || 0,
        losses: pnlData.realized?.losses || 0,
      };

      setData({
        status,
        pnl: transformedPnl,
        positions: positionsData.positions || [],
        signals: signalsData.signals || [],
        sentiment,
        loading: false,
        error: null,
      });
    } catch (error) {
      console.error('Error fetching Helix bot data:', error);
      setData(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to fetch bot data',
      }));
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  return { ...data, refresh: fetchData };
};
