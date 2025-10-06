import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Copy, ExternalLink, CheckCircle2, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { toast } from "sonner";
import { api } from "@/lib/api";

interface Alert {
  id: number;
  timestamp: string;
  symbol: string;
  address: string;
  grad_gs: number;
  gate_results: {
    locker_rep_passed: boolean;
    sniper_check_passed: boolean;
    top10_check_passed: boolean;
    lp_lock_passed: boolean;
  };
  traded: boolean;
  progress_pct: number;
}

export default function Alerts() {
  const [timeRange, setTimeRange] = useState(24);
  const [minGs, setMinGs] = useState(35);
  const [tradedFilter, setTradedFilter] = useState<boolean | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["alerts", timeRange, minGs],
    queryFn: () => api.getAlerts(timeRange, minGs),
    refetchInterval: 30000,
  });

  const filteredAlerts = tradedFilter === null 
    ? data?.alerts 
    : data?.alerts?.filter((a: Alert) => a.traded === tradedFilter);

  const copyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
    toast.success("Address copied to clipboard");
  };

  const formatRelativeTime = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    
    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
    if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}h ago`;
    return `${Math.floor(diffSecs / 86400)}d ago`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return "text-success";
    if (score >= 40) return "text-warning";
    return "text-destructive";
  };

  return (
    <div className="min-h-screen bg-background p-6 space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Alerts</h1>
        <p className="text-muted-foreground">Graduation signals and gate validation</p>
      </header>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Time Range: Last {timeRange}h
              </label>
              <Slider
                value={[timeRange]}
                onValueChange={([value]) => setTimeRange(value)}
                min={1}
                max={168}
                step={1}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Min GS Score: {minGs}
              </label>
              <Slider
                value={[minGs]}
                onValueChange={([value]) => setMinGs(value)}
                min={0}
                max={100}
                step={1}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <div className="space-y-2">
                {[
                  { label: "All", value: null },
                  { label: "Traded", value: true },
                  { label: "Not Traded", value: false },
                ].map((option) => (
                  <button
                    key={option.label}
                    onClick={() => setTradedFilter(option.value)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      tradedFilter === option.value
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary hover:bg-secondary/80"
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Alerts Grid */}
        <div className="lg:col-span-3 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>
                Showing {filteredAlerts?.length || 0} alerts
              </CardTitle>
            </CardHeader>
          </Card>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
            </div>
          ) : filteredAlerts?.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">No alerts found with current filters</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredAlerts?.map((alert: Alert) => (
                <Card key={alert.id} className="relative overflow-hidden hover:border-primary/50 transition-colors">
                  {alert.traded && (
                    <div className="absolute top-0 right-0 bg-success text-success-foreground px-3 py-1 text-xs font-bold transform rotate-45 translate-x-8 translate-y-2">
                      TRADED
                    </div>
                  )}
                  
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl">{alert.symbol}</CardTitle>
                      <a
                        href={`https://solscan.io/token/${alert.address}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary/80"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="font-mono text-xs text-muted-foreground">
                        {alert.address.slice(0, 8)}...{alert.address.slice(-4)}
                      </span>
                      <button onClick={() => copyAddress(alert.address)}>
                        <Copy className="w-3 h-3 hover:text-primary cursor-pointer" />
                      </button>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    {/* GS Score Circle */}
                    <div className="flex items-center justify-center">
                      <div className="relative w-24 h-24">
                        <svg className="w-24 h-24 transform -rotate-90">
                          <circle
                            cx="48"
                            cy="48"
                            r="40"
                            stroke="currentColor"
                            strokeWidth="8"
                            fill="none"
                            className="text-muted"
                          />
                          <circle
                            cx="48"
                            cy="48"
                            r="40"
                            stroke="currentColor"
                            strokeWidth="8"
                            fill="none"
                            strokeDasharray={`${2 * Math.PI * 40}`}
                            strokeDashoffset={`${2 * Math.PI * 40 * (1 - alert.grad_gs / 100)}`}
                            className={getScoreColor(alert.grad_gs)}
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className={`text-2xl font-bold ${getScoreColor(alert.grad_gs)}`}>
                            {alert.grad_gs.toFixed(0)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Gate Results */}
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { name: "Locker Rep", passed: alert.gate_results.locker_rep_passed },
                        { name: "Sniper Check", passed: alert.gate_results.sniper_check_passed },
                        { name: "Top 10", passed: alert.gate_results.top10_check_passed },
                        { name: "LP Lock", passed: alert.gate_results.lp_lock_passed },
                      ].map((gate) => (
                        <Badge
                          key={gate.name}
                          variant={gate.passed ? "default" : "destructive"}
                          className="justify-center"
                        >
                          {gate.passed ? (
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                          ) : (
                            <XCircle className="w-3 h-3 mr-1" />
                          )}
                          {gate.name}
                        </Badge>
                      ))}
                    </div>

                    {/* Timestamp */}
                    <p className="text-xs text-right text-muted-foreground">
                      {formatRelativeTime(alert.timestamp)}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
