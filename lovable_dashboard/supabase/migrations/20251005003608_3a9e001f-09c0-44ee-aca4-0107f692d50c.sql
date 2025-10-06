-- Enable pg_cron extension for scheduled jobs
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule wallet discovery to run every morning at 8 AM UTC
SELECT cron.schedule(
  'discover-wallets-daily',
  '0 8 * * *', -- 8 AM every day
  $$
  SELECT
    net.http_post(
        url:='https://wzyxacwjtltcswefbedu.supabase.co/functions/v1/wallet-discovery',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6eXhhY3dqdGx0Y3N3ZWZiZWR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NTI0NjMsImV4cCI6MjA3NTEyODQ2M30.AhnPcYwA_K8F0X0ALubWp1q4QTmT_IVfkZNNqR13dms"}'::jsonb,
        body:='{"action": "discover_profitable_wallets"}'::jsonb
    ) as request_id;
  $$
);