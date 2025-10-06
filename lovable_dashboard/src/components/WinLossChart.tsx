import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown } from 'lucide-react';

const API_BASE = 'https://signal-railway-deployment-production.up.railway.app';

interface WinLossStats {
  wins: number;
  losses: number;
  win_rate: number;
  total_trades: number;
  total_pnl_usd: number;
}

export const WinLossChart = () => {
  const [stats, setStats] = useState<WinLossStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE}/trading/pnl_summary`);
        const data = await response.json();
        setStats(data.realized);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching win/loss stats:', error);
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="border-primary/30 bg-card/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg text-primary">Win/Loss Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground">Loading...</div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return null;
  }

  const totalTrades = stats.wins + stats.losses;
  const winPercentage = totalTrades > 0 ? (stats.wins / totalTrades) * 100 : 0;

  return (
    <Card className="border-primary/30 bg-card/80 backdrop-blur-sm hover:border-primary/50 transition-all">
      <CardHeader>
        <CardTitle className="text-lg text-primary flex items-center gap-2">
          Win/Loss Breakdown
          <span className="text-sm text-muted-foreground font-normal">
            ({totalTrades} total trades)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-success/10 border border-success/30 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Wins</span>
              <TrendingUp className="w-4 h-4 text-success" />
            </div>
            <p className="text-3xl font-bold text-success">{stats.wins}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {winPercentage.toFixed(1)}% of trades
            </p>
          </div>

          <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Losses</span>
              <TrendingDown className="w-4 h-4 text-destructive" />
            </div>
            <p className="text-3xl font-bold text-destructive">{stats.losses}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {(100 - winPercentage).toFixed(1)}% of trades
            </p>
          </div>
        </div>

        <div className="pt-4 border-t border-border/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Win Rate</span>
            <span className="text-lg font-bold text-primary">{stats.win_rate?.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-muted/30 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-success to-success/80 h-full transition-all duration-500"
              style={{ width: `${stats.win_rate}%` }}
            />
          </div>
        </div>

        <div className="pt-2 border-t border-border/50">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Total P&L</span>
            <span className={`text-lg font-bold ${stats.total_pnl_usd >= 0 ? 'text-success' : 'text-destructive'}`}>
              ${stats.total_pnl_usd?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
