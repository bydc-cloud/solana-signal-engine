import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ExternalLink } from 'lucide-react';

const API_BASE = 'https://signal-railway-deployment-production.up.railway.app';

interface Wallet {
  address: string;
  label: string;
  tier: string;
  category: string;
  pnl: number;
  win_rate: number;
  total_trades: number;
  volume: number;
  solscan_link: string;
}

export const SmartWalletsWidget = () => {
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [timeframe, setTimeframe] = useState('1d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWallets = async () => {
      try {
        const response = await fetch(`${API_BASE}/wallets/performance?timeframe=${timeframe}&limit=20`);
        const data = await response.json();
        setWallets(data.wallets || []);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching wallets:', error);
        setLoading(false);
      }
    };

    fetchWallets();
    const interval = setInterval(fetchWallets, 60000);
    return () => clearInterval(interval);
  }, [timeframe]);

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'S': return 'bg-warning/20 text-warning border-warning/30';
      case 'A': return 'bg-primary/20 text-primary border-primary/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  if (loading) {
    return (
      <Card className="border-primary/30 bg-card/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl text-primary">Smart Money Wallets</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <p>Loading wallet data...</p>
            <p className="text-sm mt-2">First scan takes 10-15 minutes</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-primary/30 bg-card/80 backdrop-blur-sm">
      <CardHeader className="border-b border-border/50">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl text-primary">Smart Money Wallets</CardTitle>
          <Tabs value={timeframe} onValueChange={setTimeframe}>
            <TabsList className="bg-primary/10">
              <TabsTrigger value="1d">24H</TabsTrigger>
              <TabsTrigger value="7d">7D</TabsTrigger>
              <TabsTrigger value="30d">30D</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {wallets.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <p className="mb-2">⏳ Waiting for wallet scanner to complete first cycle...</p>
            <p className="text-sm">This takes 10-15 minutes on fresh deployment</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {wallets.map((wallet) => (
              <Card key={wallet.address} className="border-primary/20 hover:border-primary/40 transition-all bg-card/50">
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-bold text-foreground truncate pr-2">
                      {wallet.label || 'Unknown'}
                    </h3>
                    <Badge variant="secondary" className={getTierColor(wallet.tier)}>
                      {wallet.tier}-Tier
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-muted-foreground mb-4 truncate">
                    {wallet.category}
                  </p>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">PnL:</span>
                      <span className={`font-bold ${wallet.pnl >= 0 ? 'text-success' : 'text-destructive'}`}>
                        ${wallet.pnl?.toFixed(2) || '0.00'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Win Rate:</span>
                      <span className="font-bold text-primary">
                        {wallet.win_rate?.toFixed(1) || '0.0'}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Trades:</span>
                      <span className="font-bold">{wallet.total_trades || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Volume:</span>
                      <span className="font-bold font-mono text-xs">
                        ${wallet.volume?.toLocaleString() || '0'}
                      </span>
                    </div>
                  </div>
                  
                  <a
                    href={wallet.solscan_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-4 flex items-center justify-center gap-2 text-primary hover:text-primary/80 text-sm font-semibold transition-colors"
                  >
                    <span>View on Solscan</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
