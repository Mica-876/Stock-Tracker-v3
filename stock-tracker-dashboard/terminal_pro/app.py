import streamlit as st
import datetime
import pandas as pd

from styles import apply_custom_css
from storage import load_user_data, save_user_data, load_portfolio_data, save_portfolio_data
from data_engine import fetch_platform_data

# Modular View Imports
from views.watchlist_view import render_watchlist_tab
from views.portfolio_view import render_portfolio_tab
from views.deep_dive_view import render_deep_dive_tab
from views.comparison_view import render_comparison_tab
from views.sector_view import render_sector_tab

st.set_page_config(
    page_title="Terminal Pro - Equity Research",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS Styling
apply_custom_css()

# Session State Initialization
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = load_user_data()

if "portfolio_data" not in st.session_state:
    st.session_state["portfolio_data"] = load_portfolio_data()

# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
    st.markdown("### ⚙️ Watchlist Control Center")
    
    # Watchlist Health & Counters
    st.markdown(f"""
    <div style="background-color: #111827; border: 1px solid #1f293d; border-radius: 8px; padding: 12px; margin-bottom: 16px;">
        <span style="font-size: 11px; color: #ef4444; font-weight: 700; text-transform: uppercase;">📌 Watchlist Health</span>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
            <span style="font-size: 12px; color: #94a3b8;">Active Tickers:</span>
            <span style="font-size: 15px; color: #34d399; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{len(st.session_state['watchlist'])} Stocks</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ➕ Add Tickers")
    input_mode = st.radio("Input Mode:", ["Single Symbol", "Bulk Import (CSV/List)"], label_visibility="collapsed")

    if input_mode == "Single Symbol":
        new_symbol = st.text_input("Enter Ticker (e.g. TSLA, QQQ):", key="single_tick_in").upper().strip()
        if st.button("Add Symbol"):
            if new_symbol and new_symbol not in st.session_state["watchlist"]:
                st.session_state["watchlist"].append(new_symbol)
                save_user_data(st.session_state["watchlist"])
                st.rerun()
            elif new_symbol in st.session_state["watchlist"]:
                st.warning(f"{new_symbol} is already in the watchlist.")
    else:
        bulk_symbols = st.text_area("Paste Tickers (comma/space separated):", placeholder="AAPL, MSFT, NVDA, SPY")
        if st.button("Import Symbols"):
            if bulk_symbols:
                parsed = [s.strip().upper() for s in bulk_symbols.replace(",", " ").split() if s.strip()]
                added = 0
                for sym in parsed:
                    if sym not in st.session_state["watchlist"]:
                        st.session_state["watchlist"].append(sym)
                        added += 1
                if added > 0:
                    save_user_data(st.session_state["watchlist"])
                    st.success(f"Added {added} new symbols.")
                    st.rerun()

    st.markdown("#### ⚡ Quick Presets")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        if st.button("⚡ MegaTech"):
            st.session_state["watchlist"] = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA"]
            save_user_data(st.session_state["watchlist"])
            st.rerun()
    with c_p2:
        if st.button("⚡ Utilities"):
            st.session_state["watchlist"] = ["CMS", "DTE", "FE", "AEP", "SO", "NEE", "DUK"]
            save_user_data(st.session_state["watchlist"])
            st.rerun()

    st.markdown("---")
    st.markdown("#### 📋 Active Stock List")
    for tick in list(st.session_state["watchlist"]):
        c_name, c_del = st.columns([3, 1])
        with c_name:
            st.write(f"**{tick}**")
        with c_del:
            if st.button("❌", key=f"del_side_{tick}"):
                st.session_state["watchlist"].remove(tick)
                save_user_data(st.session_state["watchlist"])
                st.rerun()

# --- TOP EMERALD HERO BANNER WITH ANIMATED HEARTBEAT ---
now_str = datetime.datetime.now().strftime("%H:%M:%S")

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-left">
        <div class="hero-title-row">
            <div class="big-pulse-circle"></div>
            <h1 class="hero-title">EQUITY RESEARCH TERMINAL</h1>
        </div>
        <p class="hero-subtitle">Live Portfolio Tracking & Financial Deep Dive Engine</p>
    </div>
    <div>
        <div class="engine-status-pill">
            <div class="engine-pulse-dot"></div>
            <span>FETCH ENGINE ACTIVE — Last Updated: {now_str}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Primary Watchlist Data Fetch
watchlist = st.session_state["watchlist"]
df_metrics = fetch_platform_data(watchlist)

# --- MAIN WORKSPACE TABS ---
tab_watch, tab_port, tab_dive, tab_comp, tab_sec = st.tabs([
    "📊 Watchlist Overview",
    "💼 Portfolio Tracker",
    "🔍 Financial Deep Dive",
    "⚔️ Stock Comparison",
    "🍰 Sector Breakdown"
])

with tab_watch:
    render_watchlist_tab(df_metrics)

with tab_port:
    render_portfolio_tab(st.session_state["portfolio_data"], watchlist)

with tab_dive:
    render_deep_dive_tab(watchlist)

with tab_comp:
    render_comparison_tab(watchlist)

with tab_sec:
    render_sector_tab(df_metrics)