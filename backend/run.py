# backend/run.py

#!/usr/bin/env python3
"""
Startup script for the Flask trading application.
This script handles environment setup and starts the server.
"""

import os
import sys
from app import create_app

def setup_environment():
    """Set up environment variables if .env file doesn't exist."""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    project_dir = os.path.dirname(__file__)
    instance_dir = os.path.join(project_dir, 'instance')

    # Ensure instance directory exists (SQLite will need it)
    try:
        os.makedirs(instance_dir, exist_ok=True)
    except OSError:
        pass

    if not os.path.exists(env_file):
        print("Creating .env file with default values...")
        # Use absolute path for the SQLite DB to avoid `unable to open database file`
        abs_db_path = os.path.abspath(os.path.join(instance_dir, 'trading.db'))
        env_content = f"""# Flask Configuration
SECRET_KEY=d58e564d5c8e548a43b0c3b1
JWT_SECRET_KEY=ba4df79afaf868f8034f476c1d42fd59

# Database
DATABASE_URL=sqlite:///{abs_db_path}

# External APIs
API_KEY_MARKET_DATA=7QDA56EPZI4CSZIB
GEMINI_API_KEY=AIzaSyA_9fVifQFEXc1txgS37qtYlhAIsuLpjzE

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("\u2705 .env file created successfully!")

def main():
    """Main function to start the application."""
    print("🚀 Starting Flask Trading Application...")
    
    # Setup environment
    setup_environment()
    
    # Create app
    app = create_app()
    
    # Print startup information
    print("\n" + "="*50)
    print("📊 TRADING APPLICATION STARTED")
    print("="*50)
    print(f"🌐 Backend URL: http://localhost:5000")
    print(f"🔗 API Base URL: http://localhost:5000/api")
    print(f"❤️  Health Check: http://localhost:5000/api/health")
    print("="*50)
    print("\n📋 Available API Endpoints:")
    print("   Authentication:")
    print("     POST /api/auth/register")
    print("     POST /api/auth/login")
    print("     GET  /api/auth/me")
    print("   Portfolio:")
    print("     GET  /api/portfolio")
    print("     GET  /api/portfolio/balance")
    print("     GET  /api/portfolio/holdings")
    print("   Trading:")
    print("     POST /api/trading/buy")
    print("     POST /api/trading/sell")
    print("     GET  /api/trading/orders")
    print("   AI Recommendations:")
    print("     POST /api/ai/recommendations")
    print("     GET  /api/ai/market-analysis")
    print("="*50)
    print("\n🎯 Frontend should connect to: http://localhost:3000")
    print("🔧 CORS configured for localhost:3000 and file:// protocol")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    # Start the server
    try:
        # If SocketIO is present (initialized in app module), prefer socketio.run to enable websockets
        try:
            from app import socketio
            socketio.run(app, host="0.0.0.0", port=5000, debug=True)
        except Exception:
            app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
