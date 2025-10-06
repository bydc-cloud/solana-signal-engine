import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Twitter as TwitterIcon, TrendingUp, Activity, ExternalLink, RefreshCw } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useHelixBot } from "@/hooks/useHelixBot";

interface TwitterSignal {
  id: number;
  twitter_handle: string;
  account_name: string;
  tier: string;
  tweet_text: string;
  tweet_url: string;
  created_at: string;
  mentions_tokens: string;
  sentiment: string;
  signal_strength: number;
  retweet_count: number;
  like_count: number;
}

interface TrendingToken {
  token: string;
  mention_count: number;
  avg_strength: number;
  mentioned_by: string[];
}

// Mock data for testing/demo
const mockSignals: TwitterSignal[] = [
  {
    id: 1,
    twitter_handle: "cryptowhale",
    account_name: "Crypto Whale",
    tier: "S",
    tweet_text: "Just bought a huge bag of $PEPE. This one is going to moon! Diamond hands 💎",
    tweet_url: "https://twitter.com/cryptowhale/status/123",
    created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    mentions_tokens: "$PEPE",
    sentiment: "bullish",
    signal_strength: 85,
    retweet_count: 342,
    like_count: 1205,
  },
  {
    id: 2,
    twitter_handle: "degen_trader",
    account_name: "Degen Trader",
    tier: "A",
    tweet_text: "Exiting my $DOGE position. Market looking weak here.",
    tweet_url: "https://twitter.com/degen_trader/status/124",
    created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    mentions_tokens: "$DOGE",
    sentiment: "bearish",
    signal_strength: 72,
    retweet_count: 128,
    like_count: 456,
  },
  {
    id: 3,
    twitter_handle: "meme_king",
    account_name: "Meme King",
    tier: "S",
    tweet_text: "Alert: Heavy accumulation on $SHIB. Smart money is loading up.",
    tweet_url: "https://twitter.com/meme_king/status/125",
    created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    mentions_tokens: "$SHIB",
    sentiment: "bullish",
    signal_strength: 91,
    retweet_count: 567,
    like_count: 2103,
  },
];

const mockTrending: TrendingToken[] = [
  {
    token: "$PEPE",
    mention_count: 47,
    avg_strength: 82.5,
    mentioned_by: ["cryptowhale", "pepe_master", "degen_ape", "moon_boy"],
  },
  {
    token: "$SHIB",
    mention_count: 38,
    avg_strength: 76.8,
    mentioned_by: ["meme_king", "shib_army", "crypto_guru"],
  },
  {
    token: "$DOGE",
    mention_count: 29,
    avg_strength: 68.2,
    mentioned_by: ["degen_trader", "doge_master", "elon_fan"],
  },
  {
    token: "$BONK",
    mention_count: 21,
    avg_strength: 71.5,
    mentioned_by: ["bonk_trader", "sol_degen"],
  },
];

export default function TwitterPage() {
  const { sentiment, loading: botLoading } = useHelixBot();
  
  const { data: signalsData, refetch: refetchSignals, isLoading: signalsLoading } = useQuery({
    queryKey: ["twitter-signals"],
    queryFn: () => api.getTwitterSignals(24, 50),
    refetchInterval: 30000,
    retry: 2,
  });

  const { data: trendingData, refetch: refetchTrending, isLoading: trendingLoading } = useQuery({
    queryKey: ["twitter-trending"],
    queryFn: () => api.getTwitterTrending(24),
    refetchInterval: 60000,
    retry: 2,
  });

  // Use mock data if real data is empty (for testing/demo)
  const signals = signalsData?.signals?.length > 0 ? signalsData.signals : mockSignals;
  const trending = trendingData?.trending?.length > 0 ? trendingData.trending : mockTrending;

  const formatRelativeTime = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    
    if (diffSecs < 60) return `${diffSecs}s`;
    if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m`;
    if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}h`;
    return `${Math.floor(diffSecs / 86400)}d`;
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "bullish": return "text-success";
      case "bearish": return "text-destructive";
      default: return "text-muted-foreground";
    }
  };

  const getSentimentBadge = (sentiment: string) => {
    switch (sentiment) {
      case "bullish": return "default";
      case "bearish": return "destructive";
      default: return "secondary";
    }
  };

  const handleRefresh = () => {
    refetchSignals();
    refetchTrending();
    toast.success("Refreshed Twitter data");
  };

  return (
    <div className="container mx-auto p-8 space-y-8 min-h-screen mesh-gradient">
      <div>
        <h1 className="text-5xl font-bold text-gradient-primary mb-2 neon-text">Twitter Sentiment</h1>
        <p className="text-muted-foreground text-lg">Market mood from 15 crypto Twitter accounts</p>
      </div>

      {/* Sentiment Overview */}
      {sentiment && (
        <Card className="card-premium border-2">
          <CardHeader>
            <CardTitle className="font-mono">Market Sentiment</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className={`text-4xl font-bold font-mono ${
                sentiment.overall_sentiment === 'BULLISH' ? 'text-success' :
                sentiment.overall_sentiment === 'BEARISH' ? 'text-destructive' :
                'text-muted-foreground'
              }`}>
                {sentiment.overall_sentiment}
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold font-mono text-gradient-primary">
                  {sentiment.bullish_percentage.toFixed(1)}%
                </div>
                <div className="text-xs text-muted-foreground font-mono">Bullish</div>
              </div>
            </div>
            <Progress 
              value={sentiment.bullish_percentage} 
              className="h-3 mb-4"
            />
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="p-3 rounded-lg bg-success/10 border border-success/30">
                <div className="text-xs text-muted-foreground font-mono uppercase">Bullish Score</div>
                <div className="text-xl font-bold text-success font-mono">{sentiment.bullish_score.toFixed(1)}</div>
              </div>
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30">
                <div className="text-xs text-muted-foreground font-mono uppercase">Bearish Score</div>
                <div className="text-xl font-bold text-destructive font-mono">{sentiment.bearish_score.toFixed(1)}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="signals" className="w-full">
        <TabsList>
          <TabsTrigger value="signals">Twitter Signals</TabsTrigger>
          <TabsTrigger value="trending">Trending Tokens</TabsTrigger>
        </TabsList>

        <TabsContent value="signals" className="space-y-4 mt-6">
          <Card className="card-premium border-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-mono">
                <Activity className="w-5 h-5 text-primary" />
                Recent Signals ({signals.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {signalsLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-24 bg-muted/20 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : signals.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <TwitterIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No recent signals found</p>
                  <p className="text-sm">Waiting for Twitter activity...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {signals.map((signal: TwitterSignal, index: number) => (
                    <Card
                      key={signal.id}
                      className="border-border/50 glass-card card-hover slide-up"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <TwitterIcon className="w-4 h-4 text-primary" />
                            <span className="font-semibold">{signal.account_name}</span>
                            <Badge variant="outline">@{signal.twitter_handle}</Badge>
                            <Badge variant={signal.tier === "S" ? "default" : signal.tier === "A" ? "secondary" : "outline"}>
                              Tier {signal.tier}
                            </Badge>
                            <Badge variant={getSentimentBadge(signal.sentiment.toLowerCase())}>
                              {signal.sentiment}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {formatRelativeTime(signal.created_at)} ago
                            </span>
                          </div>
                          <a
                            href={signal.tweet_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:text-primary/80"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                        <p className="text-sm mb-3 leading-relaxed">{signal.tweet_text}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <div className="flex items-center gap-4">
                            <span>Likes: {signal.like_count}</span>
                            <span>Retweets: {signal.retweet_count}</span>
                            <span>Strength: {signal.signal_strength}/100</span>
                          </div>
                          <div className="ml-auto">
                            <Badge variant="outline" className="font-mono">
                              {signal.mentions_tokens}
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trending" className="space-y-4 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {trendingLoading ? (
              [1, 2, 3, 4].map((i) => (
                <div key={i} className="h-48 bg-muted/20 rounded-lg animate-pulse" />
              ))
            ) : trending.length === 0 ? (
              <Card className="col-span-full border-border/50">
                <CardContent className="text-center py-12 text-muted-foreground">
                  <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No trending tokens detected</p>
                  <p className="text-sm">Scanning Twitter for meme coin momentum...</p>
                </CardContent>
              </Card>
            ) : (
              trending.map((token: TrendingToken, index: number) => (
                <Card
                  key={token.token}
                  className={`border-primary/40 glass-card card-hover slide-up ${
                    index === 0 ? "glow-cyan col-span-full border-2" : ""
                  }`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold">{token.token}</span>
                        {index === 0 && (
                          <Badge className="bg-gradient-to-r from-primary to-accent">
                            #1 TRENDING
                          </Badge>
                        )}
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Mentions (24h)</p>
                        <p className="text-2xl font-bold text-primary">{token.mention_count}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Avg Strength</p>
                        <p className="text-2xl font-bold text-accent">{token.avg_strength.toFixed(1)}</p>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Mentioned by:</p>
                      <div className="flex flex-wrap gap-1">
                        {token.mentioned_by.map((handle: string) => (
                          <Badge key={handle} variant="outline" className="text-xs">
                            @{handle}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
