# Scanner → AURA Integration Guide

## Webhook Endpoint

Your scanner should POST signals to this webhook:

**Local:**
```
POST http://localhost:8000/api/aura/signals/webhook
```

**Railway:**
```
POST https://[your-railway-url]/api/aura/signals/webhook
```

## Request Format

### Single Signal
```json
{
  "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "symbol": "SAMO",
  "name": "Samoyedcoin",
  "score": 85.5,
  "mc": 45000000,
  "liq": 2500000,
  "price": 0.0125,
  "volume": 3500000,
  "change": 15.8,
  "holders": 12500,
  "tier": "GOLD"
}
```

### Batch Signals (Multiple)
```json
[
  {
    "address": "...",
    "symbol": "TOKEN1",
    "score": 85.5,
    ...
  },
  {
    "address": "...",
    "symbol": "TOKEN2",
    "score": 78.2,
    ...
  }
]
```

## Field Mapping

The webhook accepts flexible field names:

| AURA Field | Scanner Alternatives |
|------------|---------------------|
| token_address | address, token_address |
| momentum_score | score, momentum_score |
| market_cap | mc, market_cap |
| liquidity | liq, liquidity |
| price_usd | price, price_usd |
| volume_24h | volume, volume_24h |
| price_change_24h | change, price_change_24h |
| holder_count | holders, holder_count |

## Python Integration Example

```python
import requests

def send_signal_to_aura(signal):
    """Send signal to AURA dashboard"""
    webhook_url = "http://localhost:8000/api/aura/signals/webhook"

    try:
        response = requests.post(webhook_url, json=signal, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Signal added: {result['message']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

# In your scanner:
if signal_detected:
    send_signal_to_aura({
        "address": token_address,
        "symbol": token_symbol,
        "score": momentum_score,
        "mc": market_cap,
        "liq": liquidity,
        "tier": signal_tier  # GOLD, SILVER, BRONZE
    })
```

## Response Format

```json
{
  "success": true,
  "added": 1,
  "total": 1,
  "message": "Successfully added 1/1 signals"
}
```

## Notes

- Signals expire after 24 hours automatically
- Duplicate signals (same address) are allowed for updates
- Webhook logs all additions to AURA server logs
- Dashboard updates in real-time via WebSocket
- All fields except address/symbol/score are optional

## Testing

Test the webhook:
```bash
curl -X POST http://localhost:8000/api/aura/signals/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "symbol": "TEST",
    "score": 99.9,
    "mc": 100000000,
    "liq": 10000000,
    "tier": "GOLD"
  }'
```

Expected: `{"success": true, "added": 1, "total": 1, ...}`
