import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from storage import sync_to_file
from data_engine import get_dividend_metrics

def render_portfolio_tab():
    st.markdown("### 💼 Portfolio Management Console")

    col_user1, col_user2 = st.columns([2, 2])

    with col_user1:
        existing_users = list(st.session_state.portfolios.keys())
        active_user = st.selectbox("Select Member Profile:", existing_users)

    with col_user2:
        new_username = st.text_input("Create New Profile:")
        if st.button("➕ Create Profile") and new_username:
            clean_name = new_username.strip()
            if clean_name and clean_name not in st.session_state.portfolios:
                st.session_state.portfolios[clean_name] = []
                sync_to_file()
                st.session_state.last_updated = datetime.datetime.now().strftime("%H:%M:%S")
                st.success(f"Profile created for {clean_name}")
                st.rerun()

    st.markdown("---")

    with st.expander(f"➕ Add Position to {active_user}'s Portfolio", expanded=False):
        with st.form("add_position_form", clear_on_submit=True):
            col_p1, col_p2, col_p3 = st.columns(3)
            p_ticker = col_p1.text_input("Stock Ticker:").strip().upper()
            p_shares = col_p2.number_input("Shares:", min_value=0.001, step=1.0)
            p_buy_price = col_p3.number_input("Avg Buy Price ($):", min_value=0.01, step=1.0)

            if st.form_submit_button("Save Position") and p_ticker:
                st.session_state.portfolios[active_user].append({
                    "ticker": p_ticker,
                    "shares": float(p_shares),
                    "buy_price": float(p_buy_price)
                })
                sync_to_file()
                st.session_state.last_updated = datetime.datetime.now().strftime("%H:%M:%S")
                st.success(f"Added position for {p_ticker}!")
                st.rerun()

    user_holdings = st.session_state.portfolios.get(active_user, [])

    if user_holdings:
        portfolio_rows = []
        total_invested = 0
        total_current_val = 0
        total_annual_div = 0

        for item in user_holdings:
            t_sym = item["ticker"]
            shares = item["shares"]
            buy_p = item["buy_price"]

            stk = yf.Ticker(t_sym)
            live_p = stk.info.get("currentPrice") or stk.info.get("regularMarketPrice") or buy_p

            div_rate, div_yield = get_dividend_metrics(stk.info, live_p)
            annual_position_div = shares * div_rate
            total_annual_div += annual_position_div

            cost_basis = shares * buy_p
            current_val = shares * live_p
            pnl = current_val - cost_basis
            pnl_pct = (pnl / cost_basis) * 100 if cost_basis else 0

            total_invested += cost_basis
            total_current_val += current_val

            portfolio_rows.append({
                "Ticker": t_sym,
                "Shares Owned": shares,
                "Avg Buy Price ($)": f"${buy_p:.2f}",
                "Live Price ($)": f"${live_p:.2f}",
                "Total Cost ($)": f"${cost_basis:.2f}",
                "Current Value ($)": f"${current_val:.2f}",
                "Gain / Loss ($)": f"${pnl:.2f}",
                "Gain / Loss (%)": f"{pnl_pct:.2f}%",
                "Div Yield (%)": f"{div_yield:.2f}%",
                "Est. Annual Div ($)": f"${annual_position_div:.2f}"
            })

        total_pnl = total_current_val - total_invested
        total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested else 0
        port_div_yield = (total_annual_div / total_current_val * 100) if total_current_val else 0

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Total Invested", f"${total_invested:,.2f}")
        p2.metric("Market Value", f"${total_current_val:,.2f}")
        p3.metric("Total Return", f"${total_pnl:,.2f}", f"{total_pnl_pct:.2f}%")
        p4.metric("Est. Annual Income", f"${total_annual_div:,.2f}", f"Yield: {port_div_yield:.2f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(portfolio_rows), width="stretch", hide_index=True)

        if st.button("🗑️ Clear Portfolio Holdings"):
            st.session_state.portfolios[active_user] = []
            sync_to_file()
            st.session_state.last_updated = datetime.datetime.now().strftime("%H:%M:%S")
            st.rerun()
    else:
        st.info(f"No active holdings recorded for {active_user}.")