import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { api } from "@/lib/api";
import { ExternalLink, Copy } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { TokenLogo } from "@/components/TokenLogo";

export default function Trades() {
  const [timeFilter, setTimeFilter] = useState("24");
  const [sortField, setSortField] = useState<string>("timestamp");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const { data: trades, isLoading } = useQuery({
    queryKey: ["trades", timeFilter],
    queryFn: () => api.getTrades(Number(timeFilter), "PAPER"),
    refetchInterval: 30000,
  });

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const sortedTrades = [...(trades?.trades || [])].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];
    
    if (sortField === "timestamp") {
      aVal = new Date(aVal).getTime();
      bVal = new Date(bVal).getTime();
    }
    
    if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return <span className="text-muted-foreground/30 ml-1">↕</span>;
    return <span className="text-primary ml-1">{sortDirection === "asc" ? "↑" : "↓"}</span>;
  };

  const copyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
    toast({ title: "Address copied!" });
  };

  const formatRelativeTime = (timestamp: string) => {
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return `${Math.floor(seconds / 3600)}h ago`;
  };

  return (
    <div className="min-h-screen p-8 space-y-8 mesh-gradient">
      <LatencyIndicator />
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold text-gradient-primary mb-2 neon-text">Trades</h1>
          <p className="text-muted-foreground text-lg">Executed trading history</p>
        </div>
      </div>

      <Tabs value={timeFilter} onValueChange={setTimeFilter}>
        <TabsList>
          <TabsTrigger value="1">1h</TabsTrigger>
          <TabsTrigger value="6">6h</TabsTrigger>
          <TabsTrigger value="24">24h</TabsTrigger>
          <TabsTrigger value="168">7d</TabsTrigger>
        </TabsList>

        <TabsContent value={timeFilter} className="mt-6">
          <Card className="card-premium p-6">
            <h2 className="text-xl font-bold mb-4">
              Recent Trades ({trades?.total || 0})
            </h2>
            <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("timestamp")}
                      >
                        <div className="flex items-center">Time <SortIcon field="timestamp" /></div>
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("symbol")}
                      >
                        <div className="flex items-center">Symbol <SortIcon field="symbol" /></div>
                      </TableHead>
                      <TableHead>Address</TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("grad_gs")}
                      >
                        <div className="flex items-center">GS <SortIcon field="grad_gs" /></div>
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("size_pct")}
                      >
                        <div className="flex items-center">Size % <SortIcon field="size_pct" /></div>
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("mode")}
                      >
                        <div className="flex items-center">Mode <SortIcon field="mode" /></div>
                      </TableHead>
                      <TableHead>Route</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedTrades?.map((trade: any, idx: number) => (
                    <TableRow key={idx}>
                      <TableCell className="text-muted-foreground text-sm">
                        {formatRelativeTime(trade.timestamp)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <TokenLogo address={trade.address} symbol={trade.symbol} size="sm" />
                          <a
                            href={`https://solscan.io/token/${trade.address}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-semibold hover:text-primary flex items-center gap-1"
                          >
                            {trade.symbol}
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <code className="text-xs">{trade.address.slice(0, 8)}...</code>
                          <button onClick={() => copyAddress(trade.address)} className="hover:text-primary">
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono">{trade.grad_gs?.toFixed(0) || 0}</TableCell>
                      <TableCell className="font-mono">{trade.size_pct?.toFixed(1)}%</TableCell>
                      <TableCell>
                        <Badge variant={trade.mode === "LIVE" ? "destructive" : "secondary"}>
                          {trade.mode}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">{trade.route}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{trade.status}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
