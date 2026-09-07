"""
data_engine.py - Core data retrieval and metric calculation engine
"""

import pandas as pd
import numpy as np
import yfinance as yf

# Obsidian & Chrome Color Palette Constants
COLOR_CHROME_WHITE = "#ffffff"
COLOR_SILVER = "#cbd5e1"
COLOR_SLATE_MUTED = "#64748b"
COLOR_BG_VOID = "#07080a"
COLOR_BG_PANEL = "#0e1117"
COLOR_GRID = "rgba(203, 213, 225, 0.08)"

# Functional Accents (Strictly P&L)
COLOR_PROFIT = "#10b981"      # Emerald Neon
COLOR_LOSS = "#f43f5e"        # Crimson
COLOR_ACCENT_BLUE = "#38bdf8" # Ice Cyan
COLOR_AMBER = "#f59e0b"       # Warm Amber

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
    """Returns a unified Obsidian, Chrome & Silver Plotly styling dictionary."""
    return {
        "layout": {
            "paper_bgcolor": COLOR_BG_VOID,
            "plot_bgcolor": COLOR_BG_PANEL,
            "font": {
                "family": "Inter, -apple-system, sans-serif",
                "color": COLOR_SILVER,
                "size": 12
            },
            "title": {
                "font": {
                    "family": "Inter, sans-serif",
                    "color": COLOR_CHROME_WHITE,
                    "size": 15
                }
            },
            "xaxis": {
                "gridcolor": COLOR_GRID,
                "linecolor": "rgba(203, 213, 225, 0.15)",
                "tickcolor": "rgba(203, 213, 225, 0.15)",
                "tickfont": {"color": COLOR_SLATE_MUTED, "size": 10},
                "title": {"font": {"color": COLOR_SILVER}}
            },
            "yaxis": {
                "gridcolor": COLOR_GRID,
                "linecolor": "rgba(203, 213, 225, 0.15)",
                "tickcolor": "rgba(203, 213, 225, 0.15)",
                "tickfont": {"color": COLOR_SLATE_MUTED, "size": 10},
                "title": {"font": {"color": COLOR_SILVER}}
            },
            "legend": {
                "font": {"color": COLOR_SILVER, "size": 11},
                "bgcolor": "rgba(14, 17, 23, 0.7)",
                "bordercolor": "rgba(203, 213, 225, 0.12)",
                "borderwidth": 1
            }
        }
    }