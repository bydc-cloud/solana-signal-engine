import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { Copy, ExternalLink, TrendingUp, DollarSign, Target } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function MirrorTrades() {
  const [trades, setTrades] = useState<any[]>([]);
  const [stats, setStats] = useState({ total24h: 0, volumeMirrored: 0, successRate: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const data = await api.getMirrorTrades();
      setTrades(data.trades || []);
      setStats({
        total24h: data.total_24h || 0,
        volumeMirrored: data.volume_mirrored || 0,
        successRate: data.success_rate || 0,
      });
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch mirror trades:", error);
      setLoading(false);
    }
  };

  const copyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
    toast.success("Address copied!");
  };

  const truncateAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "success":
        return "default";
      case "pending":
        return "secondary";
      case "failed":
        return "destructive";
      default:
        return "outline";
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mirror Trades</h1>
          <p className="text-muted-foreground">Track trades copied from smart wallets</p>
        </div>
        <LatencyIndicator />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Mirror Trades 24h</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.total24h}</div>
            <p className="text-xs text-muted-foreground">Executed trades</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Volume Mirrored</CardTitle>
            <DollarSign className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">${stats.volumeMirrored.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Last 24h</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <Target className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.successRate}%</div>
            <p className="text-xs text-muted-foreground">Trade success rate</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Mirror Trade History</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading mirror trades...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Token</TableHead>
                  <TableHead>Side</TableHead>
                  <TableHead>Our Amount</TableHead>
                  <TableHead>Copied From</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {trades.map((trade, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-mono">{trade.token}</TableCell>
                    <TableCell>
                      <Badge variant={trade.side === "BUY" ? "default" : "destructive"}>
                        {trade.side}
                      </Badge>
                    </TableCell>
                    <TableCell>${trade.our_amount.toFixed(2)}</TableCell>
                    <TableCell className="font-mono">
                      <div className="flex items-center gap-2">
                        {truncateAddress(trade.copied_from)}
                        <Copy
                          className="w-3 h-3 cursor-pointer text-muted-foreground hover:text-foreground"
                          onClick={() => copyAddress(trade.copied_from)}
                        />
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{trade.time}</TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(trade.status)}>{trade.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <a
                        href={`https://solscan.io/token/${trade.token}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary/80"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
