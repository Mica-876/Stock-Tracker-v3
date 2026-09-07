import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from data_engine import fetch_comparison_profile

def render_comparison_tab(ticker_list):
    st.markdown("### ⚔️ Head-to-Head Valuation & Financial Comparison")
    st.caption("Compare fundamentals, valuation multiples, and relative returns between two competitors.")

    default_idx_a = 0
    default_idx_b = min(1, len(ticker_list) - 1)

    c_pick1, c_pick2, c_pick3 = st.columns([2, 2, 1])
    with c_pick1:
        stock_a = st.selectbox("Select Benchmark Stock (A):", ticker_list, index=default_idx_a, key="cmp_stock_a")
    with c_pick2:
        stock_b = st.selectbox("Select Competitor Stock (B):", ticker_list, index=default_idx_b, key="cmp_stock_b")
    with c_pick3:
        comp_period = st.selectbox("Timeline:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, key="cmp_period")

    if stock_a and stock_b:
        if stock_a == stock_b:
            st.warning("⚠️ Select two distinct stocks to run a comparison.")
        else:
            data_a = fetch_comparison_profile(stock_a)
            data_b = fetch_comparison_profile(stock_b)

            if data_a and data_b:
                st.markdown("<br>", unsafe_allow_html=True)
                mcol1, mcol2 = st.columns(2)
                with mcol1:
                    st.markdown(f"""
                    <div class="company-card" style="border-left-color: #10b981;">
                        <h3>🟢 {data_a['Name']} ({stock_a})</h3>
                        <span class="meta-tag">{data_a['Sector']}</span>
                        <span class="meta-tag">{data_a['Industry']}</span>
                        <p style="font-size:16px; font-weight:700; color:#34d399; margin-top:8px;">Price: ${data_a['Price']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with mcol2:
                    st.markdown(f"""
                    <div class="company-card" style="border-left-color: #38bdf8;">
                        <h3 style="color: #38bdf8 !important;">🔵 {data_b['Name']} ({stock_b})</h3>
                        <span class="meta-tag">{data_b['Sector']}</span>
                        <span class="meta-tag">{data_b['Industry']}</span>
                        <p style="font-size:16px; font-weight:700; color:#38bdf8; margin-top:8px;">Price: ${data_b['Price']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                metrics_to_compare = [
                    ("Market Cap ($B)", data_a["Market Cap ($B)"], data_b["Market Cap ($B)"]),
                    ("Revenue ($B)", data_a["Revenue ($B)"], data_b["Revenue ($B)"]),
                    ("Trailing P/E", data_a["Trailing P/E"], data_b["Trailing P/E"]),
                    ("Forward P/E", data_a["Forward P/E"], data_b["Forward P/E"]),
                    ("PEG Ratio", data_a["PEG Ratio"], data_b["PEG Ratio"]),
                    ("Price to Book (P/B)", data_a["Price to Book (P/B)"], data_b["Price to Book (P/B)"]),
                    ("EV / EBITDA", data_a["EV / EBITDA"], data_b["EV / EBITDA"]),
                    ("Operating Margin (%)", data_a["Operating Margin (%)"], data_b["Operating Margin (%)"]),
                    ("Profit Margin (%)", data_a["Profit Margin (%)"], data_b["Profit Margin (%)"]),
                    ("Return on Equity (%)", data_a["Return on Equity (%)"], data_b["Return on Equity (%)"]),
                    ("Debt to Equity", data_a["Debt to Equity"], data_b["Debt to Equity"]),
                    ("Free Cash Flow ($B)", data_a["Free Cash Flow ($B)"], data_b["Free Cash Flow ($B)"]),
                    ("Dividend Yield (%)", f"{data_a['Dividend Yield (%)']:.2f}%", f"{data_b['Dividend Yield (%)']:.2f}%"),
                    ("Beta (5Y)", data_a["Beta (5Y)"], data_b["Beta (5Y)"])
                ]

                df_comp = pd.DataFrame(metrics_to_compare, columns=["Metric / Fundamental Multiplier", f"{stock_a}", f"{stock_b}"])

                st.markdown("#### 📋 Core Financial Multipliers & Valuation")
                st.dataframe(df_comp, width="stretch", hide_index=True)

                # Normalized Return
                st.markdown("---")
                st.markdown(f"#### 📈 Relative Price Return (%) — Last {comp_period.upper()}")

                stk_a_obj = yf.Ticker(stock_a)
                stk_b_obj = yf.Ticker(stock_b)

                h_a = stk_a_obj.history(period=comp_period)
                h_b = stk_b_obj.history(period=comp_period)

                if not h_a.empty and not h_b.empty:
                    norm_a = ((h_a["Close"] - h_a["Close"].iloc[0]) / h_a["Close"].iloc[0]) * 100
                    norm_b = ((h_b["Close"] - h_b["Close"].iloc[0]) / h_b["Close"].iloc[0]) * 100

                    fig_rel = go.Figure()
                    fig_rel.add_trace(go.Scatter(
                        x=norm_a.index, 
                        y=norm_a, 
                        mode="lines", 
                        name=f"{stock_a} Return (%)",
                        line=dict(color="#10b981", width=2.5)
                    ))
                    fig_rel.add_trace(go.Scatter(
                        x=norm_b.index, 
                        y=norm_b, 
                        mode="lines", 
                        name=f"{stock_b} Return (%)",
                        line=dict(color="#38bdf8", width=2.5)
                    ))

                    fig_rel.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="#090d16",
                        plot_bgcolor="#0f172a",
                        yaxis_title="Normalized Return (%)",
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig_rel, width="stretch")
                else:
                    st.info("Historical data unavailable for this comparison window.")
            else:
                st.error("Failed to retrieve profile data for one or both tickers.")