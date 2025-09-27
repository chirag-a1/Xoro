import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- Configure the Gemini API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize the Generative Model
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error configuring Gemini AI: {e}")
    model = None

def get_ai_recommendations(portfolio: list[dict]) -> list[dict]:
    """
    Generates stock recommendations based on the user's current portfolio
    using the Gemini AI.

    Args:
        portfolio: A list of dictionaries, where each dictionary represents a stock
                   holding (e.g., {'symbol': 'RELIANCE.NS', 'quantity': 10, 'avg_price': 2800.00}).

    Returns:
        A list of recommendation dictionaries, each with 'symbol', 'reason',
        and 'confidence', or an empty list if an error occurs.
    """
    if not model:
        print("Gemini AI model is not initialized.")
        return []

    # Format the user's portfolio into a readable string for the prompt
    if not portfolio:
        portfolio_str = "The user currently has an empty portfolio and is looking for initial investments."
    else:
        portfolio_str = ", ".join([f"{item['quantity']} shares of {item['symbol']}" for item in portfolio])

    # --- Construct a detailed prompt for the AI ---
    # This prompt is engineered to guide the AI to provide relevant, well-formatted recommendations.
    prompt = f"""
    Act as an expert Indian stock market analyst. Your client's current portfolio consists of: {portfolio_str}.
    
    Based on this portfolio, perform the following tasks:
    1. Analyze the current holdings for sector concentration and potential risks.
    2. Suggest 3 to 5 stocks listed on the Indian National Stock Exchange (NSE) that would be a good addition to diversify or strengthen this portfolio.
    3. For each suggested stock, provide a brief, one-sentence justification for the recommendation (e.g., "Good for exposure to the banking sector," "Strong growth in the EV market," etc.).
    4. Assign a confidence level to each recommendation: "High", "Medium", or "Low".
    5. Do not recommend any stocks that are already in the user's portfolio.

    Return your response as a single, clean JSON array of objects. Do not include any text, explanations, or markdown formatting outside of the JSON. The JSON should follow this exact structure:
    [
        {{
            "symbol": "STOCKSYMBOL.NS",
            "reason": "Your one-sentence justification.",
            "confidence": "High"
        }},
        {{
            "symbol": "ANOTHERSYMBOL.NS",
            "reason": "Another justification.",
            "confidence": "Medium"
        }}
    ]
    """

    try:
        # --- Call the Gemini API ---
        response = model.generate_content(prompt)
        response_text = response.text

        # --- Clean and Parse the JSON Response ---
        # The AI might wrap the JSON in markdown backticks, so we need to remove them.
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse the cleaned string into a Python list
        recommendations = json.loads(response_text)
        
        # Basic validation to ensure the output is in the expected format
        if isinstance(recommendations, list) and all('symbol' in r and 'reason' in r and 'confidence' in r for r in recommendations):
             return recommendations
        else:
            print("Error: AI response was not in the expected format.")
            return []

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from AI response: {e}")
        print(f"Raw response was: {response_text}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while generating AI recommendations: {e}")
        return []
