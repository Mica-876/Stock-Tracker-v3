"""
data_engine.py - Core data retrieval, calculations, and chart templates
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# Reverted Green / Dark Theme Palette
COLOR_TEXT_LIGHT = "#f1f5f9"
COLOR_MUTED = "#94a3b8"
COLOR_BG_VOID = "#090d16"
COLOR_BG_PANEL = "#0f172a"
COLOR_GRID = "#1e293b"

COLOR_PROFIT = "#10b981"      # Emerald Green
COLOR_LOSS = "#ef4444"        # Coral Red
COLOR_ACCENT_BLUE = "#38bdf8" # Cyan
COLOR_AMBER = "#f59e0b"       # Amber

def get_dividend_metrics(info, current_price):
    """Calculates dividend payout and yield with fallbacks across equity and ETF schemas."""
    div_rate = info.get("dividendRate") or info.get("trailingAnnualDividendRate") or 0.0
    div_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield") or 0.0

    if div_yield and div_yield > 0:
        if div_yield < 0.25:
            div_yield = div_yield * 100.0
    elif div_rate and current_price and current_price > 0:
        div_yield = (div_rate / current_price) * 100.0

    if div_rate == 0.0 and div_yield > 0 and current_price > 0:
        div_rate = (div_yield / 100.0) * current_price

    return float(div_rate), float(div_yield)

def get_plotly_theme():
    """Returns the dark green-accent Plotly template."""
    return {
        "layout": {
            "paper_bgcolor": COLOR_BG_VOID,
            "plot_bgcolor": COLOR_BG_PANEL,
            "font": {
                "family": "Inter, sans-serif",
                "color": COLOR_TEXT_LIGHT,
                "size": 12
            },
            "title": {
                "font": {
                    "family": "Inter, sans-serif",
                    "color": COLOR_TEXT_LIGHT,
                    "size": 15
                }
            },
            "xaxis": {
                "gridcolor": COLOR_GRID,
                "linecolor": COLOR_GRID,
                "tickcolor": COLOR_GRID,
                "tickfont": {"color": COLOR_MUTED, "size": 10},
                "title": {"font": {"color": COLOR_MUTED}}
            },
            "yaxis": {
                "gridcolor": COLOR_GRID,
                "linecolor": COLOR_GRID,
                "tickcolor": COLOR_GRID,
                "tickfont": {"color": COLOR_MUTED, "size": 10},
                "title": {"font": {"color": COLOR_MUTED}}
            },
            "legend": {
                "font": {"color": COLOR_TEXT_LIGHT, "size": 11},
                "bgcolor": "rgba(15, 23, 42, 0.8)",
                "bordercolor": "#1e293b",
                "borderwidth": 1
            }
        }
    }

@st.cache_data(ttl=300, show_spinner=False)
def fetch_single_ticker_data(ticker):
    """Fetches metrics for a single symbol with robust fallback logic."""
    sym = ticker.upper().strip()
    stk = yf.Ticker(sym)

    hist_5d = stk.history(period="5d")
    latest_close = float(hist_5d['Close'].iloc[-1]) if not hist_5d.empty else 0.0

    fast_dict = {}
    try:
        fast = getattr(stk, "fast_info", None)
        if fast is not None:
            for k in ["last_price", "market_cap", "year_high", "year_low", "currency", "quote_type"]:
                try:
                    fast_dict[k] = getattr(fast, k, None)
                except Exception:
                    pass
    except Exception:
        pass

    try:
        info = stk.info or {}
    except Exception:
        info = {}

    quote_type = str(info.get("quoteType") or fast_dict.get("quote_type") or "").upper()
    is_etf = (quote_type in ["ETF", "MUTUALFUND"] or "fundFamily" in info or "category" in info)

    current_p = fast_dict.get("last_price") or info.get("currentPrice") or info.get("regularMarketPrice") or latest_close
    current_p = float(current_p) if current_p else 0.0

    mkt_cap = info.get("totalAssets") if is_etf else (fast_dict.get("market_cap") or info.get("marketCap"))
    mkt_cap_b = (float(mkt_cap) / 1e9) if mkt_cap else 0.0

    pe_ratio = info.get("trailingPE") or info.get("forwardPE") or 0.0
    peg_ratio = info.get("pegRatio") or 0.0
    pb_ratio = info.get("priceToBook") or 0.0
    fcf = info.get("freeCashflow")
    fcf_b = (float(fcf) / 1e9) if fcf else 0.0

    div_rate, div_yield = get_dividend_metrics(info, current_p)
    beta = info.get("beta") or info.get("beta3Year") or 1.0

    raw_sector = info.get("category") if is_etf else info.get("sector")
    if not raw_sector or str(raw_sector).lower() in ["none", "n/a", ""]:
        if sym in ["NVDA", "AAPL", "MSFT", "AMD", "NVTS", "APLD", "TSM"]:
            sector = "Technology"
        elif sym in ["CMS", "DTE", "FE", "AEP"]:
            sector = "Utilities"
        elif sym in ["AMZN", "TSLA"]:
            sector = "Consumer Cyclical"
        elif sym in ["GOOGL", "META"]:
            sector = "Communication Services"
        elif is_etf:
            sector = "Index ETF"
        else:
            sector = "Equities"
    else:
        sector = str(raw_sector)

    company_name = info.get("longName") or info.get("shortName") or sym

    return {
        "Ticker": sym,
        "Company Name": company_name,
        "Price ($)": round(current_p, 2),
        "Market Cap ($B)": round(mkt_cap_b, 2),
        "P/E Ratio": round(float(pe_ratio), 2) if pe_ratio else "N/A",
        "PEG Ratio": round(float(peg_ratio), 2) if peg_ratio else "N/A",
        "P/B Ratio": round(float(pb_ratio), 2) if pb_ratio else "N/A",
        "Free Cash Flow ($B)": round(fcf_b, 2) if fcf_b else "N/A",
        "Div Yield (%)": round(float(div_yield), 2),
        "Beta (5Y)": round(float(beta), 2),
        "Sector": sector
    }

def fetch_platform_data(ticker_list):
    """Fetches and aggregates fundamental metrics for the entire active watchlist."""
    if not ticker_list:
        return pd.DataFrame()

    results = []
    for ticker in ticker_list:
        try:
            data = fetch_single_ticker_data(ticker)
            results.append(data)
        except Exception:
            results.append({
                "Ticker": ticker.upper(),
                "Company Name": ticker.upper(),
                "Price ($)": 0.0,
                "Market Cap ($B)": 0.0,
                "P/E Ratio": "N/A",
                "PEG Ratio": "N/A",
                "P/B Ratio": "N/A",
                "Free Cash Flow ($B)": "N/A",
                "Div Yield (%)": 0.0,
                "Beta (5Y)": 1.0,
                "Sector": "Other"
            })

    return pd.DataFrame(results)