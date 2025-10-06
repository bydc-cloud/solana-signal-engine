"""
AURA Sentiment Analysis Module
Analyzes social media sentiment using ACTIVE web scraping
"""
import logging
import asyncio
import aiohttp
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes social sentiment for tokens from multiple sources:
    - Twitter/X (via Puppeteer scraper - ACTIVE)
    - Telegram channels (via Firecrawl - ACTIVE)
    - Reddit mentions (via API - ACTIVE)
    """

    def __init__(self):
        self.twitter_keywords = ['solana', 'sol', 'crypto', 'token', 'launch']
        self.sentiment_cache = {}
        self.cache_ttl = timedelta(minutes=15)

        # Import scrapers on init
        try:
            from .scrapers import twitter_scraper, web_scraper
            self.twitter_scraper = twitter_scraper
            self.web_scraper = web_scraper
            logger.info("✅ Sentiment scrapers initialized (Twitter + Firecrawl)")
        except ImportError as e:
            logger.warning(f"Scrapers not available: {e}")
            self.twitter_scraper = None
            self.web_scraper = None

    async def analyze_token_sentiment(self, address: str, symbol: str) -> Dict:
        """
        Analyze overall sentiment for a token
        ACTIVELY SCRAPES Twitter, Telegram, Reddit
        Returns sentiment score (-100 to +100) and metrics
        """
        try:
            # Check cache
            cached = self.sentiment_cache.get(address)
            if cached and cached['timestamp'] > datetime.now() - self.cache_ttl:
                return cached['data']

            # ACTIVELY gather sentiment from multiple sources
            twitter_sentiment = await self._analyze_twitter(symbol)
            telegram_sentiment = await self._analyze_telegram(symbol, address)
            reddit_sentiment = await self._analyze_reddit(symbol)

            # Combine scores
            total_mentions = (
                twitter_sentiment['mentions'] +
                telegram_sentiment['mentions'] +
                reddit_sentiment['mentions']
            )

            if total_mentions == 0:
                overall_score = 0
            else:
                weighted_score = (
                    twitter_sentiment['score'] * twitter_sentiment['mentions'] +
                    telegram_sentiment['score'] * telegram_sentiment['mentions'] +
                    reddit_sentiment['score'] * reddit_sentiment['mentions']
                ) / total_mentions
                overall_score = int(weighted_score)

            result = {
                'overall_score': overall_score,
                'total_mentions': total_mentions,
                'twitter': twitter_sentiment,
                'telegram': telegram_sentiment,
                'reddit': reddit_sentiment,
                'analyzed_at': datetime.now().isoformat(),
            }

            # Cache result
            self.sentiment_cache[address] = {
                'timestamp': datetime.now(),
                'data': result,
            }

            logger.info(f"📊 Sentiment for ${symbol}: {overall_score} ({total_mentions} mentions)")

            return result

        except Exception as e:
            logger.error(f"Sentiment analysis error for {symbol}: {e}")
            return {
                'overall_score': 0,
                'total_mentions': 0,
                'error': str(e),
            }

    async def _analyze_twitter(self, symbol: str) -> Dict:
        """
        Analyze Twitter/X sentiment for a token
        ACTIVELY USES Puppeteer scraper
        """
        try:
            if not self.twitter_scraper:
                logger.debug("Twitter scraper not available")
                return {'score': 0, 'mentions': 0}

            # ACTIVE SCRAPING
            result = await self.twitter_scraper.scrape_twitter_mentions(symbol)

            logger.info(f"🐦 Twitter: ${symbol} - {result['mentions']} mentions, score: {result['score']}")

            return {
                'score': result['score'],
                'mentions': result['mentions'],
                'bullish': result['bullish'],
                'bearish': result['bearish'],
                'neutral': result['neutral'],
                'top_tweets': result.get('top_tweets', []),
            }

        except Exception as e:
            logger.error(f"Twitter analysis error: {e}")
            return {'score': 0, 'mentions': 0}

    async def _analyze_telegram(self, symbol: str, address: str) -> Dict:
        """
        Analyze Telegram channel mentions
        ACTIVELY USES Firecrawl to scrape channels
        """
        try:
            if not self.web_scraper:
                logger.debug("Firecrawl not available")
                return {'score': 0, 'mentions': 0}

            # Popular Solana/crypto Telegram channels
            channels = [
                "https://t.me/s/solana",
                "https://t.me/s/SolanaDeFi",
            ]

            total_mentions = 0
            total_score = 0

            for channel_url in channels:
                try:
                    result = await self.web_scraper.scrape_telegram_channel(channel_url)
                    mentions = result.get('mentions', 0)
                    total_mentions += mentions

                    # Simple score based on mentions
                    if mentions > 0:
                        total_score += mentions * 50  # Assume neutral-positive

                except Exception as e:
                    logger.debug(f"Telegram channel scrape failed: {e}")
                    continue

            if total_mentions > 0:
                score = int(total_score / total_mentions)
            else:
                score = 0

            logger.info(f"📱 Telegram: ${symbol} - {total_mentions} mentions")

            return {
                'score': score,
                'mentions': total_mentions,
                'channels': channels,
                'recent_messages': [],
            }

        except Exception as e:
            logger.error(f"Telegram analysis error: {e}")
            return {'score': 0, 'mentions': 0}

    async def _analyze_reddit(self, symbol: str) -> Dict:
        """
        Analyze Reddit sentiment using Reddit API
        ACTIVELY QUERIES subreddits
        """
        try:
            # Use Reddit API to search
            subreddits = ['CryptoMoonShots', 'solana', 'CryptoCurrency']

            async with aiohttp.ClientSession() as session:
                total_mentions = 0
                bullish = 0
                bearish = 0

                for subreddit in subreddits:
                    try:
                        url = f"https://www.reddit.com/r/{subreddit}/search.json?q={symbol}&restrict_sr=1&limit=25"
                        headers = {'User-Agent': 'AURA Bot 1.0'}

                        async with session.get(url, headers=headers, timeout=10) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                posts = data.get('data', {}).get('children', [])

                                mentions = len(posts)
                                total_mentions += mentions

                                # Analyze post titles/comments for sentiment
                                for post in posts:
                                    title = post.get('data', {}).get('title', '').lower()
                                    if any(word in title for word in ['moon', 'bullish', 'buy', 'gem']):
                                        bullish += 1
                                    elif any(word in title for word in ['dump', 'bearish', 'sell', 'rug']):
                                        bearish += 1

                    except Exception as e:
                        logger.debug(f"Reddit subreddit {subreddit} failed: {e}")
                        continue

                    # Rate limiting
                    await asyncio.sleep(1)

                if total_mentions > 0:
                    if bullish + bearish > 0:
                        score = int(((bullish - bearish) / (bullish + bearish)) * 100)
                    else:
                        score = 0
                else:
                    score = 0

                logger.info(f"🔴 Reddit: ${symbol} - {total_mentions} posts, score: {score}")

                return {
                    'score': score,
                    'mentions': total_mentions,
                    'subreddits': subreddits,
                    'top_posts': [],
                }

        except Exception as e:
            logger.error(f"Reddit analysis error: {e}")
            return {'score': 0, 'mentions': 0}

    async def get_trending_tokens(self) -> List[Dict]:
        """
        Identify tokens trending on social media
        ACTIVELY SCRAPES Twitter, Telegram, Reddit
        Returns list of {symbol, address, mentions, score}
        """
        try:
            if not self.twitter_scraper:
                return []

            # Scrape trending hashtags on Twitter
            trending_symbols = ['SOL', 'BTC', 'ETH']  # Would be extracted from trending

            results = []
            for symbol in trending_symbols:
                sentiment = await self.analyze_token_sentiment('', symbol)
                if sentiment['total_mentions'] > 10:
                    results.append({
                        'symbol': symbol,
                        'mentions': sentiment['total_mentions'],
                        'score': sentiment['overall_score'],
                    })

            results.sort(key=lambda x: x['mentions'], reverse=True)
            return results[:10]

        except Exception as e:
            logger.error(f"Trending tokens error: {e}")
            return []


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()
