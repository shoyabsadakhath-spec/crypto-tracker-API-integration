"""
Cache management module with TTL support.
"""

import time
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Simple in-memory cache manager with Time-To-Live (TTL) expiration.
    
    Features:
        - Thread-safe (for single-threaded Flask dev server)
        - Automatic expiration
        - Hit/miss tracking
    """
    
    def __init__(self, default_ttl_seconds: int = 120):
        """
        Initialize cache manager.
        
        Args:
            default_ttl_seconds: Default TTL for cache entries
        """
        self._cache: Dict[str, dict] = {}
        self._default_ttl = default_ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache if not expired.
        
        Args:
            key: Cache key string
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            return None
        
        entry = self._cache[key]
        if time.time() > entry["expires_at"]:
            # Entry expired
            del self._cache[key]
            self._misses += 1
            return None
        
        self._hits += 1
        logger.debug(f"Cache HIT for key: {key}")
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Store item in cache with TTL.
        
        Args:
            key: Cache key string
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }
        logger.debug(f"Cached key: {key} with TTL: {ttl}s")
    
    def delete(self, key: str) -> bool:
        """
        Remove item from cache.
        
        Args:
            key: Cache key string
            
        Returns:
            True if key existed, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted cache key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Return cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "size": len(self._cache)
        }
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None