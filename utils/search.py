"""
Search utilities for finding cryptocurrencies by name or symbol.
"""

import re
from typing import List, Optional
from models.coin import Coin


def search_by_name(coins: List[Coin], query: str, case_sensitive: bool = False) -> List[Coin]:
    """
    Search coins by exact name match.
    
    Args:
        coins: List of Coin objects to search
        query: Search query string
        case_sensitive: Whether search is case-sensitive
        
    Returns:
        Filtered list of coins matching the name
    """
    if not query:
        return coins
    
    if not case_sensitive:
        query = query.lower()
        
    results = []
    for coin in coins:
        name = coin.name if case_sensitive else coin.name.lower()
        if query in name:
            results.append(coin)
    
    return results


def search_by_symbol(coins: List[Coin], query: str, case_sensitive: bool = False) -> List[Coin]:
    """
    Search coins by exact symbol match.
    
    Args:
        coins: List of Coin objects to search
        query: Search query string (e.g., 'BTC', 'ETH')
        case_sensitive: Whether search is case-sensitive
        
    Returns:
        Filtered list of coins matching the symbol
    """
    if not query:
        return coins
    
    if not case_sensitive:
        query = query.upper()
        
    results = []
    for coin in coins:
        symbol = coin.symbol if case_sensitive else coin.symbol.upper()
        if query in symbol:
            results.append(coin)
    
    return results


def search_partial_match(coins: List[Coin], query: str, case_sensitive: bool = False) -> List[Coin]:
    """
    Search coins by partial match on name OR symbol.
    
    Args:
        coins: List of Coin objects to search
        query: Search query string
        case_sensitive: Whether search is case-sensitive
        
    Returns:
        Filtered list of coins where name or symbol contains the query
    """
    if not query:
        return coins
    
    if not case_sensitive:
        query = query.lower()
    
    results = []
    for coin in coins:
        name = coin.name if case_sensitive else coin.name.lower()
        symbol = coin.symbol if case_sensitive else coin.symbol.lower()
        
        if query in name or query in symbol:
            results.append(coin)
    
    return results


def search_regex(coins: List[Coin], pattern: str, case_sensitive: bool = False) -> List[Coin]:
    """
    Search coins using regular expression pattern.
    
    Args:
        coins: List of Coin objects to search
        pattern: Regular expression pattern
        case_sensitive: Whether search is case-sensitive
        
    Returns:
        Filtered list of coins matching the regex pattern
    """
    if not pattern:
        return coins
    
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern, flags)
    
    results = []
    for coin in coins:
        if regex.search(coin.name) or regex.search(coin.symbol):
            results.append(coin)
    
    return results


def search_combined(coins: List[Coin], query: str, fields: List[str] = None) -> List[Coin]:
    """
    Search coins across multiple fields.
    
    Args:
        coins: List of Coin objects
        query: Search query
        fields: List of field names to search ('name', 'symbol', 'id')
        
    Returns:
        Filtered list of coins
    """
    if not query:
        return coins
    
    if fields is None:
        fields = ['name', 'symbol']
    
    query_lower = query.lower()
    results = []
    
    for coin in coins:
        matched = False
        for field in fields:
            value = getattr(coin, field, '')
            if query_lower in value.lower():
                matched = True
                break
        if matched:
            results.append(coin)
    
    return results