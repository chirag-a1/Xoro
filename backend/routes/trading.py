# backend/routes/trading.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from models import db, User, Portfolio, Stock, Trade
from utils.price_simulator import get_price

trading_bp = Blueprint("trading", __name__)

def get_current_user():
    """Get current user from JWT token."""
    user_id = get_jwt_identity()

    # Handle demo user
    if user_id == "1":
        return {"id": 1, "username": "demo"}

    return User.query.get(user_id)

def validate_trade_data(data, trade_type):
    """Validate trade data."""
    # For market orders, price may be omitted
    required_fields = ["symbol", "quantity"]
    if data.get('order_type', 'market').lower() == 'limit':
        required_fields.append('price')
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    symbol = data.get("symbol", "").strip().upper()
    quantity = data.get("quantity")
    price = data.get("price")
    
    # Validate symbol
    if not Stock.validate_symbol(symbol):
        return False, "Invalid stock symbol"
    
    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return False, "Quantity must be positive"
    except (ValueError, TypeError):
        return False, "Quantity must be a valid integer"
    
    # Validate price
    try:
        price = float(price)
        if price <= 0:
            return False, "Price must be positive"
    except (ValueError, TypeError):
        return False, "Price must be a valid number"
    
    return True, None


def execute_buy(user, symbol, quantity, price):
    total_cost = quantity * price

    portfolio = user.portfolio
    if not portfolio:
        portfolio = Portfolio(user_id=user.id, cash=100000.00)
        db.session.add(portfolio)
        db.session.flush()

    if portfolio.cash < total_cost:
        return False, "Insufficient funds"

    existing_holding = Stock.query.filter_by(portfolio_id=portfolio.id, symbol=symbol).first()
    if existing_holding:
        old_total_value = existing_holding.quantity * existing_holding.average_price
        new_total_value = old_total_value + total_cost
        new_quantity = existing_holding.quantity + quantity
        existing_holding.quantity = new_quantity
        existing_holding.average_price = new_total_value / new_quantity
    else:
        new_holding = Stock(symbol=symbol, quantity=quantity, average_price=price, portfolio_id=portfolio.id)
        db.session.add(new_holding)

    portfolio.cash -= total_cost

    trade = Trade(symbol=symbol, quantity=quantity, price=price, trade_type="BUY", user_id=user.id)
    db.session.add(trade)
    db.session.commit()

    return True, trade.to_dict()


def execute_sell(user, symbol, quantity, price):
    portfolio = user.portfolio
    if not portfolio:
        return False, "No portfolio"

    holding = Stock.query.filter_by(portfolio_id=portfolio.id, symbol=symbol).first()
    if not holding:
        return False, f"You don't own any shares of {symbol}"

    if holding.quantity < quantity:
        return False, f"Insufficient shares. You own {holding.quantity} shares of {symbol}"

    total_proceeds = quantity * price

    if holding.quantity == quantity:
        db.session.delete(holding)
    else:
        holding.quantity -= quantity

    portfolio.cash += total_proceeds

    trade = Trade(symbol=symbol, quantity=quantity, price=price, trade_type="SELL", user_id=user.id)
    db.session.add(trade)
    db.session.commit()

    return True, trade.to_dict()


@trading_bp.route("/order", methods=["POST"])
@jwt_required()
def place_order():
    """Unified order endpoint supporting market and limit orders."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400

        order_type = data.get('order_type', 'market').lower()
        side = data.get('side', 'buy').lower()

        # Basic validation
        is_valid, err = validate_trade_data(data, side.upper())
        if not is_valid:
            return jsonify({"error": err}), 400

        symbol = data.get('symbol', '').strip().upper()
        quantity = int(data.get('quantity'))

        # Determine execution price
        if order_type == 'market':
            price = get_price(symbol) or float(data.get('price', 0.0))
            if not price:
                return jsonify({"error": "Market price unavailable"}), 503
            # Execute immediately
            user = get_current_user()
            if not user:
                return jsonify({"error": "User not found"}), 404

            if side == 'buy':
                ok, result = execute_buy(user, symbol, quantity, price)
            else:
                ok, result = execute_sell(user, symbol, quantity, price)

            if not ok:
                return jsonify({"error": result}), 400

            return jsonify({"success": True, "trade": result, "executed_price": price}), 200

        elif order_type == 'limit':
            # For this simple implementation, store limit orders as pending trades in DB with price target
            # Here we'll just check if current price already meets the condition; otherwise return pending
            target_price = float(data.get('price'))
            current_price = get_price(symbol)
            if current_price and ((side == 'buy' and current_price <= target_price) or (side == 'sell' and current_price >= target_price)):
                # Execute immediately
                user = get_current_user()
                if not user:
                    return jsonify({"error": "User not found"}), 404
                if side == 'buy':
                    ok, result = execute_buy(user, symbol, quantity, current_price)
                else:
                    ok, result = execute_sell(user, symbol, quantity, current_price)

                if not ok:
                    return jsonify({"error": result}), 400

                return jsonify({"success": True, "trade": result, "executed_price": current_price}), 200
            else:
                # In a real system we'd persist pending orders and match them later. Here return pending acknowledgement.
                return jsonify({"success": True, "status": "pending", "message": "Limit order queued (simulated)."}), 200

        else:
            return jsonify({"error": "Unsupported order type"}), 400

    except Exception as e:
        db.session.rollback()
        print(f"Place order error: {e}")
        return jsonify({"error": "Failed to place order"}), 500

@trading_bp.route("/buy", methods=["POST"])
@jwt_required()
def buy_stock():
    """Buy stock shares."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        # Validate trade data
        is_valid, error_msg = validate_trade_data(data, "BUY")
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        symbol = data.get("symbol", "").strip().upper()
        quantity = int(data.get("quantity"))
        price = float(data.get("price"))
        total_cost = quantity * price
        
        # Get or create portfolio
        portfolio = user.portfolio
        if not portfolio:
            portfolio = Portfolio(user_id=user.id, cash=100000.00)
            db.session.add(portfolio)
            db.session.flush()
        
        # Check if user has enough cash
        if portfolio.cash < total_cost:
            return jsonify({"error": "Insufficient funds"}), 400
        
        # Check if user already owns this stock
        existing_holding = Stock.query.filter_by(
            portfolio_id=portfolio.id,
            symbol=symbol
        ).first()
        
        if existing_holding:
            # Update existing holding
            old_total_value = existing_holding.quantity * existing_holding.average_price
            new_total_value = old_total_value + total_cost
            new_quantity = existing_holding.quantity + quantity
            new_average_price = new_total_value / new_quantity
            
            existing_holding.quantity = new_quantity
            existing_holding.average_price = new_average_price
        else:
            # Create new holding
            new_holding = Stock(
                symbol=symbol,
                quantity=quantity,
                average_price=price,
                portfolio_id=portfolio.id
            )
            db.session.add(new_holding)
        
        # Update cash balance
        portfolio.cash -= total_cost
        
        # Record trade
        trade = Trade(
            symbol=symbol,
            quantity=quantity,
            price=price,
            trade_type="BUY",
            user_id=user.id
        )
        db.session.add(trade)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Successfully bought {quantity} shares of {symbol}",
            "trade": trade.to_dict(),
            "remaining_cash": portfolio.cash
        }), 200
        
    except IntegrityError as e:
        db.session.rollback()
        print(f"Buy trade integrity error: {e}")
        return jsonify({"error": "Trade failed due to data conflict"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Buy trade error: {e}")
        return jsonify({"error": "Failed to execute buy order"}), 500

@trading_bp.route("/sell", methods=["POST"])
@jwt_required()
def sell_stock():
    """Sell stock shares."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        # Validate trade data
        is_valid, error_msg = validate_trade_data(data, "SELL")
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        symbol = data.get("symbol", "").strip().upper()
        quantity = int(data.get("quantity"))
        price = float(data.get("price"))
        total_proceeds = quantity * price
        
        # Get portfolio
        portfolio = user.portfolio
        if not portfolio:
            return jsonify({"error": "No portfolio found"}), 404
        
        # Check if user owns this stock
        holding = Stock.query.filter_by(
            portfolio_id=portfolio.id,
            symbol=symbol
        ).first()
        
        if not holding:
            return jsonify({"error": f"You don't own any shares of {symbol}"}), 400
        
        # Check if user has enough shares to sell
        if holding.quantity < quantity:
            return jsonify({
                "error": f"Insufficient shares. You own {holding.quantity} shares of {symbol}"
            }), 400
        
        # Update holding
        if holding.quantity == quantity:
            # Sell all shares - delete holding
            db.session.delete(holding)
        else:
            # Partial sale - update quantity
            holding.quantity -= quantity
        
        # Update cash balance
        portfolio.cash += total_proceeds
        
        # Record trade
        trade = Trade(
            symbol=symbol,
            quantity=quantity,
            price=price,
            trade_type="SELL",
            user_id=user.id
        )
        db.session.add(trade)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Successfully sold {quantity} shares of {symbol}",
            "trade": trade.to_dict(),
            "remaining_cash": portfolio.cash
        }), 200
        
    except IntegrityError as e:
        db.session.rollback()
        print(f"Sell trade integrity error: {e}")
        return jsonify({"error": "Trade failed due to data conflict"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Sell trade error: {e}")
        return jsonify({"error": "Failed to execute sell order"}), 500

@trading_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_trading_history():
    """Get user's trading history."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get query parameters
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        symbol = request.args.get("symbol", "").strip().upper()
        
        # Build query
        query = Trade.query.filter_by(user_id=user.id)
        
        if symbol:
            query = query.filter_by(symbol=symbol)
        
        # Order by timestamp descending
        query = query.order_by(Trade.timestamp.desc())
        
        # Apply pagination
        trades = query.offset(offset).limit(limit).all()
        
        # Convert to dict
        trades_data = [trade.to_dict() for trade in trades]
        
        return jsonify({
            "success": True,
            "trades": trades_data,
            "count": len(trades_data)
        }), 200
        
    except Exception as e:
        print(f"Get trading history error: {e}")
        return jsonify({"error": "Failed to get trading history"}), 500

@trading_bp.route("/orders/<int:trade_id>", methods=["GET"])
@jwt_required()
def get_trade(trade_id):
    """Get specific trade details."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        trade = Trade.query.filter_by(id=trade_id, user_id=user.id).first()
        if not trade:
            return jsonify({"error": "Trade not found"}), 404
        
        return jsonify({
            "success": True,
            "trade": trade.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Get trade error: {e}")
        return jsonify({"error": "Failed to get trade"}), 500

@trading_bp.route("/market-data/<symbol>", methods=["GET"])
def get_market_data(symbol):
    """Get market data for a stock symbol (placeholder)."""
    try:
        symbol = symbol.strip().upper()
        
        if not Stock.validate_symbol(symbol):
            return jsonify({"error": "Invalid stock symbol"}), 400
        
        # This would integrate with a real market data API
        # For now, return mock data
        mock_data = {
            "symbol": symbol,
            "price": 150.00,
            "change": 2.50,
            "change_percent": 1.69,
            "volume": 1000000,
            "market_cap": 2500000000000,
            "last_updated": "2024-01-01T12:00:00Z"
        }
        
        return jsonify({
            "success": True,
            "data": mock_data
        }), 200
        
    except Exception as e:
        print(f"Get market data error: {e}")
        return jsonify({"error": "Failed to get market data"}), 500