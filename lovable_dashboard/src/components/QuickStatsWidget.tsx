import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface QuickStatsWidgetProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export function QuickStatsWidget({ title, value, subtitle, icon: Icon, trend, className }: QuickStatsWidgetProps) {
  return (
    <Card className={`border-border bg-card/50 backdrop-blur-sm hover:bg-card/70 transition-all ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-[10px] text-muted-foreground font-mono uppercase tracking-wider font-bold mb-2">
              {title}
            </p>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black font-mono text-foreground">
                {value}
              </span>
              {trend && (
                <span className={`text-xs font-mono font-bold ${trend.isPositive ? "text-success" : "text-destructive"}`}>
                  {trend.isPositive ? "+" : ""}{trend.value}%
                </span>
              )}
            </div>
            <p className="text-[10px] text-muted-foreground font-mono">
              {subtitle}
            </p>
          </div>
          <div className="flex-shrink-0">
            <div className="w-10 h-10 flex items-center justify-center bg-primary/10 border border-primary/20">
              <Icon className="w-5 h-5 text-primary opacity-70" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
