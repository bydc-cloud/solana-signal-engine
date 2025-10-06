import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Clock } from 'lucide-react';
import { TokenLogo } from '@/components/TokenLogo';

const API_BASE = 'https://signal-railway-deployment-production.up.railway.app';

interface Position {
  id: number;
  token_address: string;
  symbol: string;
  entry_price: number;
  current_price: number;
  amount_usd: number;
  unrealized_pnl_usd: number;
  unrealized_pnl_percent: number;
  holding_time_minutes: number;
  entry_time: string;
  solscan_link: string;
  birdeye_link: string;
  dexscreener_link: string;
  address_valid: boolean;
}

export const ActivePositionsWidget = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const response = await fetch(`${API_BASE}/trading/active_positions`);
        const data = await response.json();
        setPositions(data.positions || []);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching positions:', error);
        setLoading(false);
      }
    };

    fetchPositions();
    const interval = setInterval(fetchPositions, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatHoldingTime = (minutes: number) => {
    if (minutes < 60) return `${Math.floor(minutes)}m`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ${Math.floor(minutes % 60)}m`;
    return `${Math.floor(minutes / 1440)}d ${Math.floor((minutes % 1440) / 60)}h`;
  };

  if (loading) {
    return (
      <Card className="border-primary/30 bg-card/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg text-primary">Active Positions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground">Loading positions...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-primary/30 bg-card/80 backdrop-blur-sm hover:border-primary/50 transition-all">
      <CardHeader className="border-b border-border/50">
        <CardTitle className="text-lg text-primary flex items-center justify-between">
          <span>Active Positions</span>
          <Badge variant="secondary" className="bg-primary/15 text-primary border-primary/30">
            {positions.length} Open
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {positions.length === 0 ? (
          <div className="text-center py-12 px-4">
            <p className="text-muted-foreground mb-2">No active positions</p>
            <p className="text-xs text-muted-foreground">
              Positions will appear here once trades are opened
            </p>
          </div>
        ) : (
          <div className="divide-y divide-border/30">
            {positions.map((pos) => (
              <div key={pos.id} className="p-4 hover:bg-primary/5 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <TokenLogo address={pos.token_address} symbol={pos.symbol} size="sm" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-foreground">{pos.symbol}</span>
                        {pos.address_valid && (
                          <a
                            href={pos.birdeye_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:text-primary/80"
                            title="View on Birdeye"
                          >
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                        <Clock className="w-3 h-3" />
                        <span>Holding: {formatHoldingTime(pos.holding_time_minutes)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className={`text-lg font-bold ${pos.unrealized_pnl_percent >= 0 ? 'text-success' : 'text-destructive'}`}>
                      {pos.unrealized_pnl_percent >= 0 ? '+' : ''}{pos.unrealized_pnl_percent.toFixed(2)}%
                    </div>
                    <div className={`text-sm ${pos.unrealized_pnl_usd >= 0 ? 'text-success' : 'text-destructive'}`}>
                      {pos.unrealized_pnl_usd >= 0 ? '+' : ''}${pos.unrealized_pnl_usd.toFixed(2)}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-muted-foreground">Entry:</span>
                    <span className="ml-1 font-mono">${pos.entry_price.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Current:</span>
                    <span className="ml-1 font-mono">${pos.current_price.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Size:</span>
                    <span className="ml-1 font-mono">${pos.amount_usd.toFixed(0)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
