import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { WalletDiscoveryBanner } from "@/components/WalletDiscoveryBanner";
import { WinLossChart } from "@/components/WinLossChart";
import { ActivePositionsWidget } from "@/components/ActivePositionsWidget";
import { SmartWalletsWidget } from "@/components/SmartWalletsWidget";
import { SentimentWidget } from "@/components/SentimentWidget";
import { QuickStatsWidget } from "@/components/QuickStatsWidget";
import { LiveActivityFeed } from "@/components/LiveActivityFeed";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { useHelixBot } from "@/hooks/useHelixBot";
import { Play, Square, RotateCw, Activity, DollarSign, TrendingUp, TrendingDown, Radio, Target, Layers, Wallet, FileText, BarChart3, Zap, Clock } from "lucide-react";

interface Status {
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

export default function Dashboard() {
  const { status, pnl, positions: positionsData, loading } = useHelixBot();

  const handleScannerAction = async (action: "start" | "stop" | "restart") => {
    try {
      let result;
      if (action === "start") result = await api.startScanner();
      else if (action === "stop") result = await api.stopScanner();
      else result = await api.restartScanner();

      toast({
        title: `Scanner ${action}ed`,
        description: result.message || `Successfully ${action}ed the scanner`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to ${action} scanner`,
        variant: "destructive",
      });
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value);
  };

  const formatRelativeTime = (timestamp: string) => {
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const quickAccessCards = [
    {
      title: "Signal Confluence",
      description: "Multi-factor alignment scoring",
      icon: Zap,
      href: "/confluence",
      stats: "6 factors",
    },
    {
      title: "Time Analysis",
      description: "Hourly performance heatmap",
      icon: Clock,
      href: "/time-analysis",
      stats: "24/7 tracking",
    },
    {
      title: "Exit Strategy",
      description: "Automated take profit ladders",
      icon: Target,
      href: "/exit-strategy",
      stats: "Smart exits",
    },
    {
      title: "Twitter Signals",
      description: "Market sentiment & social signals",
      icon: Radio,
      href: "/twitter",
      stats: `${status?.stats_24h?.alerts || 0} signals`,
    },
    {
      title: "Active Positions",
      description: "Live trading positions & P&L",
      icon: Target,
      href: "/positions",
      stats: `${positionsData?.length || 0} open`,
    },
    {
      title: "Tier Signals",
      description: "Market cap tier analysis",
      icon: Layers,
      href: "/tiers",
      stats: "3 tiers",
    },
    {
      title: "Smart Wallets",
      description: "Top performer tracking",
      icon: Wallet,
      href: "/wallets",
      stats: "Smart money",
    },
    {
      title: "Analytics",
      description: "Performance metrics & insights",
      icon: BarChart3,
      href: "/analytics",
      stats: "Deep dive",
    },
  ];

  return (
    <div className="min-h-screen p-8 space-y-8">
      <LatencyIndicator />
      
      {/* Matrix Dashboard Header */}
      <div className="relative border border-border bg-card/50 backdrop-blur-sm p-3">
        <div className="flex items-center justify-between gap-8">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-primary font-mono text-sm">&gt;</span>
              <h1 className="text-base font-black font-mono text-foreground tracking-widest leading-none uppercase">
                MATRIX_DASHBOARD
              </h1>
            </div>
            <p className="text-muted-foreground text-[9px] font-mono font-bold pl-4 lowercase tracking-wider">
              [real-time trading intelligence system]
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-2 py-1 bg-card border border-border">
              <div className={`w-1.5 h-1.5 ${
                status?.scanner_running && status?.database_initialized 
                  ? 'bg-success' 
                  : 'bg-warning'
              }`} />
              <span className={`text-[9px] font-extrabold font-mono uppercase tracking-wider ${
                status?.scanner_running && status?.database_initialized ? 'text-success' : 'text-warning'
              }`}>
                [{status?.scanner_running && status?.database_initialized ? 'OPERATIONAL' : 'STANDBY'}]
              </span>
            </div>
            <Badge variant="outline" className="font-mono text-[9px] font-extrabold tracking-wider border-primary/50 text-primary">
              {status?.mode || 'PAPER'}
            </Badge>
          </div>
        </div>
      </div>

      <WalletDiscoveryBanner />

      {/* System Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="relative overflow-hidden p-6 border-border hover:border-primary/40 transition-all duration-300 group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <div className="relative flex items-center gap-4">
            <div className={`p-3 rounded-xl transition-all duration-300 ${
              status?.scanner_running && status?.database_initialized 
                ? 'bg-success/10 group-hover:bg-success/15' 
                : status?.scanner_running 
                ? 'bg-warning/10 group-hover:bg-warning/15' 
                : 'bg-destructive/10 group-hover:bg-destructive/15'
            }`}>
              <Activity className={`w-6 h-6 transition-transform duration-300 group-hover:scale-110 ${
                status?.scanner_running && status?.database_initialized 
                  ? 'text-success' 
                  : status?.scanner_running 
                  ? 'text-warning' 
                  : 'text-destructive'
              }`} />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1 font-medium">Scanner</p>
              <p className="text-lg font-bold font-mono">
                {status?.scanner_running && status?.database_initialized ? "ACTIVE" : status?.scanner_running ? "INIT" : "OFFLINE"}
              </p>
            </div>
          </div>
        </Card>

        <Card className="relative overflow-hidden p-6 border-border hover:border-primary/40 transition-all duration-300 group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <div className="relative flex items-center gap-4">
            <div className="p-3 rounded-xl bg-primary/10 group-hover:bg-primary/15 transition-all duration-300">
              <DollarSign className="w-6 h-6 text-primary transition-transform duration-300 group-hover:scale-110" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1 font-medium">Trading Mode</p>
              <Badge variant="outline" className="font-mono font-semibold">
                {status?.mode || "PAPER"}
              </Badge>
            </div>
          </div>
        </Card>

        <Card className="relative overflow-hidden p-6 border-border hover:border-primary/40 transition-all duration-300 group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <div className="relative flex items-center gap-4">
            <div className="p-3 rounded-xl bg-info/10 group-hover:bg-info/15 transition-all duration-300">
              <Activity className="w-6 h-6 text-info transition-transform duration-300 group-hover:scale-110" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1 font-medium">Last Sync</p>
              <p className="text-lg font-bold font-mono">
                {status?.timestamp ? formatRelativeTime(status.timestamp) : "N/A"}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Portfolio Overview */}
      <Card className="relative overflow-hidden p-8 border-border bg-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-2 mb-8">
          <span className="text-primary">&gt;</span>
          <h2 className="text-xs font-black font-mono text-foreground tracking-widest uppercase leading-none">[portfolio_overview]</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground font-mono uppercase tracking-wider font-medium">Total Equity</p>
            <p className="text-4xl font-bold font-mono text-gradient-primary tabular-nums">{formatCurrency(pnl?.total_equity || 0)}</p>
          </div>
          
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground font-mono uppercase tracking-wider font-medium">Total P&L</p>
            <p className={`text-4xl font-bold font-mono tabular-nums ${(pnl?.total_pnl || 0) >= 0 ? "text-success" : "text-destructive"}`}>
              {formatCurrency(pnl?.total_pnl || 0)}
            </p>
            <Badge variant={(pnl?.total_roi_percent || 0) >= 0 ? "default" : "destructive"} className="font-mono text-xs font-semibold mt-2">
              {(pnl?.total_roi_percent || 0).toFixed(2)}% ROI
            </Badge>
          </div>
          
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground font-mono uppercase tracking-wider font-medium flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Realized
            </p>
            <p className={`text-4xl font-bold font-mono tabular-nums ${(pnl?.realized_pnl || 0) >= 0 ? "text-success" : "text-destructive"}`}>
              {formatCurrency(pnl?.realized_pnl || 0)}
            </p>
          </div>
          
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground font-mono uppercase tracking-wider font-medium flex items-center gap-2">
              <TrendingDown className="w-4 h-4" />
              Unrealized
            </p>
            <p className={`text-4xl font-bold font-mono tabular-nums ${(pnl?.unrealized_pnl || 0) >= 0 ? "text-success" : "text-destructive"}`}>
              {formatCurrency(pnl?.unrealized_pnl || 0)}
            </p>
          </div>
        </div>
      </Card>

      {/* 24H Metrics */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-primary">&gt;</span>
          <h2 className="text-xs font-black font-mono text-foreground tracking-widest uppercase leading-none">[24h_activity]</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <QuickStatsWidget
            title="Total Trades"
            value={status?.stats_24h?.trades || 0}
            subtitle="Executed"
            icon={TrendingUp}
            trend={{ value: 12.5, isPositive: true }}
          />
          <QuickStatsWidget
            title="Signal Alerts"
            value={status?.stats_24h?.alerts || 0}
            subtitle="Detected"
            icon={Target}
          />
          <QuickStatsWidget
            title="Active Positions"
            value={positionsData?.length || 0}
            subtitle="Open Trades"
            icon={Layers}
          />
          <QuickStatsWidget
            title="Win Rate"
            value={`${(pnl?.win_rate || 0).toFixed(0)}%`}
            subtitle="Success Rate"
            icon={Activity}
            trend={{ value: pnl?.win_rate || 0, isPositive: (pnl?.win_rate || 0) >= 50 }}
          />
        </div>
      </div>

      {/* Intelligence Widgets Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <SentimentWidget />
        <LiveActivityFeed />
        <div className="space-y-6">
          <QuickStatsWidget
            title="Best Signal Today"
            value="+247%"
            subtitle="$MATRIX Token"
            icon={Zap}
            className="h-fit"
          />
          <QuickStatsWidget
            title="Optimal Trading Time"
            value="14:00-17:00"
            subtitle="UTC Window"
            icon={Clock}
            className="h-fit"
          />
        </div>
      </div>

      {/* Intelligence Modules */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-primary">&gt;</span>
          <h2 className="text-xs font-black font-mono text-foreground tracking-widest uppercase leading-none">[intelligence_modules]</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickAccessCards.map((card) => {
            const IconComponent = card.icon;
            return (
              <Link key={card.href} to={card.href}>
                <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-200 cursor-pointer h-full border-border hover:border-primary/30 bg-card/50 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="p-3 rounded-lg bg-primary/10 group-hover:bg-primary/15 transition-colors">
                        <IconComponent className="w-6 h-6 text-primary" />
                      </div>
                      <Badge variant="secondary" className="font-mono text-xs">
                        {card.stats}
                      </Badge>
                    </div>
                    
                    <h3 className="text-base font-bold font-display text-foreground uppercase">
                      {card.title}
                    </h3>
                    
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {card.description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Performance Analytics */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-primary">&gt;</span>
          <h2 className="text-xs font-black font-mono text-foreground tracking-widest uppercase leading-none">[performance_analytics]</h2>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <WinLossChart />
          <ActivePositionsWidget />
        </div>
      </div>

      {/* Smart Money Wallets Section */}
      <SmartWalletsWidget />

      {/* System Controls */}
      <Card className="relative overflow-hidden p-8 border-border bg-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-primary">&gt;</span>
          <h2 className="text-xs font-black font-mono text-foreground tracking-widest uppercase leading-none">[system_controls]</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button
            onClick={() => handleScannerAction("start")}
            disabled={status?.scanner_running}
            variant="default"
            className="relative w-full h-12 text-xs font-bold font-mono uppercase tracking-wider bg-success hover:bg-success/90 text-background disabled:opacity-50 transition-all duration-300 border border-success"
          >
            <Play className="w-4 h-4 mr-2 relative z-10" />
            <span className="relative z-10">[START_SCANNER]</span>
          </Button>
          
          <Button
            onClick={() => handleScannerAction("stop")}
            disabled={!status?.scanner_running}
            variant="destructive"
            className="relative w-full h-12 text-xs font-bold font-mono uppercase tracking-wider disabled:opacity-50 transition-all duration-300 border border-destructive"
          >
            <Square className="w-4 h-4 mr-2 relative z-10" />
            <span className="relative z-10">[STOP_SCANNER]</span>
          </Button>
          
          <Button
            onClick={() => handleScannerAction("restart")}
            variant="outline"
            className="relative w-full h-12 text-xs font-bold font-mono uppercase tracking-wider border border-warning/40 text-warning hover:bg-warning/10 hover:border-warning/60 transition-all duration-300"
          >
            <RotateCw className="w-4 h-4 mr-2 relative z-10" />
            <span className="relative z-10">[RESTART]</span>
          </Button>
        </div>
      </Card>
    </div>
  );
}
