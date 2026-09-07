import streamlit as st
import datetime

from styles import apply_custom_css
from storage import init_session_state, sync_to_file
from data_engine import fetch_platform_data

# Import UI tab views
from views.watchlist_view import render_watchlist_tab
from views.portfolio_view import render_portfolio_tab
from views.deep_dive_view import render_deep_dive_tab
from views.comparison_view import render_comparison_tab
from views.sector_view import render_sector_tab

# 1. Page Configuration
st.set_page_config(
    page_title="Terminal Pro - Green & Black Edition",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styles & Session State
apply_custom_css()
init_session_state()

# 3. Header Banner
st.markdown(f"""
<div class="app-header">
    <div>
        <h1>🟢 EQUITY RESEARCH TERMINAL</h1>
        <p>Live Portfolio Tracking & Financial Deep Dive Engine</p>
    </div>
    <div class="sync-status">
        <span class="heartbeat-pulse">🟢</span>
        <span>FETCH ENGINE ACTIVE — Last Updated: {st.session_state.last_updated}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. Watchlist Sidebar Controls
st.sidebar.markdown("## ⚙️ Watchlist Control Center")
tracked_count = len(st.session_state.ticker_list)
st.sidebar.markdown(f"""
<div class="sidebar-widget">
    <div class="sidebar-widget-title">📌 Watchlist Health</div>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size:13px; color:#94a3b8;">Active Tickers:</span>
        <span style="font-size:16px; font-weight:700; color:#34d399;">{tracked_count} Stocks</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-widget-title">➕ Add Tickers</div>', unsafe_allow_html=True)
add_mode = st.sidebar.radio("Add Method:", ["Single Symbol", "Bulk Import (CSV/List)"], horizontal=True, label_visibility="collapsed")

if add_mode == "Single Symbol":
    with st.sidebar.form("add_single_form", clear_on_submit=True):
        new_ticker = st.text_input("Enter Ticker (e.g. TSLA):", placeholder="TSLA").strip().upper()
        if st.form_submit_button(" Add Symbol") and new_ticker:
            if new_ticker not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_ticker)
                sync_to_file()
                st.session_state.last_updated = datetime.datetime.now().strftime("%H:%M:%S")
                st.sidebar.success(f"Added {new_ticker}!")
                st.rerun()
            else:
                st.sidebar.warning(f"{new_ticker} already in list.")
else:
    with st.sidebar.form("add_bulk_form", clear_on_submit=True):
        bulk_input = st.text_area("Comma-separated tickers:", placeholder="TSLA, AMD, META, NFLX")
        if st.form_submit_button(" Bulk Add") and bulk_input:
            added_symbols = []
            for sym in bulk_input.split(","):
                clean_sym = sym.strip().upper()
                if clean_sym and clean_sym not in st.session_state.ticker_list:
                    st.session_state.ticker_list.append(clean_sym)
                    added_symbols.append(clean_sym)
            if added_symbols:
                sync_to_file()
                st.session_state.last_updated = datetime.datetime.now().strftime("%H:%M:%S")
                st.sidebar.success(f"Added: {', '.join(added_symbols)}")
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("<div class=\"sidebar-widget-title\">⚡ Quick Presets</div>", unsafe_allow_html=True)
col_pre1, col_pre2 = st.sidebar.columns(2)

if col_pre1.button("💻 MegaTech"):
    tech_bundle = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA"]
    st.session_state.ticker_list = sorted(list(set(st.session_state.ticker_list + tech_bundle)))
    sync_to_file()
    st.rerun()

if col_pre2.button("⚡ Utilities"):
    util_bundle = ["CMS", "DTE", "FE", "AEP", "NEE", "SO"]
    st.session_state.ticker_list = sorted(list(set(st.session_state.ticker_list + util_bundle)))
    sync_to_file()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("<div class=\"sidebar-widget-title\">🗑️ Active Stock List</div>", unsafe_allow_html=True)

if st.session_state.ticker_list:
    ticker_to_remove = None
    for sym in list(st.session_state.ticker_list):
        c1, c2 = st.sidebar.columns([4, 1])
        c1.markdown(f"**`{sym}`**")
        if c2.button("❌", key=f"del_{sym}", help=f"Remove {sym}"):
            ticker_to_remove = sym

    if ticker_to_remove:
        st.session_state.ticker_list.remove(ticker_to_remove)
        sync_to_file()
        st.session_state.last_updated = datetime.datetime.now().strftime("%H:%M:%S")
        st.rerun()

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("🧹 Clear Entire Watchlist"):
        st.session_state.ticker_list = []
        sync_to_file()
        st.rerun()
else:
    st.sidebar.info("Watchlist is currently empty. Add symbols above!")

# 5. Tab Routing
tab_overview, tab_portfolio, tab_single_stock, tab_comparison, tab_sectors = st.tabs([
    "📊 Watchlist Overview", 
    "💼 Portfolio Tracker",
    "🔍 Financial Deep Dive", 
    "⚔️ Stock Comparison",
    "🍰 Sector Breakdown"
])

if st.session_state.ticker_list:
    df_metrics = fetch_platform_data(st.session_state.ticker_list)

    with tab_overview:
        render_watchlist_tab(df_metrics)

    with tab_portfolio:
        render_portfolio_tab()

    with tab_single_stock:
        render_deep_dive_tab(st.session_state.ticker_list)

    with tab_comparison:
        render_comparison_tab(st.session_state.ticker_list)

    with tab_sectors:
        render_sector_tab(df_metrics)
else:
    st.info("👋 Welcome! Your watchlist is currently empty. Use the Watchlist Control Center on the left sidebar to add symbols or pick a preset bundle!")