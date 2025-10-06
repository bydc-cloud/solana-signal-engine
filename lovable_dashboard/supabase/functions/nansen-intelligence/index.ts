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
    const nansenApiKey = Deno.env.get('NANSEN_API_KEY');
    
    if (!nansenApiKey) {
      throw new Error('NANSEN_API_KEY not configured');
    }

    const { action, walletAddress, tokenAddress, chain = 'eth' } = await req.json();

    const baseUrl = 'https://api.nansen.ai';
    let endpoint = '';
    let queryParams = '';

    switch (action) {
      case 'wallet_labels': {
        // Get wallet labels (smart money, fund, etc.)
        endpoint = `/v1/wallets/${walletAddress}/labels`;
        queryParams = `?chain=${chain}`;
        break;
      }

      case 'wallet_holdings': {
        // Get current holdings of a wallet
        endpoint = `/v1/wallets/${walletAddress}/holdings`;
        queryParams = `?chain=${chain}`;
        break;
      }

      case 'wallet_transactions': {
        // Get recent transactions
        endpoint = `/v1/wallets/${walletAddress}/transactions`;
        queryParams = `?chain=${chain}&limit=50`;
        break;
      }

      case 'token_smart_money': {
        // Get smart money flows for a token
        endpoint = `/v1/tokens/${tokenAddress}/smart-money`;
        queryParams = `?chain=${chain}&timeframe=24h`;
        break;
      }

      case 'token_holders': {
        // Get top token holders
        endpoint = `/v1/tokens/${tokenAddress}/holders`;
        queryParams = `?chain=${chain}&limit=100`;
        break;
      }

      case 'trending_smart_money': {
        // Get trending tokens among smart money
        endpoint = '/v1/smart-money/trending';
        queryParams = `?chain=${chain}&timeframe=24h`;
        break;
      }

      case 'whale_alerts': {
        // Get recent whale movements
        endpoint = '/v1/whale-alerts';
        queryParams = `?chain=${chain}&limit=50`;
        break;
      }

      default:
        return new Response(JSON.stringify({ error: 'Invalid action' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
    }

    console.log(`Fetching Nansen data: ${endpoint}${queryParams}`);

    const response = await fetch(`${baseUrl}${endpoint}${queryParams}`, {
      method: 'GET',
      headers: {
        'X-API-KEY': nansenApiKey,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Nansen API error:', response.status, errorText);
      
      return new Response(JSON.stringify({ 
        error: `Nansen API error: ${response.status}`,
        details: errorText 
      }), {
        status: response.status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    const data = await response.json();

    // Process and enrich the data
    let enrichedData = data;
    
    if (action === 'wallet_transactions' || action === 'whale_alerts') {
      // Filter for buy/sell transactions
      enrichedData = {
        ...data,
        trades: data.transactions?.filter((tx: any) => 
          tx.type === 'swap' || tx.type === 'buy' || tx.type === 'sell'
        ).map((tx: any) => ({
          hash: tx.hash,
          type: tx.type,
          tokenAddress: tx.token_address,
          tokenSymbol: tx.token_symbol,
          amount: tx.amount,
          amountUSD: tx.amount_usd,
          timestamp: tx.timestamp,
          walletLabel: tx.wallet_label,
        })),
      };
    }

    return new Response(JSON.stringify({ 
      success: true, 
      data: enrichedData,
      action,
      timestamp: new Date().toISOString(),
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Nansen intelligence error:', error);
    return new Response(JSON.stringify({ 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
