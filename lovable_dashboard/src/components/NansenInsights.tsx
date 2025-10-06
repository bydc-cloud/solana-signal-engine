import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { TrendingUp, Wallet, AlertTriangle } from "lucide-react";

export const NansenInsights = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [smartMoneyData, setSmartMoneyData] = useState<any>(null);
  const [whaleAlerts, setWhaleAlerts] = useState<any>(null);
  const { toast } = useToast();

  const fetchSmartMoneyTrends = async () => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('nansen-intelligence', {
        body: { 
          action: 'trending_smart_money',
          chain: 'eth'
        }
      });

      if (error) throw error;
      
      setSmartMoneyData(data.data);
      toast({
        title: "Smart Money Data Loaded",
        description: "Latest trending tokens fetched from Nansen",
      });
    } catch (error) {
      console.error('Error fetching smart money:', error);
      toast({
        title: "Error",
        description: "Failed to fetch smart money data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchWhaleAlerts = async () => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('nansen-intelligence', {
        body: { 
          action: 'whale_alerts',
          chain: 'eth'
        }
      });

      if (error) throw error;
      
      setWhaleAlerts(data.data);
      toast({
        title: "Whale Alerts Loaded",
        description: "Recent whale movements fetched",
      });
    } catch (error) {
      console.error('Error fetching whale alerts:', error);
      toast({
        title: "Error",
        description: "Failed to fetch whale alerts",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="backdrop-blur-glass border-primary/20">
      <CardHeader>
        <CardTitle className="text-gradient-primary flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Nansen Intelligence
        </CardTitle>
        <CardDescription>
          Smart money tracking and whale movement analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="smart-money" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="smart-money">Smart Money</TabsTrigger>
            <TabsTrigger value="whales">Whale Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="smart-money" className="space-y-4">
            <Button 
              onClick={fetchSmartMoneyTrends}
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? "Loading..." : "Fetch Smart Money Trends"}
            </Button>

            {smartMoneyData && (
              <div className="space-y-2">
                <h4 className="font-semibold">Trending Tokens (24h)</h4>
                {smartMoneyData.trending_tokens?.slice(0, 5).map((token: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div>
                      <p className="font-medium">{token.symbol}</p>
                      <p className="text-xs text-muted-foreground">{token.name}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant={token.sentiment === 'bullish' ? 'default' : 'destructive'}>
                        {token.smart_money_flow > 0 ? '+' : ''}{token.smart_money_flow?.toFixed(2)}%
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        {token.smart_wallets} wallets
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="whales" className="space-y-4">
            <Button 
              onClick={fetchWhaleAlerts}
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? "Loading..." : "Fetch Whale Alerts"}
            </Button>

            {whaleAlerts && (
              <div className="space-y-2">
                <h4 className="font-semibold flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Recent Whale Activity
                </h4>
                {whaleAlerts.alerts?.slice(0, 5).map((alert: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg bg-muted/50 space-y-1">
                    <div className="flex items-center justify-between">
                      <Badge variant={alert.action === 'buy' ? 'default' : 'destructive'}>
                        {alert.action.toUpperCase()}
                      </Badge>
                      <span className="text-sm font-medium">{alert.token_symbol}</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Amount: ${alert.amount_usd?.toLocaleString()}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Wallet: {alert.wallet_label || 'Unknown'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
