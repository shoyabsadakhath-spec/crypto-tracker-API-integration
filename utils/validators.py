"""
Input validation utilities for user inputs.
"""

import re
from typing import Union, Optional


def validate_price_range(price_range: str) -> Optional[tuple]:
    """
    Validate and parse price range string.
    
    Args:
        price_range: String like 'below_1', '1_to_100', etc.
        
    Returns:
        Tuple of (min_price, max_price) or None if invalid
    """
    ranges = {
        'below_1': (0, 1),
        '1_to_100': (1, 100),
        '100_to_1000': (100, 1000),
        'above_1000': (1000, float('inf'))
    }
    return ranges.get(price_range)


def validate_market_cap_category(category: str) -> Optional[tuple]:
    """
    Validate market cap category.
    
    Args:
        category: 'small', 'mid', or 'large'
        
    Returns:
        Tuple of (min, max) or None if invalid
    """
    categories = {
        'small': (0, 500_000_000),
        'mid': (500_000_000, 5_000_000_000),
        'large': (5_000_000_000, float('inf'))
    }
    return categories.get(category)


def validate_volume_category(category: str) -> Optional[tuple]:
    """
    Validate volume category.
    
    Args:
        category: 'high' or 'low'
        
    Returns:
        Tuple of (min, max) or None if invalid
    """
    categories = {
        'high': (100_000_000, float('inf')),
        'low': (0, 10_000_000)
    }
    return categories.get(category)


def validate_sort_field(field: str) -> bool:
    """
    Validate sort field name.
    
    Args:
        field: Sort field (price, market_cap, volume, change, rank)
        
    Returns:
        True if valid, False otherwise
    """
    valid_fields = {'price', 'market_cap', 'volume', 'change', 'rank'}
    return field in valid_fields


def validate_sort_order(order: str) -> bool:
    """
    Validate sort order.
    
    Args:
        order: 'asc' or 'desc'
        
    Returns:
        True if valid, False otherwise
    """
    return order in {'asc', 'desc'}


def sanitize_search_query(query: str) -> str:
    """
    Sanitize search query input.
    
    Args:
        query: Raw search query
        
    Returns:
        Sanitized query string
    """
    if not query:
        return ""
    # Remove special characters that could cause regex issues
    query = re.sub(r'[^\w\s]', '', query)
    return query.strip()


def validate_per_page(per_page: int) -> int:
    """
    Validate and clamp per_page value.
    
    Args:
        per_page: Requested items per page
        
    Returns:
        Validated per_page between 1 and 250
    """
    return max(1, min(per_page, 250))


def validate_page(page: int) -> int:
    """
    Validate page number.
    
    Args:
        page: Requested page number
        
    Returns:
        Validated page number (minimum 1)
    """
    return max(1, page)