"""
Configuration module for Crypto Market Tracker.
Contains all environment variables, constants, and API settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()


class Config:
    """Main configuration class."""
    
    # API Configuration
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    REQUEST_TIMEOUT = 10  # seconds
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 1  # Exponential backoff: 1, 2, 4 seconds
    
    # Cache Configuration
    CACHE_TTL_SECONDS = 120  # 2 minutes cache for market data
    CACHE_ENABLED = True
    
    # Pagination
    DEFAULT_PER_PAGE = 100
    MAX_PER_PAGE = 250
    
    # Filter Categories
    PRICE_RANGES = {
        "below_1": (0, 1),
        "1_to_100": (1, 100),
        "100_to_1000": (100, 1000),
        "above_1000": (1000, float('inf'))
    }
    
    MARKET_CAP_CATEGORIES = {
        "small": (0, 500_000_000),        # < $500M
        "mid": (500_000_000, 5_000_000_000),  # $500M - $5B
        "large": (5_000_000_000, float('inf'))  # > $5B
    }
    
    VOLUME_CATEGORIES = {
        "high": (100_000_000, float('inf')),   # > $100M volume
        "low": (0, 10_000_000)                  # < $10M volume
    }
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    CACHE_TTL_SECONDS = 30  # Shorter cache for development


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    CACHE_TTL_SECONDS = 300  # Longer cache for production


# Select configuration based on environment
def get_config():
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig