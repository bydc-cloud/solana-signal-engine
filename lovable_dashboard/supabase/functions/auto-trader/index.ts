import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const heliusApiKey = Deno.env.get('HELIUS_API_KEY');
    
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { action, walletAddress, mode = 'PAPER' } = await req.json();

    if (!heliusApiKey) {
      throw new Error('HELIUS_API_KEY not configured');
    }

    switch (action) {
      case 'monitor': {
        // Monitor a specific wallet for transactions
        console.log(`Monitoring wallet: ${walletAddress} in ${mode} mode`);
        
        const heliusUrl = `https://api.helius.xyz/v0/addresses/${walletAddress}/transactions?api-key=${heliusApiKey}&limit=10`;
        const response = await fetch(heliusUrl);
        
        if (!response.ok) {
          throw new Error(`Helius API error: ${response.status}`);
        }

        const transactions = await response.json();
        
        // Filter for token purchases/sales
        const trades = transactions
          .filter((tx: any) => 
            tx.type === 'SWAP' || 
            tx.type === 'TOKEN_MINT' ||
            tx.description?.includes('swap') ||
            tx.description?.includes('buy') ||
            tx.description?.includes('sell')
          )
          .map((tx: any) => ({
            signature: tx.signature,
            timestamp: tx.timestamp,
            type: tx.type,
            description: tx.description,
            tokenAddress: tx.tokenTransfers?.[0]?.mint,
            amount: tx.tokenTransfers?.[0]?.tokenAmount,
            walletAddress,
          }));

        return new Response(JSON.stringify({ 
          success: true, 
          trades,
          mode 
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      case 'copy_trade': {
        // Copy a trade from a tracked wallet
        const { trade, size_multiplier = 1.0, check_nansen = true } = await req.json();
        
        console.log(`Copying trade in ${mode} mode:`, trade);

        // Check Nansen data before executing
        let nansenSignal = 'neutral';
        if (check_nansen && trade.tokenAddress) {
          try {
            const nansenResponse = await fetch(`${supabaseUrl}/functions/v1/nansen-intelligence`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${supabaseKey}`,
              },
              body: JSON.stringify({
                action: 'token_smart_money',
                tokenAddress: trade.tokenAddress,
                chain: 'eth',
              }),
            });
            
            if (nansenResponse.ok) {
              const nansenData = await nansenResponse.json();
              const smartMoneyFlow = nansenData.data?.net_flow || 0;
              nansenSignal = smartMoneyFlow > 0 ? 'bullish' : smartMoneyFlow < 0 ? 'bearish' : 'neutral';
              console.log(`Nansen signal for ${trade.tokenAddress}: ${nansenSignal} (flow: ${smartMoneyFlow})`);
            }
          } catch (e) {
            console.error('Failed to fetch Nansen data:', e);
          }
        }

        if (mode === 'PAPER') {
          // Paper trading - just log and create alert
          await supabase.from('trading_alerts').insert({
            alert_type: 'PAPER_TRADE',
            message: `Paper trade executed: ${trade.type} ${trade.tokenAddress} | Nansen: ${nansenSignal}`,
            severity: nansenSignal === 'bullish' ? 'info' : 'warning',
          });

          return new Response(JSON.stringify({
            success: true,
            mode: 'PAPER',
            message: 'Paper trade recorded',
            nansenSignal,
            trade: {
              ...trade,
              executed: false,
              simulated: true,
              nansenSignal,
            }
          }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          });
        } else {
          // LIVE trading - would execute actual trade here
          // This requires additional DEX integration (Jupiter, Raydium, etc.)
          console.log('LIVE TRADE would execute here with proper DEX integration');
          
          await supabase.from('trading_alerts').insert({
            alert_type: 'LIVE_TRADE',
            message: `Live trade queued: ${trade.type} ${trade.tokenAddress}`,
            severity: 'warning',
          });

          return new Response(JSON.stringify({
            success: true,
            mode: 'LIVE',
            message: 'Live trade queued (DEX integration required)',
            trade: {
              ...trade,
              executed: false,
              queued: true,
            }
          }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          });
        }
      }

      case 'get_wallet_balance': {
        // Get wallet balances via Helius
        const balanceUrl = `https://api.helius.xyz/v0/addresses/${walletAddress}/balances?api-key=${heliusApiKey}`;
        const response = await fetch(balanceUrl);
        
        if (!response.ok) {
          throw new Error(`Helius API error: ${response.status}`);
        }

        const balances = await response.json();
        
        return new Response(JSON.stringify({ 
          success: true, 
          balances 
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      default:
        return new Response(JSON.stringify({ error: 'Invalid action' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
    }
  } catch (error) {
    console.error('Auto-trader error:', error);
    return new Response(JSON.stringify({ 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
