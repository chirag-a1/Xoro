from flask import Blueprint, jsonify
import random
import time

market_data_bp = Blueprint('market_data', __name__)

# Demo prices that change slightly on each request
@market_data_bp.route("/demo-prices", methods=["GET"])
def get_demo_prices():
    """Get demo prices for watchlist symbols - no auth required."""
    watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
    prices = {}
    
    for symbol in watchlist:
        base = {
            "AAPL": 175, "MSFT": 320, "GOOGL": 130, "AMZN": 130,
            "TSLA": 240, "META": 290, "NVDA": 410, "NFLX": 380
        }.get(symbol, 100)
        
        # Add small random changes
        change = round(random.uniform(-5, 5), 2)
        price = round(base + change, 2)
        change_percent = round((change / base) * 100, 2)
        
        prices[symbol] = {
            "symbol": symbol,
            "price": price,
            "change": change,
            "changePercent": change_percent,
            "timestamp": int(time.time())
        }
    
    return jsonify({
        "success": True,
        "data": prices
    })