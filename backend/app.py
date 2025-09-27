# backend/app.py

import os
import sys
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# SocketIO is an optional runtime dependency; import lazily inside create_app

# Load environment variables
load_dotenv()

# Import extensions from models to avoid circular imports
from models import db, bcrypt

# Initialize other extensions
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
# Will be set to a SocketIO instance inside create_app if available
socketio = None

def create_app(config_class='config.Config'):
    """
    Application Factory: creates and configures the Flask app instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS
    # For local development allow all origins to avoid file:// and port mismatches.
    # In production this should be restricted to trusted domains only.
    if app.config.get('DEBUG'):
        cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)
    else:
        cors.init_app(
            app,
            resources={
                r"/api/*": {
                    "origins": [
                        "http://localhost:3000",
                        "http://127.0.0.1:3000",
                        "http://localhost:8080",
                        "http://127.0.0.1:8080",
                    ],
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"],
                    "supports_credentials": False,
                }
            },
        )
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.portfolio import portfolio_bp
    from routes.trading import trading_bp
    from routes.ai_recommendations import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
    app.register_blueprint(trading_bp, url_prefix="/api/trading")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    
    # Initialize SocketIO for real-time features (lazy import)
    try:
        from flask_socketio import SocketIO as _SocketIO
        global socketio
        socketio = _SocketIO()
        socketio.init_app(app, cors_allowed_origins='*')
    except Exception:
        # SocketIO not available or failed to init; continue without realtime
        socketio = None

    # Start price simulator background emitter (if available)
    try:
        from utils.price_simulator import PriceSimulator
        simulator = PriceSimulator(socketio)
        simulator.start()
    except Exception as e:
        print(f"Price simulator not started: {e}")
    
    # Create database tables
    with app.app_context():
        from models import User, Portfolio, Stock, Trade
        db.create_all()
        
        # Print registered routes for debugging
        print("\n=== REGISTERED ROUTES ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.methods} {rule.rule}")
        print("========================\n")
    
    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"}), 200
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized"}), 401
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    print("Starting Flask development server...")
    print("Backend running on: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/")
    # Use socketio.run so websocket server runs too (falls back to Flask run if socketio not initialized)
    try:
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    except Exception:
        app.run(host="0.0.0.0", port=5000, debug=True)