import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, Wallet, TrendingUp, Target, AlertCircle } from "lucide-react";

interface ActivityItem {
  id: string;
  type: "signal" | "wallet" | "position" | "alert";
  title: string;
  description: string;
  timestamp: string;
  metadata?: any;
}

export function LiveActivityFeed() {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActivities();
    const interval = setInterval(fetchActivities, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivities = async () => {
    try {
      // Fetch from multiple endpoints and combine
      const [signalsRes, positionsRes] = await Promise.all([
        fetch("https://signal-railway-deployment-production.up.railway.app/trading/signals?hours=1&limit=10"),
        fetch("https://signal-railway-deployment-production.up.railway.app/trading/active_positions"),
      ]);

      const [signalsData, positionsData] = await Promise.all([
        signalsRes.json(),
        positionsRes.json(),
      ]);

      const newActivities: ActivityItem[] = [];

      // Add signal activities
      signalsData.signals?.slice(0, 5).forEach((signal: any) => {
        newActivities.push({
          id: `signal-${signal.token_address}-${signal.timestamp}`,
          type: "signal",
          title: `New Signal: ${signal.symbol || signal.token_symbol}`,
          description: `Momentum: ${signal.momentum_score || 0} | GS: ${signal.tier || "N/A"}`,
          timestamp: signal.timestamp || signal.created_at,
          metadata: signal,
        });
      });

      // Add position activities
      positionsData.positions?.slice(0, 3).forEach((pos: any) => {
        newActivities.push({
          id: `position-${pos.id}`,
          type: "position",
          title: `${pos.token_symbol} Position`,
          description: `PnL: ${pos.pnl_percentage?.toFixed(1)}% (${pos.pnl_usd >= 0 ? "+" : ""}$${pos.pnl_usd?.toFixed(2)})`,
          timestamp: pos.entry_time || new Date().toISOString(),
          metadata: pos,
        });
      });

      // Sort by timestamp descending
      newActivities.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      setActivities(newActivities.slice(0, 10));
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch activities:", error);
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "signal": return <Target className="w-3 h-3" />;
      case "wallet": return <Wallet className="w-3 h-3" />;
      case "position": return <TrendingUp className="w-3 h-3" />;
      case "alert": return <AlertCircle className="w-3 h-3" />;
      default: return <Activity className="w-3 h-3" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case "signal": return "text-primary";
      case "wallet": return "text-accent";
      case "position": return "text-success";
      case "alert": return "text-warning";
      default: return "text-muted-foreground";
    }
  };

  const formatRelativeTime = (timestamp: string) => {
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <Card className="border-border bg-card/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase tracking-wider text-primary flex items-center gap-2">
          <Activity className="w-4 h-4" />
          <span className="text-primary">&gt;</span>
          [live_activity_stream]
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-xs text-muted-foreground font-mono">Loading activity...</p>
        ) : activities.length === 0 ? (
          <p className="text-xs text-muted-foreground font-mono">No recent activity</p>
        ) : (
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className="border border-border p-3 hover:bg-card/50 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div className={`flex-shrink-0 ${getActivityColor(activity.type)}`}>
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-mono font-bold text-foreground truncate">
                        {activity.title}
                      </p>
                      <p className="text-[10px] font-mono text-muted-foreground truncate">
                        {activity.description}
                      </p>
                      <p className="text-[9px] font-mono text-muted-foreground/60 mt-1">
                        {formatRelativeTime(activity.timestamp)}
                      </p>
                    </div>
                    <Badge variant="outline" className="font-mono text-[9px] uppercase flex-shrink-0">
                      {activity.type}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
