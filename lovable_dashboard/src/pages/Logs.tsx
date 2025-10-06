import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { api } from "@/lib/api";
import { useHelixBot } from "@/hooks/useHelixBot";
import { Download, RefreshCw, AlertCircle, AlertTriangle, Info, Bug, Activity, Calendar, Clock } from "lucide-react";
import { toZonedTime, formatInTimeZone } from "date-fns-tz";

interface LogEntry {
  text: string;
  level: string;
  timestamp: Date | null;
  index: number;
}

interface GroupedLogs {
  today: LogEntry[];
  yesterday: LogEntry[];
  older: LogEntry[];
}

export default function Logs() {
  const [lines, setLines] = useState(500);
  const [searchTerm, setSearchTerm] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"grouped" | "stream">("grouped");
  
  const { status } = useHelixBot();

  const { data, refetch, isLoading } = useQuery({
    queryKey: ["logs", lines],
    queryFn: () => api.getLogs(lines),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  const parseLogTimestamp = (log: string): Date | null => {
    // Try to extract timestamp from log (format: YYYY-MM-DD HH:MM:SS)
    const timestampMatch = log.match(/(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})/);
    if (timestampMatch) {
      const utcDate = new Date(`${timestampMatch[1]}T${timestampMatch[2]}Z`);
      return toZonedTime(utcDate, 'America/Los_Angeles');
    }
    return null;
  };

  const getLogLevel = (log: string): string => {
    if (log.includes("ERROR") || log.includes("error")) return "error";
    if (log.includes("WARNING") || log.includes("warning") || log.includes("WARN")) return "warning";
    if (log.includes("INFO") || log.includes("info")) return "info";
    if (log.includes("DEBUG") || log.includes("debug")) return "debug";
    return "info";
  };

  const groupLogsByDate = (logs: string[]): GroupedLogs => {
    const now = toZonedTime(new Date(), 'America/Los_Angeles');
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const grouped: GroupedLogs = {
      today: [],
      yesterday: [],
      older: []
    };

    // Reverse logs so most recent is first
    const reversedLogs = [...logs].reverse();

    reversedLogs.forEach((log, index) => {
      const timestamp = parseLogTimestamp(log);
      const entry: LogEntry = {
        text: log,
        level: getLogLevel(log),
        timestamp,
        index
      };

      if (timestamp) {
        if (timestamp >= today) {
          grouped.today.push(entry);
        } else if (timestamp >= yesterday) {
          grouped.yesterday.push(entry);
        } else {
          grouped.older.push(entry);
        }
      } else {
        grouped.today.push(entry); // Logs without timestamp go to today
      }
    });

    return grouped;
  };

  const logStats = useMemo(() => {
    if (!data?.logs) return { error: 0, warning: 0, info: 0, debug: 0, total: 0 };
    
    const stats = { error: 0, warning: 0, info: 0, debug: 0, total: data.logs.length };
    data.logs.forEach((log: string) => {
      const level = getLogLevel(log);
      stats[level as keyof typeof stats]++;
    });
    return stats;
  }, [data?.logs]);

  const groupedLogs = useMemo(() => {
    if (!data?.logs) return { today: [], yesterday: [], older: [] };
    return groupLogsByDate(data.logs);
  }, [data?.logs]);

  const filteredLogs = useMemo(() => {
    if (!data?.logs) return [];
    
    let logs = [...data.logs]; // Create a copy
    
    // Reverse to show most recent first
    logs = logs.reverse();
    
    // Filter by level
    if (levelFilter !== "all") {
      logs = logs.filter((log: string) => getLogLevel(log) === levelFilter);
    }
    
    // Filter by search term
    if (searchTerm) {
      logs = logs.filter((log: string) =>
        log.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return logs;
  }, [data?.logs, levelFilter, searchTerm]);

  const formatRelativeTime = (timestamp: string) => {
    const now = toZonedTime(new Date(), 'America/Los_Angeles');
    const pstTime = toZonedTime(new Date(timestamp), 'America/Los_Angeles');
    const seconds = Math.floor((now.getTime() - pstTime.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const getLogColor = (log: string) => {
    const level = getLogLevel(log);
    switch (level) {
      case "error": return "text-destructive";
      case "warning": return "text-warning";
      case "info": return "text-foreground";
      case "debug": return "text-muted-foreground";
      default: return "text-foreground";
    }
  };

  const getLogIcon = (log: string) => {
    const level = getLogLevel(log);
    switch (level) {
      case "error": return <AlertCircle className="w-4 h-4 text-destructive" />;
      case "warning": return <AlertTriangle className="w-4 h-4 text-warning" />;
      case "info": return <Info className="w-4 h-4 text-primary" />;
      case "debug": return <Bug className="w-4 h-4 text-muted-foreground" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const downloadLogs = () => {
    const blob = new Blob([data?.logs.join("\n") || ""], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `helix-logs-${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen p-6 space-y-6">
      <LatencyIndicator />
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gradient-primary font-mono">System Logs</h1>
          <p className="text-muted-foreground font-mono text-sm mt-1">
            Most recent logs first • {status?.scanner_running ? '🟢 Live' : '🔴 Offline'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="font-mono">
            {status?.mode || 'PAPER'} Mode
          </Badge>
          {status?.timestamp && (
            <Badge variant="secondary" className="font-mono text-xs">
              Last update: {formatRelativeTime(status.timestamp)}
            </Badge>
          )}
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="border-primary/30 bg-card/80 backdrop-blur-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2 font-mono uppercase">
              <Activity className="w-4 h-4" />
              Total Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">{logStats.total}</div>
          </CardContent>
        </Card>

        <Card className="border-destructive/30 bg-card/80 backdrop-blur-sm cursor-pointer hover:border-destructive/50 transition-all" onClick={() => setLevelFilter(levelFilter === "error" ? "all" : "error")}>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2 font-mono uppercase">
              <AlertCircle className="w-4 h-4 text-destructive" />
              Errors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive font-mono">{logStats.error}</div>
            <Badge variant="destructive" className="mt-1 text-xs font-mono">
              {logStats.total > 0 ? ((logStats.error / logStats.total) * 100).toFixed(1) : 0}%
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-warning/30 bg-card/80 backdrop-blur-sm cursor-pointer hover:border-warning/50 transition-all" onClick={() => setLevelFilter(levelFilter === "warning" ? "all" : "warning")}>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2 font-mono uppercase">
              <AlertTriangle className="w-4 h-4 text-warning" />
              Warnings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-warning font-mono">{logStats.warning}</div>
            <Badge variant="secondary" className="mt-1 text-xs bg-warning/20 text-warning font-mono">
              {logStats.total > 0 ? ((logStats.warning / logStats.total) * 100).toFixed(1) : 0}%
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-primary/30 bg-card/80 backdrop-blur-sm cursor-pointer hover:border-primary/50 transition-all" onClick={() => setLevelFilter(levelFilter === "info" ? "all" : "info")}>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2 font-mono uppercase">
              <Info className="w-4 h-4 text-primary" />
              Info
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">{logStats.info}</div>
            <Badge variant="secondary" className="mt-1 text-xs font-mono">
              {logStats.total > 0 ? ((logStats.info / logStats.total) * 100).toFixed(1) : 0}%
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-muted/30 bg-card/80 backdrop-blur-sm cursor-pointer hover:border-muted/50 transition-all" onClick={() => setLevelFilter(levelFilter === "debug" ? "all" : "debug")}>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2 font-mono uppercase">
              <Bug className="w-4 h-4" />
              Debug
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-muted-foreground font-mono">{logStats.debug}</div>
            <Badge variant="outline" className="mt-1 text-xs font-mono">
              {logStats.total > 0 ? ((logStats.debug / logStats.total) * 100).toFixed(1) : 0}%
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <Card className="p-6 border-primary/30 bg-card/80 backdrop-blur-sm">
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Label className="text-sm font-mono">View:</Label>
              <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as any)}>
                <TabsList>
                  <TabsTrigger value="grouped" className="font-mono">
                    <Calendar className="w-4 h-4 mr-1" />
                    Grouped
                  </TabsTrigger>
                  <TabsTrigger value="stream" className="font-mono">
                    <Clock className="w-4 h-4 mr-1" />
                    Stream
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            <div className="flex items-center gap-2">
              <Label className="text-sm font-mono">Lines:</Label>
              <select
                value={lines}
                onChange={(e) => setLines(Number(e.target.value))}
                className="px-3 py-2 rounded-lg bg-secondary border border-border text-sm font-mono"
              >
                <option value={100}>100</option>
                <option value={500}>500</option>
                <option value={1000}>1000</option>
                <option value={2000}>2000</option>
              </select>
            </div>

            <Input
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-xs font-mono"
            />

            <div className="flex items-center gap-2">
              <Switch
                id="auto-refresh"
                checked={autoRefresh}
                onCheckedChange={setAutoRefresh}
              />
              <Label htmlFor="auto-refresh" className="text-sm font-mono">Auto-refresh (5s)</Label>
            </div>

            <Button onClick={() => refetch()} size="sm" variant="cyber">
              <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
              Refresh
            </Button>

            <Button onClick={downloadLogs} size="sm" variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          </div>

          {/* Level Filter Tabs */}
          <Tabs value={levelFilter} onValueChange={setLevelFilter}>
            <TabsList>
              <TabsTrigger value="all" className="font-mono">
                All <Badge variant="secondary" className="ml-2 font-mono">{logStats.total}</Badge>
              </TabsTrigger>
              <TabsTrigger value="error" className="font-mono">
                <AlertCircle className="w-4 h-4 mr-1" />
                Errors <Badge variant="destructive" className="ml-2 font-mono">{logStats.error}</Badge>
              </TabsTrigger>
              <TabsTrigger value="warning" className="font-mono">
                <AlertTriangle className="w-4 h-4 mr-1" />
                Warnings <Badge variant="secondary" className="ml-2 bg-warning/20 text-warning font-mono">{logStats.warning}</Badge>
              </TabsTrigger>
              <TabsTrigger value="info" className="font-mono">
                <Info className="w-4 h-4 mr-1" />
                Info <Badge variant="secondary" className="ml-2 font-mono">{logStats.info}</Badge>
              </TabsTrigger>
              <TabsTrigger value="debug" className="font-mono">
                <Bug className="w-4 h-4 mr-1" />
                Debug <Badge variant="outline" className="ml-2 font-mono">{logStats.debug}</Badge>
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </Card>

      {/* Log Viewer */}
      {viewMode === "grouped" ? (
        <Tabs defaultValue="today" className="w-full">
          <Card className="border-primary/30 bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 font-mono">
                  <Calendar className="w-5 h-5 text-primary" />
                  Grouped Logs
                  <Badge variant="outline" className="ml-2 font-mono">{filteredLogs?.length || 0} / {logStats.total}</Badge>
                </CardTitle>
                {levelFilter !== "all" && (
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => setLevelFilter("all")}
                    className="text-xs font-mono"
                  >
                    Clear Filter
                  </Button>
                )}
              </div>
              <TabsList className="mt-4">
                <TabsTrigger value="today" className="font-mono">
                  Today <Badge className="ml-2">{groupedLogs.today.length}</Badge>
                </TabsTrigger>
                <TabsTrigger value="yesterday" className="font-mono">
                  Yesterday <Badge className="ml-2">{groupedLogs.yesterday.length}</Badge>
                </TabsTrigger>
                <TabsTrigger value="older" className="font-mono">
                  Older <Badge className="ml-2">{groupedLogs.older.length}</Badge>
                </TabsTrigger>
              </TabsList>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-12">
                  <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
                  <p className="text-muted-foreground mt-4 font-mono">Loading logs...</p>
                </div>
              ) : (
                <>
                  <TabsContent value="today">
                    {renderLogGroup(groupedLogs.today, "No logs today")}
                  </TabsContent>
                  <TabsContent value="yesterday">
                    {renderLogGroup(groupedLogs.yesterday, "No logs yesterday")}
                  </TabsContent>
                  <TabsContent value="older">
                    {renderLogGroup(groupedLogs.older, "No older logs")}
                  </TabsContent>
                </>
              )}
            </CardContent>
          </Card>
        </Tabs>
      ) : (
        <Card className="p-6 bg-[#0a0a0f] border-primary/30 bg-card/80 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2 font-mono">
              <Clock className="w-5 h-5 text-primary" />
              Log Stream
              <Badge variant="outline" className="ml-2 font-mono">{filteredLogs?.length || 0} / {logStats.total} lines</Badge>
            </h2>
            {levelFilter !== "all" && (
              <Button 
                size="sm" 
                variant="ghost" 
                onClick={() => setLevelFilter("all")}
                className="text-xs font-mono"
              >
                Clear Filter
              </Button>
            )}
          </div>
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
              <p className="text-muted-foreground mt-4 font-mono">Loading logs...</p>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="font-mono">No logs found matching your filters</p>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => { setLevelFilter("all"); setSearchTerm(""); }}
                className="mt-4 font-mono"
              >
                Clear All Filters
              </Button>
            </div>
          ) : (
            <div className="bg-[#0a0a0f] rounded-lg p-4 h-[600px] overflow-y-auto font-mono text-xs border border-border/50 scroll-smooth">
              <div className="space-y-0.5">
                {filteredLogs?.map((log: string, index: number) => (
                  <div key={index} className="flex gap-3 py-2 hover:bg-muted/10 rounded px-2 transition-colors group border-b border-border/20">
                    <span className="text-primary/60 text-right w-16 flex-shrink-0 select-none font-semibold">
                      #{filteredLogs.length - index}
                    </span>
                    <span className="flex-shrink-0 mt-0.5">
                      {getLogIcon(log)}
                    </span>
                    <span className={`${getLogColor(log)} flex-1 break-all leading-relaxed`}>{log}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

function renderLogGroup(logs: LogEntry[], emptyMessage: string) {
  if (logs.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p className="font-mono">{emptyMessage}</p>
      </div>
    );
  }

  const getLogColor = (level: string) => {
    switch (level) {
      case "error": return "text-destructive";
      case "warning": return "text-warning";
      case "info": return "text-foreground";
      case "debug": return "text-muted-foreground";
      default: return "text-foreground";
    }
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case "error": return <AlertCircle className="w-4 h-4 text-destructive" />;
      case "warning": return <AlertTriangle className="w-4 h-4 text-warning" />;
      case "info": return <Info className="w-4 h-4 text-primary" />;
      case "debug": return <Bug className="w-4 h-4 text-muted-foreground" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-[#0a0a0f] rounded-lg p-4 h-[600px] overflow-y-auto font-mono text-xs border border-border/50 scroll-smooth">
      <div className="space-y-0.5">
        {logs.map((entry) => (
          <div key={entry.index} className="flex gap-3 py-2 hover:bg-muted/10 rounded px-2 transition-colors group border-b border-border/20">
            <span className="text-primary/60 text-right w-16 flex-shrink-0 select-none font-semibold">
              #{logs.length - logs.indexOf(entry)}
            </span>
            <span className="flex-shrink-0 mt-0.5">
              {getLogIcon(entry.level)}
            </span>
            {entry.timestamp && (
              <span className="text-primary/40 text-xs flex-shrink-0 font-semibold">
                {formatInTimeZone(entry.timestamp, 'America/Los_Angeles', 'HH:mm:ss')} PST
              </span>
            )}
            <span className={`${getLogColor(entry.level)} flex-1 break-all leading-relaxed`}>{entry.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
