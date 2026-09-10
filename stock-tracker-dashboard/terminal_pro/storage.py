"""
storage.py - Persistent JSON Storage for Watchlist and Portfolio Profiles
"""

import json
import os

WATCHLIST_FILE = "watchlist.json"
PORTFOLIO_FILE = "portfolio.json"

DEFAULT_WATCHLIST = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA",
    "CMS", "DTE", "FE", "AEP", "AMD"
]

DEFAULT_PORTFOLIO = {
    "profiles": {
        "Default Portfolio": {
            "cash": 10000.0,
            "positions": {}
        }
    }
}

# --- WATCHLIST STORAGE ---
def load_user_data():
    """Loads the user's active stock watchlist."""
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass
    return list(DEFAULT_WATCHLIST)

def save_user_data(ticker_list):
    """Saves the user's stock watchlist to disk."""
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(ticker_list, f, indent=4)
    except Exception as e:
        print(f"Error saving watchlist: {e}")

# Aliases for backwards compatibility
load_data = load_user_data
save_data = save_user_data


# --- PORTFOLIO STORAGE ---
def load_portfolio_data():
    """Loads multi-profile portfolio holdings and cash balances."""
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "profiles" in data:
                    return data
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_PORTFOLIO))

def save_portfolio_data(portfolio_dict):
    """Saves multi-profile portfolio holdings and cash balances."""
    try:
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(portfolio_dict, f, indent=4)
    except Exception as e:
        print(f"Error saving portfolio data: {e}")