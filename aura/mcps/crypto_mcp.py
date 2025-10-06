"""
Unified Crypto Data MCP
Wraps Birdeye, DeFiLlama, Solscan, DexScreener, RugCheck APIs
"""
import os
import requests
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

# API Keys from environment
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")


class CryptoDataMCP:
    """Unified crypto data interface"""

    def __init__(self):
        self.birdeye_base = "https://public-api.birdeye.so"
        self.defillama_base = "https://api.llama.fi"
        self.solscan_base = "https://api.solscan.io"
        self.dexscreener_base = "https://api.dexscreener.com/latest"
        self.rugcheck_base = "https://api.rugcheck.xyz/v1"

    # ═══════════════════════════════════════════════════════════
    # BIRDEYE (Already integrated, just wrapping)
    # ═══════════════════════════════════════════════════════════

    def get_token_overview(self, address: str) -> Optional[Dict]:
        """Get token overview from Birdeye"""
        try:
            headers = {"X-API-KEY": BIRDEYE_API_KEY}
            url = f"{self.birdeye_base}/defi/token_overview"
            params = {"address": address}

            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("data")
            else:
                logger.warning(f"Birdeye overview failed {response.status_code} for {address}")
                return None
        except Exception as e:
            logger.error(f"Birdeye overview error: {e}")
            return None

    def get_token_security(self, address: str) -> Optional[Dict]:
        """Get token security info from Birdeye"""
        try:
            headers = {"X-API-KEY": BIRDEYE_API_KEY}
            url = f"{self.birdeye_base}/defi/token_security"
            params = {"address": address}

            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("data")
            else:
                logger.warning(f"Birdeye security failed {response.status_code} for {address}")
                return None
        except Exception as e:
            logger.error(f"Birdeye security error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # DEFILLAMA (TVL, Protocol Data)
    # ═══════════════════════════════════════════════════════════

    def get_protocol_tvl(self, protocol: str) -> Optional[Dict]:
        """Get protocol TVL from DeFiLlama"""
        try:
            url = f"{self.defillama_base}/protocol/{protocol}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    "tvl": data.get("tvl"),
                    "chain_tvls": data.get("chainTvls", {}),
                    "change_1d": data.get("change_1d"),
                    "change_7d": data.get("change_7d"),
                }
            else:
                logger.warning(f"DeFiLlama TVL failed {response.status_code} for {protocol}")
                return None
        except Exception as e:
            logger.error(f"DeFiLlama TVL error: {e}")
            return None

    def get_chain_tvl(self, chain: str = "Solana") -> Optional[Dict]:
        """Get chain TVL from DeFiLlama"""
        try:
            url = f"{self.defillama_base}/v2/historicalChainTvl/{chain}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    latest = data[-1]
                    return {
                        "date": latest.get("date"),
                        "tvl": latest.get("tvl"),
                    }
            else:
                logger.warning(f"DeFiLlama chain TVL failed {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"DeFiLlama chain TVL error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # SOLSCAN (Transaction History, Holder Analysis)
    # ═══════════════════════════════════════════════════════════

    def get_token_holders(self, address: str, limit: int = 10) -> Optional[List[Dict]]:
        """Get top holders from Solscan"""
        try:
            url = f"{self.solscan_base}/token/holders"
            params = {"token": address, "limit": limit, "offset": 0}

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                holders = []
                for holder in data.get("data", []):
                    holders.append({
                        "address": holder.get("owner"),
                        "amount": holder.get("amount"),
                        "decimals": holder.get("decimals"),
                        "rank": holder.get("rank"),
                    })
                return holders
            else:
                logger.warning(f"Solscan holders failed {response.status_code} for {address}")
                return None
        except Exception as e:
            logger.error(f"Solscan holders error: {e}")
            return None

    def get_token_transfers(self, address: str, limit: int = 20) -> Optional[List[Dict]]:
        """Get recent transfers from Solscan"""
        try:
            url = f"{self.solscan_base}/token/transfer"
            params = {"token": address, "limit": limit, "offset": 0}

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                transfers = []
                for tx in data.get("data", []):
                    transfers.append({
                        "signature": tx.get("trans_id"),
                        "block_time": tx.get("block_time"),
                        "from": tx.get("src"),
                        "to": tx.get("dst"),
                        "amount": tx.get("amount"),
                    })
                return transfers
            else:
                logger.warning(f"Solscan transfers failed {response.status_code} for {address}")
                return None
        except Exception as e:
            logger.error(f"Solscan transfers error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # DEXSCREENER (Trading Data, Price Charts)
    # ═══════════════════════════════════════════════════════════

    def get_dex_pairs(self, address: str) -> Optional[List[Dict]]:
        """Get DEX pairs from DexScreener"""
        try:
            url = f"{self.dexscreener_base}/dex/tokens/{address}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                pairs = []
                for pair in data.get("pairs", []):
                    pairs.append({
                        "chain_id": pair.get("chainId"),
                        "dex_id": pair.get("dexId"),
                        "pair_address": pair.get("pairAddress"),
                        "base_token": pair.get("baseToken", {}).get("symbol"),
                        "quote_token": pair.get("quoteToken", {}).get("symbol"),
                        "price_usd": pair.get("priceUsd"),
                        "volume_24h": pair.get("volume", {}).get("h24"),
                        "liquidity_usd": pair.get("liquidity", {}).get("usd"),
                        "price_change_24h": pair.get("priceChange", {}).get("h24"),
                    })
                return pairs
            else:
                logger.warning(f"DexScreener failed {response.status_code} for {address}")
                return None
        except Exception as e:
            logger.error(f"DexScreener error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # RUGCHECK (Security Analysis)
    # ═══════════════════════════════════════════════════════════

    def get_rugcheck_report(self, address: str) -> Optional[Dict]:
        """Get security report from RugCheck"""
        try:
            url = f"{self.rugcheck_base}/tokens/{address}/report"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    "score": data.get("score"),
                    "risks": data.get("risks", []),
                    "markets": data.get("markets", []),
                    "top_holders": data.get("topHolders", []),
                    "created_at": data.get("tokenMeta", {}).get("createdAt"),
                }
            else:
                logger.warning(f"RugCheck failed {response.status_code} for {address}")
                return None
        except Exception as e:
            logger.error(f"RugCheck error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # UNIFIED ENRICHMENT
    # ═══════════════════════════════════════════════════════════

    def enrich_token(self, address: str) -> Dict:
        """
        Fetch all available data for a token from all sources
        Returns unified enriched token data
        """
        enriched = {
            "address": address,
            "timestamp": None,
            "birdeye": {},
            "defillama": {},
            "solscan": {},
            "dexscreener": {},
            "rugcheck": {},
        }

        from datetime import datetime
        enriched["timestamp"] = datetime.now().isoformat()

        # Birdeye
        overview = self.get_token_overview(address)
        if overview:
            enriched["birdeye"]["overview"] = overview

        security = self.get_token_security(address)
        if security:
            enriched["birdeye"]["security"] = security

        # Solscan
        holders = self.get_token_holders(address, limit=10)
        if holders:
            enriched["solscan"]["top_holders"] = holders

        transfers = self.get_token_transfers(address, limit=20)
        if transfers:
            enriched["solscan"]["recent_transfers"] = transfers

        # DexScreener
        pairs = self.get_dex_pairs(address)
        if pairs:
            enriched["dexscreener"]["pairs"] = pairs

        # RugCheck
        rugcheck = self.get_rugcheck_report(address)
        if rugcheck:
            enriched["rugcheck"]["report"] = rugcheck

        return enriched


# Singleton instance
crypto_mcp = CryptoDataMCP()
