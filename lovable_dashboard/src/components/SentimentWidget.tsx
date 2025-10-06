import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface SentimentData {
  bullish_score: number;
  bearish_score: number;
  bullish_percentage: number;
  overall_sentiment: string;
  breakdown: any[];
  timestamp: string;
}

export function SentimentWidget() {
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSentiment();
    const interval = setInterval(fetchSentiment, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchSentiment = async () => {
    try {
      const response = await fetch(
        "https://signal-railway-deployment-production.up.railway.app/twitter/sentiment"
      );
      const data = await response.json();
      setSentiment(data);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch sentiment:", error);
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === "BULLISH") return "text-success";
    if (sentiment === "BEARISH") return "text-destructive";
    return "text-muted-foreground";
  };

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === "BULLISH") return <TrendingUp className="w-4 h-4" />;
    if (sentiment === "BEARISH") return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  return (
    <Card className="border-border bg-card/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-sm font-mono uppercase tracking-wider text-primary flex items-center gap-2">
          <span className="text-primary">&gt;</span>
          [market_sentiment]
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-xs text-muted-foreground font-mono">Loading sentiment...</p>
        ) : sentiment ? (
          <div className="space-y-4">
            {/* Overall Sentiment */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={getSentimentColor(sentiment.overall_sentiment)}>
                  {getSentimentIcon(sentiment.overall_sentiment)}
                </div>
                <span className={`text-lg font-black font-mono ${getSentimentColor(sentiment.overall_sentiment)}`}>
                  {sentiment.overall_sentiment}
                </span>
              </div>
              <Badge variant="outline" className="font-mono text-xs">
                {sentiment.bullish_percentage.toFixed(0)}% Bullish
              </Badge>
            </div>

            {/* Score Breakdown */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-success">Bullish Signals:</span>
                <span className="text-success font-bold">{sentiment.bullish_score}</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-destructive">Bearish Signals:</span>
                <span className="text-destructive font-bold">{sentiment.bearish_score}</span>
              </div>
            </div>

            {/* Timestamp */}
            <p className="text-[10px] text-muted-foreground font-mono pt-2 border-t border-border">
              Updated: {new Date(sentiment.timestamp).toLocaleTimeString()}
            </p>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground font-mono">No sentiment data</p>
        )}
      </CardContent>
    </Card>
  );
}
