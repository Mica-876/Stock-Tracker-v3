import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from data_engine import get_dividend_metrics

def get_security_profile(ticker):
    """Fetches and normalizes data for either an EQUITY or an ETF."""
    stk = yf.Ticker(ticker)
    info = stk.info or {}
    
    quote_type = info.get("quoteType", "EQUITY")
    is_etf = (quote_type == "ETF")
    
    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("navPrice", 0.0)
    div_rate, div_yield = get_dividend_metrics(info, current_price)

    # In ETFs, market cap is absent; use totalAssets (AUM) instead
    size_val = info.get("totalAssets") if is_etf else info.get("marketCap")
    size_label = "AUM / Total Assets" if is_etf else "Market Cap"
    
    # In ETFs, expense ratio is key; for equities, profit margin is key
    perf_metric_val = info.get("annualReportExpenseRatio") or info.get("expenseRatio") if is_etf else info.get("profitMargins")
    if is_etf and perf_metric_val is not None:
        perf_metric_str = f"{perf_metric_val * 100:.2f}% (Expense Ratio)" if perf_metric_val < 1 else f"{perf_metric_val:.2f}% (Expense Ratio)"
    elif not is_etf and perf_metric_val is not None:
        perf_metric_str = f"{perf_metric_val * 100:.2f}% (Profit Margin)"
    else:
        perf_metric_str = "N/A"

    profile = {
        "ticker": ticker,
        "name": info.get("longName") or info.get("shortName") or ticker,
        "type": "ETF" if is_etf else "Equity",
        "price": current_price,
        "currency": info.get("currency", "USD"),
        "size_label": size_label,
        "size_val": size_val,
        "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
        "beta": info.get("beta") or info.get("beta3Year"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "div_yield": div_yield,
        "special_metric": perf_metric_str,
        "category": info.get("category") if is_etf else info.get("sector", "N/A")
    }
    return stk, profile

def render_comparison_tab(ticker_list):
    st.markdown("### ⚖️ Head-to-Head Comparison: Stocks & ETFs")
    st.caption("Benchmark individual companies directly against index or sector ETFs.")

    # Allow custom ticker entry if desired ETF isn't in default list
    c_in1, c_in2, c_in3 = st.columns([2, 2, 1.5])
    with c_in1:
        ticker_a = st.text_input("Asset A (Stock or ETF):", value="NVDA").upper().strip()
    with c_in2:
        ticker_b = st.text_input("Asset B (Stock or ETF Benchmark):", value="QQQ").upper().strip()
    with c_in3:
        timeframe = st.selectbox("Comparison Horizon:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd"], index=3)

    if not ticker_a or not ticker_b:
        st.warning("Please provide two tickers to compare.")
        return

    if ticker_a == ticker_b:
        st.info("Select two different securities to run a comparative analysis.")
        return

    with st.spinner(f"Fetching comparative data for {ticker_a} and {ticker_b}..."):
        try:
            stk_a, data_a = get_security_profile(ticker_a)
            stk_b, data_b = get_security_profile(ticker_b)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return

    # --- TOP LEVEL SUMMARY CARDS ---
    card1, card2 = st.columns(2)
    for col, data in zip([card1, card2], [data_a, data_b]):
        with col:
            st.markdown(f"""
            <div class="company-card">
                <h3>{data['name']} ({data['ticker']})</h3>
                <span class="meta-tag">Type: {data['type']}</span>
                <span class="meta-tag">Class: {data['category']}</span>
                <h2 style="color: #10b981; margin: 10px 0 0 0;">${data['price']:.2f} <span style="font-size: 14px; color: #94a3b8;">{data['currency']}</span></h2>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- NORMALIZED RETURN OVERLAY CHART ---
    st.markdown("#### 📈 Normalized % Return Growth")
    st.caption(f"Tracks percentage performance over the chosen timeframe ({timeframe}). Baseline = 0.00%.")

    hist_a = stk_a.history(period=timeframe)
    hist_b = stk_b.history(period=timeframe)

    if not hist_a.empty and not hist_b.empty:
        # Align indices (inner join on dates to ensure matching timestamps)
        aligned_df = pd.DataFrame({
            data_a['ticker']: hist_a['Close'],
            data_b['ticker']: hist_b['Close']
        }).dropna()

        if not aligned_df.empty:
            # Baseline normalization: ((P_t - P_0) / P_0) * 100
            norm_a = ((aligned_df[data_a['ticker']] - aligned_df[data_a['ticker']].iloc[0]) / aligned_df[data_a['ticker']].iloc[0]) * 100
            norm_b = ((aligned_df[data_b['ticker']] - aligned_df[data_b['ticker']].iloc[0]) / aligned_df[data_b['ticker']].iloc[0]) * 100

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=aligned_df.index,
                y=norm_a,
                mode='lines',
                name=f"{data_a['ticker']} ({data_a['type']})",
                line=dict(color='#10b981', width=2.5)
            ))
            fig.add_trace(go.Scatter(
                x=aligned_df.index,
                y=norm_b,
                mode='lines',
                name=f"{data_b['ticker']} ({data_b['type']})",
                line=dict(color='#38bdf8', width=2.5)
            ))

            fig.update_layout(
                title=f"{data_a['ticker']} vs {data_b['ticker']} Relative Return (%)",
                yaxis_title="Total Return (%)",
                hovermode="x unified",
                template="plotly_dark",
                paper_bgcolor='#090d16',
                plot_bgcolor='#0f172a',
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, width="stretch")

            # Final period return readout
            ret_a = norm_a.iloc[-1]
            ret_b = norm_b.iloc[-1]
            delta = ret_a - ret_b

            r1, r2, r3 = st.columns(3)
            r1.metric(f"{data_a['ticker']} Total Return", f"{ret_a:+.2f}%")
            r2.metric(f"{data_b['ticker']} Total Return", f"{ret_b:+.2f}%")
            r3.metric("Spread / Outperformance", f"{delta:+.2f}%", help=f"Positive means {data_a['ticker']} beat {data_b['ticker']}.")
    else:
        st.warning("Insufficient historical overlap to construct a comparative performance chart.")

    st.markdown("---")

    # --- SIDE-BY-SIDE METRICS MATRIX ---
    st.markdown("#### 📊 Comparative Metric Matrix")

    def format_size(val):
        if not val or pd.isna(val):
            return "N/A"
        if val >= 1e12:
            return f"${val / 1e12:.2f}T"
        if val >= 1e9:
            return f"${val / 1e9:.2f}B"
        if val >= 1e6:
            return f"${val / 1e6:.2f}M"
        return f"${val:,.0f}"

    def format_val(val, suffix="", prefix=""):
        if val is None or pd.isna(val):
            return "N/A"
        return f"{prefix}{val:.2f}{suffix}"

    matrix_data = {
        "Indicator / Metric": [
            "Asset Classification",
            "Sector / Sub-Category",
            "Current Price",
            "Size (Market Cap or Fund AUM)",
            "Trailing / Forward P/E",
            "Dividend Yield (%)",
            "Beta (Volatility Benchmark)",
            "52-Week High",
            "52-Week Low",
            "Fee / Margin Structure"
        ],
        f"{data_a['ticker']} ({data_a['type']})": [
            data_a['type'],
            str(data_a['category']),
            f"${data_a['price']:.2f}",
            format_size(data_a['size_val']),
            format_val(data_a['pe_ratio']),
            format_val(data_a['div_yield'], suffix="%"),
            format_val(data_a['beta']),
            format_val(data_a['52w_high'], prefix="$"),
            format_val(data_a['52w_low'], prefix="$"),
            data_a['special_metric']
        ],
        f"{data_b['ticker']} ({data_b['type']})": [
            data_b['type'],
            str(data_b['category']),
            f"${data_b['price']:.2f}",
            format_size(data_b['size_val']),
            format_val(data_b['pe_ratio']),
            format_val(data_b['div_yield'], suffix="%"),
            format_val(data_b['beta']),
            format_val(data_b['52w_high'], prefix="$"),
            format_val(data_b['52w_low'], prefix="$"),
            data_b['special_metric']
        ]
    }

    st.dataframe(pd.DataFrame(matrix_data), width="stretch", hide_index=True)