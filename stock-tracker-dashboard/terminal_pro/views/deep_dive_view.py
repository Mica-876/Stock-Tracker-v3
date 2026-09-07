import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from data_engine import get_dividend_metrics

def render_deep_dive_tab(ticker_list):
    st.markdown("### 🔍 Financial Statement Breakdown & Corporate Profile")

    col_select1, col_select2, col_select3 = st.columns([2, 2, 2])

    with col_select1:
        selected_stock = st.selectbox("Select Target Stock:", ticker_list)

    with col_select2:
        selected_year = st.selectbox("Select Year:", [2026, 2025, 2024, 2023, 2022, 2021], index=0)

    with col_select3:
        chart_style = st.selectbox("Chart Format:", ["Line Chart with Moving Averages", "Candlestick"])

    if selected_stock:
        stk = yf.Ticker(selected_stock)
        info = stk.info

        long_name = info.get("longName") or info.get("shortName") or selected_stock
        sector_name = info.get("sector", "N/A")
        industry_name = info.get("industry", "N/A")
        city = info.get("city", "")
        country = info.get("country", "")
        location = f"{city}, {country}".strip(", ") if (city or country) else "N/A"
        website = info.get("website", "")
        summary = info.get("longBusinessSummary", "No corporate overview description available for this ticker.")

        st.markdown(f"""
        <div class="company-card">
            <h3>🏢 {long_name} ({selected_stock})</h3>
            <div>
                <span class="meta-tag">Sector: {sector_name}</span>
                <span class="meta-tag">Industry: {industry_name}</span>
                <span class="meta-tag">HQ: {location}</span>
                {"<a href='" + website + "' target='_blank' style='color:#34d399; font-size:12px; font-weight:600; text-decoration:none;'>🌐 Official Website</a>" if website else ""}
            </div>
            <p><strong>Company Profile & Operations:</strong><br>{summary}</p>
        </div>
        """, unsafe_allow_html=True)

        # --- DYNAMIC HISTORICAL FINANCIAL EXTRACTION ---
        try:
            financials_df = stk.financials
            balance_sheet_df = stk.balance_sheet
            cashflow_df = stk.cashflow
        except Exception:
            financials_df, balance_sheet_df, cashflow_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Find matching column for the selected year
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
            
            # Helper safely extract line item
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
            forward_pe = None  # Forward P/E is strictly forward-looking
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

        # Fundamentals Metric Display
        f1, f2, f3, f4 = st.columns(4)

        f1.metric(f"Revenue ({selected_year})", f"${rev / 1e9:.2f}B" if rev else "N/A")
        f1.metric("Profit Margin", f"{profit_margin * 100:.2f}%" if profit_margin is not None else "N/A")

        f2.metric("Diluted EPS", f"${eps:.2f}" if eps is not None else "N/A")
        f2.metric("P/E Benchmark", f"{forward_pe:.2f} (Fwd)" if forward_pe else "N/A")

        f3.metric("Total Cash", f"${total_cash / 1e9:.2f}B" if total_cash else "N/A")
        f3.metric("Debt-to-Equity", f"{debt_to_equity:.2f}" if debt_to_equity is not None else "N/A")

        f4.metric("Return on Equity (ROE)", f"{roe * 100:.2f}%" if roe is not None else "N/A")
        f4.metric("Operating Cash Flow", f"${operating_cash / 1e9:.2f}B" if operating_cash else "N/A")

        st.markdown("---")

        # --- DIVIDEND CALCULATOR SECTION ---
        st.markdown(f"### 💰 Dividend Calculator for {selected_stock}")

        current_p = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        div_rate, div_yield = get_dividend_metrics(info, current_p)

        calc_c1, calc_c2 = st.columns([1, 2])

        with calc_c1:
            shares_input = st.number_input(
                f"Number of {selected_stock} Shares Held:",
                min_value=0.0,
                value=100.0,
                step=10.0
            )

        annual_payout = shares_input * div_rate
        quarterly_payout = annual_payout / 4
        position_value = shares_input * current_p

        with calc_c2:
            m_div1, m_div2, m_div3, m_div4 = st.columns(4)
            m_div1.metric("Dividend Yield", f"{div_yield:.2f}%")
            m_div2.metric("Payout / Share", f"${div_rate:.2f}/yr")
            m_div3.metric("Annual Income", f"${annual_payout:,.2f}")
            m_div4.metric("Quarterly Income", f"${quarterly_payout:,.2f}")

        if div_yield == 0:
            st.info(f"ℹ️ {selected_stock} currently does not pay a regular dividend, or dividend data is unavailable.")
        else:
            st.caption(f"Estimated total investment value for {shares_input:,.0f} shares: **${position_value:,.2f}**")

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
        s3.metric(f"{selected_year} Projected Dividend Income", f"${tot_payout:,.2f}")

        st.caption(f"_{overview_model['labels']['footerNote']}_")
        st.markdown("---")

        # Historical Chart
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
                title=f"{selected_stock} - Price Performance ({selected_year})",
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

            # News Feed
            st.markdown("---")
            st.markdown(f"#### 📰 Recent Headlines for {selected_stock}")
            try:
                news_items = stk.news
                if news_items:
                    for item in news_items[:5]:
                        title = item.get("title", "No Title")
                        link = item.get("link", "#")
                        publisher = item.get("publisher", "Unknown")
                        st.write(f"• **[{title}]({link})** — *{publisher}*")
                else:
                    st.info("No headlines available.")
            except Exception:
                st.info("News feed currently offline.")
        else:
            st.warning(f"No price data found for {selected_stock} in {selected_year}.")