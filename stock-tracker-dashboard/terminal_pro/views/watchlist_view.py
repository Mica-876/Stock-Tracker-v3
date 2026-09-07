import streamlit as st

def render_watchlist_tab(df_metrics):
    col_hdr1, col_hdr2 = st.columns([4, 1])
    with col_hdr1:
        st.markdown("### 📊 Watchlist Fundamentals Table")
    with col_hdr2:
        st.download_button(
            label="📥 Export CSV",
            data=df_metrics.to_csv(index=False),
            file_name="watchlist_metrics.csv",
            mime="text/csv",
            width="stretch"
        )

    view_mode = st.radio("Display Grouping:", ["Grouped by Sector", "Combined Table"], horizontal=True)

    if view_mode == "Combined Table":
        st.dataframe(df_metrics, width="stretch", hide_index=True)
    else:
        unique_sectors = df_metrics["Sector"].unique() if "Sector" in df_metrics.columns else []
        for sector in sorted(unique_sectors):
            st.markdown(f"#### 🏷️ {sector}")
            sector_df = df_metrics[df_metrics["Sector"] == sector].drop(columns=["Sector"])
            st.dataframe(sector_df, width="stretch", hide_index=True)