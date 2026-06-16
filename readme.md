# Crypto Market Tracker

A production-ready cryptocurrency market tracking web application built with Python Flask and CoinGecko API. Features real-time market data, advanced filtering, search, sorting, and caching.

## Features

### Core Functionality
- **Dashboard**: Display top cryptocurrencies with price, market cap, volume, and 24h changes
- **Search**: Search by coin name or symbol with partial and case-insensitive matching
- **Filters**:
  - Price range (Below $1, $1-$100, $100-$1000, Above $1000)
  - Market cap (Small/Mid/Large cap)
  - Volume (High/Low volume)
  - Performance (Top gainers/losers, positive/negative change)
- **Sorting**: Sort by price, market cap, volume, percentage change, or rank (ascending/descending)
- **Pagination**: Navigate through large datasets efficiently

### Technical Highlights
- **Clean Architecture**: Separation of concerns with services, models, utils, and cache layers
- **Caching**: In-memory cache with TTL to reduce API calls
- **Error Handling**: Comprehensive error handling with retry logic and graceful degradation
- **Type Hints**: Full type annotations for better code maintainability
- **Logging**: Detailed logging for debugging and monitoring
- **API Integration**: Custom API client with timeout handling and exponential backoff retries

## Tech Stack

- **Backend**: Python 3.9+, Flask
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (jQuery)
- **API**: CoinGecko Public API
- **Caching**: Custom in-memory cache manager
- **HTTP Client**: Python requests (no SDKs or wrappers)

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Instructions

1. **Clone or extract the project**:
```bash
cd crypto_market_tracker enter
pip install -r requirements.txt enter
python app.py enter 
server will come in terminal
then ctrl+enter the web app automatically open in your browser 
