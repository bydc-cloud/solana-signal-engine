import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Activity, Target, Clock } from "lucide-react";
import { api } from "@/lib/api";

export default function PnlDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['pnl-summary'],
    queryFn: () => api.getPnlSummary(),
    refetchInterval: 30000, // Refresh every 30s
  });

  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }
    return `${hours}h`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="text-center text-muted-foreground py-8">Loading PnL data...</div>
      </div>
    );
  }

  const realized = data?.realized || {};
  const unrealized = data?.unrealized || {};
  const paperEquity = data?.paper_equity || {};

  return (
    <div className="min-h-screen bg-background p-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-gradient-primary">PnL Dashboard</h1>
        <p className="text-muted-foreground">Comprehensive profit & loss breakdown</p>
      </header>

      {/* Paper Equity Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="backdrop-blur-glass border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Equity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{formatCurrency(paperEquity.total_usd || 0)}</div>
          </CardContent>
        </Card>

        <Card className="backdrop-blur-glass border-success/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Realized PnL</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-success">{formatCurrency(paperEquity.realized_pnl || 0)}</div>
          </CardContent>
        </Card>

        <Card className="backdrop-blur-glass border-warning/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Unrealized PnL</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${(paperEquity.unrealized_pnl || 0) >= 0 ? 'text-success' : 'text-destructive'}`}>
              {formatCurrency(paperEquity.unrealized_pnl || 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Realized Performance */}
      <Card className="backdrop-blur-glass border-primary/20 mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Realized Performance
          </CardTitle>
          <CardDescription>Closed trades statistics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Total Trades</p>
              <p className="text-2xl font-bold">{realized.total_trades || 0}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Win Rate</p>
              <div className="flex items-center gap-2">
                <p className="text-2xl font-bold">{(realized.win_rate || 0).toFixed(1)}%</p>
                <Badge variant="default" className="bg-success">
                  {realized.wins || 0}W - {realized.losses || 0}L
                </Badge>
              </div>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Total PnL</p>
              <p className={`text-2xl font-bold ${(realized.total_pnl_usd || 0) >= 0 ? 'text-success' : 'text-destructive'}`}>
                {formatCurrency(realized.total_pnl_usd || 0)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Avg PnL</p>
              <p className={`text-2xl font-bold ${(realized.avg_pnl_usd || 0) >= 0 ? 'text-success' : 'text-destructive'}`}>
                {formatCurrency(realized.avg_pnl_usd || 0)}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 pt-6 border-t">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-8 h-8 text-success" />
              <div>
                <p className="text-xs text-muted-foreground">Best Trade</p>
                <p className="text-lg font-bold text-success">{formatCurrency(realized.best_trade_usd || 0)}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <TrendingDown className="w-8 h-8 text-destructive" />
              <div>
                <p className="text-xs text-muted-foreground">Worst Trade</p>
                <p className="text-lg font-bold text-destructive">{formatCurrency(realized.worst_trade_usd || 0)}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Clock className="w-8 h-8 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Avg Hold Time</p>
                <p className="text-lg font-bold">{formatTime(realized.avg_holding_time_minutes || 0)}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Unrealized Positions */}
      <Card className="backdrop-blur-glass border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Active Positions
          </CardTitle>
          <CardDescription>Current open trades</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Active Positions</p>
              <p className="text-2xl font-bold">{unrealized.active_positions || 0}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Total Exposure</p>
              <p className="text-2xl font-bold">{formatCurrency(unrealized.total_exposure_usd || 0)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Unrealized PnL</p>
              <p className={`text-2xl font-bold ${(unrealized.total_pnl_usd || 0) >= 0 ? 'text-success' : 'text-destructive'}`}>
                {formatCurrency(unrealized.total_pnl_usd || 0)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
