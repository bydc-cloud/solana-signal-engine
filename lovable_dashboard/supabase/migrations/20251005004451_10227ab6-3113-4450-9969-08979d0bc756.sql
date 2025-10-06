-- Add columns for wallet verification and proof
ALTER TABLE tracked_wallets 
ADD COLUMN IF NOT EXISTS verification_url text,
ADD COLUMN IF NOT EXISTS reasoning text,
ADD COLUMN IF NOT EXISTS wallet_type text DEFAULT 'smart_money';