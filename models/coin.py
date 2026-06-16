"""
Coin data model representing cryptocurrency information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Coin:
    """
    Represents a cryptocurrency with its market data.
    
    Attributes:
        id: CoinGecko unique identifier (e.g., 'bitcoin')
        name: Full name of the coin (e.g., 'Bitcoin')
        symbol: Trading symbol (e.g., 'btc')
        current_price: Current price in USD
        market_cap: Total market capitalization
        market_cap_rank: Rank by market cap
        price_change_percentage_24h: 24h price change percentage
        total_volume: 24h trading volume
        image_url: URL to coin logo image
        ath: All-time high price
        ath_change_percentage: Percentage from ATH
        last_updated: Timestamp of last data update
    """
    
    id: str
    name: str
    symbol: str
    current_price: float
    market_cap: float
    market_cap_rank: int
    price_change_percentage_24h: float
    total_volume: float
    image_url: str
    ath: Optional[float] = None
    ath_change_percentage: Optional[float] = None
    last_updated: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> "Coin":
        """
        Create a Coin instance from CoinGecko API response.
        Handles missing fields gracefully.
        
        Args:
            data: Dictionary from CoinGecko /coins/markets endpoint
            
        Returns:
            Coin object with populated fields
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", "Unknown"),
            symbol=data.get("symbol", "").upper(),
            current_price=data.get("current_price", 0.0),
            market_cap=data.get("market_cap", 0.0),
            market_cap_rank=data.get("market_cap_rank", 0),
            price_change_percentage_24h=data.get("price_change_percentage_24h", 0.0),
            total_volume=data.get("total_volume", 0.0),
            image_url=data.get("image", ""),
            ath=data.get("ath"),
            ath_change_percentage=data.get("ath_change_percentage"),
            last_updated=data.get("last_updated")
        )
    
    def to_dict(self) -> dict:
        """Convert Coin object to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "current_price": self.current_price,
            "market_cap": self.market_cap,
            "market_cap_rank": self.market_cap_rank,
            "price_change_percentage_24h": self.price_change_percentage_24h,
            "total_volume": self.total_volume,
            "image_url": self.image_url,
            "ath": self.ath,
            "ath_change_percentage": self.ath_change_percentage,
            "last_updated": self.last_updated
        }
    
    def get_formatted_price(self) -> str:
        """Return formatted price string."""
        if self.current_price < 0.01:
            return f"${self.current_price:.8f}"
        elif self.current_price < 1:
            return f"${self.current_price:.4f}"
        else:
            return f"${self.current_price:,.2f}"
    
    def get_formatted_market_cap(self) -> str:
        """Return formatted market cap (e.g., $1.2B)."""
        if self.market_cap >= 1_000_000_000:
            return f"${self.market_cap / 1_000_000_000:.2f}B"
        elif self.market_cap >= 1_000_000:
            return f"${self.market_cap / 1_000_000:.2f}M"
        else:
            return f"${self.market_cap:,.0f}"