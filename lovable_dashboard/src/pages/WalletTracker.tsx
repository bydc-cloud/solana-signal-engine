import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RefreshCw, Wallet, ArrowUpDown } from "lucide-react";
import { toast } from "sonner";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { Link } from "react-router-dom";

interface TrackedWallet {
  id: string;
  wallet_address: string;
  label: string | null;
  total_pnl_usd: number;
  win_rate: number;
  total_trades: number;
  active_positions: number;
  avg_holding_time_hours: number;
  last_trade_at: string | null;
  performance_score: number;
  nansen_labels: string[];
  sol_balance?: number;
  total_balance_usd?: number;
  reasoning?: string | null;
  verification_url?: string | null;
  wallet_type?: string;
  is_verified?: boolean;
  chain?: string;
}

export default function WalletTracker() {
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [timeFilter, setTimeFilter] = useState<'1d' | '7d' | '30d' | 'all'>('all');
  const [sortBy, setSortBy] = useState<'pnl_high' | 'pnl_low' | 'recent_trade' | 'win_rate' | 'wallet_value'>('wallet_value');
  const [walletsWithBalances, setWalletsWithBalances] = useState<TrackedWallet[]>([]);

  // Auto-discover wallets on mount if none exist
  const { data: initialCheck } = useQuery({
    queryKey: ['check-wallets'],
    queryFn: async () => {
      const { count } = await supabase
        .from('tracked_wallets')
        .select('*', { count: 'exact', head: true });
      
      if (count === 0) {
        handleDiscoverWallets();
      }
      return count;
    },
  });

  const { data: wallets, refetch: refetchWallets } = useQuery({
    queryKey: ['tracked-wallets'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('tracked_wallets')
        .select('*')
        .eq('is_active', true)
        .order('performance_score', { ascending: false });
      
      if (error) throw error;
      
      // Fetch live balances for top 20 wallets
      const walletsData = data as TrackedWallet[];
      const topWallets = walletsData.filter(w => (w.chain ?? 'solana') === 'solana').slice(0, 20);
      
      const walletsWithLiveData = await Promise.all(
        topWallets.map(async (wallet) => {
          try {
            const { data: balanceData } = await supabase.functions.invoke('wallet-discovery', {
              body: { 
                action: 'get_wallet_balance',
                wallet_address: wallet.wallet_address 
              }
            });
            
            return {
              ...wallet,
              sol_balance: balanceData?.sol_balance || 0,
              total_balance_usd: balanceData?.total_balance_usd || 0,
            };
          } catch (error) {
            console.error(`Failed to fetch balance for ${wallet.wallet_address}`);
            return wallet;
          }
        })
      );
      
      setWalletsWithBalances(walletsWithLiveData);
      return [...walletsWithLiveData, ...walletsData.slice(20)];
    },
    refetchInterval: 30000, // Refresh every 30s
  });

  // Filter and sort wallets
  const filteredWallets = useMemo(() => {
    if (!wallets) return [];
    
    let filtered = [...wallets];
    
    // Time filter - filter by last_trade_at
    if (timeFilter !== 'all') {
      const cutoffDate = new Date();
      if (timeFilter === '1d') cutoffDate.setDate(cutoffDate.getDate() - 1);
      else if (timeFilter === '7d') cutoffDate.setDate(cutoffDate.getDate() - 7);
      else cutoffDate.setDate(cutoffDate.getDate() - 30);
      
      filtered = filtered.filter(w => {
        if (!w.last_trade_at) return false;
        return new Date(w.last_trade_at) >= cutoffDate;
      });
    }
    
    // Sort
    switch (sortBy) {
      case 'pnl_high':
        filtered.sort((a, b) => Number(b.total_pnl_usd) - Number(a.total_pnl_usd));
        break;
      case 'pnl_low':
        filtered.sort((a, b) => Number(a.total_pnl_usd) - Number(b.total_pnl_usd));
        break;
      case 'recent_trade':
        filtered.sort((a, b) => {
          if (!a.last_trade_at) return 1;
          if (!b.last_trade_at) return -1;
          return new Date(b.last_trade_at).getTime() - new Date(a.last_trade_at).getTime();
        });
        break;
      case 'win_rate':
        filtered.sort((a, b) => Number(b.win_rate) - Number(a.win_rate));
        break;
      case 'wallet_value':
        filtered.sort((a, b) => (b.total_balance_usd || 0) - (a.total_balance_usd || 0));
        break;
    }
    
    return filtered;
  }, [wallets, timeFilter, sortBy]);

  const handleDiscoverWallets = async () => {
    setIsDiscovering(true);
    try {
      const { data, error } = await supabase.functions.invoke('wallet-discovery', {
        body: { action: 'discover_profitable_wallets' }
      });

      if (error) throw error;

      toast.success(`Synced ${data.added} wallets with latest data!`);
      refetchWallets();
    } catch (error) {
      console.error('Discovery error:', error);
      toast.error('Failed to sync wallet data');
    } finally {
      setIsDiscovering(false);
    }
  };

  const formatAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatPercentage = (val: number) => `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
  const formatNumber = (val: number) => val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const formatRelativeTime = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };
  const removeEmojis = (str: string) => str.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();

  return (
    <div className="min-h-screen bg-background p-6">
      <LatencyIndicator />
      <header className="mb-6">
        <div className="flex items-center justify-between">
          <div>
          <h1 className="text-3xl font-bold text-gradient-primary">Wallet Tracker</h1>
            <p className="text-muted-foreground">
              {walletsWithBalances?.length > 0 
                ? `Tracking ${walletsWithBalances.length} wallets with live on-chain balances` 
                : "Top 100 smart money wallets with verified performance"}
            </p>
          </div>
          <div className="flex gap-3">
            <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
              <SelectTrigger className="w-[200px]">
                <ArrowUpDown className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="wallet_value">Wallet Value (High)</SelectItem>
                <SelectItem value="pnl_high">Trading PnL (High)</SelectItem>
                <SelectItem value="pnl_low">Trading PnL (Low)</SelectItem>
                <SelectItem value="win_rate">Win Rate (High)</SelectItem>
                <SelectItem value="recent_trade">Most Recent Trade</SelectItem>
              </SelectContent>
            </Select>
            
            <Tabs value={timeFilter} onValueChange={(v) => setTimeFilter(v as any)}>
              <TabsList>
                <TabsTrigger value="all">All Time</TabsTrigger>
                <TabsTrigger value="1d">1D</TabsTrigger>
                <TabsTrigger value="7d">7D</TabsTrigger>
                <TabsTrigger value="30d">30D</TabsTrigger>
              </TabsList>
            </Tabs>
            
            <Button
              onClick={handleDiscoverWallets}
              disabled={isDiscovering}
              variant="outline"
              size="lg"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isDiscovering ? 'animate-spin' : ''}`} />
              {isDiscovering ? 'Syncing...' : 'Refresh Data'}
            </Button>
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="backdrop-blur-glass border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {timeFilter === 'all' ? 'Total Wallets' : `Wallets (${timeFilter})`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{filteredWallets?.length || 0}</div>
          </CardContent>
        </Card>

        <Card className="backdrop-blur-glass border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Wallet Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary">
              {formatCurrency(walletsWithBalances?.reduce((sum, w) => sum + (w.total_balance_usd || 0), 0) || 0)}
            </div>
          </CardContent>
        </Card>

        <Card className="backdrop-blur-glass border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Win Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {((filteredWallets?.reduce((sum, w) => sum + Number(w.win_rate), 0) || 0) / (filteredWallets?.length || 1)).toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card className="backdrop-blur-glass border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Positions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-success">
              {filteredWallets?.reduce((sum, w) => sum + Number(w.active_positions), 0) || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="w-full">
        {/* Wallets List */}
        <Card className="backdrop-blur-glass border-primary/20">
          <CardHeader>
            <CardTitle>Top Performing Wallets</CardTitle>
            <CardDescription>Ranked by performance score and profitability</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {filteredWallets?.map((wallet) => (
                <Link
                  key={wallet.id}
                  to={`/wallets/${wallet.id}`}
                  className="block"
                >
                  <div className="p-5 rounded-xl border-2 border-border/50 hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 bg-card/50 hover:bg-card backdrop-blur-sm">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          <Wallet className="w-4 h-4 text-primary flex-shrink-0" />
                          <span className="font-bold text-base">{removeEmojis(wallet.label || formatAddress(wallet.wallet_address))}</span>
                          {wallet.is_verified && (
                            <Badge variant="default" className="text-xs bg-success border-0">
                              Verified
                            </Badge>
                          )}
                          <Badge variant="outline" className="text-xs border-primary/30">
                            {String(wallet.chain || 'solana').toUpperCase()}
                          </Badge>
                          <Badge variant="secondary" className="text-xs">
                            Score: {wallet.performance_score.toFixed(0)}
                          </Badge>
                          {wallet.verification_url && (
                            <Button 
                              variant="link"
                              size="sm"
                              className="h-auto p-0 text-xs text-primary hover:underline"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                window.open(wallet.verification_url, '_blank', 'noopener,noreferrer');
                              }}
                            >
                              View on Solscan
                            </Button>
                          )}
                        </div>
                        {wallet.reasoning && (
                          <p className="text-xs text-muted-foreground mb-2 max-w-2xl">{wallet.reasoning}</p>
                        )}
                        {wallet.nansen_labels && wallet.nansen_labels.length > 0 && (
                          <div className="flex gap-1 mt-2 flex-wrap">
                            {wallet.nansen_labels.map((label, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {removeEmojis(label)}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        {wallet.total_balance_usd !== undefined && wallet.total_balance_usd > 0 ? (
                          <>
                            <div className="text-2xl font-bold text-primary">
                              {formatCurrency(wallet.total_balance_usd)}
                            </div>
                            <div className="text-xs text-muted-foreground">Live Wallet Value</div>
                            {Number(wallet.total_pnl_usd) > 0 && (
                              <div className="text-sm text-success mt-1">
                                +{formatCurrency(Number(wallet.total_pnl_usd))} est. P&L
                              </div>
                            )}
                          </>
                        ) : wallet.chain && wallet.chain !== 'solana' ? (
                          <>
                            <div className="text-sm font-medium text-muted-foreground">Balance not available</div>
                            <div className="text-xs text-muted-foreground">EVM wallet</div>
                            {Number(wallet.total_pnl_usd) > 0 && (
                              <div className="text-sm text-success mt-1">
                                {formatCurrency(Number(wallet.total_pnl_usd))} est. P&L
                              </div>
                            )}
                          </>
                        ) : Number(wallet.total_pnl_usd) > 0 ? (
                          <>
                            <div className={`text-xl font-bold text-success`}>
                              {formatCurrency(Number(wallet.total_pnl_usd))}
                            </div>
                            <div className="text-xs text-muted-foreground">Estimated P&L</div>
                          </>
                        ) : (
                          <>
                            <div className="text-sm font-medium text-muted-foreground">Calculating...</div>
                            <div className="text-xs text-muted-foreground">P&L pending</div>
                          </>
                        )}
                      </div>
                    </div>

                    {wallet.sol_balance !== undefined && wallet.sol_balance > 0 && (
                      <div className="mb-4 p-3 rounded-lg bg-primary/5 border border-primary/10">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs text-muted-foreground font-medium">SOL Balance</p>
                            <p className="font-bold text-base mt-0.5">{formatNumber(wallet.sol_balance)} SOL</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-muted-foreground font-medium">USD Value</p>
                            <p className="font-bold text-base mt-0.5">{formatCurrency(wallet.total_balance_usd || 0)}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-5 gap-6 pt-3 border-t border-border/50">
                      <div>
                        <p className="text-muted-foreground text-xs font-medium mb-1">Win Rate</p>
                        <p className="font-bold text-sm">{wallet.win_rate.toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground text-xs font-medium mb-1">Trades</p>
                        <p className="font-bold text-sm">{wallet.total_trades}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground text-xs font-medium mb-1">Active</p>
                        <p className="font-bold text-sm text-success">{wallet.active_positions || 0}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground text-xs font-medium mb-1">Avg Hold</p>
                        <p className="font-bold text-sm">{wallet.avg_holding_time_hours.toFixed(1)}h</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground text-xs font-medium mb-1">Last Trade</p>
                        <p className="font-bold text-xs">{formatRelativeTime(wallet.last_trade_at)}</p>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
