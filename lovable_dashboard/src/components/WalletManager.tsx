import { useState } from "react";
import { Plus, Trash2, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

interface Wallet {
  id: string;
  coin_name: string;
  coin_symbol: string;
  wallet_address: string;
  chain: string;
  notes: string | null;
  created_at: string;
}

export function WalletManager() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    coin_name: "",
    coin_symbol: "",
    wallet_address: "",
    chain: "ethereum",
    notes: "",
  });

  const { data: wallets = [], isLoading } = useQuery({
    queryKey: ["wallets"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("meme_coin_wallets")
        .select("*")
        .order("created_at", { ascending: false });

      if (error) throw error;
      return data as Wallet[];
    },
  });

  const saveMutation = useMutation({
    mutationFn: async (data: typeof formData & { id?: string }) => {
      const { data: result, error } = await supabase.functions.invoke(
        "wallet-management",
        {
          body: {
            action: data.id ? "update" : "create",
            data,
          },
        }
      );

      if (error) throw error;
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      setIsAdding(false);
      setEditingId(null);
      setFormData({
        coin_name: "",
        coin_symbol: "",
        wallet_address: "",
        chain: "ethereum",
        notes: "",
      });
      toast({
        title: "Success",
        description: "Wallet saved successfully",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.functions.invoke("wallet-management", {
        body: { action: "delete", data: { id } },
      });

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      toast({
        title: "Success",
        description: "Wallet deleted successfully",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleEdit = (wallet: Wallet) => {
    setEditingId(wallet.id);
    setFormData({
      coin_name: wallet.coin_name,
      coin_symbol: wallet.coin_symbol,
      wallet_address: wallet.wallet_address,
      chain: wallet.chain,
      notes: wallet.notes || "",
    });
    setIsAdding(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveMutation.mutate(editingId ? { ...formData, id: editingId } : formData);
  };

  return (
    <Card className="backdrop-blur-glass border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-gradient-primary">Wallet Addresses</CardTitle>
          {!isAdding && (
            <Button
              onClick={() => setIsAdding(true)}
              size="sm"
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Wallet
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {isAdding && (
          <form onSubmit={handleSubmit} className="space-y-4 p-4 border border-primary/20 rounded-lg">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="coin_name">Coin Name</Label>
                <Input
                  id="coin_name"
                  value={formData.coin_name}
                  onChange={(e) =>
                    setFormData({ ...formData, coin_name: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="coin_symbol">Symbol</Label>
                <Input
                  id="coin_symbol"
                  value={formData.coin_symbol}
                  onChange={(e) =>
                    setFormData({ ...formData, coin_symbol: e.target.value })
                  }
                  required
                />
              </div>
            </div>
            <div>
              <Label htmlFor="wallet_address">Wallet Address</Label>
              <Input
                id="wallet_address"
                value={formData.wallet_address}
                onChange={(e) =>
                  setFormData({ ...formData, wallet_address: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="chain">Chain</Label>
              <Input
                id="chain"
                value={formData.chain}
                onChange={(e) =>
                  setFormData({ ...formData, chain: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={saveMutation.isPending}>
                {saveMutation.isPending ? "Saving..." : "Save"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsAdding(false);
                  setEditingId(null);
                  setFormData({
                    coin_name: "",
                    coin_symbol: "",
                    wallet_address: "",
                    chain: "ethereum",
                    notes: "",
                  });
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        )}

        {isLoading ? (
          <p className="text-muted-foreground">Loading wallets...</p>
        ) : wallets.length === 0 ? (
          <p className="text-muted-foreground">No wallets added yet</p>
        ) : (
          <div className="space-y-2">
            {wallets.map((wallet) => (
              <div
                key={wallet.id}
                className="p-4 border border-primary/20 rounded-lg hover:bg-primary/5 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{wallet.coin_name}</span>
                      <span className="text-sm text-muted-foreground">
                        ({wallet.coin_symbol})
                      </span>
                    </div>
                    <p className="text-sm font-mono text-muted-foreground break-all">
                      {wallet.wallet_address}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Chain: {wallet.chain}
                    </p>
                    {wallet.notes && (
                      <p className="text-sm text-muted-foreground">{wallet.notes}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleEdit(wallet)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => deleteMutation.mutate(wallet.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
