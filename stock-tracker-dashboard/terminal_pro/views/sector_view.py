import streamlit as st
import plotly.express as px

def render_sector_tab(df_metrics):
    st.markdown("### 🍰 Sector Allocation & Risk Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        if "Sector" in df_metrics.columns and not df_metrics.empty:
            fig_pie = px.pie(
                df_metrics, 
                names="Sector", 
                title="Watchlist Sector Allocation", 
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.Greens
            )
            fig_pie.update_layout(paper_bgcolor='#090d16', plot_bgcolor='#0f172a')
            st.plotly_chart(fig_pie, width="stretch")

    with col2:
        if "Beta (5Y)" in df_metrics.columns and not df_metrics.empty:
            fig_beta = px.bar(
                df_metrics, 
                x="Ticker", 
                y="Beta (5Y)", 
                color="Sector", 
                title="5Y Beta Volatility Score", 
                template="plotly_dark"
            )
            fig_beta.update_layout(paper_bgcolor='#090d16', plot_bgcolor='#0f172a')
            st.plotly_chart(fig_beta, width="stretch")