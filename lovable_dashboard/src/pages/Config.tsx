import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, Save, RotateCcw } from "lucide-react";
import { toast } from "sonner";
import { WalletManager } from "@/components/WalletManager";
import { AutoTradeSettings } from "@/components/AutoTradeSettings";

const API_BASE = "https://sheeplike-genealogic-emmett.ngrok-free.dev";

interface Config {
  mode: string;
  grad_min_score: number;
  grad_per_trade_cap: number;
  grad_global_exposure_cap: number;
  grad_max_concurrent: number;
  grad_locker_rep_min: number;
  grad_sniper_pct_max: number;
  grad_top10_pct_max: number;
  grad_lp_lock_min_days: number;
}

export default function ConfigPage() {
  const queryClient = useQueryClient();
  const [hasChanges, setHasChanges] = useState(false);
  const [localConfig, setLocalConfig] = useState<Partial<Config>>({});

  const { data: config } = useQuery<Config>({
    queryKey: ["config"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/config`);
      if (!res.ok) throw new Error("Failed to fetch config");
      const data = await res.json();
      setLocalConfig(data);
      return data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ key, value }: { key: string; value: string }) => {
      const res = await fetch(`${API_BASE}/config/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value }),
      });
      if (!res.ok) throw new Error("Failed to update config");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Configuration saved");
      setHasChanges(false);
      queryClient.invalidateQueries({ queryKey: ["config"] });
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`);
    },
  });

  const restartMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${API_BASE}/scanner/restart`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Failed to restart scanner");
      return res.json();
    },
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ["status"] });
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`);
    },
  });

  const handleSliderChange = (key: keyof Config, value: number) => {
    setLocalConfig((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!config) return;

    const updates = Object.entries(localConfig).filter(
      ([key, value]) => value !== config[key as keyof Config]
    );

    for (const [key, value] of updates) {
      await updateMutation.mutateAsync({
        key: key.toUpperCase(),
        value: String(value),
      });
    }
  };

  const parameters = [
    {
      key: "grad_min_score",
      label: "Min Graduation Score",
      min: 0,
      max: 100,
      step: 1,
      description: "Minimum quality score to execute trade",
      recommended: "40-70",
    },
    {
      key: "grad_per_trade_cap",
      label: "Per Trade Cap",
      min: 0.001,
      max: 0.1,
      step: 0.001,
      description: "Max % of equity per single trade",
      recommended: "0.01-0.03",
      format: (v: number) => `${(v * 100).toFixed(1)}%`,
    },
    {
      key: "grad_global_exposure_cap",
      label: "Global Exposure Cap",
      min: 0.1,
      max: 1.0,
      step: 0.05,
      description: "Max % of equity in open positions",
      recommended: "0.50-0.80",
      format: (v: number) => `${(v * 100).toFixed(0)}%`,
    },
    {
      key: "grad_max_concurrent",
      label: "Max Concurrent Positions",
      min: 1,
      max: 50,
      step: 1,
      description: "Max number of simultaneous trades",
      recommended: "5-15",
    },
  ];

  return (
    <div className="min-h-screen bg-background p-6 space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Configuration</h1>
        <p className="text-muted-foreground">Adjust trading parameters and manage wallets</p>
      </header>

      <div className="space-y-6">
          {/* Warning Banner */}
          <Alert variant="destructive" className="bg-warning/10 border-warning">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Configuration changes require scanner restart to take effect
            </AlertDescription>
          </Alert>

          {/* Wallet Manager */}
          <WalletManager />

          {/* Auto-Trading Settings */}
          <AutoTradeSettings />

          {/* Mode Toggle */}
          <Card className={config?.mode === "LIVE" ? "border-destructive/50" : ""}>
            <CardHeader>
              <CardTitle>Trading Mode</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                {["PAPER", "LIVE"].map((mode) => (
                  <button
                    key={mode}
                    onClick={() => {
                      setLocalConfig((prev) => ({ ...prev, mode }));
                      setHasChanges(true);
                    }}
                    className={`flex-1 px-6 py-4 rounded-lg border-2 transition-all ${
                      localConfig.mode === mode
                        ? mode === "LIVE"
                          ? "border-destructive bg-destructive/10"
                          : "border-primary bg-primary/10"
                        : "border-border hover:border-muted-foreground"
                    }`}
                  >
                    <p className="font-bold text-lg">{mode}</p>
                    {mode === "LIVE" && (
                      <p className="text-xs text-destructive mt-1">Uses real funds. Proceed with caution.</p>
                    )}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Parameter Sliders */}
          <Card>
            <CardHeader>
              <CardTitle>Trading Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-8">
              {parameters.map((param) => {
                const value = localConfig[param.key as keyof Config] as number;
                return (
                  <div key={param.key} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">{param.label}</label>
                      <span className="text-lg font-bold text-primary">
                        {param.format ? param.format(value) : value}
                      </span>
                    </div>
                    <Slider
                      value={[value]}
                      onValueChange={([v]) => handleSliderChange(param.key as keyof Config, v)}
                      min={param.min}
                      max={param.max}
                      step={param.step}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>{param.description}</span>
                      <span>Recommended: {param.recommended}</span>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button
              onClick={handleSave}
              disabled={!hasChanges || updateMutation.isPending}
              className="bg-success hover:bg-success/80"
            >
              <Save className="w-4 h-4 mr-2" />
              {updateMutation.isPending ? "Saving..." : "Save Configuration"}
            </Button>

            {hasChanges && (
              <Button
                onClick={() => restartMutation.mutate()}
                disabled={restartMutation.isPending}
                className="bg-warning hover:bg-warning/80 text-warning-foreground"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                {restartMutation.isPending ? "Restarting..." : "Restart Scanner"}
              </Button>
            )}
          </div>
      </div>
    </div>
  );
}
