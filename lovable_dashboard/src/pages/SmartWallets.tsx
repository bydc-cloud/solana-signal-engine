import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { LatencyIndicator } from "@/components/LatencyIndicator";
import { Wallet, TrendingUp, Copy, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function SmartWallets() {
  const [trackedWallets, setTrackedWallets] = useState<any[]>([]);
  const [walletTrades, setWalletTrades] = useState<any[]>([]);
  const [stats, setStats] = useState({ total: 0, bestPerformer: "N/A", mirrorTrades: 0 });
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<string>("pnl_30d");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [walletsData, tradesData] = await Promise.all([
        api.getTrackedWallets(),
        api.getWalletTrades(),
      ]);
      
      setTrackedWallets(walletsData.wallets || []);
      setWalletTrades(tradesData.trades || []);
      setStats({
        total: walletsData.wallets?.length || 0,
        bestPerformer: walletsData.best_performer || "N/A",
        mirrorTrades: tradesData.total_mirror_trades || 0,
      });
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch wallet data:", error);
      setLoading(false);
    }
  };

  const copyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
    toast.success("Address copied!");
  };

  const truncateAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  const formatPnL = (value: number) => {
    const formatted = value >= 0 ? `+$${value.toFixed(2)}` : `-$${Math.abs(value).toFixed(2)}`;
    return <span className={value >= 0 ? "text-success" : "text-destructive"}>{formatted}</span>;
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const sortedWallets = [...trackedWallets].sort((a, b) => {
    const aVal = a[sortField] ?? 0;
    const bVal = b[sortField] ?? 0;
    if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return <span className="text-muted-foreground/30 ml-1">↕</span>;
    return <span className="text-primary ml-1">{sortDirection === "asc" ? "↑" : "↓"}</span>;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Smart Wallets</h1>
          <p className="text-muted-foreground">Track high-performing wallets and their trades</p>
        </div>
        <LatencyIndicator />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tracked</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">Active wallets</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Best 24h Performer</CardTitle>
            <TrendingUp className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.bestPerformer}</div>
            <p className="text-xs text-muted-foreground">Top wallet</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Mirror Trades</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.mirrorTrades}</div>
            <p className="text-xs text-muted-foreground">Last 24h</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="wallets">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="wallets">Tracked Wallets</TabsTrigger>
              <TabsTrigger value="trades">Wallet Trades</TabsTrigger>
            </TabsList>

            <TabsContent value="wallets" className="mt-6">
              {loading ? (
                <div className="text-center py-8 text-muted-foreground">Loading wallets...</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Address</TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("label")}
                      >
                        <div className="flex items-center">Label <SortIcon field="label" /></div>
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("pnl_1d")}
                      >
                        <div className="flex items-center">1d P&L <SortIcon field="pnl_1d" /></div>
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("pnl_30d")}
                      >
                        <div className="flex items-center">30d P&L <SortIcon field="pnl_30d" /></div>
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("win_rate")}
                      >
                        <div className="flex items-center">Win Rate <SortIcon field="win_rate" /></div>
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:text-primary transition-colors select-none"
                        onClick={() => handleSort("total_trades")}
                      >
                        <div className="flex items-center">Trades <SortIcon field="total_trades" /></div>
                      </TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedWallets.map((wallet, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-mono">
                          <div className="flex items-center gap-2">
                            {truncateAddress(wallet.address)}
                            <Copy
                              className="w-3 h-3 cursor-pointer text-muted-foreground hover:text-foreground"
                              onClick={() => copyAddress(wallet.address)}
                            />
                          </div>
                        </TableCell>
                        <TableCell>{wallet.label}</TableCell>
                        <TableCell>{formatPnL(wallet.pnl_1d)}</TableCell>
                        <TableCell>{formatPnL(wallet.pnl_30d)}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={wallet.win_rate} className="w-20" />
                            <span className="text-sm">{wallet.win_rate}%</span>
                          </div>
                        </TableCell>
                        <TableCell>{wallet.total_trades}</TableCell>
                        <TableCell>
                          <a
                            href={`https://solscan.io/account/${wallet.address}`}
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
            </TabsContent>

            <TabsContent value="trades" className="mt-6">
              {loading ? (
                <div className="text-center py-8 text-muted-foreground">Loading trades...</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Wallet Label</TableHead>
                      <TableHead>Token</TableHead>
                      <TableHead>Side</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Time</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {walletTrades.map((trade, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">{trade.wallet_label}</TableCell>
                        <TableCell className="font-mono">{trade.token}</TableCell>
                        <TableCell>
                          <Badge variant={trade.side === "BUY" ? "default" : "destructive"}>
                            {trade.side}
                          </Badge>
                        </TableCell>
                        <TableCell>${trade.amount.toFixed(2)}</TableCell>
                        <TableCell className="text-muted-foreground">{trade.time}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
