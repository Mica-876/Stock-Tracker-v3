import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #090d16; color: #e2e8f0; }
        @keyframes heartbeat {
            0% { transform: scale(1); opacity: 0.7; }
            14% { transform: scale(1.3); opacity: 1; filter: drop-shadow(0 0 6px #10b981); }
            28% { transform: scale(1); opacity: 0.7; }
            42% { transform: scale(1.3); opacity: 1; filter: drop-shadow(0 0 6px #10b981); }
            70% { transform: scale(1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 0.7; }
        }
        .heartbeat-pulse {
            display: inline-block;
            color: #10b981;
            font-size: 16px;
            animation: heartbeat 1.8s infinite ease-in-out;
            margin-right: 6px;
        }
        .sync-status {
            background: #0f172a;
            border: 1px solid #059669;
            border-radius: 20px;
            padding: 4px 14px;
            display: inline-flex;
            align-items: center;
            font-size: 13px;
            color: #10b981;
            font-weight: 600;
        }
        .company-card {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-left: 4px solid #10b981;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .company-card h3 {
            color: #34d399 !important;
            margin-top: 0;
            margin-bottom: 6px;
            font-size: 22px;
        }
        .company-card .meta-tag {
            display: inline-block;
            background-color: #1e293b;
            color: #a7f3d0;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 8px;
            margin-bottom: 12px;
        }
        .company-card p {
            color: #cbd5e1;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 0;
        }
        section[data-testid="stSidebar"] {
            background-color: #0b1320;
            border-right: 1px solid #1e293b;
        }
        .sidebar-widget {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
        }
        .sidebar-widget-title {
            color: #10b981;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        div[data-testid="stMetric"] {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-left: 4px solid #10b981;
            padding: 14px 18px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
        div[data-testid="stMetric"] label { color: #94a3b8 !important; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #34d399 !important;
            font-weight: 700;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid #1e293b;
        }
        .stTabs [data-baseweb="tab"] {
            height: 46px;
            background-color: #0f172a;
            color: #94a3b8;
            border-radius: 6px 6px 0px 0px;
            padding: 8px 18px;
            font-weight: 600;
            border: 1px solid #1e293b;
            border-bottom: none;
        }
        .stTabs [aria-selected="true"] {
            background-color: #059669 !important;
            color: #ffffff !important;
            border-color: #059669 !important;
        }
        .app-header {
            background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
            border: 1px solid #059669;
            color: #ffffff;
            padding: 20px 28px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .app-header h1 {
            color: #34d399 !important;
            font-weight: 800;
            font-size: 26px;
            margin: 0 0 4px 0;
        }
        .app-header p {
            color: #a7f3d0;
            font-size: 13px;
            margin: 0;
        }
        .stButton>button {
            background-color: #059669;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .stButton>button:hover {
            background-color: #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)