import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { api } from "@/lib/api";
import { Activity, Zap, Target, XCircle, Clock, Timer } from "lucide-react";

export default function Metrics() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ["metrics"],
    queryFn: api.getMetrics,
    refetchInterval: 30000,
  });

  const metricCards = [
    {
      title: "Total Cycles",
      value: metrics?.total_cycles || 0,
      icon: Activity,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10",
    },
    {
      title: "Total Signals",
      value: metrics?.total_signals || 0,
      icon: Zap,
      color: "text-purple-400",
      bg: "bg-purple-500/10",
    },
    {
      title: "Watchlist Alerts",
      value: metrics?.watchlist_alerts || 0,
      icon: Target,
      color: "text-success",
      bg: "bg-success/10",
    },
    {
      title: "Empty Cycles",
      value: metrics?.empty_cycles || 0,
      icon: XCircle,
      color: "text-warning",
      bg: "bg-warning/10",
    },
    {
      title: "Avg Cycle Time",
      value: `${(metrics?.avg_cycle_time || 0).toFixed(2)}s`,
      icon: Clock,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
    },
    {
      title: "Last Cycle Time",
      value: `${(metrics?.last_cycle_time || 0).toFixed(2)}s`,
      icon: Timer,
      color: "text-pink-400",
      bg: "bg-pink-500/10",
    },
  ];

  return (
    <div className="min-h-screen p-8 space-y-8 mesh-gradient">
      <LatencyIndicator />
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold text-gradient-primary mb-2 neon-text">Scanner Metrics</h1>
          <p className="text-muted-foreground text-lg">Performance and operational statistics</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metricCards.map((metric) => {
          const Icon = metric.icon;
          return (
            <Card key={metric.title} className="p-6 card-premium border-2">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${metric.bg}`}>
                  <Icon className={`w-6 h-6 ${metric.color}`} />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-muted-foreground mb-1">{metric.title}</p>
                  <p className="text-2xl font-bold font-mono">{metric.value}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Additional Stats */}
      <Card className="card-premium p-6">
        <h2 className="text-xl font-bold mb-4">Performance Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-muted-foreground mb-2">Signal Rate</p>
            <p className="text-3xl font-bold font-mono">
              {metrics?.total_cycles > 0 
                ? ((metrics.total_signals / metrics.total_cycles) * 100).toFixed(1) 
                : 0}%
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Signals per cycle
            </p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground mb-2">Empty Rate</p>
            <p className="text-3xl font-bold font-mono">
              {metrics?.total_cycles > 0 
                ? ((metrics.empty_cycles / metrics.total_cycles) * 100).toFixed(1) 
                : 0}%
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Cycles with no signals
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
