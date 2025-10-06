import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { api } from "@/lib/api";
import { Copy, ExternalLink, Activity } from "lucide-react";
import { toast } from "sonner";
import { TokenLogo } from "@/components/TokenLogo";

export default function TierSignals() {
  const [signalType, setSignalType] = useState<string>("all");
  const [sortField, setSortField] = useState<string>("timestamp");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  
  const { data: status } = useQuery({
    queryKey: ["status"],
    queryFn: api.getStatus,
    refetchInterval: 10000,
  });

  const { data: tiers, isLoading: tiersLoading } = useQuery({
    queryKey: ["tiers"],
    queryFn: api.getTiers,
    refetchInterval: 30000,
  });

  const { data: signals, isLoading: signalsLoading } = useQuery({
    queryKey: ["recent_signals", signalType],
    queryFn: () => api.getRecentSignals(20, signalType !== "all" ? signalType : undefined),
    refetchInterval: 30000,
  });

  const getMomentumColor = (score: number) => {
    if (score > 20) return "text-success";
    if (score >= 10) return "text-warning";
    return "text-destructive";
  };

  const getRiskColor = (score: number) => {
    if (score > 70) return "text-destructive";
    if (score >= 40) return "text-warning";
    return "text-success";
  };

  const getGsColor = (score: number) => {
    if (score > 70) return "text-success";
    if (score >= 40) return "text-warning";
    return "text-destructive";
  };

  const getWinRateColor = (rate: number) => {
    if (rate >= 70) return "text-success";
    if (rate >= 60) return "text-warning";
    return "text-destructive";
  };

  const formatMarketCap = (cap: number) => {
    if (cap >= 1000000) return `$${(cap / 1000000).toFixed(1)}M`;
    if (cap >= 1000) return `$${(cap / 1000).toFixed(1)}k`;
    return `$${cap}`;
  };

  const formatTimeAgo = (timestamp: string) => {
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return `${Math.floor(seconds / 3600)}h ago`;
  };

  const copyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
    toast.success("Address copied!");
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const sortedSignals = [...(signals?.signals || [])].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];
    
    if (sortField === "timestamp" || sortField === "created_at") {
      aVal = new Date(aVal || a.created_at || a.timestamp).getTime();
      bVal = new Date(bVal || b.created_at || b.timestamp).getTime();
    }
    
    if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return <span className="text-muted-foreground/30 ml-1">↕</span>;
    return <span className="text-primary ml-1">{sortDirection === "asc" ? "↑" : "↓"}</span>;
  };

  const tierConfigs = [
    { 
      id: 1, 
      name: "Pre-Graduation", 
      range: "$30k-$70k", 
      icon: "🌱",
      color: "warning",
      description: "Early momentum"
    },
    { 
      id: 2, 
      name: "Graduation Zone", 
      range: "$70k-$150k", 
      icon: "🚀",
      color: "primary",
      description: "Strong signals"
    },
    { 
      id: 3, 
      name: "Established", 
      range: "$150k-$500k", 
      icon: "💎",
      color: "accent",
      description: "Proven performers"
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <LatencyIndicator />
      
      {/* Database Initialization Banner */}
      {status && !status.database_initialized && (
        <div className="bg-warning/10 border-b border-warning/20 px-6 py-3 backdrop-blur-glass">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-warning animate-pulse" />
            <div>
              <p className="text-sm font-medium text-warning">Scanner Initializing Database</p>
              <p className="text-xs text-muted-foreground">
                The scanner is running and initializing the database. Signals will appear once initialization is complete (usually 1-2 minutes).
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="p-8 border-b border-border/50 bg-card/30 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gradient-primary mb-2">Market Tiers</h1>
            <p className="text-muted-foreground">Real-time signal monitoring across market cap tiers</p>
          </div>
          <div className="flex items-center gap-3 px-5 py-2.5 rounded-lg bg-primary/10 border border-primary/30">
            <div className="w-2.5 h-2.5 bg-primary rounded-full" />
            <span className="text-sm font-semibold text-primary">
              {status?.database_initialized ? 'LIVE' : 'INITIALIZING'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-8 space-y-8">
        {/* Tier Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tierConfigs.map(({ id, name, range, icon }) => {
            const tierData = tiers?.tiers?.find((t: any) => t.tier === id);
            return (
              <Card key={id} className="border-primary/30 bg-card/80 backdrop-blur-sm hover:border-primary/50 transition-all">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-3xl p-2 rounded-lg bg-primary/10">{icon}</div>
                      <div>
                        <CardTitle className="text-lg text-primary">{name}</CardTitle>
                        <p className="text-xs text-muted-foreground">{range}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-primary">{tierData?.signals_24h || 0}</div>
                      <div className="text-xs text-muted-foreground">signals</div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Avg Graduation</span>
                      <span className={`font-semibold ${getGsColor(tierData?.avg_gs || 0)}`}>
                        {tierData?.avg_gs?.toFixed(0) || 0}
                      </span>
                    </div>
                    <Progress value={tierData?.avg_gs || 0} className="h-2" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Avg Momentum</span>
                      <span className={`font-semibold ${getMomentumColor(tierData?.avg_momentum || 0)}`}>
                        {tierData?.avg_momentum?.toFixed(0) || 0}
                      </span>
                    </div>
                    <Progress value={tierData?.avg_momentum || 0} className="h-2" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Avg Risk</span>
                      <span className={`font-semibold ${getRiskColor(tierData?.avg_risk || 0)}`}>
                        {tierData?.avg_risk?.toFixed(0) || 0}
                      </span>
                    </div>
                    <Progress value={tierData?.avg_risk || 0} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Recent Signals Table */}
        <Card className="border-primary/30 bg-card/80 backdrop-blur-sm">
          <CardHeader className="border-b border-border/50">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl text-primary">Recent Signals</CardTitle>
                <p className="text-sm text-muted-foreground">Latest trading opportunities</p>
              </div>
              <Tabs value={signalType} onValueChange={setSignalType}>
                <TabsList className="bg-primary/10">
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="token">Token</TabsTrigger>
                  <TabsTrigger value="wallet">Wallet</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {signalsLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4" />
                <p className="text-muted-foreground">Loading signals...</p>
              </div>
            ) : !signals?.signals || signals.signals.length === 0 ? (
              <div className="text-center py-16 px-6">
                <Activity className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-xl font-semibold mb-2">No Signals Yet</h3>
                <p className="text-muted-foreground mb-4 max-w-md mx-auto">
                  The Railway scanner is running but hasn't generated any signals yet. 
                  {tiers?.total_signals === 0 && " The database is still initializing."}
                </p>
                <div className="flex flex-col gap-2 text-sm text-muted-foreground">
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span>Scanner Status: Running</span>
                  </div>
                  <p>Signals will appear here once the scanner completes initialization and starts detecting opportunities.</p>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent border-border/50">
                      <TableHead 
                        className="text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                        onClick={() => handleSort("symbol")}
                      >
                        <div className="flex items-center">Symbol <SortIcon field="symbol" /></div>
                      </TableHead>
                      <TableHead 
                        className="text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                        onClick={() => handleSort("tier")}
                      >
                        <div className="flex items-center">Tier <SortIcon field="tier" /></div>
                      </TableHead>
                      <TableHead 
                        className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                        onClick={() => handleSort("market_cap")}
                      >
                        <div className="flex items-center justify-end">Market Cap <SortIcon field="market_cap" /></div>
                      </TableHead>
                      {signalType !== 'wallet' && (
                        <>
                          <TableHead 
                            className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                            onClick={() => handleSort("momentum")}
                          >
                            <div className="flex items-center justify-end">Momentum <SortIcon field="momentum" /></div>
                          </TableHead>
                          <TableHead 
                            className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                            onClick={() => handleSort("risk")}
                          >
                            <div className="flex items-center justify-end">Risk <SortIcon field="risk" /></div>
                          </TableHead>
                          <TableHead 
                            className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                            onClick={() => handleSort("gs")}
                          >
                            <div className="flex items-center justify-end">GS <SortIcon field="gs" /></div>
                          </TableHead>
                        </>
                      )}
                      {signalType === 'wallet' && (
                        <>
                          <TableHead 
                            className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                            onClick={() => handleSort("win_rate")}
                          >
                            <div className="flex items-center justify-end">Win Rate <SortIcon field="win_rate" /></div>
                          </TableHead>
                          <TableHead 
                            className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                            onClick={() => handleSort("total_pnl_usd")}
                          >
                            <div className="flex items-center justify-end">Total PnL <SortIcon field="total_pnl_usd" /></div>
                          </TableHead>
                          <TableHead 
                            className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                            onClick={() => handleSort("performance_score")}
                          >
                            <div className="flex items-center justify-end">Score <SortIcon field="performance_score" /></div>
                          </TableHead>
                        </>
                      )}
                      <TableHead 
                        className="text-right text-primary cursor-pointer hover:text-primary/80 transition-colors select-none"
                        onClick={() => handleSort("timestamp")}
                      >
                        <div className="flex items-center justify-end">Time <SortIcon field="timestamp" /></div>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedSignals?.map((signal: any, idx: number) => (
                      <TableRow key={idx} className="hover:bg-primary/5 border-border/30 transition-colors">
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <TokenLogo 
                              address={signal.address} 
                              symbol={signal.symbol || signal.wallet_label} 
                              size="sm" 
                            />
                            <div className="flex items-center gap-2">
                              <a
                                href={`https://solscan.io/${signalType === 'wallet' ? 'account' : 'token'}/${signal.address}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-semibold hover:text-primary transition-colors"
                              >
                                {signal.symbol || signal.wallet_label || 'Unknown'}
                              </a>
                              <button
                                onClick={() => copyAddress(signal.address)}
                                className="text-muted-foreground hover:text-foreground transition-colors"
                                title="Copy address"
                              >
                                <Copy className="w-3 h-3" />
                              </button>
                              {signalType !== 'wallet' && (
                                <a
                                  href={`https://birdeye.so/token/${signal.address}?chain=solana`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary/80 transition-colors"
                                  title="View on Birdeye"
                                >
                                  <ExternalLink className="w-3 h-3" />
                                </a>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="secondary" 
                            className="font-semibold bg-primary/15 text-primary border-primary/30"
                          >
                            {signal.tier === 1 ? 'T1 🌱' : signal.tier === 2 ? 'T2 🚀' : signal.tier === 3 ? 'T3 💎' : 'N/A'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {formatMarketCap(signal.market_cap)}
                        </TableCell>
                        {signalType !== 'wallet' && (
                          <>
                            <TableCell className="text-right">
                              <span className={`font-bold ${getMomentumColor(signal.momentum || 0)}`}>
                                {signal.momentum?.toFixed(0) || 0}
                              </span>
                            </TableCell>
                            <TableCell className="text-right">
                              <span className={`font-bold ${getRiskColor(signal.risk || 0)}`}>
                                {signal.risk?.toFixed(0) || 0}
                              </span>
                            </TableCell>
                            <TableCell className="text-right">
                              <span className={`font-bold ${getGsColor(signal.gs || 0)}`}>
                                {signal.gs?.toFixed(0) || 0}
                              </span>
                            </TableCell>
                          </>
                        )}
                        {signalType === 'wallet' && (
                          <>
                            <TableCell className="text-right">
                              <span className={`font-bold ${getWinRateColor(signal.win_rate || 0)}`}>
                                {signal.win_rate?.toFixed(1) || 0}%
                              </span>
                            </TableCell>
                            <TableCell className="text-right">
                              <span className={`font-bold ${signal.total_pnl_usd >= 0 ? 'text-success' : 'text-destructive'}`}>
                                ${signal.total_pnl_usd?.toLocaleString() || 0}
                              </span>
                            </TableCell>
                            <TableCell className="text-right">
                              <span className="font-bold">
                                {signal.performance_score?.toFixed(0) || 0}
                              </span>
                            </TableCell>
                          </>
                        )}
                        <TableCell className="text-right text-xs text-muted-foreground">
                          {formatTimeAgo(signal.timestamp || signal.created_at)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}