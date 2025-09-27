# backend/routes/portfolio.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Portfolio, Stock

portfolio_bp = Blueprint("portfolio", __name__)

def get_current_user():
    """Get current user from JWT token."""
    user_id = get_jwt_identity()

    # Handle demo user
    if user_id == "1":
        return {"id": 1, "username": "demo"}

    return User.query.get(user_id)

@portfolio_bp.route("/", methods=["GET"])
@jwt_required()
def get_portfolio():
    """Get user's portfolio with holdings."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        portfolio = user.portfolio
        if not portfolio:
            # Create portfolio if it doesn't exist
            portfolio = Portfolio(user_id=user.id, cash=100000.00)
            db.session.add(portfolio)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "data": portfolio.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Get portfolio error: {e}")
        return jsonify({"error": "Failed to get portfolio"}), 500

@portfolio_bp.route("/balance", methods=["GET"])
@jwt_required()
def get_balance():
    """Get user's cash balance."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        portfolio = user.portfolio
        if not portfolio:
            portfolio = Portfolio(user_id=user.id, cash=100000.00)
            db.session.add(portfolio)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "balance": portfolio.cash
        }), 200
        
    except Exception as e:
        print(f"Get balance error: {e}")
        return jsonify({"error": "Failed to get balance"}), 500

@portfolio_bp.route("/holdings", methods=["GET"])
@jwt_required()
def get_holdings():
    """Get user's stock holdings."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        portfolio = user.portfolio
        if not portfolio:
            return jsonify({
                "success": True,
                "holdings": []
            }), 200
        
        holdings = [holding.to_dict() for holding in portfolio.holdings]
        
        return jsonify({
            "success": True,
            "holdings": holdings
        }), 200
        
    except Exception as e:
        print(f"Get holdings error: {e}")
        return jsonify({"error": "Failed to get holdings"}), 500

@portfolio_bp.route("/holding/<symbol>", methods=["GET"])
@jwt_required()
def get_holding(symbol):
    """Get specific stock holding."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        portfolio = user.portfolio
        if not portfolio:
            return jsonify({"error": "Holding not found"}), 404
        
        holding = Stock.query.filter_by(
            portfolio_id=portfolio.id,
            symbol=symbol.upper()
        ).first()
        
        if not holding:
            return jsonify({"error": "Holding not found"}), 404
        
        return jsonify({
            "success": True,
            "holding": holding.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Get holding error: {e}")
        return jsonify({"error": "Failed to get holding"}), 500

@portfolio_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_portfolio_stats():
    """Get portfolio statistics."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        portfolio = user.portfolio
        if not portfolio:
            portfolio = Portfolio(user_id=user.id, cash=100000.00)
            db.session.add(portfolio)
            db.session.commit()
        
        # Calculate stats
        total_value = portfolio.cash
        total_invested = 0
        holdings_count = len(portfolio.holdings)
        
        for holding in portfolio.holdings:
            holding_value = holding.quantity * holding.average_price
            total_value += holding_value
            total_invested += holding_value
        
        # Calculate gains (simplified - would need current market prices)
        total_gain = total_value - 100000.00  # Starting amount
        total_gain_percent = (total_gain / 100000.00) * 100 if 100000.00 > 0 else 0
        
        stats = {
            "total_value": round(total_value, 2),
            "cash_balance": round(portfolio.cash, 2),
            "total_invested": round(total_invested, 2),
            "total_gain": round(total_gain, 2),
            "total_gain_percent": round(total_gain_percent, 2),
            "holdings_count": holdings_count
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
        
    except Exception as e:
        print(f"Get portfolio stats error: {e}")
        return jsonify({"error": "Failed to get portfolio stats"}), 500

@portfolio_bp.route("/reset", methods=["POST"])
@jwt_required()
def reset_portfolio():
    """Reset portfolio to initial state (for testing)."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        portfolio = user.portfolio
        if portfolio:
            # Delete all holdings
            Stock.query.filter_by(portfolio_id=portfolio.id).delete()
            # Reset cash
            portfolio.cash = 100000.00
        else:
            # Create new portfolio
            portfolio = Portfolio(user_id=user.id, cash=100000.00)
            db.session.add(portfolio)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Portfolio reset successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Reset portfolio error: {e}")
        return jsonify({"error": "Failed to reset portfolio"}), 500