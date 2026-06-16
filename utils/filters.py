"""
Filter utilities for cryptocurrency data.
"""

from typing import List, Callable, Optional, Tuple
from models.coin import Coin


def filter_by_price_range(
    coins: List[Coin],
    min_price: float,
    max_price: float
) -> List[Coin]:
    """
    Filter coins by price range.
    
    Args:
        coins: List of Coin objects
        min_price: Minimum price (inclusive)
        max_price: Maximum price (inclusive)
        
    Returns:
        Filtered list of coins
    """
    return [
        coin for coin in coins
        if min_price <= coin.current_price <= max_price
    ]


def filter_by_market_cap_range(
    coins: List[Coin],
    min_market_cap: float,
    max_market_cap: float
) -> List[Coin]:
    """
    Filter coins by market cap range.
    
    Args:
        coins: List of Coin objects
        min_market_cap: Minimum market cap (inclusive)
        max_market_cap: Maximum market cap (inclusive)
        
    Returns:
        Filtered list of coins
    """
    return [
        coin for coin in coins
        if min_market_cap <= coin.market_cap <= max_market_cap
    ]


def filter_by_volume_range(
    coins: List[Coin],
    min_volume: float,
    max_volume: float
) -> List[Coin]:
    """
    Filter coins by trading volume range.
    
    Args:
        coins: List of Coin objects
        min_volume: Minimum volume (inclusive)
        max_volume: Maximum volume (inclusive)
        
    Returns:
        Filtered list of coins
    """
    return [
        coin for coin in coins
        if min_volume <= coin.total_volume <= max_volume
    ]


def filter_top_gainers(coins: List[Coin], top_n: int = 10) -> List[Coin]:
    """
    Get top gainers by 24h price change percentage.
    
    Args:
        coins: List of Coin objects
        top_n: Number of top gainers to return
        
    Returns:
        List of top gainers (highest positive change)
    """
    gainers = [coin for coin in coins if coin.price_change_percentage_24h > 0]
    gainers.sort(key=lambda x: x.price_change_percentage_24h, reverse=True)
    return gainers[:top_n]


def filter_top_losers(coins: List[Coin], top_n: int = 10) -> List[Coin]:
    """
    Get top losers by 24h price change percentage.
    
    Args:
        coins: List of Coin objects
        top_n: Number of top losers to return
        
    Returns:
        List of top losers (most negative change)
    """
    losers = [coin for coin in coins if coin.price_change_percentage_24h < 0]
    losers.sort(key=lambda x: x.price_change_percentage_24h)
    return losers[:top_n]


def filter_positive_change(coins: List[Coin]) -> List[Coin]:
    """
    Filter coins with positive 24h price change.
    
    Args:
        coins: List of Coin objects
        
    Returns:
        List of coins with positive change
    """
    return [coin for coin in coins if coin.price_change_percentage_24h > 0]


def filter_negative_change(coins: List[Coin]) -> List[Coin]:
    """
    Filter coins with negative 24h price change.
    
    Args:
        coins: List of Coin objects
        
    Returns:
        List of coins with negative change
    """
    return [coin for coin in coins if coin.price_change_percentage_24h < 0]


def filter_high_volume(coins: List[Coin], threshold: float = 100_000_000) -> List[Coin]:
    """
    Filter coins with high trading volume.
    
    Args:
        coins: List of Coin objects
        threshold: Minimum volume threshold (default $100M)
        
    Returns:
        List of high volume coins
    """
    return [coin for coin in coins if coin.total_volume >= threshold]


def filter_low_volume(coins: List[Coin], threshold: float = 10_000_000) -> List[Coin]:
    """
    Filter coins with low trading volume.
    
    Args:
        coins: List of Coin objects
        threshold: Maximum volume threshold (default $10M)
        
    Returns:
        List of low volume coins
    """
    return [coin for coin in coins if coin.total_volume <= threshold]


def apply_filters(
    coins: List[Coin],
    filters: List[Tuple[Callable, dict]]
) -> List[Coin]:
    """
    Apply multiple filters sequentially.
    
    Args:
        coins: List of Coin objects
        filters: List of tuples (filter_function, kwargs)
        
    Returns:
        Filtered list of coins
    """
    result = coins
    for filter_func, kwargs in filters:
        result = filter_func(result, **kwargs)
    return result