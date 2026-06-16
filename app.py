"""
Flask web application for Crypto Market Tracker.
Provides dashboard, search, filtering, and sorting functionality.
"""

import logging
from flask import Flask, render_template, jsonify, request

from config import get_config
from services.crypto_service import CryptoService
from cache.cache_manager import CacheManager
from utils.search import search_partial_match
from utils.filters import (
    filter_by_price_range, filter_by_market_cap_range,
    filter_by_volume_range, filter_top_gainers,
    filter_top_losers, filter_positive_change, filter_negative_change,
    filter_high_volume, filter_low_volume
)
from utils.validators import (
    validate_price_range, validate_market_cap_category,
    validate_volume_category, validate_sort_field,
    validate_sort_order, sanitize_search_query,
    validate_per_page, validate_page
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
config = get_config()
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Initialize services
cache_manager = CacheManager(default_ttl_seconds=config.CACHE_TTL_SECONDS)
crypto_service = CryptoService(cache_manager=cache_manager)


@app.route('/')
def dashboard():
    """Render main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/markets')
def get_markets():
    """
    API endpoint for market data with search, filter, and sort capabilities.
    
    Query Parameters:
        - search: Search query (name or symbol)
        - price_range: below_1, 1_to_100, 100_to_1000, above_1000
        - cap_category: small, mid, large
        - volume_category: high, low
        - performance: gainers, losers, positive, negative
        - sort_by: price, market_cap, volume, change, rank
        - sort_order: asc, desc
        - page: Page number
        - per_page: Items per page
    """
    try:
        # Get query parameters
        search_query = request.args.get('search', '').strip()
        price_range_key = request.args.get('price_range', '')
        cap_category_key = request.args.get('cap_category', '')
        volume_category_key = request.args.get('volume_category', '')
        performance_type = request.args.get('performance', '')
        sort_by = request.args.get('sort_by', 'market_cap')
        sort_order = request.args.get('sort_order', 'desc')
        page = validate_page(int(request.args.get('page', 1)))
        per_page = validate_per_page(int(request.args.get('per_page', 50)))
        
        # Fetch market data from service
        coins = crypto_service.get_market_data(per_page=250)  # Get more for filtering
        
        if not coins:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch market data',
                'data': [],
                'total': 0
            }), 500
        
        # Apply search filter
        if search_query:
            sanitized = sanitize_search_query(search_query)
            if sanitized:
                coins = search_partial_match(coins, sanitized)
        
        # Apply price range filter
        if price_range_key:
            price_range = validate_price_range(price_range_key)
            if price_range:
                min_price, max_price = price_range
                coins = filter_by_price_range(coins, min_price, max_price)
        
        # Apply market cap category filter
        if cap_category_key:
            cap_range = validate_market_cap_category(cap_category_key)
            if cap_range:
                min_cap, max_cap = cap_range
                coins = filter_by_market_cap_range(coins, min_cap, max_cap)
        
        # Apply volume category filter
        if volume_category_key:
            volume_range = validate_volume_category(volume_category_key)
            if volume_range:
                min_vol, max_vol = volume_range
                coins = filter_by_volume_range(coins, min_vol, max_vol)
        
        # Apply performance filter
        if performance_type:
            if performance_type == 'gainers':
                coins = filter_top_gainers(coins, top_n=len(coins))
            elif performance_type == 'losers':
                coins = filter_top_losers(coins, top_n=len(coins))
            elif performance_type == 'positive':
                coins = filter_positive_change(coins)
            elif performance_type == 'negative':
                coins = filter_negative_change(coins)
            elif performance_type == 'high_volume':
                coins = filter_high_volume(coins)
            elif performance_type == 'low_volume':
                coins = filter_low_volume(coins)
        
        # Apply sorting
        if validate_sort_field(sort_by) and validate_sort_order(sort_order):
            reverse = (sort_order == 'desc')
            
            sort_key_map = {
                'price': lambda x: x.current_price,
                'market_cap': lambda x: x.market_cap,
                'volume': lambda x: x.total_volume,
                'change': lambda x: x.price_change_percentage_24h,
                'rank': lambda x: x.market_cap_rank
            }
            
            sort_key = sort_key_map.get(sort_by, lambda x: x.market_cap)
            coins.sort(key=sort_key, reverse=reverse)
        
        # Apply pagination
        total = len(coins)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_coins = coins[start_idx:end_idx]
        
        # Convert to dict for JSON response
        coin_dicts = [coin.to_dict() for coin in paginated_coins]
        
        return jsonify({
            'success': True,
            'data': coin_dicts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 0,
            'filters_applied': {
                'search': search_query,
                'price_range': price_range_key,
                'cap_category': cap_category_key,
                'volume_category': volume_category_key,
                'performance': performance_type,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
        
    except Exception as e:
        logger.error(f"Error in /api/markets: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': [],
            'total': 0
        }), 500


@app.route('/api/global')
def get_global_stats():
    """API endpoint for global market statistics."""
    try:
        stats = crypto_service.get_global_stats()
        if stats:
            return jsonify({
                'success': True,
                'data': stats
            })
        return jsonify({
            'success': False,
            'error': 'Failed to fetch global stats'
        }), 500
    except Exception as e:
        logger.error(f"Error in /api/global: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trending')
def get_trending():
    """API endpoint for trending coins."""
    try:
        trending = crypto_service.get_trending_coins()
        return jsonify({
            'success': True,
            'data': trending
        })
    except Exception as e:
        logger.error(f"Error in /api/trending: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/coin/<coin_id>')
def get_coin_details(coin_id):
    """API endpoint for detailed coin information."""
    try:
        details = crypto_service.get_coin_details(coin_id)
        if details:
            return jsonify({
                'success': True,
                'data': details
            })
        return jsonify({
            'success': False,
            'error': 'Coin not found'
        }), 404
    except Exception as e:
        logger.error(f"Error in /api/coin/{coin_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/historical/<coin_id>')
def get_historical(coin_id):
    """API endpoint for historical price data."""
    try:
        days = int(request.args.get('days', 7))
        historical = crypto_service.get_historical_prices(coin_id, days=days)
        if historical:
            return jsonify({
                'success': True,
                'data': historical
            })
        return jsonify({
            'success': False,
            'error': 'Failed to fetch historical data'
        }), 500
    except Exception as e:
        logger.error(f"Error in /api/historical/{coin_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cache/stats')
def cache_stats():
    """API endpoint for cache statistics (debug only)."""
    if app.debug:
        return jsonify(cache_manager.get_stats())
    return jsonify({'error': 'Not available in production'}), 403


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f"Starting Crypto Market Tracker on port {config.PORT}")
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )