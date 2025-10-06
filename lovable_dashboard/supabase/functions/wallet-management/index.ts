import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.38.4';

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
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { action, data } = await req.json();
    console.log('Wallet management request:', action, data);

    switch (action) {
      case 'create': {
        const { data: wallet, error } = await supabase
          .from('meme_coin_wallets')
          .insert({
            coin_name: data.coin_name,
            coin_symbol: data.coin_symbol,
            wallet_address: data.wallet_address,
            chain: data.chain || 'ethereum',
            notes: data.notes || null,
          })
          .select()
          .single();

        if (error) throw error;

        return new Response(JSON.stringify({ success: true, wallet }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      case 'update': {
        const { data: wallet, error } = await supabase
          .from('meme_coin_wallets')
          .update({
            coin_name: data.coin_name,
            coin_symbol: data.coin_symbol,
            wallet_address: data.wallet_address,
            chain: data.chain,
            notes: data.notes,
          })
          .eq('id', data.id)
          .select()
          .single();

        if (error) throw error;

        return new Response(JSON.stringify({ success: true, wallet }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      case 'delete': {
        const { error } = await supabase
          .from('meme_coin_wallets')
          .delete()
          .eq('id', data.id);

        if (error) throw error;

        return new Response(JSON.stringify({ success: true }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      case 'list': {
        const { data: wallets, error } = await supabase
          .from('meme_coin_wallets')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;

        return new Response(JSON.stringify({ success: true, wallets }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      default:
        throw new Error(`Unknown action: ${action}`);
    }
  } catch (error) {
    console.error('Error in wallet-management function:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
