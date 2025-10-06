-- Add verification status column
ALTER TABLE public.tracked_wallets 
ADD COLUMN IF NOT EXISTS is_verified boolean DEFAULT false;

-- Add chain column to store blockchain type
ALTER TABLE public.tracked_wallets 
ADD COLUMN IF NOT EXISTS chain text DEFAULT 'solana';

-- Add index for verified wallets
CREATE INDEX IF NOT EXISTS idx_tracked_wallets_verified 
ON public.tracked_wallets(is_verified) 
WHERE is_verified = true;