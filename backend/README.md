# Backend (Flask Trading API)

This folder contains the Flask backend for the Xoro Premium Trading App.

## Features
- User authentication (JWT)
- Portfolio management
- Trading operations (buy/sell)
- AI recommendations
- SQLite database
- CORS configuration

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the backend server:
   ```bash
   python app.py
   ```
   or
   ```bash
   python run.py
   ```

## API Endpoints
See the main project README for a full list of endpoints and usage examples.

## Notes
- Ensure the backend is running before starting the frontend.
- Database file is auto-created in `instance/trading.db`.
