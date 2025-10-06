import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { TrendingUp, Target, Clock, DollarSign, AlertTriangle, Zap } from "lucide-react";
import { TokenLogo } from "@/components/TokenLogo";
import { useToast } from "@/hooks/use-toast";

interface Position {
  id: string;
  token_symbol: string;
  token_address: string;
  entry_price: number;
  current_price: number;
  amount: number;
  pnl_usd: number;
  pnl_percentage: number;
  entry_time: string;
}

interface ExitStrategy {
  positionId: string;
  takeProfitLevels: { percent: number; sellPercent: number }[];
  trailingStop: { enabled: boolean; percentage: number };
  timeBasedExit: { enabled: boolean; hours: number };
  smartMoneyExit: { enabled: boolean; walletCount: number };
}

export default function ExitStrategy() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);
  const [strategy, setStrategy] = useState<ExitStrategy>({
    positionId: "",
    takeProfitLevels: [
      { percent: 50, sellPercent: 33 },
      { percent: 100, sellPercent: 33 },
      { percent: 200, sellPercent: 34 },
    ],
    trailingStop: { enabled: true, percentage: 15 },
    timeBasedExit: { enabled: false, hours: 24 },
    smartMoneyExit: { enabled: true, walletCount: 2 },
  });
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchPositions();
    const interval = setInterval(fetchPositions, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchPositions = async () => {
    try {
      const response = await fetch(
        "https://signal-railway-deployment-production.up.railway.app/trading/active_positions"
      );
      const data = await response.json();
      setPositions(data.positions || []);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch positions:", error);
      setLoading(false);
    }
  };

  const applyStrategy = (positionId: string) => {
    toast({
      title: "Exit Strategy Applied",
      description: `Strategy configured for ${positions.find(p => p.id === positionId)?.token_symbol}`,
    });
  };

  const calculateExitLevels = (position: Position) => {
    return strategy.takeProfitLevels.map(level => ({
      ...level,
      targetPrice: position.entry_price * (1 + level.percent / 100),
      amountToSell: position.amount * (level.sellPercent / 100),
      usdValue: position.entry_price * (1 + level.percent / 100) * position.amount * (level.sellPercent / 100),
    }));
  };

  const selectedPos = positions.find(p => p.id === selectedPosition);

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-primary text-xl font-black font-mono">&gt;</span>
          <h1 className="text-2xl font-black font-mono uppercase tracking-wider text-foreground">
            [exit_automation_protocol]
          </h1>
        </div>
        <p className="text-xs text-muted-foreground font-mono tracking-wide ml-8">
          smart exit strategies // automated take profit ladders // risk management
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Active Positions */}
        <div className="lg:col-span-1">
          <Card className="border-border bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-sm font-mono uppercase tracking-wider text-primary">
                [Active Positions]
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p className="text-muted-foreground font-mono text-xs">Loading positions...</p>
              ) : positions.length === 0 ? (
                <p className="text-muted-foreground font-mono text-xs">No active positions</p>
              ) : (
                <div className="space-y-3">
                  {positions.map(pos => (
                    <div
                      key={pos.id}
                      onClick={() => setSelectedPosition(pos.id)}
                      className={`p-3 border cursor-pointer transition-all ${
                        selectedPosition === pos.id
                          ? "border-primary bg-primary/10"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <TokenLogo address={pos.token_address} symbol={pos.token_symbol} size="sm" />
                        <div className="flex-1">
                          <p className="font-mono text-sm font-bold text-foreground">{pos.token_symbol}</p>
                          <p className="font-mono text-xs text-muted-foreground">
                            {pos.amount.toFixed(2)} tokens
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono text-muted-foreground">PnL:</span>
                        <span className={`text-sm font-mono font-bold ${pos.pnl_usd >= 0 ? "text-success" : "text-destructive"}`}>
                          {pos.pnl_usd >= 0 ? "+" : ""}{pos.pnl_usd.toFixed(2)} USD ({pos.pnl_percentage.toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right: Strategy Configuration */}
        <div className="lg:col-span-2 space-y-6">
          {selectedPos ? (
            <>
              {/* Take Profit Ladder */}
              <Card className="border-border bg-card/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-sm font-mono uppercase tracking-wider text-success flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    [Take Profit Ladder]
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {strategy.takeProfitLevels.map((level, idx) => {
                    const exitLevel = calculateExitLevels(selectedPos)[idx];
                    return (
                      <div key={idx} className="border border-border p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <Label className="font-mono text-xs uppercase text-foreground">
                            Level {idx + 1}: +{level.percent}%
                          </Label>
                          <Badge variant="outline" className="font-mono text-xs">
                            Sell {level.sellPercent}%
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                          <div>
                            <p className="text-muted-foreground">Target Price:</p>
                            <p className="text-foreground font-bold">${exitLevel.targetPrice.toFixed(6)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Sell Amount:</p>
                            <p className="text-foreground font-bold">{exitLevel.amountToSell.toFixed(2)} tokens</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">USD Value:</p>
                            <p className="text-success font-bold">${exitLevel.usdValue.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Distance:</p>
                            <p className={`font-bold ${exitLevel.targetPrice > selectedPos.current_price ? "text-info" : "text-success"}`}>
                              {((exitLevel.targetPrice / selectedPos.current_price - 1) * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              {/* Trailing Stop */}
              <Card className="border-border bg-card/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-sm font-mono uppercase tracking-wider text-warning flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    [Trailing Stop Loss]
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label className="font-mono text-xs text-foreground">Enable Trailing Stop</Label>
                    <Switch
                      checked={strategy.trailingStop.enabled}
                      onCheckedChange={(checked) =>
                        setStrategy({
                          ...strategy,
                          trailingStop: { ...strategy.trailingStop, enabled: checked },
                        })
                      }
                    />
                  </div>
                  {strategy.trailingStop.enabled && (
                    <div className="space-y-3">
                      <Label className="font-mono text-xs text-muted-foreground">
                        Trail Distance: {strategy.trailingStop.percentage}% below peak
                      </Label>
                      <Slider
                        value={[strategy.trailingStop.percentage]}
                        onValueChange={([value]) =>
                          setStrategy({
                            ...strategy,
                            trailingStop: { ...strategy.trailingStop, percentage: value },
                          })
                        }
                        min={5}
                        max={30}
                        step={1}
                        className="w-full"
                      />
                      <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                        <div>
                          <p className="text-muted-foreground">Current Price:</p>
                          <p className="text-foreground font-bold">${selectedPos.current_price.toFixed(6)}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Stop Loss Trigger:</p>
                          <p className="text-destructive font-bold">
                            ${(selectedPos.current_price * (1 - strategy.trailingStop.percentage / 100)).toFixed(6)}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Additional Exit Conditions */}
              <Card className="border-border bg-card/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-sm font-mono uppercase tracking-wider text-info flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    [Additional Exit Conditions]
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Time-Based Exit */}
                  <div className="border border-border p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="font-mono text-xs text-foreground flex items-center gap-2">
                        <Clock className="w-3 h-3" />
                        Time-Based Exit
                      </Label>
                      <Switch
                        checked={strategy.timeBasedExit.enabled}
                        onCheckedChange={(checked) =>
                          setStrategy({
                            ...strategy,
                            timeBasedExit: { ...strategy.timeBasedExit, enabled: checked },
                          })
                        }
                      />
                    </div>
                    {strategy.timeBasedExit.enabled && (
                      <div className="space-y-2">
                        <Label className="font-mono text-xs text-muted-foreground">
                          Exit after {strategy.timeBasedExit.hours} hours
                        </Label>
                        <Slider
                          value={[strategy.timeBasedExit.hours]}
                          onValueChange={([value]) =>
                            setStrategy({
                              ...strategy,
                              timeBasedExit: { ...strategy.timeBasedExit, hours: value },
                            })
                          }
                          min={1}
                          max={72}
                          step={1}
                          className="w-full"
                        />
                      </div>
                    )}
                  </div>

                  {/* Smart Money Exit */}
                  <div className="border border-border p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="font-mono text-xs text-foreground flex items-center gap-2">
                        <Target className="w-3 h-3" />
                        Smart Money Exit Signal
                      </Label>
                      <Switch
                        checked={strategy.smartMoneyExit.enabled}
                        onCheckedChange={(checked) =>
                          setStrategy({
                            ...strategy,
                            smartMoneyExit: { ...strategy.smartMoneyExit, enabled: checked },
                          })
                        }
                      />
                    </div>
                    {strategy.smartMoneyExit.enabled && (
                      <p className="text-xs font-mono text-muted-foreground">
                        Auto-sell when {strategy.smartMoneyExit.walletCount}+ S-tier wallets exit this position
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Apply Button */}
              <Button
                onClick={() => applyStrategy(selectedPos.id)}
                className="w-full font-mono uppercase text-sm"
                size="lg"
              >
                Apply Exit Strategy
              </Button>
            </>
          ) : (
            <Card className="border-border bg-card/50 backdrop-blur-sm">
              <CardContent className="p-12 text-center">
                <AlertTriangle className="w-12 h-12 text-warning mx-auto mb-4 opacity-50" />
                <p className="text-muted-foreground font-mono">Select a position to configure exit strategy</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
