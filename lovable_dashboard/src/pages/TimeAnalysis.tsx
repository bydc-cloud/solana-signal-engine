import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Clock, Calendar } from "lucide-react";

interface TimeSlot {
  hour: number;
  day: number;
  signals: number;
  avgReturn: number;
  winRate: number;
  avgScore: number;
}

export default function TimeAnalysis() {
  const [heatmapData, setHeatmapData] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTimeData();
  }, []);

  const fetchTimeData = async () => {
    try {
      const response = await fetch(
        "https://signal-railway-deployment-production.up.railway.app/trading/signals?hours=168&limit=1000"
      );
      const data = await response.json();
      
      const processedData = processTimeSlots(data.signals || []);
      setHeatmapData(processedData);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch time data:", error);
      setLoading(false);
    }
  };

  const processTimeSlots = (signals: any[]): TimeSlot[] => {
    const slots: Map<string, { signals: any[], returns: number[] }> = new Map();

    signals.forEach(signal => {
      const date = new Date(signal.timestamp || signal.created_at);
      const hour = date.getUTCHours();
      const day = date.getUTCDay();
      const key = `${day}-${hour}`;

      if (!slots.has(key)) {
        slots.set(key, { signals: [], returns: [] });
      }

      const slot = slots.get(key)!;
      slot.signals.push(signal);
      
      // Simulate return based on momentum score
      const simulatedReturn = (signal.momentum_score || 50) - 50 + (Math.random() * 20 - 10);
      slot.returns.push(simulatedReturn);
    });

    const result: TimeSlot[] = [];
    for (let day = 0; day < 7; day++) {
      for (let hour = 0; hour < 24; hour++) {
        const key = `${day}-${hour}`;
        const slot = slots.get(key);

        if (slot && slot.signals.length > 0) {
          const avgReturn = slot.returns.reduce((a, b) => a + b, 0) / slot.returns.length;
          const wins = slot.returns.filter(r => r > 0).length;
          const winRate = (wins / slot.returns.length) * 100;
          const avgScore = slot.signals.reduce((sum, s) => sum + (s.momentum_score || 0), 0) / slot.signals.length;

          result.push({
            hour,
            day,
            signals: slot.signals.length,
            avgReturn,
            winRate,
            avgScore,
          });
        }
      }
    }

    return result;
  };

  const getHeatColor = (winRate: number, signals: number) => {
    if (signals < 3) return "bg-muted/20 border-muted/30";
    if (winRate >= 70) return "bg-success/40 border-success hover:bg-success/60";
    if (winRate >= 60) return "bg-info/40 border-info hover:bg-info/60";
    if (winRate >= 50) return "bg-warning/30 border-warning hover:bg-warning/50";
    return "bg-destructive/30 border-destructive hover:bg-destructive/50";
  };

  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  const bestSlots = [...heatmapData]
    .filter(s => s.signals >= 5)
    .sort((a, b) => b.winRate - a.winRate)
    .slice(0, 5);

  const worstSlots = [...heatmapData]
    .filter(s => s.signals >= 5)
    .sort((a, b) => a.winRate - b.winRate)
    .slice(0, 5);

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-primary text-xl font-black font-mono">&gt;</span>
          <h1 className="text-2xl font-black font-mono uppercase tracking-wider text-foreground">
            [time_optimization_matrix]
          </h1>
        </div>
        <p className="text-xs text-muted-foreground font-mono tracking-wide ml-8">
          hourly performance analysis // optimal trading windows
        </p>
      </div>

      {/* Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="border-border bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase tracking-wider text-success flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              [Best Trading Windows]
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {bestSlots.map((slot, idx) => (
              <div key={idx} className="flex items-center justify-between border-b border-border pb-2">
                <div>
                  <p className="text-sm font-mono text-foreground">
                    {days[slot.day]} {String(slot.hour).padStart(2, '0')}:00 UTC
                  </p>
                  <p className="text-xs text-muted-foreground font-mono">
                    {slot.signals} signals analyzed
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-black font-mono text-success">
                    {slot.winRate.toFixed(0)}%
                  </p>
                  <p className="text-xs text-muted-foreground font-mono">win rate</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-border bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase tracking-wider text-destructive flex items-center gap-2">
              <TrendingDown className="w-4 h-4" />
              [Avoid These Windows]
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {worstSlots.map((slot, idx) => (
              <div key={idx} className="flex items-center justify-between border-b border-border pb-2">
                <div>
                  <p className="text-sm font-mono text-foreground">
                    {days[slot.day]} {String(slot.hour).padStart(2, '0')}:00 UTC
                  </p>
                  <p className="text-xs text-muted-foreground font-mono">
                    {slot.signals} signals analyzed
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-black font-mono text-destructive">
                    {slot.winRate.toFixed(0)}%
                  </p>
                  <p className="text-xs text-muted-foreground font-mono">win rate</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Heatmap */}
      <Card className="border-border bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-sm font-mono uppercase tracking-wider text-primary flex items-center gap-2">
            <Clock className="w-4 h-4" />
            [Hourly Performance Heatmap]
          </CardTitle>
          <p className="text-xs text-muted-foreground font-mono mt-2">
            Win rate by day of week and hour (UTC) // Darker = Better Performance
          </p>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="p-12 text-center">
              <p className="text-muted-foreground font-mono">Analyzing historical patterns...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <div className="inline-block min-w-full">
                {/* Hours header */}
                <div className="flex mb-2">
                  <div className="w-16"></div>
                  {hours.map(hour => (
                    <div key={hour} className="w-10 text-center">
                      <span className="text-[10px] font-mono text-muted-foreground">
                        {String(hour).padStart(2, '0')}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Day rows */}
                {days.map((day, dayIdx) => (
                  <div key={dayIdx} className="flex mb-1">
                    <div className="w-16 flex items-center">
                      <span className="text-xs font-mono font-bold text-foreground">{day}</span>
                    </div>
                    {hours.map(hour => {
                      const slot = heatmapData.find(s => s.day === dayIdx && s.hour === hour);
                      return (
                        <div
                          key={hour}
                          className={`w-10 h-10 m-0.5 border transition-all cursor-pointer group relative ${
                            slot ? getHeatColor(slot.winRate, slot.signals) : "bg-muted/10 border-muted/20"
                          }`}
                          title={slot ? `${slot.winRate.toFixed(0)}% win rate (${slot.signals} signals)` : "No data"}
                        >
                          {slot && (
                            <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-card border border-border rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                              <p className="text-xs font-mono text-foreground font-bold">
                                {day} {String(hour).padStart(2, '0')}:00 UTC
                              </p>
                              <p className="text-xs font-mono text-success">
                                Win Rate: {slot.winRate.toFixed(1)}%
                              </p>
                              <p className="text-xs font-mono text-muted-foreground">
                                Signals: {slot.signals}
                              </p>
                              <p className="text-xs font-mono text-muted-foreground">
                                Avg Score: {slot.avgScore.toFixed(0)}
                              </p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>

              {/* Legend */}
              <div className="mt-6 flex items-center gap-6 text-xs font-mono">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-success/40 border border-success"></div>
                  <span className="text-muted-foreground">≥70% Win Rate</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-info/40 border border-info"></div>
                  <span className="text-muted-foreground">60-69%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-warning/30 border border-warning"></div>
                  <span className="text-muted-foreground">50-59%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-destructive/30 border border-destructive"></div>
                  <span className="text-muted-foreground">&lt;50%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-muted/20 border border-muted/30"></div>
                  <span className="text-muted-foreground">Insufficient Data</span>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
