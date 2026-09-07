"""
styles.py - Obsidian, Brushed Chrome & Liquid Silver Theme
"""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Font & Canvas */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .font-mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Base Canvas & Backgrounds */
.stApp {
    background: radial-gradient(circle at 50% -10%, #171c24 0%, #0c0e12 60%, #060709 100%) !important;
    color: #e2e8f0 !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1217 0%, #08090c 100%) !important;
    border-right: 1px solid rgba(203, 213, 225, 0.12) !important;
}

section[data-testid="stSidebar"] .stMarkdown h1, 
section[data-testid="stSidebar"] .stMarkdown h2, 
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #f8fafc !important;
    letter-spacing: -0.01em;
}

/* Top Hero Banner Transformation */
div[data-testid="stVerticalBlock"] > div:has(.hero-banner) {
    background: transparent !important;
}

.hero-banner {
    background: linear-gradient(135deg, rgba(30, 36, 48, 0.7) 0%, rgba(15, 18, 24, 0.85) 100%) !important;
    border: 1px solid rgba(203, 213, 225, 0.22) !important;
    border-radius: 10px !important;
    padding: 18px 24px !important;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(14px);
    margin-bottom: 20px;
}

.hero-title {
    background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase;
    margin: 0 !important;
}

.hero-subtitle {
    color: #94a3b8 !important;
    font-size: 13px !important;
    margin-top: 4px !important;
    font-weight: 400;
}

.engine-status-pill {
    background: linear-gradient(180deg, #1c222c 0%, #10141a 100%) !important;
    border: 1px solid rgba(203, 213, 225, 0.25) !important;
    border-radius: 9999px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
    color: #e2e8f0;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 2px 6px rgba(0,0,0,0.4);
}

.engine-pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #38bdf8;
    border-radius: 50%;
    box-shadow: 0 0 10px #38bdf8, 0 0 4px #ffffff;
}

/* Chrome Glass Cards & Containers */
.company-card, 
div[data-testid="stMetric"], 
div[data-testid="stContainer"][data-border="true"] {
    background: linear-gradient(180deg, rgba(22, 27, 36, 0.75) 0%, rgba(12, 15, 20, 0.85) 100%) !important;
    border: 1px solid rgba(203, 213, 225, 0.16) !important;
    border-radius: 10px !important;
    box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(12px) !important;
    padding: 16px !important;
}

/* Metrics Typography */
div[data-testid="stMetricLabel"] p {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

div[data-testid="stMetricValue"] div {
    color: #f8fafc !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

/* Brushed Chrome Metal Badges */
.meta-tag {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
    border: 1px solid rgba(203, 213, 225, 0.22) !important;
    color: #cbd5e1 !important;
    border-radius: 5px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    display: inline-block;
    margin-right: 6px;
    margin-bottom: 6px;
}

/* Navigation Tabs */
div[data-testid="stTabs"] {
    border-bottom: 1px solid rgba(203, 213, 225, 0.12) !important;
    margin-bottom: 20px;
}

button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #94a3b8 !important;
    border: none !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"]:hover {
    color: #f1f5f9 !important;
    border-bottom: 2px solid rgba(203, 213, 225, 0.4) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid #e2e8f0 !important;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

/* Dataframe / Table Overrides */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(203, 213, 225, 0.15) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
}

/* Form Controls & Inputs */
input, select, div[data-baseweb="select"] {
    background-color: #12151b !important;
    border: 1px solid rgba(203, 213, 225, 0.2) !important;
    color: #f8fafc !important;
    border-radius: 6px !important;
}

input:focus, div[data-baseweb="select"]:focus-within {
    border-color: #cbd5e1 !important;
    box-shadow: 0 0 8px rgba(203, 213, 225, 0.3) !important;
}

/* Chrome Metal Buttons */
.stButton > button {
    background: linear-gradient(180deg, #2b323f 0%, #171b23 100%) !important;
    border: 1px solid rgba(203, 213, 225, 0.3) !important;
    color: #f1f5f9 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    padding: 6px 18px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.12) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    border-color: #e2e8f0 !important;
    color: #ffffff !important;
    box-shadow: 0 0 14px rgba(203, 213, 225, 0.35), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(1px);
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.6) !important;
}

/* Section Dividers */
hr {
    border: 0 !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(203, 213, 225, 0.2), transparent) !important;
    margin: 28px 0 !important;
}
</style>
"""

def apply_custom_css():
    """Injects the Obsidian, Chrome and Silver custom styling into Streamlit."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)