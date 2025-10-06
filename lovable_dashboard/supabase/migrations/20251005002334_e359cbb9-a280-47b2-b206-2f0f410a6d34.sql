-- Create tracked wallets performance table
CREATE TABLE IF NOT EXISTS public.tracked_wallets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_address TEXT NOT NULL UNIQUE,
  label TEXT,
  total_pnl_usd DECIMAL(20, 2) DEFAULT 0,
  win_rate DECIMAL(5, 2) DEFAULT 0,
  total_trades INTEGER DEFAULT 0,
  active_positions INTEGER DEFAULT 0,
  avg_holding_time_hours DECIMAL(10, 2) DEFAULT 0,
  last_trade_at TIMESTAMP WITH TIME ZONE,
  discovered_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  is_active BOOLEAN DEFAULT true,
  nansen_labels TEXT[],
  performance_score DECIMAL(5, 2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create wallet positions table
CREATE TABLE IF NOT EXISTS public.wallet_positions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_id UUID REFERENCES public.tracked_wallets(id) ON DELETE CASCADE,
  token_address TEXT NOT NULL,
  token_symbol TEXT NOT NULL,
  token_name TEXT,
  entry_price DECIMAL(20, 8),
  current_price DECIMAL(20, 8),
  amount DECIMAL(30, 8),
  pnl_usd DECIMAL(20, 2),
  pnl_percentage DECIMAL(10, 2),
  entry_time TIMESTAMP WITH TIME ZONE,
  exit_time TIMESTAMP WITH TIME ZONE,
  holding_time_hours DECIMAL(10, 2),
  is_closed BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create indexes
CREATE INDEX idx_tracked_wallets_performance ON public.tracked_wallets(performance_score DESC, total_pnl_usd DESC);
CREATE INDEX idx_tracked_wallets_active ON public.tracked_wallets(is_active, last_trade_at DESC);
CREATE INDEX idx_wallet_positions_wallet ON public.wallet_positions(wallet_id);
CREATE INDEX idx_wallet_positions_open ON public.wallet_positions(is_closed, wallet_id);

-- Enable RLS
ALTER TABLE public.tracked_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallet_positions ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Allow public read on tracked_wallets" ON public.tracked_wallets FOR SELECT USING (true);
CREATE POLICY "Allow public insert on tracked_wallets" ON public.tracked_wallets FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update on tracked_wallets" ON public.tracked_wallets FOR UPDATE USING (true);

CREATE POLICY "Allow public read on wallet_positions" ON public.wallet_positions FOR SELECT USING (true);
CREATE POLICY "Allow public insert on wallet_positions" ON public.wallet_positions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update on wallet_positions" ON public.wallet_positions FOR UPDATE USING (true);

-- Create trigger for updated_at
CREATE TRIGGER update_tracked_wallets_updated_at
  BEFORE UPDATE ON public.tracked_wallets
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_wallet_positions_updated_at
  BEFORE UPDATE ON public.wallet_positions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();