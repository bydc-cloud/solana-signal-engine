import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { api } from "@/lib/api";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar, ScatterChart, Scatter, ZAxis, Legend
} from "recharts";
import { TrendingUp, TrendingDown, Activity, PieChart as PieChartIcon, BarChart3, Sparkles } from "lucide-react";

export default function Analytics() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics"],
    queryFn: api.getPerformance,
    refetchInterval: 60000,
  });

  const { data: closedTrades } = useQuery({
    queryKey: ["closedTrades"],
    queryFn: () => api.getClosedTrades(168, 100),
    refetchInterval: 60000,
  });

  const { data: pnlSummary } = useQuery({
    queryKey: ["pnlSummary"],
    queryFn: api.getPnlSummary,
    refetchInterval: 30000,
  });

  const COLORS = {
    profit: "hsl(var(--success))",
    loss: "hsl(var(--destructive))",
    primary: "hsl(var(--primary))",
    secondary: "hsl(var(--secondary))",
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value);
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  // Prepare bubble chart data (trade performance scatter)
  const bubbleData = closedTrades?.trades?.map((trade: any) => ({
    holdTime: trade.holding_time_minutes || 0,
    pnl: trade.pnl_usd || 0,
    size: Math.abs(trade.pnl_usd || 1),
    symbol: trade.symbol,
  })) || [];

  // Prepare pie chart data (win/loss distribution)
  const pieData = [
    { name: "Wins", value: pnlSummary?.realized?.wins || 0, color: COLORS.profit },
    { name: "Losses", value: pnlSummary?.realized?.losses || 0, color: COLORS.loss },
  ];

  // Prepare cumulative P&L data
  const cumulativePnL = closedTrades?.trades?.reduce((acc: any[], trade: any, index: number) => {
    const prevTotal = index > 0 ? acc[index - 1].total : 0;
    return [...acc, {
      index: index + 1,
      total: prevTotal + (trade.pnl_usd || 0),
      pnl: trade.pnl_usd || 0,
    }];
  }, []) || [];

  // Custom label renderer for pie chart
  const renderPieLabel = (entry: any) => {
    const percent = entry.percent || 0;
    return `${entry.name}: ${entry.value} (${(percent * 100).toFixed(0)}%)`;
  };

  return (
    <div className="min-h-screen p-8 space-y-8 mesh-gradient">
      <LatencyIndicator />
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold text-gradient-primary mb-2 neon-text">Analytics</h1>
          <p className="text-muted-foreground text-lg">Performance metrics and insights</p>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 card-premium border-2 glow-green">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-success" />
            <p className="text-sm text-muted-foreground">Total Return</p>
          </div>
          <p className="text-3xl font-bold text-success">
            {data?.metrics?.total_return_pct >= 0 ? "+" : ""}
            {data?.metrics?.total_return_pct?.toFixed(2) || 0}%
          </p>
        </Card>

        <Card className="p-6 card-premium border-2 glow-cyan">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-primary" />
            <p className="text-sm text-muted-foreground">Realized P&L</p>
          </div>
          <p className={`text-3xl font-bold ${(data?.metrics?.realized_pnl || 0) >= 0 ? "text-success" : "text-destructive"}`}>
            {formatCurrency(data?.metrics?.realized_pnl || 0)}
          </p>
        </Card>

        <Card className="p-6 card-premium border-2 glow-purple">
          <div className="flex items-center gap-3 mb-2">
            <TrendingDown className="w-5 h-5 text-warning" />
            <p className="text-sm text-muted-foreground">Unrealized P&L</p>
          </div>
          <p className={`text-3xl font-bold ${(data?.metrics?.unrealized_pnl || 0) >= 0 ? "text-success" : "text-destructive"}`}>
            {formatCurrency(data?.metrics?.unrealized_pnl || 0)}
          </p>
        </Card>
      </div>

      {/* Equity Chart */}
      <Card className="card-premium p-6">
        <h2 className="text-xl font-bold mb-4">Equity History</h2>
        {isLoading ? (
          <div className="h-80 flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data?.equity_history || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatDate}
                stroke="hsl(var(--muted-foreground))"
              />
              <YAxis 
                tickFormatter={(value) => formatCurrency(value)}
                stroke="hsl(var(--muted-foreground))"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
                labelFormatter={(label) => new Date(label).toLocaleString()}
                formatter={(value: number) => [formatCurrency(value), "Equity"]}
              />
              <Line
                type="monotone"
                dataKey="equity_usd"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6, fill: "hsl(var(--primary))" }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* Cumulative P&L Chart */}
      <Card className="card-premium p-6">
        <div className="flex items-center gap-3 mb-4">
          <BarChart3 className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-bold">Cumulative P&L</h2>
        </div>
        {cumulativePnL.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={cumulativePnL}>
              <defs>
                <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                dataKey="index" 
                stroke="hsl(var(--muted-foreground))"
                label={{ value: 'Trade #', position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                tickFormatter={(value) => formatCurrency(value)}
                stroke="hsl(var(--muted-foreground))"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
                formatter={(value: number) => [formatCurrency(value), "Total P&L"]}
              />
              <Area
                type="monotone"
                dataKey="total"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorPnl)"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-80 flex items-center justify-center text-muted-foreground">
            No trade data available yet
          </div>
        )}
      </Card>

      {/* Win/Loss Distribution & Trade Performance Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Win/Loss Pie Chart */}
        <Card className="card-premium p-6">
          <div className="flex items-center gap-3 mb-4">
            <PieChartIcon className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">Win/Loss Distribution</h2>
          </div>
          {pieData[0].value + pieData[1].value > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderPieLabel}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-muted-foreground">
              No trades completed yet
            </div>
          )}
        </Card>

        {/* Performance Metrics Summary */}
        <Card className="card-premium p-6">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">Performance Summary</h2>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/20">
              <span className="text-muted-foreground">Win Rate</span>
              <span className="text-lg font-bold">{pnlSummary?.realized?.win_rate?.toFixed(1) || 0}%</span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/20">
              <span className="text-muted-foreground">Avg P&L per Trade</span>
              <span className={`text-lg font-bold ${(pnlSummary?.realized?.avg_pnl_usd || 0) >= 0 ? "text-success" : "text-destructive"}`}>
                {formatCurrency(pnlSummary?.realized?.avg_pnl_usd || 0)}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/20">
              <span className="text-muted-foreground">Best Trade</span>
              <span className="text-lg font-bold text-success">
                {formatCurrency(pnlSummary?.realized?.best_trade_usd || 0)}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/20">
              <span className="text-muted-foreground">Worst Trade</span>
              <span className="text-lg font-bold text-destructive">
                {formatCurrency(pnlSummary?.realized?.worst_trade_usd || 0)}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/20">
              <span className="text-muted-foreground">Avg Hold Time</span>
              <span className="text-lg font-bold">
                {pnlSummary?.realized?.avg_holding_time_minutes 
                  ? `${Math.floor(pnlSummary.realized.avg_holding_time_minutes / 60)}h ${Math.floor(pnlSummary.realized.avg_holding_time_minutes % 60)}m`
                  : "0m"}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Bubble Chart - Trade Performance Map */}
      <Card className="card-premium p-6">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-bold">Trade Performance Bubble Map</h2>
          <p className="text-sm text-muted-foreground ml-auto">Bubble size = P&L magnitude</p>
        </div>
        {bubbleData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                type="number" 
                dataKey="holdTime" 
                name="Hold Time"
                stroke="hsl(var(--muted-foreground))"
                label={{ value: 'Hold Time (minutes)', position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                type="number" 
                dataKey="pnl" 
                name="P&L"
                stroke="hsl(var(--muted-foreground))"
                tickFormatter={(value) => formatCurrency(value)}
                label={{ value: 'P&L (USD)', angle: -90, position: 'insideLeft' }}
              />
              <ZAxis type="number" dataKey="size" range={[50, 400]} name="Size" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
                formatter={(value: any, name: string) => {
                  if (name === "P&L") return [formatCurrency(value), name];
                  if (name === "Hold Time") return [`${value} min`, name];
                  return [value, name];
                }}
                labelFormatter={(_, payload) => payload?.[0]?.payload?.symbol || "Trade"}
              />
              <Legend />
              <Scatter 
                name="Profitable Trades" 
                data={bubbleData.filter((d: any) => d.pnl >= 0)} 
                fill={COLORS.profit}
                fillOpacity={0.6}
              />
              <Scatter 
                name="Loss Trades" 
                data={bubbleData.filter((d: any) => d.pnl < 0)} 
                fill={COLORS.loss}
                fillOpacity={0.6}
              />
            </ScatterChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-96 flex items-center justify-center text-muted-foreground">
            Trade bubble map will appear once you have closed positions
          </div>
        )}
      </Card>
    </div>
  );
}
