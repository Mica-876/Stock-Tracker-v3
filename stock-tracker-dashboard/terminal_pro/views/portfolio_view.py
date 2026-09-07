import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# Safe modular import for storage functions
try:
    import storage
except ImportError:
    from .. import storage

# Safe modular import for dividend engine
try:
    from data_engine import get_dividend_metrics
except ImportError:
    from ..data_engine import get_dividend_metrics

def load_stored_portfolio():
    """Safely retrieves portfolio data from storage module."""
    if hasattr(storage, "load_portfolio_data"):
        return storage.load_portfolio_data()
    elif hasattr(storage, "load_data"):
        return storage.load_data()
    elif hasattr(storage, "load_user_data"):
        return storage.load_user_data()
    return {"profiles": {"Default Portfolio": {"cash": 10000.0, "positions": {}}}}

def persist_portfolio(portfolio_data):
    """Safely dispatches to whichever save function exists in storage.py."""
    if hasattr(storage, "save_portfolio_data"):
        storage.save_portfolio_data(portfolio_data)
    elif hasattr(storage, "save_data"):
        storage.save_data(portfolio_data)
    elif hasattr(storage, "save_user_data"):
        storage.save_user_data(portfolio_data)

def render_portfolio_tab(portfolio_data=None, ticker_list=None):
    st.markdown("### 💼 Portfolio Management & Execution Terminal")
    st.caption("Manage positions, execute buy/sell orders, track realized P&L, and monitor asset allocations.")

    # 1. Fallback if app.py calls render_portfolio_tab() without arguments
    if portfolio_data is None:
        if "portfolio_data" in st.session_state:
            portfolio_data = st.session_state["portfolio_data"]
        else:
            portfolio_data = load_stored_portfolio()
            st.session_state["portfolio_data"] = portfolio_data

    if ticker_list is None:
        ticker_list = st.session_state.get("watchlist", ["NVDA", "AAPL", "MSFT", "GOOGL"])

    # 2. Ensure profile structure exists
    if "profiles" not in portfolio_data or not portfolio_data["profiles"]:
        portfolio_data["profiles"] = {
            "Default Portfolio": {
                "cash": 10000.0,
                "positions": {}
            }
        }

    profile_names = list(portfolio_data["profiles"].keys())

    # Ensure active profile selection state
    if "active_profile" not in st.session_state or st.session_state["active_profile"] not in profile_names:
        st.session_state["active_profile"] = profile_names[0]

    # --- PROFILE MANAGEMENT HUB ---
    with st.expander("⚙️ Manage Portfolio Profiles", expanded=False):
        c_prof1, c_prof2, c_prof3 = st.columns([2, 2, 2])

        with c_prof1:
            active_profile = st.selectbox(
                "Active Portfolio Profile:",
                options=profile_names,
                index=profile_names.index(st.session_state["active_profile"])
            )
            st.session_state["active_profile"] = active_profile

        with c_prof2:
            new_profile_name = st.text_input("New Profile Name:", placeholder="e.g. Dividend Growth ISA").strip()
            if st.button("➕ Create Profile"):
                if new_profile_name and new_profile_name not in portfolio_data["profiles"]:
                    portfolio_data["profiles"][new_profile_name] = {
                        "cash": 10000.0,
                        "positions": {}
                    }
                    persist_portfolio(portfolio_data)
                    st.session_state["active_profile"] = new_profile_name
                    st.success(f"Profile '{new_profile_name}' created.")
                    st.rerun()
                elif new_profile_name in portfolio_data["profiles"]:
                    st.warning("A profile with that name already exists.")

        with c_prof3:
            st.markdown("**Delete Profile**")
            can_delete = len(profile_names) > 1
            if can_delete:
                confirm_delete = st.checkbox(f"Confirm deleting '{active_profile}'", key="delete_confirm_chk")
                if st.button("🗑️ Delete Profile", disabled=not confirm_delete):
                    del portfolio_data["profiles"][active_profile]
                    persist_portfolio(portfolio_data)
                    remaining_profiles = list(portfolio_data["profiles"].keys())
                    st.session_state["active_profile"] = remaining_profiles[0]
                    st.success(f"Profile '{active_profile}' successfully removed.")
                    st.rerun()
            else:
                st.caption("⚠️ Cannot delete the only remaining profile.")

    active_profile = st.session_state["active_profile"]
    current_portfolio = portfolio_data["profiles"][active_profile]
    positions = current_portfolio.setdefault("positions", {})
    cash = float(current_portfolio.get("cash", 0.0))

    st.markdown("---")

    # --- TRADE & POSITION ORDER DESK ---
    st.markdown(f"#### 🎯 Trade & Position Execution ({active_profile})")

    trade_tab_buy, trade_tab_sell, trade_tab_close = st.tabs(["🟢 Buy / Add Position", "🟠 Sell / Trim Position", "🔴 Liquidate Position"])

    with trade_tab_buy:
        c_b1, c_b2, c_b3, c_b4 = st.columns([1.5, 1.5, 1.5, 1.5])
        with c_b1:
            buy_ticker = st.text_input("Asset Ticker (Buy):", value="NVDA", key="buy_tick_in").upper().strip()
        with c_b2:
            buy_shares = st.number_input("Shares to Buy:", min_value=0.01, value=10.0, step=1.0, key="buy_sh_in")
        with c_b3:
            buy_price = st.number_input("Purchase Price ($):", min_value=0.01, value=120.0, step=5.0, key="buy_px_in")
        with c_b4:
            st.write("")
            st.write("")
            deduct_cash = st.checkbox("Deduct from Cash balance", value=True, key="chk_deduct_cash")
            if st.button("Confirm Buy Order", key="btn_confirm_buy"):
                total_cost = buy_shares * buy_price
                if deduct_cash and total_cost > cash:
                    st.error(f"Insufficient cash. Required: ${total_cost:,.2f}, Available: ${cash:,.2f}")
                else:
                    if buy_ticker in positions:
                        # Weighted average cost basis calculation
                        old_shares = float(positions[buy_ticker].get("shares", 0))
                        old_cost = float(positions[buy_ticker].get("avg_cost", 0))
                        new_shares = old_shares + buy_shares
                        new_cost = ((old_shares * old_cost) + total_cost) / new_shares
                        positions[buy_ticker] = {"shares": new_shares, "avg_cost": new_cost}
                    else:
                        positions[buy_ticker] = {"shares": buy_shares, "avg_cost": buy_price}

                    if deduct_cash:
                        current_portfolio["cash"] = cash - total_cost

                    persist_portfolio(portfolio_data)
                    st.success(f"Executed BUY for {buy_shares} {buy_ticker} at ${buy_price:.2f}.")
                    st.rerun()

    with trade_tab_sell:
        if positions:
            c_s1, c_s2, c_s3, c_s4 = st.columns([1.5, 1.5, 1.5, 1.5])
            with c_s1:
                sell_ticker = st.selectbox("Select Asset to Sell:", options=list(positions.keys()), key="sell_tick_in")
                avail_shares = float(positions[sell_ticker].get("shares", 0.0))
                cost_basis_each = float(positions[sell_ticker].get("avg_cost", 0.0))
                st.caption(f"Held: **{avail_shares:,.2f}** shares (Cost Basis: **${cost_basis_each:.2f}**)")
            with c_s2:
                sell_shares = st.number_input("Shares to Sell:", min_value=0.01, max_value=avail_shares, value=min(10.0, avail_shares), step=1.0, key="sell_sh_in")
            with c_s3:
                sell_price = st.number_input("Sale Execution Price ($):", min_value=0.01, value=cost_basis_each, step=5.0, key="sell_px_in")
            with c_s4:
                st.write("")
                st.write("")
                credit_cash = st.checkbox("Credit Proceeds to Cash", value=True, key="chk_credit_cash")
                if st.button("Confirm Sell Order", key="btn_confirm_sell"):
                    proceeds = sell_shares * sell_price
                    realized_pnl = (sell_price - cost_basis_each) * sell_shares
                    remaining_sh = avail_shares - sell_shares

                    if remaining_sh <= 0.0001:
                        del positions[sell_ticker]
                    else:
                        positions[sell_ticker]["shares"] = remaining_sh

                    if credit_cash:
                        current_portfolio["cash"] = cash + proceeds

                    persist_portfolio(portfolio_data)
                    st.success(f"Sold {sell_shares:,.2f} of {sell_ticker} at ${sell_price:.2f}. Realized P&L: ${realized_pnl:+,.2f}.")
                    st.rerun()
        else:
            st.info("No active positions available to sell.")

    with trade_tab_close:
        if positions:
            c_cl1, c_cl2 = st.columns([2, 2])
            with c_cl1:
                close_ticker = st.selectbox("Position to Liquidate (100%):", options=list(positions.keys()), key="close_tick_in")
                c_sh = float(positions[close_ticker].get("shares", 0.0))
                c_cost = float(positions[close_ticker].get("avg_cost", 0.0))
                st.caption(f"Currently holding: **{c_sh:,.2f}** shares")
            with c_cl2:
                st.write("")
                st.write("")
                if st.button(f"🚨 Liquidate Entire {close_ticker} Position"):
                    # Pull live price to calculate proceeds
                    stk = yf.Ticker(close_ticker)
                    fast = getattr(stk, "fast_info", None)
                    p = getattr(fast, "last_price", None)
                    if p is None:
                        try:
                            h = stk.history(period="1d")
                            p = float(h['Close'].iloc[-1]) if not h.empty else c_cost
                        except Exception:
                            p = c_cost

                    total_proceeds = c_sh * float(p)
                    current_portfolio["cash"] = cash + total_proceeds
                    del positions[close_ticker]
                    persist_portfolio(portfolio_data)
                    st.success(f"Closed out {close_ticker}. Deposited ${total_proceeds:,.2f} back into Cash.")
                    st.rerun()
        else:
            st.info("No positions currently held to liquidate.")

    st.markdown("---")

    # --- CASH MANAGEMENT ---
    with st.expander("💵 Adjust Cash Balance Directly", expanded=False):
        c_cash1, c_cash2 = st.columns([2, 4])
        with c_cash1:
            new_cash = st.number_input(f"Cash Reserve for '{active_profile}' ($):", min_value=0.0, value=cash, step=500.0)
            if new_cash != cash:
                current_portfolio["cash"] = float(new_cash)
                persist_portfolio(portfolio_data)
                st.rerun()

    # --- PORTFOLIO VALUATION ENGINE ---
    portfolio_rows = []
    total_market_val = 0.0
    total_cost_basis = 0.0
    total_annual_dividends = 0.0

    if positions:
        for ticker, pos in positions.items():
            sh = float(pos.get("shares", 0))
            cost = float(pos.get("avg_cost", 0))
            cost_val = sh * cost

            # Live price extraction with resilient fallback
            stk = yf.Ticker(ticker)
            fast = getattr(stk, "fast_info", None)
            cur_p = None
            if fast is not None:
                try:
                    cur_p = getattr(fast, "last_price", None)
                except Exception:
                    pass
            
            if cur_p is None:
                try:
                    hist = stk.history(period="5d")
                    cur_p = float(hist['Close'].iloc[-1]) if not hist.empty else cost
                except Exception:
                    cur_p = cost

            market_val = sh * cur_p
            unrealized_gain = market_val - cost_val
            gain_pct = (unrealized_gain / cost_val) * 100 if cost_val > 0 else 0.0

            # Dividend calculation
            try:
                info = stk.info or {}
            except Exception:
                info = {}
            div_rate, div_yield = get_dividend_metrics(info, cur_p)
            annual_div_income = sh * div_rate

            total_market_val += market_val
            total_cost_basis += cost_val
            total_annual_dividends += annual_div_income

            portfolio_rows.append({
                "Ticker": ticker,
                "Shares": sh,
                "Avg Cost": f"${cost:,.2f}",
                "Current Price": f"${cur_p:,.2f}",
                "Cost Basis": cost_val,
                "Market Value": market_val,
                "P&L ($)": unrealized_gain,
                "Return (%)": gain_pct,
                "Div Yield (%)": div_yield,
                "Annual Divs ($)": annual_div_income
            })

    total_portfolio_worth = total_market_val + current_portfolio.get("cash", 0.0)
    total_pnl = total_market_val - total_cost_basis
    overall_return = (total_pnl / total_cost_basis) * 100 if total_cost_basis > 0 else 0.0
    portfolio_yield = (total_annual_dividends / total_market_val) * 100 if total_market_val > 0 else 0.0

    # --- TOP LEVEL METRICS BAR ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Portfolio Value", f"${total_portfolio_worth:,.2f}", help="Total equity value + Cash reserve.")
    m2.metric("Unrealized P&L", f"${total_pnl:+,.2f}", f"{overall_return:+.2f}%")
    m3.metric("Annual Dividend Income", f"${total_annual_dividends:,.2f}", f"{portfolio_yield:.2f}% Yield")
    m4.metric("Cash Reserve", f"${current_portfolio.get('cash', 0.0):,.2f}")

    # --- HOLDINGS TABLE & PIE CHART ---
    if portfolio_rows:
        df_display = pd.DataFrame(portfolio_rows)

        col_table, col_pie = st.columns([3, 2])

        with col_table:
            st.markdown(f"#### 📋 Current Holdings ({active_profile})")
            formatted_df = pd.DataFrame({
                "Ticker": df_display["Ticker"],
                "Shares": df_display["Shares"].map("{:,.2f}".format),
                "Avg Cost": df_display["Avg Cost"],
                "Price": df_display["Current Price"],
                "Market Value": df_display["Market Value"].map("${:,.2f}".format),
                "Unrealized P&L": df_display["P&L ($)"].map("${:+,.2f}".format),
                "Gain/Loss": df_display["Return (%)"].map("{:+.2f}%".format),
                "Annual Div": df_display["Annual Divs ($)"].map("${:,.2f}".format)
            })
            st.dataframe(formatted_df, width="stretch", hide_index=True)

        with col_pie:
            st.markdown("#### 🥧 Asset Allocation")
            pie_data = [{"Asset": r["Ticker"], "Value": r["Market Value"]} for r in portfolio_rows]
            if current_portfolio.get("cash", 0.0) > 0:
                pie_data.append({"Asset": "Cash", "Value": current_portfolio.get("cash", 0.0)})

            pie_df = pd.DataFrame(pie_data)
            fig_pie = px.pie(
                pie_df,
                names="Asset",
                values="Value",
                hole=0.45,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_pie.update_layout(
                paper_bgcolor='#090d16',
                plot_bgcolor='#0f172a',
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, width="stretch")
    else:
        st.info(f"No positions open in '{active_profile}'. Use the Buy desk above to add your first position.")