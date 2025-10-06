import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { useState, useMemo } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, TrendingUp, Wallet, Activity, BarChart3, ExternalLink, DollarSign, RefreshCw } from "lucide-react";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from "recharts";

export default function WalletDetail() {
  const { id } = useParams();
  const [pnlTimeFilter, setPnlTimeFilter] = useState<'1d' | '7d' | '30d' | 'all'>('7d');

  const { data: wallet, error: walletError, isLoading: walletLoading } = useQuery({
    queryKey: ['wallet-detail', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('tracked_wallets')
        .select('*')
        .eq('id', id)
        .maybeSingle();
      
      if (error) throw error;

      if (!data) return null;

      // Fetch live balance
      const { data: balanceData } = await supabase.functions.invoke('wallet-discovery', {
        body: { 
          action: 'get_wallet_balance',
          wallet_address: data.wallet_address 
        }
      });

      return {
        ...data,
        sol_balance: balanceData?.sol_balance || 0,
        total_balance_usd: balanceData?.total_balance_usd || 0,
        tokens_count: balanceData?.tokens || 0,
      };
    },
    refetchInterval: 30000,
    retry: 1,
  });

  const { data: positions, refetch: refetchPositions, isRefetching: positionsRefreshing } = useQuery({
    queryKey: ['wallet-positions', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('wallet_positions')
        .select('*')
        .eq('wallet_id', id)
        .order('pnl_usd', { ascending: false });
      
      if (error) throw error;
      return data;
    },
    enabled: !!id,
    refetchInterval: 30000,
  });

  const { data: trades, isLoading: tradesLoading } = useQuery({
    queryKey: ['wallet-trades', wallet?.wallet_address],
    queryFn: async () => {
      if (!wallet?.wallet_address) return [];
      
      try {
        // Fetch recent transactions from the wallet using the wallet-discovery edge function
        const { data: txData, error } = await supabase.functions.invoke('wallet-discovery', {
          body: { 
            action: 'get_wallet_transactions',
            wallet_address: wallet.wallet_address,
            limit: 50
          }
        });

        if (error) {
          console.error('Error fetching wallet transactions:', error);
          return [];
        }

        return txData?.transactions || [];
      } catch (error) {
        console.error('Failed to fetch wallet transactions:', error);
        return [];
      }
    },
    enabled: !!wallet,
    refetchInterval: 60000, // Refresh every minute
  });

  const handleRefreshPositions = async () => {
    try {
      if (!wallet?.wallet_address || !id) return;
      await supabase.functions.invoke('wallet-discovery', {
        body: {
          action: 'refresh_wallet_positions',
          wallet_id: id,
          wallet_address: wallet.wallet_address,
        }
      });
      await refetchPositions();
    } catch (e) {
      console.error('Failed to refresh positions', e);
    }
  };

  // Filter trades by time period
  const filteredTrades = useMemo(() => {
    if (!trades || pnlTimeFilter === 'all') return trades;
    
    const cutoffDate = new Date();
    if (pnlTimeFilter === '1d') cutoffDate.setDate(cutoffDate.getDate() - 1);
    else if (pnlTimeFilter === '7d') cutoffDate.setDate(cutoffDate.getDate() - 7);
    else cutoffDate.setDate(cutoffDate.getDate() - 30);
    
    return trades.filter(t => new Date(t.timestamp) >= cutoffDate);
  }, [trades, pnlTimeFilter]);

  // Calculate PnL metrics from positions data
  const pnlMetrics = useMemo(() => {
    if (!positions || positions.length === 0) {
      return {
        totalPnl: Number(wallet?.total_pnl_usd) || 0,
        avgPnl: 0,
        winRate: Number(wallet?.win_rate) || 0,
        bestTrade: 0,
        worstTrade: 0,
        activePnl: 0,
      };
    }
    
    // Apply time filter
    let filteredPositions = positions.filter(p => p.is_closed);
    
    if (pnlTimeFilter !== 'all') {
      const cutoffDate = new Date();
      if (pnlTimeFilter === '1d') cutoffDate.setDate(cutoffDate.getDate() - 1);
      else if (pnlTimeFilter === '7d') cutoffDate.setDate(cutoffDate.getDate() - 7);
      else cutoffDate.setDate(cutoffDate.getDate() - 30);
      
      filteredPositions = filteredPositions.filter(p => {
        const exitDate = new Date(p.exit_time || p.updated_at);
        return exitDate >= cutoffDate;
      });
    }
    
    const totalPnl = filteredPositions.reduce((sum, p) => sum + (Number(p.pnl_usd) || 0), 0);
    const pnlValues = filteredPositions.map(p => Number(p.pnl_usd) || 0);
    const winningTrades = filteredPositions.filter(p => Number(p.pnl_usd) > 0).length;
    const activePnl = positions.filter(p => !p.is_closed).reduce((sum, p) => sum + (Number(p.pnl_usd) || 0), 0);
    
    return {
      totalPnl,
      avgPnl: filteredPositions.length > 0 ? totalPnl / filteredPositions.length : 0,
      winRate: filteredPositions.length > 0 ? (winningTrades / filteredPositions.length) * 100 : Number(wallet?.win_rate) || 0,
      bestTrade: pnlValues.length > 0 ? Math.max(...pnlValues) : 0,
      worstTrade: pnlValues.length > 0 ? Math.min(...pnlValues) : 0,
      activePnl,
    };
  }, [positions, pnlTimeFilter, wallet]);

  // Generate PnL chart data from positions
  const pnlChartData = useMemo(() => {
    if (!positions || positions.length === 0) return [];
    
    // Apply time filter to positions
    let filteredPositions = positions.filter(p => p.is_closed);
    
    if (pnlTimeFilter !== 'all') {
      const cutoffDate = new Date();
      if (pnlTimeFilter === '1d') cutoffDate.setDate(cutoffDate.getDate() - 1);
      else if (pnlTimeFilter === '7d') cutoffDate.setDate(cutoffDate.getDate() - 7);
      else cutoffDate.setDate(cutoffDate.getDate() - 30);
      
      filteredPositions = filteredPositions.filter(p => {
        const exitDate = new Date(p.exit_time || p.updated_at);
        return exitDate >= cutoffDate;
      });
    }
    
    let cumulativePnl = 0;
    
    return filteredPositions
      .sort((a, b) => new Date(a.exit_time || a.updated_at).getTime() - new Date(b.exit_time || b.updated_at).getTime())
      .map(pos => {
        cumulativePnl += Number(pos.pnl_usd) || 0;
        return {
          time: new Date(pos.exit_time || pos.updated_at).toLocaleDateString(),
          timestamp: pos.exit_time || pos.updated_at,
          cumulativePnl,
          pnl: Number(pos.pnl_usd) || 0,
        };
      });
  }, [positions, pnlTimeFilter]);

  // Generate daily PnL bars from positions
  const dailyPnlData = useMemo(() => {
    if (!positions) return [];
    
    // Apply time filter to positions
    let filteredPositions = positions.filter(p => p.is_closed);
    
    if (pnlTimeFilter !== 'all') {
      const cutoffDate = new Date();
      if (pnlTimeFilter === '1d') cutoffDate.setDate(cutoffDate.getDate() - 1);
      else if (pnlTimeFilter === '7d') cutoffDate.setDate(cutoffDate.getDate() - 7);
      else cutoffDate.setDate(cutoffDate.getDate() - 30);
      
      filteredPositions = filteredPositions.filter(p => {
        const exitDate = new Date(p.exit_time || p.updated_at);
        return exitDate >= cutoffDate;
      });
    }
    
    const dailyMap = new Map<string, number>();
    filteredPositions.forEach(pos => {
      const day = new Date(pos.exit_time || pos.updated_at).toLocaleDateString();
      dailyMap.set(day, (dailyMap.get(day) || 0) + (Number(pos.pnl_usd) || 0));
    });
    
    return Array.from(dailyMap.entries())
      .map(([date, pnl]) => ({ date, pnl }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .slice(-30);
  }, [positions, pnlTimeFilter]);

  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatPercentage = (val: number) => `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
  const formatAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  const removeEmojis = (str: string) => str.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();

  if (!wallet) {
    return (
      <div className="min-h-screen bg-background p-6 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 mx-auto mb-4 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading wallet data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <LatencyIndicator />
      
      <div className="max-w-7xl mx-auto">
        <Link to="/wallets">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Wallets
          </Button>
        </Link>

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Wallet className="w-8 h-8 text-primary" />
              <div>
                <h1 className="text-3xl font-bold">{removeEmojis(wallet.label || formatAddress(wallet.wallet_address))}</h1>
                <p className="text-muted-foreground font-mono text-sm">{wallet.wallet_address}</p>
              </div>
            </div>
            <div className="flex gap-2">
              {wallet.is_verified && (
                <Badge variant="default" className="bg-success">
                  Verified
                </Badge>
              )}
              <Badge variant="secondary">
                Score: {wallet.performance_score?.toFixed(0) || 0}
              </Badge>
              {wallet.verification_url && (
                <a href={wallet.verification_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="sm">
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Solscan
                  </Button>
                </a>
              )}
            </div>
          </div>

          {wallet.reasoning && (
            <Card className="backdrop-blur-glass border-primary/20">
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">{wallet.reasoning}</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Balance Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <Card className="backdrop-blur-glass border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-primary" />
                Wallet Balance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Total USD Value</p>
                  <p className="text-3xl font-bold text-primary">
                    {formatCurrency(wallet.total_balance_usd || 0)}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground">SOL Balance</p>
                    <p className="text-lg font-semibold">
                      {wallet.sol_balance?.toFixed(4) || '0.0000'} SOL
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">SOL Value</p>
                    <p className="text-lg font-semibold">
                      {formatCurrency((wallet.sol_balance || 0) * 150)}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="backdrop-blur-glass border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                PnL ({pnlTimeFilter.toUpperCase()})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Total PnL</p>
                  <p className={`text-3xl font-bold ${pnlMetrics.totalPnl >= 0 ? 'text-success' : 'text-destructive'}`}>
                    {pnlMetrics.totalPnl >= 0 ? '+' : ''}{formatCurrency(pnlMetrics.totalPnl)}
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <p className="text-muted-foreground">Avg PnL</p>
                    <p className={`font-semibold ${pnlMetrics.avgPnl >= 0 ? 'text-success' : 'text-destructive'}`}>
                      {formatCurrency(pnlMetrics.avgPnl)}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Best</p>
                    <p className="font-semibold text-success">{formatCurrency(pnlMetrics.bestTrade)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Worst</p>
                    <p className="font-semibold text-destructive">{formatCurrency(pnlMetrics.worstTrade)}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="backdrop-blur-glass border-primary/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Win Rate ({pnlTimeFilter})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {pnlMetrics.winRate.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {wallet.total_trades || 0} total trades
              </p>
            </CardContent>
          </Card>

          <Card className="backdrop-blur-glass border-primary/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">All-Time Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {wallet.win_rate?.toFixed(1) || 0}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {wallet.total_trades || 0} total trades
              </p>
            </CardContent>
          </Card>

          <Card className="backdrop-blur-glass border-primary/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {positions && positions.filter(p => !p.is_closed).length > 0
                  ? positions.filter(p => !p.is_closed).length
                  : (wallet as any)?.tokens_count || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {pnlMetrics.activePnl >= 0 ? '+' : ''}{formatCurrency(pnlMetrics.activePnl)} unrealized
              </p>
            </CardContent>
          </Card>

          <Card className="backdrop-blur-glass border-primary/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Performance Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {wallet.performance_score?.toFixed(0) || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Avg hold: {wallet.avg_holding_time_hours?.toFixed(1) || 0}h
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="pnl" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="pnl">PnL Analytics</TabsTrigger>
            <TabsTrigger value="positions">Positions</TabsTrigger>
            <TabsTrigger value="trades">Recent Trades</TabsTrigger>
          </TabsList>

          <TabsContent value="pnl" className="mt-6 space-y-6">
            {/* Time Filter */}
            <Card className="backdrop-blur-glass border-primary/20">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>PnL Performance</CardTitle>
                  <Tabs value={pnlTimeFilter} onValueChange={(v: any) => setPnlTimeFilter(v)}>
                    <TabsList>
                      <TabsTrigger value="1d">1D</TabsTrigger>
                      <TabsTrigger value="7d">7D</TabsTrigger>
                      <TabsTrigger value="30d">30D</TabsTrigger>
                      <TabsTrigger value="all">All</TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>
                <CardDescription>
                  Based on tracked positions and wallet metrics
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Cumulative PnL Chart */}
            <Card className="backdrop-blur-glass border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Cumulative PnL
                </CardTitle>
                <CardDescription>Running total over time</CardDescription>
              </CardHeader>
              <CardContent>
                {pnlChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={350}>
                    <AreaChart data={pnlChartData}>
                      <defs>
                        <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="hsl(var(--success))" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="hsl(var(--success))" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="cumulativePnl" 
                        stroke="hsl(var(--success))" 
                        fill="url(#colorPnl)" 
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[350px] flex items-center justify-center text-muted-foreground">
                    <div className="text-center">
                      <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No closed positions data for this time period</p>
                      <p className="text-sm mt-1">Try selecting a different time range</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Daily PnL Bar Chart */}
            <Card className="backdrop-blur-glass border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Daily PnL Breakdown
                </CardTitle>
                <CardDescription>Individual trade performance by day</CardDescription>
              </CardHeader>
              <CardContent>
                {dailyPnlData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dailyPnlData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={11} angle={-45} textAnchor="end" height={80} />
                      <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Bar 
                        dataKey="pnl" 
                        fill="hsl(var(--primary))"
                        radius={[8, 8, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    <div className="text-center">
                      <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No trading activity for this time period</p>
                      <p className="text-sm mt-1">Try selecting a different time range</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="positions" className="mt-6">
            <Card className="backdrop-blur-glass border-primary/20">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Active Positions</CardTitle>
                    <CardDescription>Current holdings and unrealized PnL</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={handleRefreshPositions} disabled={!wallet || positionsRefreshing}>
                    <RefreshCw className={`w-4 h-4 mr-2 ${positionsRefreshing ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {positions?.filter(p => !p.is_closed).length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <Wallet className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No active positions</p>
                      <p className="text-sm mt-1">All positions have been closed or not yet tracked</p>
                    </div>
                  ) : (
                    positions?.filter(p => !p.is_closed).map((pos) => (
                      <div key={pos.id} className="p-4 rounded-lg border bg-card">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <span className="font-bold text-lg">{pos.token_symbol}</span>
                            <p className="text-xs text-muted-foreground">{pos.token_name}</p>
                          </div>
                          <div className="text-right">
                            <div className={`text-lg font-bold ${Number(pos.pnl_usd) >= 0 ? 'text-success' : 'text-destructive'}`}>
                              {formatPercentage(Number(pos.pnl_percentage) || 0)}
                            </div>
                            <div className={`text-sm ${Number(pos.pnl_usd) >= 0 ? 'text-success' : 'text-destructive'}`}>
                              {formatCurrency(Number(pos.pnl_usd) || 0)}
                            </div>
                          </div>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
                          <div>
                            <p>Amount</p>
                            <p className="font-semibold text-foreground">{Number(pos.amount)?.toFixed(2)}</p>
                          </div>
                          <div>
                            <p>Entry Price</p>
                            <p className="font-semibold text-foreground">{formatCurrency(Number(pos.entry_price) || 0)}</p>
                          </div>
                          <div>
                            <p>Current Price</p>
                            <p className="font-semibold text-foreground">{formatCurrency(Number(pos.current_price) || 0)}</p>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trades" className="mt-6">
            <Card className="backdrop-blur-glass border-primary/20">
              <CardHeader>
                <CardTitle>Recent Trades</CardTitle>
                <CardDescription>Latest on-chain activity for this wallet</CardDescription>
              </CardHeader>
              <CardContent>
                {tradesLoading ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Activity className="w-8 h-8 mx-auto mb-2 animate-spin text-primary" />
                    <p>Loading transactions...</p>
                  </div>
                ) : trades && trades.length > 0 ? (
                  <div className="space-y-2">
                    {trades.map((trade) => (
                      <div key={trade.id} className="p-3 rounded-lg border bg-card flex items-center justify-between hover:border-primary/40 transition-colors">
                        <div className="flex items-center gap-3">
                          <Badge 
                            variant={
                              trade.type === 'SWAP' ? 'default' : 
                              trade.type === 'RECEIVE' ? 'secondary' : 
                              'outline'
                            }
                          >
                            {trade.type}
                          </Badge>
                          <div>
                            <p className="font-semibold">{trade.description || trade.token}</p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(trade.timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="text-right flex items-center gap-2">
                          <div>
                            {trade.amount_usd > 0 && (
                              <p className="font-semibold text-sm">{formatCurrency(trade.amount_usd)}</p>
                            )}
                            {trade.signature && (
                              <a 
                                href={`https://solscan.io/tx/${trade.signature}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-primary hover:underline"
                                onClick={(e) => e.stopPropagation()}
                              >
                                View on Solscan
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>No recent transactions found</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
