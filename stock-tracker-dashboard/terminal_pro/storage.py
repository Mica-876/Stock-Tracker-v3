import json
import os
import datetime
import streamlit as st

DATA_FILE = "saved_platform_data.json"

def load_storage():
    default_data = {
        "watchlist": ["CMS", "DTE", "FE", "AEP", "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL"],
        "portfolios": {
            "Default User": [
                {"ticker": "NVDA", "shares": 10, "buy_price": 120.00},
                {"ticker": "AAPL", "shares": 15, "buy_price": 175.50}
            ]
        }
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def save_storage(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def init_session_state():
    platform_data = load_storage()
    if "ticker_list" not in st.session_state:
        st.session_state.ticker_list = platform_data.get("watchlist", [])

    if "portfolios" not in st.session_state:
        st.session_state.portfolios = platform_data.get("portfolios", {})

    if "last_updated" not in st.session_state:
        st.session_state.last_updated = datetime.datetime.now().strftime("%H:%M:%S")

def sync_to_file():
    save_storage({
        "watchlist": st.session_state.ticker_list,
        "portfolios": st.session_state.portfolios
    })