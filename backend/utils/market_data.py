# backend/utils/market_data.py

import os
import requests
import time
from dotenv import load_dotenv

# --- REAL API IMPLEMENTATION ---
# This version uses the Alpha Vantage API to fetch live stock market data.
# Make sure your ALPHA_VANTAGE_API_KEY is set in the .env file.

load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment variables. Please set it in your .env file.")

def get_live_price(symbol: str) -> float | None:
    """
    Fetches the live price for a single stock symbol from Alpha Vantage.
    
    Args:
        symbol: The stock symbol (e.g., "RELIANCE.NS").
    
    Returns:
        The live price as a float, or None if an error occurs.
    """
    url = (
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE"
        f"&symbol={symbol}"
        f"&apikey={ALPHA_VANTAGE_API_KEY}"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad HTTP status codes
        data = response.json()

        # Alpha Vantage returns a 'Note' when the API call limit is reached
        if "Note" in data:
            print(f"Alpha Vantage API rate limit reached for {symbol}. Please wait.")
            return None

        quote = data.get('Global Quote')
        
        # Check if the quote is valid and contains the price
        if quote and '05. price' in quote:
            return float(quote['05. price'])
        else:
            print(f"Warning: Price data not found in API response for {symbol}. Response: {data}")
            return None
            
    except requests.RequestException as e:
        print(f"Error fetching data for {symbol} from Alpha Vantage: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing price data for {symbol}: {e}")
        return None


def get_batch_live_prices(symbols: list[str]) -> dict:
    """
    Fetches live prices for a list of stock symbols.
    
    To respect the Alpha Vantage free tier limit (e.g., 5 calls per minute),
    this function fetches prices sequentially with a delay between calls.
    """
    prices = {}
    for symbol in symbols:
        price = get_live_price(symbol)
        if price is not None:
            prices[symbol.upper()] = price
        # Add a delay to avoid hitting the API rate limit.
        # 12 seconds per call allows 5 calls per minute.
        time.sleep(12) 
        
    return prices

