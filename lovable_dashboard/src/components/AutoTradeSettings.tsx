import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";

export const AutoTradeSettings = () => {
  const [autoTradeEnabled, setAutoTradeEnabled] = useState(false);
  const [sizeMultiplier, setSizeMultiplier] = useState([0.5]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const { toast } = useToast();

  const handleStartMonitoring = async () => {
    setIsMonitoring(true);
    toast({
      title: "Wallet Monitoring Started",
      description: "Now tracking trades from configured wallets",
    });

    try {
      // Get all wallets from database
      const { data: wallets } = await supabase
        .from('meme_coin_wallets')
        .select('*');

      if (wallets && wallets.length > 0) {
        // Monitor each wallet from tracked_wallets instead
        const { data: trackedWallets } = await supabase
          .from('tracked_wallets')
          .select('wallet_address, label')
          .eq('is_active', true)
          .order('performance_score', { ascending: false })
          .limit(10);

        if (trackedWallets && trackedWallets.length > 0) {
          for (const wallet of trackedWallets) {
            const { data } = await supabase.functions.invoke('auto-trader', {
              body: { 
                action: 'monitor', 
                walletAddress: wallet.wallet_address,
                mode: 'PAPER'
              }
            });
            
            console.log(`Monitoring ${wallet.label || wallet.wallet_address}:`, data);
          }
        }
      }
    } catch (error) {
      console.error('Monitoring error:', error);
      toast({
        title: "Monitoring Error",
        description: "Failed to start wallet monitoring",
        variant: "destructive",
      });
    }
  };

  const handleStopMonitoring = () => {
    setIsMonitoring(false);
    toast({
      title: "Monitoring Stopped",
      description: "Wallet tracking has been disabled",
    });
  };

  return (
    <Card className="backdrop-blur-glass border-primary/20">
      <CardHeader>
        <CardTitle className="text-gradient-primary">Auto-Trading Settings</CardTitle>
        <CardDescription>
          Configure automated copy trading from tracked wallets
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="auto-trade">Enable Auto-Trading</Label>
            <p className="text-sm text-muted-foreground">
              Automatically copy trades from tracked wallets
            </p>
          </div>
          <Switch
            id="auto-trade"
            checked={autoTradeEnabled}
            onCheckedChange={setAutoTradeEnabled}
          />
        </div>

        {autoTradeEnabled && (
          <>
            <div className="space-y-4">
              <Label>Position Size Multiplier: {sizeMultiplier[0].toFixed(2)}x</Label>
              <Slider
                value={sizeMultiplier}
                onValueChange={setSizeMultiplier}
                min={0.1}
                max={2.0}
                step={0.1}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Copy trade size relative to tracked wallet (0.1x = 10%, 1x = 100%, 2x = 200%)
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleStartMonitoring}
                disabled={isMonitoring}
                className="flex-1"
              >
                {isMonitoring ? "Monitoring Active" : "Start Monitoring"}
              </Button>
              {isMonitoring && (
                <Button
                  onClick={handleStopMonitoring}
                  variant="destructive"
                  className="flex-1"
                >
                  Stop Monitoring
                </Button>
              )}
            </div>
          </>
        )}

        <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 p-4">
          <p className="text-sm text-yellow-500">
            ⚠️ Currently in PAPER TRADING mode. Trades will be simulated only. 
            Switch to LIVE mode in Config to enable real trades.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
