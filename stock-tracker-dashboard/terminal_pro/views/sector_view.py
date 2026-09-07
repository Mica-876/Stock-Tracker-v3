import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

# High-contrast terminal color mapping for consistent sector palettes
SECTOR_COLOR_MAP = {
    "Technology": "#f97316",              # Bright Orange
    "Utilities": "#3b82f6",               # Vivid Blue
    "Consumer Cyclical": "#10b981",       # Emerald Green
    "Communication Services": "#a855f7",  # Purple
    "Financial Services": "#eab308",      # Gold / Amber
    "Healthcare": "#ec4899",              # Magenta / Pink
    "Industrials": "#06b6d4",             # Cyan
    "Energy": "#ef4444",                  # Coral Red
    "Consumer Defensive": "#84cc16",      # Lime
    "Real Estate": "#14b8a6",             # Teal
    "Basic Materials": "#f43f5e"          # Rose
}

@st.cache_data(ttl=600, show_spinner=False)
def fetch_sector_and_beta_single(ticker):
    """Fallback fetcher for single tickers if sector/beta are missing from dataframe."""
    stk = yf.Ticker(ticker)
    info = {}
    try:
        info = stk.info or {}
    except Exception:
        pass

    fast = getattr(stk, "fast_info", None)
    quote_type = str(info.get("quoteType") or getattr(fast, "quote_type", "")).upper()
    is_etf = (quote_type in ["ETF", "MUTUALFUND"] or "fundFamily" in info or "category" in info)

    raw_sector = info.get("sector") if not is_etf else info.get("category")
    if not raw_sector or str(raw_sector).lower() in ["none", "n/a", ""]:
        if ticker.upper() in ["NVDA", "AAPL", "MSFT", "AMD", "NVTS", "APLD"]:
            sector = "Technology"
        elif ticker.upper() in ["CMS", "DTE", "FE", "AEP"]:
            sector = "Utilities"
        elif ticker.upper() in ["AMZN", "TSLA"]:
            sector = "Consumer Cyclical"
        elif ticker.upper() in ["GOOGL", "META"]:
            sector = "Communication Services"
        elif is_etf:
            sector = "Index ETF"
        else:
            sector = "Other Equities"
    else:
        sector = str(raw_sector)

    beta = info.get("beta") or info.get("beta3Year")
    if beta is None:
        try:
            hist = stk.history(period="1y")
            if not hist.empty and len(hist) > 30:
                stock_ret = hist['Close'].pct_change().dropna()
                spy = yf.Ticker("SPY").history(period="1y")['Close'].pct_change().dropna()
                comb = pd.DataFrame({"s": stock_ret, "m": spy}).dropna()
                cov = comb.cov().iloc[0, 1]
                var = comb["m"].var()
                beta = (cov / var) if var > 0 else 1.0
            else:
                beta = 1.0
        except Exception:
            beta = 1.0

    return {"Ticker": ticker.upper(), "Sector": sector, "Beta (5Y)": round(float(beta), 2)}

def render_sector_tab(data_input=None):
    st.markdown("### 🍰 Sector Allocation & Risk Breakdown")
    st.caption("Inspect sector concentration, asset diversification, and market sensitivity across the watchlist.")

    # 1. Safely handle whether input is a DataFrame (from app.py) or a List of Tickers
    if data_input is None:
        st.info("Watchlist is currently empty. Add tickers from the control center to analyze sectors.")
        return

    records = []

    if isinstance(data_input, pd.DataFrame):
        if data_input.empty:
            st.info("Watchlist is currently empty. Add tickers from the control center to analyze sectors.")
            return

        # Check if Sector and Beta already exist in the passed DataFrame
        df_cols = [c.lower() for c in data_input.columns]
        ticker_col = next((c for c in data_input.columns if c.lower() in ["ticker", "symbol"]), None)
        sector_col = next((c for c in data_input.columns if "sector" in c.lower()), None)
        beta_col = next((c for c in data_input.columns if "beta" in c.lower()), None)

        if ticker_col:
            for _, row in data_input.iterrows():
                t = str(row[ticker_col]).upper().strip()
                s = str(row[sector_col]) if sector_col and pd.notnull(row[sector_col]) and str(row[sector_col]).lower() not in ["none", "n/a", ""] else None
                b = row[beta_col] if beta_col and pd.notnull(row[beta_col]) else None

                if s and b is not None:
                    try:
                        b_val = float(str(b).replace("x", "").strip())
                    except Exception:
                        b_val = 1.0
                    records.append({"Ticker": t, "Sector": s, "Beta (5Y)": round(b_val, 2)})
                else:
                    records.append(fetch_sector_and_beta_single(t))
        else:
            st.warning("Could not identify Ticker column in metrics data.")
            return

    elif isinstance(data_input, list):
        if len(data_input) == 0:
            st.info("Watchlist is currently empty. Add tickers from the control center to analyze sectors.")
            return
        with st.spinner("Analyzing sector allocations and volatility profiles..."):
            records = [fetch_sector_and_beta_single(t) for t in data_input]

    else:
        st.error("Unsupported data format passed to sector view.")
        return

    df = pd.DataFrame(records)

    col_pie, col_bar = st.columns([1, 1.2])

    # --- 1. SECTOR ALLOCATION PIE CHART ---
    with col_pie:
        st.markdown("#### Watchlist Sector Allocation")

        sector_counts = df["Sector"].value_counts().reset_index()
        sector_counts.columns = ["Sector", "Count"]

        # High-contrast mapping for distinct slices
        palette = [
            SECTOR_COLOR_MAP.get(s, px.colors.qualitative.Vivid[i % len(px.colors.qualitative.Vivid)])
            for i, s in enumerate(sector_counts["Sector"])
        ]

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=sector_counts["Sector"],
                    values=sector_counts["Count"],
                    hole=0.45,
                    marker=dict(colors=palette, line=dict(color="#090d16", width=2)),
                    textinfo="percent",
                    textfont=dict(size=13, color="#ffffff"),
                    hoverinfo="label+value+percent",
                    insidetextorientation="radial"
                )
            ]
        )

        fig_pie.update_layout(
            paper_bgcolor="#090d16",
            plot_bgcolor="#0f172a",
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.95,
                xanchor="left",
                x=1.02,
                font=dict(color="#e2e8f0", size=11)
            ),
            margin=dict(l=10, r=10, t=30, b=10),
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, width="stretch")

    # --- 2. BETA VOLATILITY BAR CHART ---
    with col_bar:
        st.markdown("#### 5Y Beta Volatility Score")

        df_sorted = df.sort_values(by="Beta (5Y)", ascending=True)

        fig_bar = px.bar(
            df_sorted,
            x="Ticker",
            y="Beta (5Y)",
            color="Sector",
            color_discrete_map=SECTOR_COLOR_MAP,
            template="plotly_dark",
            text="Beta (5Y)"
        )

        fig_bar.update_traces(textposition="outside", textfont=dict(color="#94a3b8", size=10))
        fig_bar.update_layout(
            paper_bgcolor="#090d16",
            plot_bgcolor="#0f172a",
            yaxis=dict(title="Beta (Market Sensitivity)", gridcolor="#1e293b"),
            xaxis=dict(title="Ticker", tickangle=-90),
            margin=dict(l=20, r=20, t=30, b=10),
            legend=dict(font=dict(color="#e2e8f0", size=11))
        )
        st.plotly_chart(fig_bar, width="stretch")

    st.markdown("---")

    # --- SECTOR CONCENTRATION BREAKDOWN TABLE ---
    st.markdown("#### 📑 Breakdown by Sector")
    table_data = []
    for sector, group in df.groupby("Sector"):
        table_data.append({
            "Sector": sector,
            "Total Assets": len(group),
            "Tickers": ", ".join(group["Ticker"].tolist()),
            "Average Beta": f"{group['Beta (5Y)'].mean():.2f}"
        })

    st.dataframe(pd.DataFrame(table_data), width="stretch", hide_index=True)