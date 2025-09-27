# backend/routes/ai_recommendations.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Portfolio, Stock, Trade
import requests
import json
import os

ai_bp = Blueprint("ai", __name__)

def get_current_user():
    """Get current user from JWT token. Returns None when no token provided."""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)

def get_portfolio_summary(user):
    """Get portfolio summary for AI analysis."""
    # Support guest/unauthenticated users by returning default values
    if not user:
        return {
            "cash": 100000.00,
            "holdings": [],
            "total_value": 100000.00
        }

    portfolio = user.portfolio
    if not portfolio:
        return {
            "cash": 100000.00,
            "holdings": [],
            "total_value": 100000.00
        }
    
    holdings = []
    total_invested = portfolio.cash
    
    for holding in portfolio.holdings:
        holdings.append({
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "average_price": holding.average_price,
            "current_value": holding.quantity * holding.average_price
        })
        total_invested += holding.quantity * holding.average_price
    
    return {
        "cash": portfolio.cash,
        "holdings": holdings,
        "total_value": total_invested
    }

def get_recent_trades(user, limit=10):
    """Get recent trades for AI analysis."""
    if not user:
        return []

    trades = Trade.query.filter_by(user_id=user.id)\
                       .order_by(Trade.timestamp.desc())\
                       .limit(limit).all()
    
    return [trade.to_dict() for trade in trades]

@ai_bp.route("/recommendations", methods=["POST"])
@jwt_required(optional=True)
def get_ai_recommendations():
    """Get AI-powered trading recommendations."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json() or {}
        analysis_type = data.get("type", "general")  # general, buy, sell, portfolio
        
        # Get portfolio data
        portfolio_summary = get_portfolio_summary(user)
        recent_trades = get_recent_trades(user)
        
        # Prepare data for AI analysis
        analysis_data = {
            "user_id": user.id,
            "portfolio": portfolio_summary,
            "recent_trades": recent_trades,
            "analysis_type": analysis_type,
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Generate recommendations using Gemini AI
        recommendations = generate_gemini_recommendations(analysis_data)
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "analysis_type": analysis_type
        }), 200
        
    except Exception as e:
        print(f"AI recommendations error: {e}")
        return jsonify({"error": "Failed to generate recommendations"}), 500

def generate_gemini_recommendations(data):
    """Generate recommendations using Gemini AI."""
    try:
        # Gemini API configuration
        api_key = os.environ.get('GEMINI_API_KEY')
        # Prefer service-account based OAuth if GOOGLE_APPLICATION_CREDENTIALS is set
        use_service_account = bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        # Prepare prompt
        prompt = f"""
        You are a professional financial advisor analyzing a paper trading portfolio.
        
        Portfolio Data:
        - Cash Balance: ${data['portfolio']['cash']:,.2f}
        - Total Value: ${data['portfolio']['total_value']:,.2f}
        - Holdings: {len(data['portfolio']['holdings'])} stocks
        
        Current Holdings:
        {json.dumps(data['portfolio']['holdings'], indent=2)}
        
        Recent Trades:
        {json.dumps(data['recent_trades'][:5], indent=2)}
        
        Analysis Type: {data['analysis_type']}
        
        Please provide 3-5 specific, actionable trading recommendations with:
        1. Action (BUY/SELL/HOLD)
        2. Stock symbol
        3. Reasoning
        4. Confidence level (60-95%)
        5. Risk assessment
        
        Format as JSON array with fields: action, symbol, reasoning, confidence, risk_level.
        Focus on realistic recommendations for a paper trading account.
        """
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        # Attempt authenticated request
        response = None
        # If a service account credential is provided, use OAuth2 to get an access token
        if use_service_account:
            try:
                # Lazy-import google auth libraries; they may not be installed in all dev setups
                from google.oauth2 import service_account
                from google.auth.transport.requests import Request as GoogleRequest

                creds = service_account.Credentials.from_service_account_file(
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS']
                )
                # Scope for cloud platform access
                scoped = creds.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
                scoped.refresh(GoogleRequest())
                access_token = scoped.token
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.post(url, json=payload, headers=headers, timeout=30)
            except Exception as e:
                # If google-auth isn't available or refresh failed, fall back to API key path below
                print(f"Service account auth failed: {e}")
                response = None

        # If service-account call not used or failed, try API key if present
        if response is None:
            if api_key:
                response = requests.post(f"{url}?key={api_key}", json=payload, timeout=30)
            else:
                # No credentials configured — return a helpful error object to the frontend
                print("No Gemini credentials configured: set GOOGLE_APPLICATION_CREDENTIALS or GEMINI_API_KEY")
                return [{
                    "action": "ERROR",
                    "symbol": None,
                    "reasoning": "Gemini API not configured on the server. Provide service account credentials or an API key.",
                    "confidence": 0,
                    "risk_level": "None"
                }]

        if response is not None and response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']

                # Try to parse JSON from response
                try:
                    # Extract JSON from the response text
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                        recommendations = json.loads(json_str)
                        return recommendations
                except json.JSONDecodeError:
                    pass

                # Fallback: return structured recommendations
                return [
                    {
                        "action": "BUY",
                        "symbol": "AAPL",
                        "reasoning": "Strong fundamentals and growth potential",
                        "confidence": 75,
                        "risk_level": "Medium"
                    },
                    {
                        "action": "HOLD",
                        "symbol": "MSFT",
                        "reasoning": "Stable performance, good for long-term",
                        "confidence": 80,
                        "risk_level": "Low"
                    }
                ]

        # If the API returned a 401/403, include a clear error message in logs and return fallback
        if response is not None and response.status_code in (401, 403):
            print(f"Gemini API authentication error: HTTP {response.status_code} - {response.text}")
            # Return a structured error recommendation so frontend can display an explanation
            return [{
                "action": "ERROR",
                "symbol": None,
                "reasoning": "Gemini API authentication failed (401/403). Please configure Google Cloud service account credentials or enable the API and provide an API key.",
                "confidence": 0,
                "risk_level": "None"
            }]

        # Generic fallback recommendations if API fails
        return [
            {
                "action": "BUY",
                "symbol": "AAPL",
                "reasoning": "Strong fundamentals and growth potential",
                "confidence": 75,
                "risk_level": "Medium"
            },
            {
                "action": "BUY",
                "symbol": "GOOGL",
                "reasoning": "AI and cloud computing growth",
                "confidence": 70,
                "risk_level": "Medium"
            },
            {
                "action": "HOLD",
                "symbol": "MSFT",
                "reasoning": "Stable performance, good for long-term",
                "confidence": 80,
                "risk_level": "Low"
            }
        ]
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Return fallback recommendations
        return [
            {
                "action": "BUY",
                "symbol": "AAPL",
                "reasoning": "Strong fundamentals and growth potential",
                "confidence": 75,
                "risk_level": "Medium"
            }
        ]

@ai_bp.route("/market-analysis", methods=["GET"])
@jwt_required(optional=True)
def get_market_analysis():
    """Get general market analysis."""
    try:
        # This would integrate with real market data APIs
        # For now, return mock analysis
        
        analysis = {
            "market_trend": "Bullish",
            "sector_performance": {
                "Technology": "+2.5%",
                "Healthcare": "+1.8%",
                "Finance": "+1.2%",
                "Energy": "-0.5%"
            },
            "top_gainers": ["AAPL", "MSFT", "GOOGL"],
            "top_losers": ["TSLA", "META"],
            "market_sentiment": "Positive",
            "volatility_index": "Low",
            "last_updated": "2024-01-01T12:00:00Z"
        }
        
        return jsonify({
            "success": True,
            "analysis": analysis
        }), 200
        
    except Exception as e:
        print(f"Market analysis error: {e}")
        return jsonify({"error": "Failed to get market analysis"}), 500

@ai_bp.route("/portfolio-analysis", methods=["GET"])
@jwt_required(optional=True)
def get_portfolio_analysis():
    """Get AI analysis of user's portfolio."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        portfolio_summary = get_portfolio_summary(user)
        recent_trades = get_recent_trades(user, 20)
        
        # Calculate portfolio metrics
        total_value = portfolio_summary["total_value"]
        cash_percentage = (portfolio_summary["cash"] / total_value) * 100
        holdings_count = len(portfolio_summary["holdings"])
        
        # Analyze recent trading activity
        buy_trades = [t for t in recent_trades if t["trade_type"] == "BUY"]
        sell_trades = [t for t in recent_trades if t["trade_type"] == "SELL"]
        
        analysis = {
            "portfolio_metrics": {
                "total_value": total_value,
                "cash_percentage": round(cash_percentage, 2),
                "holdings_count": holdings_count,
                "diversification_score": min(holdings_count * 10, 100)
            },
            "trading_activity": {
                "total_trades": len(recent_trades),
                "buy_trades": len(buy_trades),
                "sell_trades": len(sell_trades),
                "activity_level": "High" if len(recent_trades) > 10 else "Moderate"
            },
            "recommendations": [
                "Consider diversifying your portfolio",
                "Monitor cash allocation",
                "Review recent trading patterns"
            ],
            "risk_assessment": {
                "overall_risk": "Medium",
                "concentration_risk": "Low" if holdings_count > 5 else "High",
                "liquidity_risk": "Low" if cash_percentage > 20 else "Medium"
            }
        }
        
        return jsonify({
            "success": True,
            "analysis": analysis
        }), 200
        
    except Exception as e:
        print(f"Portfolio analysis error: {e}")
        return jsonify({"error": "Failed to analyze portfolio"}), 500