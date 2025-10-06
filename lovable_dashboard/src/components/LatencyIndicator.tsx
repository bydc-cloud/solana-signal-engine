import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Activity } from "lucide-react";

export const LatencyIndicator = () => {
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [timeSince, setTimeSince] = useState<string>("just now");

  useEffect(() => {
    const interval = setInterval(() => {
      const seconds = Math.floor((Date.now() - lastUpdate.getTime()) / 1000);
      
      if (seconds < 60) {
        setTimeSince(`${seconds}s ago`);
      } else if (seconds < 3600) {
        setTimeSince(`${Math.floor(seconds / 60)}m ago`);
      } else {
        setTimeSince(`${Math.floor(seconds / 3600)}h ago`);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [lastUpdate]);

  // Update timestamp when component mounts or data refreshes
  useEffect(() => {
    setLastUpdate(new Date());
  }, []);

  const getStatusColor = () => {
    const seconds = Math.floor((Date.now() - lastUpdate.getTime()) / 1000);
    if (seconds < 30) return "bg-success";
    if (seconds < 120) return "bg-warning";
    return "bg-destructive";
  };

  return (
    <Badge variant="outline" className="fixed top-4 right-4 z-50 flex items-center gap-2">
      <Activity className="w-3 h-3" />
      <span className="text-xs">Live Data</span>
      <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`} />
      <span className="text-xs text-muted-foreground">{timeSince}</span>
    </Badge>
  );
};
