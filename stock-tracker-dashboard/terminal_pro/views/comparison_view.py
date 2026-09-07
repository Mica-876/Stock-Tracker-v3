import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from data_engine import get_dividend_metrics

def get_security_profile(ticker):
    """Fetches robust data with fallbacks for both Equity and ETF securities."""
    stk = yf.Ticker(ticker)
    
    # 1. Fetch historical data first to ensure we have actual live prices
    hist_recent = stk.history(period="5d")
    latest_close = float(hist_recent['Close'].iloc[-1]) if not hist_recent.empty else 0.0

    # 2. Extract fast_info (much more reliable and unthrottled on cloud servers)
    fast = getattr(stk, "fast_info", {})
    
    # 3. Extract regular info safely
    try:
        info = stk.info or {}
    except Exception:
        info = {}

    # Identify whether asset is an ETF or Equity
    quote_type = str(info.get("quoteType", "") or getattr(fast, "quote_type", "")).upper()
    is_etf = (
        quote_type in ["ETF", "MUTUALFUND"]
        or "fundFamily" in info
        or "category" in info
        or info.get("legalType") == "Exchange Traded Fund"
    )

    # Determine Price with bulletproof fallback
    current_price = (
        getattr(fast, "last_price", None)
        or info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("navPrice")
        or latest_close
    )
    current_price = float(current_price) if current_price else 0.0

    # Determine Size (AUM for ETF, Market Cap for Equities)
    if is_etf:
        size_val = (
            info.get("totalAssets")
            or getattr(fast, "market_cap", None)
            or info.get("marketCap")
        )
        size_label = "Fund AUM / Assets"
    else:
        size_val = getattr(fast, "market_cap", None) or info.get("marketCap")
        size_label = "Market Cap"

    # 52-Week Range
    high_52 = getattr(fast, "year_high", None) or info.get("fiftyTwoWeekHigh")
    low_52 = getattr(fast, "year_low", None) or info.get("fiftyTwoWeekLow")

    # Valuation & Multiples
    pe_ratio = info.get("trailingPE") or info.get("forwardPE")
    beta = info.get("beta") or info.get("beta3Year")

    # Margin / Expense Structure
    if is_etf:
        expense_ratio = info.get("annualReportExpenseRatio") or info.get("expenseRatio")
        if expense_ratio is not None:
            special_metric = f"{expense_ratio * 100:.2f}% (Expense Ratio)" if expense_ratio < 1 else f"{expense_ratio:.2f}% (Expense Ratio)"
        else:
            special_metric = "N/A"
    else:
        profit_margin = info.get("profitMargins")
        if profit_margin is not None:
            special_metric = f"{profit_margin * 100:.2f}% (Profit Margin)"
        else:
            special_metric = "N/A"

    # Dividend calculation
    div_rate, div_yield = get_dividend_metrics(info, current_price)

    profile = {
        "ticker": ticker.upper(),
        "name": info.get("longName") or info.get("shortName") or ticker.upper(),
        "type": "ETF" if is_etf else "Equity",
        "price": current_price,
        "currency": info.get("currency", "USD") or "USD",
        "size_label": size_label,
        "size_val": float(size_val) if size_val else None,
        "pe_ratio": float(pe_ratio) if pe_ratio else None,
        "beta": float(beta) if beta else None,
        "52w_high": float(high_52) if high_52 else None,
        "52w_low": float(low_52) if low_52 else None,
        "div_yield": div_yield,
        "special_metric": special_metric,
        "category": info.get("category") if is_etf else info.get("sector", "N/A"),
        "industry": info.get("fundFamily") if is_etf else info.get("industry", "N/A")
    }

    return stk, profile


def render_comparison_tab(ticker_list):
    st.markdown("### ⚖️ Head-to-Head Comparison: Stocks & ETFs")
    st.caption("Benchmark corporate equities directly against major sector or index ETFs.")

    c_in1, c_in2, c_in3 = st.columns([2, 2, 1.5])
    with c_in1:
        ticker_a = st.text_input("Asset A (Stock or ETF):", value="NVDA").upper().strip()
    with c_in2:
        ticker_b = st.text_input("Asset B (Stock or ETF Benchmark):", value="QQQ").upper().strip()
    with c_in3:
        timeframe = st.selectbox("Comparison Horizon:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd"], index=3)

    if not ticker_a or not ticker_b:
        st.warning("Please specify two tickers to run the comparison.")
        return

    if ticker_a == ticker_b:
        st.info("Please choose two different tickers to compare.")
        return

    with st.spinner(f"Querying financial metrics for {ticker_a} and {ticker_b}..."):
        try:
            stk_a, data_a = get_security_profile(ticker_a)
            stk_b, data_b = get_security_profile(ticker_b)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return

    # --- TOP LEVEL SUMMARY CARDS ---
    card1, card2 = st.columns(2)
    for col, data, accent in zip([card1, card2], [data_a, data_b], ["#10b981", "#38bdf8"]):
        with col:
            st.markdown(f"""
            <div class="company-card" style="border-left: 4px solid {accent};">
                <h3 style="margin-bottom: 4px;">{data['name']} ({data['ticker']})</h3>
                <div style="margin-bottom: 8px;">
                    <span class="meta-tag">Type: {data['type']}</span>
                    <span class="meta-tag">Sector/Class: {data['category']}</span>
                    {f'<span class="meta-tag">{data["industry"]}</span>' if data["industry"] != "N/A" else ''}
                </div>
                <h2 style="color: {accent}; margin: 8px 0 0 0;">${data['price']:.2f} <span style="font-size: 14px; color: #94a3b8;">{data['currency']}</span></h2>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- NORMALIZED RETURN OVERLAY CHART ---
    st.markdown("#### 📈 Normalized % Return Growth")
    st.caption(f"Percentage return indexed from the start of the selected {timeframe} window (Baseline = 0.00%).")

    hist_a = stk_a.history(period=timeframe)
    hist_b = stk_b.history(period=timeframe)

    if not hist_a.empty and not hist_b.empty:
        # Align timestamps
        aligned_df = pd.DataFrame({
            data_a['ticker']: hist_a['Close'],
            data_b['ticker']: hist_b['Close']
        }).dropna()

        if not aligned_df.empty:
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
                title=f"{data_a['ticker']} vs {data_b['ticker']} Total Return (%)",
                yaxis_title="Return (%)",
                hovermode="x unified",
                template="plotly_dark",
                paper_bgcolor='#090d16',
                plot_bgcolor='#0f172a',
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, width="stretch")

            ret_a = norm_a.iloc[-1]
            ret_b = norm_b.iloc[-1]
            delta = ret_a - ret_b

            r1, r2, r3 = st.columns(3)
            r1.metric(f"{data_a['ticker']} Return", f"{ret_a:+.2f}%")
            r2.metric(f"{data_b['ticker']} Return", f"{ret_b:+.2f}%")
            r3.metric("Spread / Outperformance", f"{delta:+.2f}%", help=f"Positive indicates {data_a['ticker']} outperformed {data_b['ticker']}.")
    else:
        st.warning("Could not pull matching historical data for this timeframe.")

    st.markdown("---")

    # --- SIDE-BY-SIDE METRICS MATRIX ---
    st.markdown("#### 📊 Comparative Fundamentals & Multipliers")

    def format_size(val):
        if not val or pd.isna(val) or val == 0:
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

    matrix_rows = [
        ("Asset Classification", data_a['type'], data_b['type']),
        ("Sector / Sub-Category", str(data_a['category']), str(data_b['category'])),
        ("Current Price", f"${data_a['price']:.2f}", f"${data_b['price']:.2f}"),
        ("Size (Market Cap / Fund AUM)", format_size(data_a['size_val']), format_size(data_b['size_val'])),
        ("P/E Ratio (Trailing/Fwd)", format_val(data_a['pe_ratio']), format_val(data_b['pe_ratio'])),
        ("Dividend Yield (%)", format_val(data_a['div_yield'], suffix="%"), format_val(data_b['div_yield'], suffix="%")),
        ("Beta (Market Sensitivity)", format_val(data_a['beta']), format_val(data_b['beta'])),
        ("52-Week High", format_val(data_a['52w_high'], prefix="$"), format_val(data_b['52w_high'], prefix="$")),
        ("52-Week Low", format_val(data_a['52w_low'], prefix="$"), format_val(data_b['52w_low'], prefix="$")),
        ("Fee / Operating Structure", data_a['special_metric'], data_b['special_metric'])
    ]

    df_matrix = pd.DataFrame(
        matrix_rows,
        columns=["Metric / Indicator", f"{data_a['ticker']} ({data_a['type']})", f"{data_b['ticker']} ({data_b['type']})"]
    )

    st.dataframe(df_matrix, width="stretch", hide_index=True)