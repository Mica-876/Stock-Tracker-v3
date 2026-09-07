import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from data_engine import get_dividend_metrics

@st.cache_data(ttl=300, show_spinner=False)
def fetch_security_bundle(ticker):
    """Fetches fast_info, 1-year history, financials, and info with resilience."""
    stk = yf.Ticker(ticker)
    
    # 1. Price history (for returns, volatility, and calculated beta)
    try:
        hist_1y = stk.history(period="1y")
    except Exception:
        hist_1y = pd.DataFrame()

    # 2. Fast info attributes
    fast_dict = {}
    try:
        fast = getattr(stk, "fast_info", None)
        if fast is not None:
            for attr in ["last_price", "market_cap", "year_high", "year_low", "currency", "quote_type"]:
                try:
                    fast_dict[attr] = getattr(fast, attr, None)
                except Exception:
                    pass
    except Exception:
        pass

    # 3. Regular info dictionary
    try:
        info = stk.info or {}
    except Exception:
        info = {}

    # 4. Financial statements for backup valuation metrics
    try:
        fin_df = stk.financials
    except Exception:
        fin_df = pd.DataFrame()

    return info, fast_dict, hist_1y, fin_df

@st.cache_data(ttl=600, show_spinner=False)
def get_spy_returns():
    """Fetches benchmark S&P 500 returns for beta calculation."""
    try:
        spy = yf.Ticker("SPY").history(period="1y")
        if not spy.empty:
            return spy['Close'].pct_change().dropna()
    except Exception:
        pass
    return pd.Series(dtype=float)

def calculate_beta(stock_hist, spy_returns):
    """Calculates 1-year statistical Beta vs S&P 500 as an info fallback."""
    if stock_hist.empty or spy_returns.empty:
        return None
    try:
        stock_returns = stock_hist['Close'].pct_change().dropna()
        combined = pd.DataFrame({"stock": stock_returns, "spy": spy_returns}).dropna()
        if len(combined) > 30:
            cov = np.cov(combined["stock"], combined["spy"])[0][1]
            var = np.var(combined["spy"])
            if var > 0:
                return float(cov / var)
    except Exception:
        pass
    return None

def get_security_profile(ticker):
    """Processes cached data with algorithmic fallbacks for missing fundamental metrics."""
    ticker_clean = ticker.upper().strip()
    stk = yf.Ticker(ticker_clean)
    info, fast_dict, hist_1y, fin_df = fetch_security_bundle(ticker_clean)
    spy_ret = get_spy_returns()

    latest_close = float(hist_1y['Close'].iloc[-1]) if not hist_1y.empty else 0.0

    # Determine asset type
    quote_type = str(info.get("quoteType") or fast_dict.get("quote_type") or "").upper()
    is_etf = (
        quote_type in ["ETF", "MUTUALFUND"]
        or "fundFamily" in info
        or "category" in info
        or info.get("legalType") == "Exchange Traded Fund"
    )

    # Current Price
    current_price = (
        fast_dict.get("last_price")
        or info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("navPrice")
        or latest_close
    )
    current_price = float(current_price) if current_price else 0.0

    # Size (Market Cap for Stocks, AUM for ETFs)
    if is_etf:
        size_val = (
            info.get("totalAssets")
            or fast_dict.get("market_cap")
            or info.get("marketCap")
        )
        size_label = "Fund AUM"
    else:
        size_val = fast_dict.get("market_cap") or info.get("marketCap")
        size_label = "Market Cap"

    # 52-Week Range
    high_52 = fast_dict.get("year_high") or info.get("fiftyTwoWeekHigh")
    if high_52 is None and not hist_1y.empty:
        high_52 = float(hist_1y['High'].max())

    low_52 = fast_dict.get("year_low") or info.get("fiftyTwoWeekLow")
    if low_52 is None and not hist_1y.empty:
        low_52 = float(hist_1y['Low'].min())

    # Valuation Multiples (P/E Ratio Fallback)
    pe_ratio = info.get("trailingPE") or info.get("forwardPE")
    if pe_ratio is None and not is_etf and current_price > 0:
        # Fallback EPS extraction from financial statements
        eps_val = info.get("trailingEps")
        if eps_val is None and fin_df is not None and not fin_df.empty:
            for item in ["Diluted EPS", "Basic EPS"]:
                if item in fin_df.index:
                    try:
                        eps_val = float(fin_df.loc[item].iloc[0])
                        break
                    except Exception:
                        pass
        if eps_val and eps_val > 0:
            pe_ratio = current_price / eps_val

    # Beta (Direct info -> Statistical Covariance against SPY fallback)
    beta = info.get("beta") or info.get("beta3Year")
    if beta is None:
        beta = calculate_beta(hist_1y, spy_ret)

    # Operating Structure / Expense Ratio / Profit Margin
    if is_etf:
        expense_ratio = info.get("annualReportExpenseRatio") or info.get("expenseRatio")
        if expense_ratio is not None:
            special_metric = f"{expense_ratio * 100:.2f}% (Exp. Ratio)" if expense_ratio < 1 else f"{expense_ratio:.2f}% (Exp. Ratio)"
        else:
            special_metric = "Index Replicated (ETF)"
    else:
        profit_margin = info.get("profitMargins")
        if profit_margin is None and fin_df is not None and not fin_df.empty:
            # Mathematical fallback: Net Income / Total Revenue
            try:
                net_inc = None
                rev = None
                for k in ["Net Income", "Net Income Common Stockholders"]:
                    if k in fin_df.index:
                        net_inc = float(fin_df.loc[k].iloc[0])
                        break
                for k in ["Total Revenue", "Operating Revenue", "Revenue"]:
                    if k in fin_df.index:
                        rev = float(fin_df.loc[k].iloc[0])
                        break
                if net_inc is not None and rev and rev > 0:
                    profit_margin = net_inc / rev
            except Exception:
                pass

        if profit_margin is not None:
            special_metric = f"{profit_margin * 100:.2f}% (Profit Margin)"
        else:
            special_metric = "Corporate Equity"

    # Sector & Industry classification
    raw_cat = info.get("category") if is_etf else info.get("sector")
    if not raw_cat or str(raw_cat).lower() in ["none", "n/a", ""]:
        # Ticker known profile heuristics
        category = "Technology" if ticker_clean in ["NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "META", "TSM", "INTC"] else ("Index ETF" if is_etf else "Equities")
    else:
        category = str(raw_cat)

    # Dividend Calculation
    div_rate, div_yield = get_dividend_metrics(info, current_price)

    profile = {
        "ticker": ticker_clean,
        "name": info.get("longName") or info.get("shortName") or ticker_clean,
        "type": "ETF" if is_etf else "Equity",
        "price": current_price,
        "currency": fast_dict.get("currency") or info.get("currency") or "USD",
        "size_label": size_label,
        "size_val": float(size_val) if size_val else None,
        "pe_ratio": float(pe_ratio) if pe_ratio else None,
        "beta": float(beta) if beta else None,
        "52w_high": float(high_52) if high_52 else None,
        "52w_low": float(low_52) if low_52 else None,
        "div_yield": div_yield,
        "special_metric": special_metric,
        "category": category
    }

    return stk, profile, hist_1y


def render_comparison_tab(ticker_list):
    st.markdown("### ⚖️ Head-to-Head Comparison: Stocks & ETFs")
    st.caption("Benchmark corporate equities directly against index or sector ETFs.")

    c_in1, c_in2, c_in3 = st.columns([2, 2, 1.5])
    with c_in1:
        ticker_a = st.text_input("Asset A (Stock or ETF):", value="NVDA").upper().strip()
    with c_in2:
        ticker_b = st.text_input("Asset B (Stock or ETF Benchmark):", value="AMD").upper().strip()
    with c_in3:
        timeframe = st.selectbox("Comparison Horizon:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd"], index=3)

    if not ticker_a or not ticker_b:
        st.warning("Please specify two tickers to run the comparison.")
        return

    if ticker_a == ticker_b:
        st.info("Please choose two different tickers to compare.")
        return

    with st.spinner(f"Querying and calculating indicators for {ticker_a} and {ticker_b}..."):
        try:
            stk_a, data_a, hist_a_full = get_security_profile(ticker_a)
            stk_b, data_b, hist_b_full = get_security_profile(ticker_b)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return

    # --- TOP LEVEL SUMMARY CARDS ---
    card1, card2 = st.columns(2)
    for col, data, border_color in zip([card1, card2], [data_a, data_b], ["#10b981", "#38bdf8"]):
        with col:
            with st.container(border=True):
                st.markdown(f"<h4 style='margin:0; color:{border_color};'>{data['name']} ({data['ticker']})</h4>", unsafe_allow_html=True)
                st.caption(f"Asset Type: **{data['type']}** | Category: **{data['category']}**")
                st.metric(
                    label=f"Current Price ({data['currency']})",
                    value=f"${data['price']:,.2f}" if data['price'] > 0 else "N/A"
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- NORMALIZED RETURN OVERLAY CHART ---
    st.markdown("#### 📈 Normalized % Return Growth")
    st.caption(f"Percentage return indexed from the start of the selected {timeframe} window (Baseline = 0.00%).")

    hist_a = stk_a.history(period=timeframe)
    hist_b = stk_b.history(period=timeframe)

    if not hist_a.empty and not hist_b.empty:
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
        st.warning("Could not pull matching historical price series for this timeframe.")

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
        ("Sector / Sub-Category", data_a['category'], data_b['category']),
        ("Current Price", f"${data_a['price']:.2f}", f"${data_b['price']:.2f}"),
        (f"Size ({data_a['size_label']} / {data_b['size_label']})", format_size(data_a['size_val']), format_size(data_b['size_val'])),
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