import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from data_engine import get_dividend_metrics

def format_compact_currency(val):
    """Formats large currency figures cleanly to prevent container clipping."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        val = float(val)
        if abs(val) >= 1e12:
            return f"${val / 1e12:.2f}T"
        if abs(val) >= 1e9:
            return f"${val / 1e9:.2f}B"
        if abs(val) >= 1e6:
            return f"${val / 1e6:.2f}M"
        if abs(val) >= 1e3:
            return f"${val / 1e3:.1f}K"
        return f"${val:,.2f}"
    except Exception:
        return "N/A"

def render_deep_dive_tab(ticker_list):
    st.markdown("### 🔍 Financial Statement Breakdown & Corporate Profile")

    col_select1, col_select2, col_select3 = st.columns([2, 2, 2])

    with col_select1:
        selected_stock = st.selectbox("Select Target Stock or ETF:", ticker_list)

    with col_select2:
        selected_year = st.selectbox("Select Year:", [2026, 2025, 2024, 2023, 2022, 2021], index=0)

    with col_select3:
        chart_style = st.selectbox("Chart Format:", ["Line Chart with Moving Averages", "Candlestick"])

    if not selected_stock:
        st.info("Select or enter a symbol to begin analysis.")
        return

    stk = yf.Ticker(selected_stock)
    
    try:
        info = stk.info or {}
    except Exception:
        info = {}

    fast = getattr(stk, "fast_info", None)

    # Robust ETF vs Equity Detection
    quote_type = str(info.get("quoteType") or getattr(fast, "quote_type", "")).upper()
    is_etf = (
        quote_type in ["ETF", "MUTUALFUND"]
        or "fundFamily" in info
        or "category" in info
        or info.get("legalType") == "Exchange Traded Fund"
    )

    long_name = info.get("longName") or info.get("shortName") or selected_stock
    classification = "Exchange Traded Fund (ETF)" if is_etf else "Corporate Equity"
    category = info.get("category") if is_etf else info.get("sector", "N/A")
    family_industry = info.get("fundFamily") if is_etf else info.get("industry", "N/A")
    city = info.get("city", "")
    country = info.get("country", "")
    location = f"{city}, {country}".strip(", ") if (city or country) else "Global"
    summary = info.get("longBusinessSummary") or "No business summary or prospectus available for this ticker."

    # Native Card Container: eliminates raw HTML injection and string escape crashes
    with st.container(border=True):
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown(f"<h3 style='margin:0 0 6px 0; color:#34d399;'>🏢 {long_name} ({selected_stock})</h3>", unsafe_allow_html=True)
            tag_html = f"""
            <span class="meta-tag">Class: {classification}</span>
            <span class="meta-tag">Category: {category}</span>
            <span class="meta-tag">HQ/Provider: {family_industry if is_etf else location}</span>
            """
            st.markdown(tag_html, unsafe_allow_html=True)
        with h_col2:
            website = info.get("website", "")
            if website:
                st.markdown(f"<div style='text-align:right;'><a href='{website}' target='_blank' style='color:#38bdf8; font-size:12px; text-decoration:none; font-weight:600;'>🌐 Official Page</a></div>", unsafe_allow_html=True)

        st.markdown(f"<p style='color:#94a3b8; font-size:13px; line-height:1.5; margin-top:10px;'><strong>Profile & Investment Strategy:</strong><br>{summary}</p>", unsafe_allow_html=True)

    # Current Price extraction with fallback hierarchy
    latest_hist = stk.history(period="5d")
    latest_close = float(latest_hist['Close'].iloc[-1]) if not latest_hist.empty else 0.0
    current_p = (
        getattr(fast, "last_price", None)
        or info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("navPrice")
        or latest_close
    )
    current_p = float(current_p) if current_p else 0.0

    st.markdown("---")

    # --- FUNDAMENTALS SECTION ---
    if is_etf:
        st.markdown("#### 📊 Fund Fundamentals & Performance Metrics")
        st.caption(f"Showing fund structure metrics for **{selected_stock}** (ETFs do not file single-entity corporate earnings).")

        fund_aum = info.get("totalAssets") or getattr(fast, "market_cap", None)
        expense_ratio = info.get("annualReportExpenseRatio") or info.get("expenseRatio")
        exp_str = f"{expense_ratio * 100:.2f}%" if (expense_ratio and expense_ratio < 1) else (f"{expense_ratio:.2f}%" if expense_ratio else "N/A")
        
        nav_price = info.get("navPrice") or current_p
        pe_benchmark = info.get("trailingPE") or info.get("forwardPE")
        beta_val = info.get("beta") or info.get("beta3Year")
        high_52 = getattr(fast, "year_high", None) or info.get("fiftyTwoWeekHigh")
        low_52 = getattr(fast, "year_low", None) or info.get("fiftyTwoWeekLow")

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Net Assets (AUM)", format_compact_currency(fund_aum))
        e1.metric("Net Asset Value (NAV)", f"${nav_price:.2f}" if nav_price else "N/A")

        e2.metric("Expense Ratio", exp_str)
        e2.metric("Portfolio P/E", f"{pe_benchmark:.2f}" if pe_benchmark else "N/A")

        e3.metric("52-Week High", f"${high_52:.2f}" if high_52 else "N/A")
        e3.metric("52-Week Low", f"${low_52:.2f}" if low_52 else "N/A")

        e4.metric("3Y Beta", f"{beta_val:.2f}" if beta_val else "N/A")
        e4.metric("Fund Family", str(family_industry)[:18])

    else:
        st.markdown(f"#### 📑 Financial Statements & Corporate Metrics ({selected_year})")
        try:
            financials_df = stk.financials
            balance_sheet_df = stk.balance_sheet
            cashflow_df = stk.cashflow
        except Exception:
            financials_df, balance_sheet_df, cashflow_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        def get_col_for_year(df, yr):
            if df is not None and not df.empty:
                for col in df.columns:
                    try:
                        if hasattr(col, "year") and col.year == yr:
                            return col
                        elif str(yr) in str(col):
                            return col
                    except Exception:
                        continue
            return None

        col_fin = get_col_for_year(financials_df, selected_year)
        col_bs = get_col_for_year(balance_sheet_df, selected_year)
        col_cf = get_col_for_year(cashflow_df, selected_year)

        is_historical_year = col_fin is not None

        if is_historical_year:
            st.caption(f"Showing filed audited statements for FY **{selected_year}**")
            
            def get_item(df, target_col, keys):
                if df is not None and not df.empty and target_col in df.columns:
                    for k in keys:
                        if k in df.index and pd.notnull(df.loc[k, target_col]):
                            return float(df.loc[k, target_col])
                return None

            rev = get_item(financials_df, col_fin, ["Total Revenue", "Operating Revenue", "Revenue"])
            net_income = get_item(financials_df, col_fin, ["Net Income", "Net Income Common Stockholders"])
            eps = get_item(financials_df, col_fin, ["Diluted EPS", "Basic EPS"])
            profit_margin = (net_income / rev) if (rev and net_income) else None

            total_cash = get_item(balance_sheet_df, col_bs, ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents", "Other Short Term Investments"])
            stockholder_equity = get_item(balance_sheet_df, col_bs, ["Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"])
            total_debt = get_item(balance_sheet_df, col_bs, ["Total Debt", "Long Term Debt", "Current Debt"])
            
            debt_to_equity = (total_debt / stockholder_equity) if (total_debt and stockholder_equity and stockholder_equity > 0) else None
            roe = (net_income / stockholder_equity) if (net_income and stockholder_equity and stockholder_equity > 0) else None
            operating_cash = get_item(cashflow_df, col_cf, ["Operating Cash Flow", "Cash Flows from Operating Activities"])
            forward_pe = None
        else:
            st.caption(f"Filed full-year statement unavailable for **{selected_year}**. Displaying latest TTM metrics.")
            rev = info.get("totalRevenue", None)
            profit_margin = info.get("profitMargins", None)
            eps = info.get("trailingEps", None)
            forward_pe = info.get("forwardPE", None)
            total_cash = info.get("totalCash", None)
            debt_to_equity = info.get("debtToEquity", None)
            if debt_to_equity:
                debt_to_equity = debt_to_equity / 100.0 if debt_to_equity > 10 else debt_to_equity
            roe = info.get("returnOnEquity", None)
            operating_cash = info.get("operatingCashflow", None)

        f1, f2, f3, f4 = st.columns(4)
        f1.metric(f"Revenue ({selected_year})", format_compact_currency(rev))
        f1.metric("Profit Margin", f"{profit_margin * 100:.2f}%" if profit_margin is not None else "N/A")

        f2.metric("Diluted EPS", f"${eps:.2f}" if eps is not None else "N/A")
        f2.metric("P/E Benchmark", f"{forward_pe:.2f} (Fwd)" if forward_pe else "N/A")

        f3.metric("Total Cash", format_compact_currency(total_cash))
        f3.metric("Debt-to-Equity", f"{debt_to_equity:.2f}" if debt_to_equity is not None else "N/A")

        f4.metric("Return on Equity (ROE)", f"{roe * 100:.2f}%" if roe is not None else "N/A")
        f4.metric("Operating Cash Flow", format_compact_currency(operating_cash))

    st.markdown("---")

    # --- DIVIDEND CALCULATOR SECTION ---
    st.markdown(f"### 💰 Dividend & Income Calculator for {selected_stock}")

    div_rate, div_yield = get_dividend_metrics(info, current_p)

    calc_c1, calc_c2 = st.columns([1.1, 3.2])

    with calc_c1:
        shares_input = st.number_input(
            f"Number of {selected_stock} Shares Held:",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

    annual_payout = shares_input * div_rate
    quarterly_payout = annual_payout / 4.0
    position_value = shares_input * current_p

    with calc_c2:
        m_div1, m_div2, m_div3, m_div4 = st.columns(4)
        m_div1.metric("Dividend Yield", f"{div_yield:.2f}%")
        m_div2.metric("Annual / Share", f"${div_rate:.2f}")
        m_div3.metric("Annual Income", format_compact_currency(annual_payout))
        m_div4.metric("Quarterly Payout", format_compact_currency(quarterly_payout))

    if div_yield == 0:
        st.info(f"ℹ️ {selected_stock} currently does not pay a regular dividend, or distributions are non-standard.")
    else:
        st.caption(f"Estimated total value for {shares_input:,.0f} shares: **${position_value:,.2f}**")

    st.markdown("---")

    # --- DYNAMIC PROJECTION ENGINE ---
    overview_model = {
        "labels": {
            "currencySymbol": "$",
            "title": f"{selected_year} Financial Overview",
            "subtitle": f"Calendar Year {selected_year} Projection & Dividend Analysis",
            "xAxis": "Quarter",
            "yAxis": "Amount",
            "slidersTitle": f"Adjust {selected_year} Parameters",
            "footerNote": f"*Adjusted baseline to {selected_year} calendar year and updated dividend metrics to match current portfolio yield."
        },
        "params": [
            { "key": "portfolio_base", "label": "Portfolio Principal", "value": 100000, "min": 10000, "max": 500000, "step": 5000 },
            { "key": "div_yield", "label": "Current Dividend Yield (%)", "value": float(div_yield) if div_yield > 0 else 3.5, "min": 0.5, "max": 10.0, "step": 0.1 },
            { "key": "quarter", "label": f"{selected_year} Quarters Elapsed", "value": 4, "min": 1, "max": 4, "step": 1 }
        ],
        "series": [
            {
                "label": f"{selected_year} Cumulative Dividend Income",
                "colorVar": "#10b981",
                "formula": "(portfolio_base * (div_yield / 100)) * (t / 4)"
            }
        ]
    }

    st.markdown(f"### 📈 {overview_model['labels']['title']}")
    st.caption(overview_model['labels']['subtitle'])

    col_params, col_chart = st.columns([1, 2])

    param_values = {}
    with col_params:
        st.markdown(f"**{overview_model['labels']['slidersTitle']}**")
        for p in overview_model['params']:
            param_values[p['key']] = st.slider(
                p['label'],
                min_value=float(p['min']) if isinstance(p['min'], float) else p['min'],
                max_value=float(p['max']) if isinstance(p['max'], float) else p['max'],
                value=float(p['value']) if isinstance(p['value'], float) else p['value'],
                step=float(p['step']) if isinstance(p['step'], float) else p['step']
            )

    quarters = list(range(1, int(param_values['quarter']) + 1))
    chart_df = pd.DataFrame({"quarter": [f"Q{q}" for q in quarters]})

    for s in overview_model['series']:
        y_values = []
        for q in quarters:
            context = {**param_values, "t": q}
            y_values.append(eval(s['formula'], {}, context))
        chart_df[s['label']] = y_values

    with col_chart:
        fig_proj = px.line(
            chart_df,
            x="quarter",
            y=overview_model['series'][0]['label'],
            title=overview_model['series'][0]['label'],
            markers=True,
            template="plotly_dark"
        )
        fig_proj.update_traces(line_color=overview_model['series'][0]['colorVar'], fill='tozeroy')
        fig_proj.update_layout(
            xaxis_title=overview_model['labels']['xAxis'],
            yaxis_title=f"{overview_model['labels']['yAxis']} ({overview_model['labels']['currencySymbol']})",
            paper_bgcolor='#090d16',
            plot_bgcolor='#0f172a'
        )
        st.plotly_chart(fig_proj, width="stretch")

    tot_payout = (param_values['portfolio_base'] * (param_values['div_yield'] / 100)) * (param_values['quarter'] / 4)
    s1, s2, s3 = st.columns(3)
    s1.metric("Target Year", str(selected_year))
    s2.metric("Annual Dividend Yield", f"{param_values['div_yield']:.2f}%")
    s3.metric(f"{selected_year} Projected Income", format_compact_currency(tot_payout))

    st.caption(f"_{overview_model['labels']['footerNote']}_")
    st.markdown("---")

    # --- HISTORICAL PRICE ACTION ---
    start_date = f"{selected_year}-01-01"
    end_date = f"{selected_year}-12-31"
    hist = stk.history(start=start_date, end=end_date)

    if not hist.empty:
        hist["50_SMA"] = hist["Close"].rolling(window=50).mean()
        hist["200_SMA"] = hist["Close"].rolling(window=200).mean()

        start_p = hist['Close'].iloc[0]
        end_p = hist['Close'].iloc[-1]
        year_return = ((end_p - start_p) / start_p) * 100
        high_p = hist['High'].max()
        low_p = hist['Low'].min()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Start Price", f"${start_p:.2f}")
        m2.metric("Current / End Price", f"${end_p:.2f}", f"{year_return:.2f}%")
        m3.metric(f"{selected_year} High", f"${high_p:.2f}")
        m4.metric(f"{selected_year} Low", f"${low_p:.2f}")

        st.markdown("<br>", unsafe_allow_html=True)

        fig = go.Figure()
        if chart_style == "Line Chart with Moving Averages":
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close Price', line=dict(color='#10b981', width=2.5)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['50_SMA'], mode='lines', name='50-Day SMA', line=dict(color='#f59e0b', width=1.5)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['200_SMA'], mode='lines', name='200-Day SMA', line=dict(color='#ef4444', width=1.5)))
        else:
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=selected_stock
            ))

        fig.update_layout(
            title=f"{selected_stock} - Performance ({selected_year})",
            hovermode="x unified",
            yaxis_title="Price ($)",
            template="plotly_dark",
            paper_bgcolor='#090d16',
            plot_bgcolor='#0f172a',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, width="stretch")

        # Monthly Gains
        st.markdown(f"#### 📅 {selected_stock} Monthly Breakdown ({selected_year})")
        hist_monthly = stk.history(start=start_date, end=end_date, interval="1mo")

        if not hist_monthly.empty and len(hist_monthly) >= 2:
            hist_monthly["Monthly Return (%)"] = hist_monthly["Close"].pct_change() * 100
            monthly_df = pd.DataFrame({
                "Month": [d.strftime("%B") for d in hist_monthly.index],
                "Close Price ($)": [f"${p:.2f}" for p in hist_monthly["Close"]],
                "Monthly Gain (%)": [f"{r:.2f}%" if pd.notnull(r) else "0.00%" for r in hist_monthly["Monthly Return (%)"]]
            })
            st.dataframe(monthly_df, width="stretch", hide_index=True)

        # News Feed (Modern Nested Payload Parser)
        st.markdown("---")
        st.markdown(f"#### 📰 Recent Headlines for {selected_stock}")
        try:
            news_items = stk.news
            if news_items:
                valid_news_count = 0
                for item in news_items:
                    content = item.get("content", item)
                    title = content.get("title")
                    link = (
                        content.get("clickThroughUrl", {}).get("url")
                        or content.get("canonicalUrl", {}).get("url")
                        or content.get("link")
                        or item.get("link")
                        or "#"
                    )
                    provider = content.get("provider", {})
                    publisher = provider.get("displayName") if isinstance(provider, dict) else content.get("publisher", "Yahoo Finance")
                    pub_date = content.get("pubDate", "")
                    time_str = f" • *{pub_date[:10]}*" if pub_date else ""

                    if title:
                        st.markdown(f"• **[{title}]({link})** — *{publisher}*{time_str}")
                        valid_news_count += 1
                        if valid_news_count >= 5:
                            break

                if valid_news_count == 0:
                    st.info(f"No recent headlines formatted for {selected_stock}.")
            else:
                st.info(f"No headlines currently available for {selected_stock}.")
        except Exception:
            st.info("News feed currently offline.")
    else:
        st.warning(f"No historical price action found for {selected_stock} in {selected_year}.")