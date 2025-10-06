-- Create meme_coin_wallets table
CREATE TABLE IF NOT EXISTS public.meme_coin_wallets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coin_name TEXT NOT NULL,
  coin_symbol TEXT NOT NULL,
  wallet_address TEXT NOT NULL,
  chain TEXT NOT NULL DEFAULT 'ethereum',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.meme_coin_wallets ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (no auth required for now)
CREATE POLICY "Allow public read access" ON public.meme_coin_wallets
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert" ON public.meme_coin_wallets
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update" ON public.meme_coin_wallets
  FOR UPDATE USING (true);

CREATE POLICY "Allow public delete" ON public.meme_coin_wallets
  FOR DELETE USING (true);

-- Create trading_alerts table
CREATE TABLE IF NOT EXISTS public.trading_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_id UUID REFERENCES public.meme_coin_wallets(id) ON DELETE CASCADE,
  alert_type TEXT NOT NULL,
  message TEXT NOT NULL,
  severity TEXT NOT NULL DEFAULT 'info',
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.trading_alerts ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Allow public read access" ON public.trading_alerts
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert" ON public.trading_alerts
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update" ON public.trading_alerts
  FOR UPDATE USING (true);

CREATE POLICY "Allow public delete" ON public.trading_alerts
  FOR DELETE USING (true);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for meme_coin_wallets
CREATE TRIGGER update_meme_coin_wallets_updated_at
  BEFORE UPDATE ON public.meme_coin_wallets
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();