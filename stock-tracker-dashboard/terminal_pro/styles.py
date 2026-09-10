"""
styles.py - Emerald Neon & Deep Slate Dark Terminal Theme with Pulse Animations
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

/* --- THE ORIGINAL EMERALD HERO BANNER --- */
.hero-banner {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.16) 0%, rgba(6, 78, 59, 0.28) 50%, rgba(11, 17, 30, 0.95) 100%) !important;
    border: 1px solid #059669 !important;
    border-radius: 12px !important;
    padding: 20px 24px !important;
    margin-bottom: 24px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15), inset 0 1px 1px rgba(52, 211, 153, 0.2) !important;
}

.hero-left {
    display: flex;
    flex-direction: column;
}

.hero-title-row {
    display: flex;
    align-items: center;
    gap: 14px;
}

.hero-title {
    color: #34d399 !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase;
    margin: 0 !important;
    line-height: 1.1 !important;
}

.hero-subtitle {
    color: #94a3b8 !important;
    font-size: 13px !important;
    margin-top: 6px !important;
    margin-bottom: 0 !important;
}

/* Status Pill with Heartbeat */
.engine-status-pill {
    background-color: rgba(6, 78, 59, 0.4) !important;
    border: 1px solid #10b981 !important;
    border-radius: 9999px !important;
    padding: 6px 14px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #a7f3d0 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    letter-spacing: 0.02em;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}

/* Pulse Heartbeat Animation */
@keyframes green-heartbeat {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        transform: scale(1.15);
        box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.engine-pulse-dot {
    width: 10px;
    height: 10px;
    background-color: #10b981;
    border-radius: 50%;
    animation: green-heartbeat 1.8s infinite cubic-bezier(0.45, 0, 0.55, 1);
}

.big-pulse-circle {
    width: 22px;
    height: 22px;
    background: radial-gradient(circle, #34d399 30%, #059669 80%);
    border-radius: 50%;
    animation: green-heartbeat 1.6s infinite ease-in-out;
    box-shadow: 0 0 12px #10b981;
}

/* Cards & Containers */
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

/* Responsive Metric Values */
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
    """Injects the restored Green Terminal styling and heartbeat animations into Streamlit."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)