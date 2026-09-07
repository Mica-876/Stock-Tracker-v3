"""
styles.py - Emerald Neon & Deep Slate Dark Terminal Theme
"""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* Base Typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .font-mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Background Canvas */
.stApp {
    background-color: #0b0f19 !important;
    color: #f1f5f9 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0d1322 !important;
    border-right: 1px solid #1e293b !important;
}

/* Top Hero Banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
    border-radius: 12px !important;
    padding: 20px 24px !important;
    margin-bottom: 20px !important;
}

.hero-title {
    color: #10b981 !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: 0.03em !important;
    margin: 0 !important;
}

.hero-subtitle {
    color: #94a3b8 !important;
    font-size: 13px !important;
    margin-top: 4px !important;
}

.engine-status-pill {
    background-color: #111e2e !important;
    border: 1px solid rgba(16, 185, 129, 0.4) !important;
    border-radius: 9999px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
    color: #34d399;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.engine-pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
}

/* Cards & Metric Blocks */
.company-card, 
div[data-testid="stMetric"], 
div[data-testid="stContainer"][data-border="true"] {
    background-color: #111827 !important;
    border: 1px solid #1f293d !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    padding: 12px 14px !important;
    overflow: visible !important;
}

/* Responsive Metric Values (Prevents $1.0... Ellipsis Bug) */
div[data-testid="stMetricLabel"] p {
    color: #94a3b8 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: nowrap !important;
    overflow: hidden;
    text-overflow: ellipsis;
}

div[data-testid="stMetricValue"] {
    overflow: visible !important;
}

div[data-testid="stMetricValue"] > div {
    color: #34d399 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: clamp(14px, 1.25vw, 22px) !important;
    letter-spacing: -0.02em;
    white-space: nowrap !important;
    text-overflow: clip !important;
    overflow: visible !important;
    line-height: 1.2 !important;
}

/* Meta Badges */
.meta-tag {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #93c5fd !important;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
    margin-right: 6px;
    margin-bottom: 6px;
}

/* Tab Bar */
div[data-testid="stTabs"] {
    border-bottom: 1px solid #1f293d !important;
    margin-bottom: 20px;
}

button[data-baseweb="tab"] {
    color: #94a3b8 !important;
    border: none !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
}

button[data-baseweb="tab"]:hover {
    color: #f8fafc !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #34d399 !important;
    border-bottom: 2px solid #10b981 !important;
}

/* Form Inputs */
input, select, div[data-baseweb="select"] {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    color: #f8fafc !important;
    border-radius: 6px !important;
}

/* Green Action Buttons */
.stButton > button {
    background: linear-gradient(180deg, #059669 0%, #047857 100%) !important;
    border: 1px solid #10b981 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 6px 18px !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.5) !important;
    transform: translateY(-1px);
}

/* Dividers */
hr {
    border: 0 !important;
    height: 1px !important;
    background: #1e293b !important;
    margin: 28px 0 !important;
}
</style>
"""

def apply_custom_css():
    """Injects the restored Green Terminal styling into Streamlit."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)