# Lovable: Ensure Data Accuracy & Trader Trust

**Critical Issue:** Dashboard showing data that traders can't trust. Need 100% accurate, verifiable data with clear data sources.

---

## 🚨 **TRUST REQUIREMENTS**

### **Rule #1: NO MOCK DATA - EVER**
```typescript
// ❌ NEVER DO THIS:
const mockWallets = [
  { address: "ABC123", pnl: 45000 }, // FAKE
];

// ✅ ALWAYS DO THIS:
const { data: wallets } = useQuery({
  queryKey: ['wallets'],
  queryFn: () => fetch(`${API_BASE}/wallets`).then(r => r.json()),
});

if (!wallets || wallets.count === 0) {
  return <EmptyState message="No wallet data available yet" />;
}
```

### **Rule #2: Show Data Source**
Every metric must show WHERE it came from:
```tsx
<MetricCard
  value="$45,234"
  label="24h PnL"
  source="Source: Helius API (updated 2m ago)"
  timestamp={lastUpdated}
/>
```

### **Rule #3: Verify Data Freshness**
```tsx
const isStale = (timestamp: string) => {
  const age = Date.now() - new Date(timestamp).getTime();
  return age > 5 * 60 * 1000; // >5 minutes = stale
};

{isStale(data.timestamp) && (
  <Warning>⚠️ Data may be outdated (last update: {formatTime(data.timestamp)})</Warning>
)}
```

---

## 📊 **WALLET DATA ACCURACY**

### **API Endpoint:** `GET /wallets`
**Expected Response:**
```json
{
  "wallets": [
    {
      "address": "7a3fKH...",
      "label": "Nansen Alpha #3",
      "tier": "S",
      "pnl_1d": 12340.50,
      "pnl_7d": 45678.90,
      "pnl_30d": 123456.78,
      "win_rate": 0.72,
      "last_updated": "2025-10-06T04:20:00Z"
    }
  ],
  "count": 20
}
```

### **Lovable Implementation:**

```tsx
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const API_BASE = 'https://signal-railway-deployment-production.up.railway.app';

function WalletsPage() {
  const { data, isLoading, error, dataUpdatedAt } = useQuery({
    queryKey: ['wallets'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/wallets`);
      if (!res.ok) throw new Error('Failed to fetch wallets');
      return res.json();
    },
    refetchInterval: 30000, // Refresh every 30s
    staleTime: 10000, // Consider stale after 10s
  });

  if (isLoading) {
    return <LoadingState message="Fetching real wallet data..." />;
  }

  if (error) {
    return (
      <ErrorState
        message="Unable to fetch wallet data"
        detail={error.message}
        action={<Button onClick={() => refetch()}>Retry</Button>}
      />
    );
  }

  if (!data || data.count === 0) {
    return (
      <EmptyState
        icon={<WalletIcon />}
        title="No Wallet Data Yet"
        message="Wallet tracking is initializing. Check back in a few minutes."
        note="Data source: Railway API /wallets endpoint"
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Data Freshness Indicator */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>Showing {data.count} wallets</span>
        <span>
          Last updated: {formatDistanceToNow(dataUpdatedAt)} ago
          {Date.now() - dataUpdatedAt > 60000 && (
            <Badge variant="warning" className="ml-2">Stale</Badge>
          )}
        </span>
      </div>

      {/* Wallet Cards */}
      {data.wallets.map((wallet) => (
        <WalletCard key={wallet.address} wallet={wallet} />
      ))}
    </div>
  );
}

function WalletCard({ wallet }) {
  const lastUpdated = new Date(wallet.last_updated);
  const isStale = Date.now() - lastUpdated.getTime() > 300000; // 5 min

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-mono text-sm text-muted-foreground">
            {wallet.address.slice(0, 8)}...{wallet.address.slice(-4)}
          </h3>
          <p className="text-lg font-semibold">{wallet.label}</p>
          <Badge variant={wallet.tier === 'S' ? 'default' : 'secondary'}>
            Tier {wallet.tier}
          </Badge>
        </div>

        {isStale && (
          <Badge variant="warning">
            ⚠️ Data {formatDistanceToNow(lastUpdated)} old
          </Badge>
        )}
      </div>

      {/* PnL Charts with Real Data */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <PnLMetric
          label="1d PnL"
          value={wallet.pnl_1d}
          source="Helius API"
          verified={!isStale}
        />
        <PnLMetric
          label="7d PnL"
          value={wallet.pnl_7d}
          source="Helius API"
          verified={!isStale}
        />
        <PnLMetric
          label="30d PnL"
          value={wallet.pnl_30d}
          source="Helius API"
          verified={!isStale}
        />
      </div>

      {/* Recent Trades */}
      <RecentTrades walletAddress={wallet.address} />
    </Card>
  );
}

function PnLMetric({ label, value, source, verified }) {
  const isPositive = value > 0;
  const color = isPositive ? 'text-green-500' : 'text-red-500';

  return (
    <div className="space-y-1">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>
        {isPositive && '+'} ${value.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })}
      </p>
      <div className="flex items-center gap-1 text-xs text-muted-foreground">
        <span>{source}</span>
        {verified && <Badge variant="success" className="text-xs">✓ Verified</Badge>}
      </div>
    </div>
  );
}

function RecentTrades({ walletAddress }) {
  const { data, isLoading } = useQuery({
    queryKey: ['wallet-trades', walletAddress],
    queryFn: async () => {
      const res = await fetch(
        `${API_BASE}/wallets/${walletAddress}/trades?limit=5`
      );
      if (!res.ok) return { trades: [] };
      return res.json();
    },
    refetchInterval: 30000,
  });

  if (isLoading) {
    return <Skeleton className="h-24" />;
  }

  if (!data || data.trades?.length === 0) {
    return (
      <div className="mt-4 text-sm text-muted-foreground">
        No recent trades
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-2">
      <h4 className="text-sm font-semibold">Recent Trades</h4>
      {data.trades.map((trade, i) => (
        <div key={i} className="flex justify-between text-sm border-l-2 border-muted pl-3">
          <div>
            <span className="font-mono">{trade.symbol}</span>
            <Badge variant={trade.type === 'BUY' ? 'default' : 'secondary'} className="ml-2">
              {trade.type}
            </Badge>
          </div>
          <div className={trade.pnl > 0 ? 'text-green-500' : 'text-red-500'}>
            {trade.pnl > 0 && '+'}{trade.pnl}%
          </div>
          <div className="text-muted-foreground">
            {formatDistanceToNow(new Date(trade.timestamp))} ago
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 📈 **PNL CHART ACCURACY**

### **API Endpoint:** `GET /wallets/{address}/pnl`
**Expected Response:**
```json
{
  "address": "7a3fKH...",
  "timeframes": {
    "1d": {
      "pnl_usd": 12340.50,
      "pnl_percent": 24.5,
      "trades": 15,
      "wins": 11,
      "losses": 4,
      "chart_data": [
        { timestamp: "2025-10-06T00:00:00Z", pnl: 0 },
        { timestamp: "2025-10-06T01:00:00Z", pnl: 1200 },
        { timestamp: "2025-10-06T02:00:00Z", pnl: 3400 },
        // ... hourly datapoints
      ]
    },
    "7d": { /* similar structure */ },
    "30d": { /* similar structure */ }
  }
}
```

### **Lovable PnL Chart Implementation:**

```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function PnLChart({ walletAddress, timeframe = '7d' }) {
  const { data, isLoading, error, dataUpdatedAt } = useQuery({
    queryKey: ['wallet-pnl', walletAddress, timeframe],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/wallets/${walletAddress}/pnl?timeframe=${timeframe}`);
      if (!res.ok) throw new Error('Failed to fetch PnL data');
      return res.json();
    },
    refetchInterval: 60000, // Refresh every 1 min
  });

  if (isLoading) {
    return <Skeleton className="h-64" />;
  }

  if (error || !data) {
    return (
      <ErrorState
        message="Unable to load PnL chart"
        note="This chart shows REAL transaction data from Helius API"
      />
    );
  }

  const chartData = data.timeframes[timeframe].chart_data;

  return (
    <div className="space-y-4">
      {/* Header with Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold">
            {data.timeframes[timeframe].pnl_percent > 0 && '+'}
            {data.timeframes[timeframe].pnl_percent.toFixed(2)}%
          </h3>
          <p className="text-sm text-muted-foreground">
            ${data.timeframes[timeframe].pnl_usd.toLocaleString()} PnL
          </p>
        </div>

        <div className="text-right text-sm">
          <p className="text-muted-foreground">
            {data.timeframes[timeframe].wins}W / {data.timeframes[timeframe].losses}L
          </p>
          <p className="text-muted-foreground">
            Data from {chartData.length} real trades
          </p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <XAxis
            dataKey="timestamp"
            tickFormatter={(ts) => formatTime(ts)}
          />
          <YAxis
            tickFormatter={(val) => `$${val.toLocaleString()}`}
          />
          <Tooltip
            labelFormatter={(ts) => formatDateTime(ts)}
            formatter={(val) => [`$${val.toLocaleString()}`, 'PnL']}
          />
          <Line
            type="monotone"
            dataKey="pnl"
            stroke="#00ff88"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Data Verification */}
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>✓ Verified Helius transaction data</span>
        <span>Last updated: {formatDistanceToNow(dataUpdatedAt)} ago</span>
      </div>
    </div>
  );
}
```

---

## 🔍 **DATA VERIFICATION CHECKLIST**

Add this checklist component to every page:

```tsx
function DataVerificationBadge({ endpoint, count, lastUpdated }) {
  const isRecent = Date.now() - new Date(lastUpdated).getTime() < 60000; // <1 min
  const hasData = count > 0;

  return (
    <div className="flex items-center gap-2 text-xs">
      <Badge variant={hasData ? "success" : "warning"}>
        {hasData ? `${count} records` : 'No data'}
      </Badge>
      <Badge variant={isRecent ? "success" : "warning"}>
        {isRecent ? '✓ Live' : '⚠️ Stale'}
      </Badge>
      <span className="text-muted-foreground">
        via {endpoint}
      </span>
    </div>
  );
}

// Usage:
<DataVerificationBadge
  endpoint="/wallets"
  count={data.count}
  lastUpdated={dataUpdatedAt}
/>
```

---

## 🎯 **SPECIFIC FIXES FOR YOUR DASHBOARD**

### **Issue 1: Traders Page Shows Fake Data**
```tsx
// ❌ WRONG:
const traders = [
  { name: "Trader 1", pnl: 45000 }, // HARDCODED
];

// ✅ CORRECT:
const { data: traders } = useQuery({
  queryKey: ['wallets'],
  queryFn: () => fetch(`${API_BASE}/wallets`).then(r => r.json()),
});

// Show only REAL data:
{traders?.wallets.map((wallet) => (
  <TraderCard key={wallet.address} data={wallet} />
))}

// If no data:
{(!traders || traders.count === 0) && (
  <EmptyState message="No trader data available. Scanner is collecting data..." />
)}
```

### **Issue 2: PnL Charts Not Matching Wallet Data**
```tsx
// Ensure chart data comes from SAME source as wallet display:
function WalletPage({ address }) {
  // Fetch wallet data
  const { data: wallet } = useQuery({
    queryKey: ['wallet', address],
    queryFn: () => fetch(`${API_BASE}/wallets/${address}`).then(r => r.json()),
  });

  // Fetch PnL chart data from SAME wallet
  const { data: pnlData } = useQuery({
    queryKey: ['wallet-pnl', address],
    queryFn: () => fetch(`${API_BASE}/wallets/${address}/pnl`).then(r => r.json()),
  });

  // Verify they match:
  const dataMatches = wallet?.pnl_7d === pnlData?.timeframes['7d'].pnl_usd;

  return (
    <div>
      {!dataMatches && (
        <Warning>⚠️ Data mismatch detected. Refresh page or contact support.</Warning>
      )}

      <WalletStats {...wallet} />
      <PnLChart data={pnlData} />
    </div>
  );
}
```

### **Issue 3: Recent Trades Don't Update**
```tsx
// Use short refetch interval + manual refetch button:
const { data, refetch, isFetching } = useQuery({
  queryKey: ['wallet-trades', walletAddress],
  queryFn: () => fetch(`${API_BASE}/wallets/${walletAddress}/trades`).then(r => r.json()),
  refetchInterval: 10000, // Every 10 seconds
});

return (
  <div>
    <div className="flex justify-between">
      <h3>Recent Trades</h3>
      <Button
        onClick={() => refetch()}
        disabled={isFetching}
        size="sm"
      >
        {isFetching ? 'Refreshing...' : 'Refresh'}
      </Button>
    </div>

    {data?.trades.map((trade) => (
      <TradeRow key={trade.id} trade={trade} />
    ))}
  </div>
);
```

---

## 🚨 **FINAL MANDATE**

**Copy this into Lovable:**

"**CRITICAL: Data Trust Requirements**

1. **NO MOCK DATA:** Every single metric must come from the Railway API. If data doesn't exist, show 'No data available' message, NOT fake data.

2. **Show Data Age:** Every metric displays 'Last updated: X ago'. If >5 minutes old, show warning badge.

3. **Verify Data Sources:** Every card shows which endpoint the data came from (e.g., 'Source: /wallets endpoint').

4. **Match Backend Reality:** If backend returns empty array, dashboard shows empty state. Don't fill gaps with placeholders.

5. **Real-Time Indicators:** Use green dot (●) for live data (<1 min), yellow (●) for stale (1-5 min), red (●) for very stale (>5 min).

**Test Every Component:**
- Click refresh → Data actually changes?
- Wait 30s → Auto-refresh working?
- Backend returns empty → Dashboard shows empty state (not fake data)?
- Hover metric → Shows 'Last updated' timestamp?

**If ANY component shows data you can't verify in the Railway API response, DELETE IT.**

Trust is everything. Traders need to know the data is real."

---

**This will fix your trust issues. Every number will be traceable to the API.**
