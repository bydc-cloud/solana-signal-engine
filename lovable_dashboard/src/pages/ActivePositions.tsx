import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, TrendingUp, TrendingDown } from "lucide-react";
import { useHelixBot } from "@/hooks/useHelixBot";
import { TokenLogo } from "@/components/TokenLogo";

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

export default function ActivePositions() {
  const { positions, loading } = useHelixBot();

  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatPercentage = (val: number) => `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
  };

  const totalPnl = positions.reduce((sum, pos) => sum + (pos.unrealized_pnl_usd || 0), 0);

  return (
    <div className="container mx-auto p-8 space-y-8 min-h-screen mesh-gradient">
      <div>
        <h1 className="text-5xl font-bold text-gradient-primary mb-2 neon-text">Active Positions</h1>
        <p className="text-muted-foreground text-lg">Monitor your open trades with live P&L</p>
      </div>

      <Card className="card-premium border-2">
        <CardHeader className="border-b border-border/50">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-mono">Active Positions</CardTitle>
              <p className="text-sm text-muted-foreground font-mono mt-1">{positions.length} open trades</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground font-mono uppercase tracking-wide">Total Unrealized PnL</p>
              <p className={`text-2xl font-bold font-mono ${totalPnl >= 0 ? 'text-success' : 'text-destructive'}`}>
                {formatCurrency(totalPnl)}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <div className="text-center text-muted-foreground font-mono py-8">Loading positions...</div>
          ) : positions.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <TrendingUp className="w-16 h-16 mx-auto mb-3 opacity-50" />
              <p className="font-mono text-lg">No active positions</p>
              <p className="text-sm mt-1 font-mono">Open positions will appear here once the bot executes trades</p>
            </div>
          ) : (
            <div className="space-y-4">
              {positions.map((position, idx) => (
                <Card key={idx} className="card-premium border hover:border-primary/60 transition-all">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <TokenLogo address={position.solscan_link.split('/').pop() || ''} symbol={position.symbol} size="lg" />
                    <div>
                      <CardTitle className="text-lg font-mono">{position.symbol}</CardTitle>
                      <div className="flex gap-1 mt-1">
                        <a 
                          href={position.birdeye_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:underline flex items-center gap-1 font-mono"
                        >
                          Chart <ExternalLink className="w-3 h-3" />
                        </a>
                        <span className="text-muted-foreground">•</span>
                        <a 
                          href={position.solscan_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:underline flex items-center gap-1 font-mono"
                        >
                          Solscan <ExternalLink className="w-3 h-3" />
                        </a>
                        <span className="text-muted-foreground">•</span>
                        <a 
                          href={position.dexscreener_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:underline flex items-center gap-1 font-mono"
                        >
                          DEX <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  </div>
                  <Badge variant={position.unrealized_pnl_usd >= 0 ? 'default' : 'destructive'} className="text-lg font-mono">
                    {formatPercentage(position.unrealized_pnl_percent)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground font-mono uppercase tracking-wide">Entry Price</p>
                    <p className="text-sm font-semibold font-mono">{formatCurrency(position.entry_price)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground font-mono uppercase tracking-wide">Current Price</p>
                    <div className="flex items-center gap-1">
                      <p className="text-sm font-semibold font-mono">{formatCurrency(position.current_price)}</p>
                      {position.current_price > position.entry_price ? (
                        <TrendingUp className="w-3 h-3 text-success" />
                      ) : (
                        <TrendingDown className="w-3 h-3 text-destructive" />
                      )}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground font-mono uppercase tracking-wide">Size</p>
                    <p className="text-sm font-semibold font-mono">{formatCurrency(position.size_usd || 0)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground font-mono uppercase tracking-wide">Unrealized PnL</p>
                    <p className={`text-sm font-semibold font-mono ${position.unrealized_pnl_usd >= 0 ? 'text-success' : 'text-destructive'}`}>
                      {formatCurrency(position.unrealized_pnl_usd)}
                    </p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-border/50 flex items-center justify-between">
                  <div className="text-xs text-muted-foreground font-mono">
                    Holding: {formatTime(position.holding_time_minutes)}
                  </div>
                  {position.entry_time && (
                    <div className="text-xs text-muted-foreground font-mono">
                      Entry: {new Date(position.entry_time).toLocaleString()}
                    </div>
                  )}
                </div>
              </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
