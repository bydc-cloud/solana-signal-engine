import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TrendingUp, Target, AlertTriangle, Zap, Activity, Shield } from "lucide-react";
import { TokenLogo } from "@/components/TokenLogo";

interface SignalFactor {
  name: string;
  score: number;
  maxScore: number;
  icon: any;
  status: "excellent" | "good" | "weak" | "poor";
}

interface ConfluenceSignal {
  symbol: string;
  address: string;
  totalScore: number;
  factors: SignalFactor[];
  momentum: number;
  smartMoney: number;
  cvd: number;
  holderQuality: number;
  volume: number;
  riskScore: number;
  timestamp: string;
  marketCap?: number;
  price?: number;
}

export default function SignalConfluence() {
  const [signals, setSignals] = useState<ConfluenceSignal[]>([]);
  const [filter, setFilter] = useState<"all" | "perfect" | "strong">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchSignals = async () => {
    try {
      const response = await fetch(
        "https://signal-railway-deployment-production.up.railway.app/trading/signals?hours=24&limit=50"
      );
      const data = await response.json();
      
      const processedSignals = data.signals?.map((signal: any) => 
        calculateConfluenceScore(signal)
      ) || [];
      
      setSignals(processedSignals.sort((a, b) => b.totalScore - a.totalScore));
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch signals:", error);
      setLoading(false);
    }
  };

  const calculateConfluenceScore = (signal: any): ConfluenceSignal => {
    // Factor 1: Momentum Score (0-20 points)
    const momentumScore = Math.min(20, (signal.momentum_score || 0) * 0.2);
    const momentumStatus = momentumScore >= 15 ? "excellent" : momentumScore >= 10 ? "good" : momentumScore >= 5 ? "weak" : "poor";

    // Factor 2: Smart Money Activity (0-25 points)
    const smartMoneyCount = signal.smart_money_count || 0;
    const smartMoneyScore = Math.min(25, smartMoneyCount >= 3 ? 25 : smartMoneyCount >= 2 ? 20 : smartMoneyCount >= 1 ? 12 : 0);
    const smartMoneyStatus = smartMoneyScore >= 20 ? "excellent" : smartMoneyScore >= 12 ? "good" : smartMoneyScore >= 5 ? "weak" : "poor";

    // Factor 3: CVD (Buy-Sell Pressure) (0-15 points)
    const cvdRatio = signal.buy_sell_ratio || 1;
    const cvdScore = cvdRatio > 2 ? 15 : cvdRatio > 1.5 ? 12 : cvdRatio > 1 ? 8 : 0;
    const cvdStatus = cvdScore >= 12 ? "excellent" : cvdScore >= 8 ? "good" : cvdScore >= 4 ? "weak" : "poor";

    // Factor 4: Holder Quality (0-10 points)
    const holderScore = signal.holder_concentration_improving ? 10 : signal.holder_count > 100 ? 6 : 3;
    const holderStatus = holderScore >= 8 ? "excellent" : holderScore >= 6 ? "good" : holderScore >= 3 ? "weak" : "poor";

    // Factor 5: Volume Surge (0-15 points)
    const volumeMultiplier = signal.volume_24h_change_pct || 0;
    const volumeScore = volumeMultiplier > 300 ? 15 : volumeMultiplier > 200 ? 12 : volumeMultiplier > 100 ? 8 : volumeMultiplier > 50 ? 5 : 0;
    const volumeStatus = volumeScore >= 12 ? "excellent" : volumeScore >= 8 ? "good" : volumeScore >= 4 ? "weak" : "poor";

    // Factor 6: Risk Score (0-15 points) - Lower risk = higher score
    const riskValue = signal.risk_score || 100;
    const riskScore = riskValue < 30 ? 15 : riskValue < 40 ? 12 : riskValue < 60 ? 8 : riskValue < 80 ? 5 : 0;
    const riskStatus = riskScore >= 12 ? "excellent" : riskScore >= 8 ? "good" : riskScore >= 4 ? "weak" : "poor";

    const totalScore = Math.round(momentumScore + smartMoneyScore + cvdScore + holderScore + volumeScore + riskScore);

    return {
      symbol: signal.symbol || signal.token_symbol || "UNKNOWN",
      address: signal.token_address || signal.address || "",
      totalScore,
      factors: [
        { name: "Momentum", score: momentumScore, maxScore: 20, icon: TrendingUp, status: momentumStatus },
        { name: "Smart Money", score: smartMoneyScore, maxScore: 25, icon: Target, status: smartMoneyStatus },
        { name: "Buy Pressure", score: cvdScore, maxScore: 15, icon: Zap, status: cvdStatus },
        { name: "Holder Quality", score: holderScore, maxScore: 10, icon: Activity, status: holderStatus },
        { name: "Volume Surge", score: volumeScore, maxScore: 15, icon: TrendingUp, status: volumeStatus },
        { name: "Risk Level", score: riskScore, maxScore: 15, icon: Shield, status: riskStatus },
      ],
      momentum: signal.momentum_score || 0,
      smartMoney: smartMoneyCount,
      cvd: cvdRatio,
      holderQuality: holderScore,
      volume: volumeMultiplier,
      riskScore: riskValue,
      timestamp: signal.timestamp || new Date().toISOString(),
      marketCap: signal.market_cap,
      price: signal.price,
    };
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-success";
    if (score >= 60) return "text-info";
    if (score >= 40) return "text-warning";
    return "text-destructive";
  };

  const getScoreBadge = (score: number) => {
    if (score >= 80) return { label: "PERFECT SETUP", variant: "default" as const, className: "bg-success text-success-foreground" };
    if (score >= 60) return { label: "STRONG", variant: "default" as const, className: "bg-info text-info-foreground" };
    if (score >= 40) return { label: "MODERATE", variant: "default" as const, className: "bg-warning text-warning-foreground" };
    return { label: "WEAK", variant: "destructive" as const };
  };

  const getFactorColor = (status: string) => {
    switch (status) {
      case "excellent": return "text-success";
      case "good": return "text-info";
      case "weak": return "text-warning";
      default: return "text-muted-foreground";
    }
  };

  const filteredSignals = signals.filter(signal => {
    if (filter === "perfect") return signal.totalScore >= 80;
    if (filter === "strong") return signal.totalScore >= 60;
    return true;
  });

  const stats = {
    perfect: signals.filter(s => s.totalScore >= 80).length,
    strong: signals.filter(s => s.totalScore >= 60).length,
    total: signals.length,
    avgScore: signals.length > 0 ? Math.round(signals.reduce((sum, s) => sum + s.totalScore, 0) / signals.length) : 0,
  };

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-primary text-xl font-black font-mono">&gt;</span>
          <h1 className="text-2xl font-black font-mono uppercase tracking-wider text-foreground">
            [signal_confluence_engine]
          </h1>
        </div>
        <p className="text-xs text-muted-foreground font-mono tracking-wide ml-8">
          multi-factor alignment scoring system // 6-dimensional signal analysis
        </p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-border bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1">[Perfect Setups]</p>
                <p className="text-2xl font-black font-mono text-success">{stats.perfect}</p>
              </div>
              <Target className="w-8 h-8 text-success opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-border bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1">[Strong Signals]</p>
                <p className="text-2xl font-black font-mono text-info">{stats.strong}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-info opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-border bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1">[Total Signals]</p>
                <p className="text-2xl font-black font-mono text-foreground">{stats.total}</p>
              </div>
              <Activity className="w-8 h-8 text-primary opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-border bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1">[Avg Score]</p>
                <p className={`text-2xl font-black font-mono ${getScoreColor(stats.avgScore)}`}>{stats.avgScore}/100</p>
              </div>
              <Zap className="w-8 h-8 text-primary opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Tabs value={filter} onValueChange={(v) => setFilter(v as any)} className="mb-6">
        <TabsList className="bg-card border border-border">
          <TabsTrigger value="all" className="font-mono text-xs uppercase">
            All Signals ({signals.length})
          </TabsTrigger>
          <TabsTrigger value="strong" className="font-mono text-xs uppercase">
            Strong (≥60) ({signals.filter(s => s.totalScore >= 60).length})
          </TabsTrigger>
          <TabsTrigger value="perfect" className="font-mono text-xs uppercase">
            Perfect (≥80) ({signals.filter(s => s.totalScore >= 80).length})
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Signals Grid */}
      {loading ? (
        <Card className="border-border bg-card/50">
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground font-mono">Loading confluence data...</p>
          </CardContent>
        </Card>
      ) : filteredSignals.length === 0 ? (
        <Card className="border-border bg-card/50">
          <CardContent className="p-12 text-center">
            <AlertTriangle className="w-12 h-12 text-warning mx-auto mb-4 opacity-50" />
            <p className="text-muted-foreground font-mono">No signals match current filter</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredSignals.map((signal, idx) => (
            <Card key={`${signal.address}-${idx}`} className="border-border bg-card/50 backdrop-blur-sm hover:bg-card/70 transition-all">
              <CardContent className="p-6">
                <div className="flex items-start gap-6">
                  {/* Left: Token Info */}
                  <div className="flex-shrink-0">
                    <TokenLogo address={signal.address} symbol={signal.symbol} className="w-16 h-16 mb-2" />
                    <div className="text-center">
                      <p className="font-black font-mono text-lg text-foreground">{signal.symbol}</p>
                      <p className="text-xs text-muted-foreground font-mono">
                        {signal.address.slice(0, 4)}...{signal.address.slice(-4)}
                      </p>
                    </div>
                  </div>

                  {/* Center: Score Visualization */}
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-4">
                      <div>
                        <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1">Confluence Score</p>
                        <div className="flex items-baseline gap-2">
                          <span className={`text-4xl font-black font-mono ${getScoreColor(signal.totalScore)}`}>
                            {signal.totalScore}
                          </span>
                          <span className="text-lg text-muted-foreground font-mono">/100</span>
                        </div>
                      </div>
                      <div className="ml-auto">
                        <Badge {...getScoreBadge(signal.totalScore)} className="font-mono text-xs">
                          {getScoreBadge(signal.totalScore).label}
                        </Badge>
                      </div>
                    </div>

                    {/* Factor Breakdown */}
                    <div className="grid grid-cols-3 gap-4">
                      {signal.factors.map((factor, factorIdx) => {
                        const Icon = factor.icon;
                        const percentage = (factor.score / factor.maxScore) * 100;
                        return (
                          <div key={factorIdx} className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Icon className={`w-3 h-3 ${getFactorColor(factor.status)}`} />
                              <span className="text-xs font-mono text-muted-foreground">{factor.name}</span>
                            </div>
                            <div className="space-y-1">
                              <Progress value={percentage} className="h-1.5" />
                              <div className="flex items-center justify-between">
                                <span className={`text-xs font-mono font-bold ${getFactorColor(factor.status)}`}>
                                  {Math.round(factor.score)}/{factor.maxScore}
                                </span>
                                <span className={`text-[10px] font-mono uppercase tracking-wider ${getFactorColor(factor.status)}`}>
                                  {factor.status}
                                </span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Right: Actions */}
                  <div className="flex-shrink-0 flex flex-col gap-2">
                    <Button 
                      size="sm" 
                      className="font-mono text-xs uppercase"
                      onClick={() => window.open(`https://dexscreener.com/solana/${signal.address}`, '_blank')}
                    >
                      View Chart
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="font-mono text-xs uppercase"
                      onClick={() => navigator.clipboard.writeText(signal.address)}
                    >
                      Copy CA
                    </Button>
                  </div>
                </div>

                {/* Timestamp */}
                <div className="mt-4 pt-4 border-t border-border">
                  <p className="text-[10px] text-muted-foreground font-mono">
                    Signal detected: {new Date(signal.timestamp).toLocaleString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
