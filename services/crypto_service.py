"""
Crypto service layer integrating with CoinGecko API.
Handles all cryptocurrency data fetching with caching.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.api_client import APIClient, APIClientError
from models.coin import Coin
from cache.cache_manager import CacheManager
from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class CryptoService:
    """
    Service for interacting with CoinGecko API.
    Provides methods for market data, coin details, trending, historical prices, and global stats.
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize CryptoService with API client and cache.
        
        Args:
            cache_manager: Optional CacheManager instance (creates new if not provided)
        """
        self.api_client = APIClient(
            base_url=config.COINGECKO_BASE_URL,
            timeout=config.REQUEST_TIMEOUT,
            max_retries=config.MAX_RETRIES,
            backoff_factor=config.RETRY_BACKOFF_FACTOR
        )
        self.cache = cache_manager or CacheManager(default_ttl_seconds=config.CACHE_TTL_SECONDS)
        self.cache_enabled = config.CACHE_ENABLED
    
    def get_market_data(
        self,
        vs_currency: str = "usd",
        per_page: int = 100,
        page: int = 1,
        sparkline: bool = False,
        price_change_percentage: str = "24h"
    ) -> List[Coin]:
        """
        Fetch cryptocurrency market data from CoinGecko.
        
        Args:
            vs_currency: Target currency (usd, eur, etc.)
            per_page: Number of results per page (max 250)
            page: Page number for pagination
            sparkline: Include sparkline data
            price_change_percentage: Price change timeframe
            
        Returns:
            List of Coin objects
        """
        # Build cache key
        cache_key = f"market_{vs_currency}_{per_page}_{page}_{sparkline}_{price_change_percentage}"
        
        # Check cache
        if self.cache_enabled:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Returning cached market data for {vs_currency}")
                return cached_data
        
        try:
            logger.info(f"Fetching market data from CoinGecko: page={page}, per_page={per_page}")
            
            params = {
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": min(per_page, config.MAX_PER_PAGE),
                "page": page,
                "sparkline": str(sparkline).lower(),
                "price_change_percentage": price_change_percentage
            }
            
            response = self.api_client.get("/coins/markets", params=params)
            
            if not isinstance(response, list):
                logger.error(f"Unexpected API response type: {type(response)}")
                return []
            
            coins = [Coin.from_api_response(item) for item in response]
            
            # Cache the results
            if self.cache_enabled:
                self.cache.set(cache_key, coins)
            
            logger.info(f"Successfully fetched {len(coins)} coins")
            return coins
            
        except APIClientError as e:
            logger.error(f"Failed to fetch market data: {e}")
            return []
    
    def get_coin_details(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information for a specific coin.
        
        Args:
            coin_id: CoinGecko coin identifier (e.g., 'bitcoin')
            
        Returns:
            Dictionary with coin details or None if error
        """
        cache_key = f"coin_details_{coin_id}"
        
        if self.cache_enabled:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            logger.info(f"Fetching details for coin: {coin_id}")
            response = self.api_client.get(f"/coins/{coin_id}")
            
            if self.cache_enabled:
                self.cache.set(cache_key, response, ttl_seconds=300)  # 5 minutes for details
            
            return response
            
        except APIClientError as e:
            logger.error(f"Failed to fetch coin details for {coin_id}: {e}")
            return None
    
    def get_trending_coins(self) -> List[Dict[str, Any]]:
        """
        Fetch trending coins from CoinGecko.
        
        Returns:
            List of trending coin data
        """
        cache_key = "trending_coins"
        
        if self.cache_enabled:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            logger.info("Fetching trending coins")
            response = self.api_client.get("/search/trending")
            
            trending = response.get("coins", [])
            
            if self.cache_enabled:
                self.cache.set(cache_key, trending, ttl_seconds=300)
            
            return trending
            
        except APIClientError as e:
            logger.error(f"Failed to fetch trending coins: {e}")
            return []
    
    def get_historical_prices(
        self,
        coin_id: str,
        days: int = 7,
        vs_currency: str = "usd"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch historical price data for a coin.
        
        Args:
            coin_id: CoinGecko coin identifier
            days: Number of days of historical data (1, 7, 14, 30, 90, 180, 365, max)
            vs_currency: Target currency
            
        Returns:
            Dictionary with market_chart data
        """
        cache_key = f"historical_{coin_id}_{days}_{vs_currency}"
        
        if self.cache_enabled:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            logger.info(f"Fetching historical data for {coin_id}, days={days}")
            params = {
                "vs_currency": vs_currency,
                "days": days
            }
            response = self.api_client.get(f"/coins/{coin_id}/market_chart", params=params)
            
            if self.cache_enabled:
                self.cache.set(cache_key, response, ttl_seconds=600)  # 10 minutes
            
            return response
            
        except APIClientError as e:
            logger.error(f"Failed to fetch historical prices for {coin_id}: {e}")
            return None
    
    def get_global_stats(self) -> Optional[Dict[str, Any]]:
        """
        Fetch global cryptocurrency market statistics.
        
        Returns:
            Dictionary with global market data
        """
        cache_key = "global_stats"
        
        if self.cache_enabled:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            logger.info("Fetching global market statistics")
            response = self.api_client.get("/global")
            
            global_data = response.get("data", {})
            
            if self.cache_enabled:
                self.cache.set(cache_key, global_data, ttl_seconds=60)  # 1 minute
            
            return global_data
            
        except APIClientError as e:
            logger.error(f"Failed to fetch global stats: {e}")
            return None
    
    def close(self):
        """Close API client session."""
        self.api_client.close()