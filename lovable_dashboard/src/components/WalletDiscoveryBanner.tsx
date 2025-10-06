import { useState, useEffect } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { TrendingUp, X } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export const WalletDiscoveryBanner = () => {
  const [show, setShow] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);

  useEffect(() => {
    checkIfNeedsDiscovery();
  }, []);

  const checkIfNeedsDiscovery = async () => {
    try {
      const { data, error } = await supabase
        .from('tracked_wallets')
        .select('id')
        .limit(1);

      if (error) throw error;
      
      // Show banner if no wallets tracked
      if (!data || data.length === 0) {
        setShow(true);
      }
    } catch (error) {
      console.error('Error checking wallets:', error);
    }
  };

  const handleDiscover = async () => {
    setIsDiscovering(true);
    try {
      const { data, error } = await supabase.functions.invoke('wallet-discovery', {
        body: { action: 'discover_profitable_wallets' }
      });

      if (error) throw error;

      toast.success(`Discovered ${data.added} profitable wallets! Check the Wallets page.`);
      setShow(false);
    } catch (error) {
      console.error('Discovery error:', error);
      toast.error('Failed to discover wallets');
    } finally {
      setIsDiscovering(false);
    }
  };

  if (!show) return null;

  return (
    <Alert className="mb-6 border-primary/50 bg-primary/5">
      <TrendingUp className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <span>
          <strong>No wallets tracked yet.</strong> Discover profitable smart money wallets from Nansen to start auto-trading.
        </span>
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={handleDiscover}
            disabled={isDiscovering}
            className="bg-primary hover:bg-primary/80"
          >
            {isDiscovering ? 'Discovering...' : 'Discover Now'}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShow(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </AlertDescription>
    </Alert>
  );
};
