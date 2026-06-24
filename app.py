"""
═════════════════════════════════════════════════════════════════
Delhi Air Quality Intelligence Platform
Downstream Application — Team Matatizo
═════════════════════════════════════════════════════════════════
Built on top of the cleaned dataset from Milestones 1–3:
    1. AQI Dashboard
    2. PM2.5 Forecasting Model
    3. Air Quality Alert System
    4. Health Advisory Report Generator
═════════════════════════════════════════════════════════════════
Run locally:    streamlit run app.py
Deploy:         Push to GitHub → Streamlit Cloud → connect repo
═════════════════════════════════════════════════════════════════
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
from pathlib import Path

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Delhi Air Quality Intelligence",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif !important;
    }

    .main-header {
        font-family: 'Outfit', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        padding: 0;
        margin-bottom: 0;
        background: linear-gradient(90deg, #1B8A9E 0%, #17A2B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-family: 'Outfit', sans-serif;
        color: #1B8A9E;
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }
    .feature-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-left: 4px solid #1B8A9E;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: #1B8A9E;
        box-shadow: 0 8px 30px rgba(27, 138, 158, 0.18);
    }
    .aqi-good     { background:#2D9C6F; color:white; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-block; box-shadow: 0 2px 4px rgba(45,156,111,0.2); }
    .aqi-satisf   { background:#A8D88B; color:#0F2A3D; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-block; box-shadow: 0 2px 4px rgba(168,216,139,0.2); }
    .aqi-moderate { background:#F1C40F; color:#0F2A3D; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-block; box-shadow: 0 2px 4px rgba(241,196,15,0.2); }
    .aqi-poor     { background:#E67E22; color:white; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-block; box-shadow: 0 2px 4px rgba(230,126,34,0.2); }
    .aqi-vpoor    { background:#E74C3C; color:white; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-block; box-shadow: 0 2px 4px rgba(231,76,60,0.2); }
    .aqi-severe   { background:#922B21; color:white; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-block; box-shadow: 0 2px 4px rgba(146,43,33,0.2); }
    
    div[data-testid="metric-container"] {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        border-top: 4px solid #1B8A9E !important;
        padding: 18px 22px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px) !important;
        border-color: #1B8A9E !important;
        box-shadow: 0 8px 30px rgba(27, 138, 158, 0.18) !important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] > div, div[data-testid="stMetricLabel"] * {
        color: var(--text-color) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        opacity: 0.8;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] > div, div[data-testid="stMetricValue"] * {
        color: var(--text-color) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricDelta"], div[data-testid="stMetricDelta"] > div, div[data-testid="stMetricDelta"] * {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Flowchart layout */
    .flow-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 24px 0;
        width: 100%;
    }
    .flow-step {
        display: flex;
        align-items: center;
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 14px;
        padding: 16px 20px;
        width: 100%;
        max-width: 600px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
    }
    .flow-step:hover {
        transform: translateY(-2px);
        border-color: #1B8A9E;
    }
    .flow-badge {
        background-color: #1B8A9E;
        color: white;
        font-weight: 700;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 18px;
        flex-shrink: 0;
        box-shadow: 0 2px 6px rgba(27, 138, 158, 0.3);
    }
    .flow-content {
        flex-grow: 1;
    }
    .flow-content strong {
        font-size: 1.05rem;
        color: var(--text-color);
        display: block;
    }
    .flow-content p {
        margin: 4px 0 0 0;
        font-size: 0.88rem;
        opacity: 0.8;
        color: var(--text-color);
        line-height: 1.4;
    }
    .flow-arrow {
        font-size: 1.6rem;
        color: #1B8A9E;
        margin: 6px 0;
        font-weight: bold;
        text-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .highlight-step {
        border: 2px solid #1B8A9E;
        background: linear-gradient(90deg, rgba(27,138,158,0.05) 0%, rgba(23,162,184,0.05) 100%);
    }
    .highlight-badge {
        background: linear-gradient(135deg, #1B8A9E 0%, #17A2B8 100%);
    }
    
    /* Alert details */
    .alert-banner {
        padding: 16px;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-left: 5px solid #1B8A9E;
        border-radius: 12px;
        margin-top: 24px;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }

    /* Sidebar Custom Radio Icons (replacing emojis with SVGs) */
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        padding-left: 28px !important;
        position: relative;
        display: inline-flex;
        align-items: center;
        min-height: 22px;
    }
    
    div[data-testid="stRadio"] label:nth-of-type(1) div[data-testid="stMarkdownContainer"] p::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 18px;
        height: 18px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%231B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>');
        background-repeat: no-repeat;
        background-size: contain;
    }
    div[data-testid="stRadio"] label:nth-of-type(2) div[data-testid="stMarkdownContainer"] p::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 18px;
        height: 18px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%231B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>');
        background-repeat: no-repeat;
        background-size: contain;
    }
    div[data-testid="stRadio"] label:nth-of-type(3) div[data-testid="stMarkdownContainer"] p::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 18px;
        height: 18px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%231B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5 5 3Z"/><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1 1-2.5Z"/></svg>');
        background-repeat: no-repeat;
        background-size: contain;
    }
    div[data-testid="stRadio"] label:nth-of-type(4) div[data-testid="stMarkdownContainer"] p::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 18px;
        height: 18px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%231B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/><path d="M22 8h-2M2 8h2M12 2v2"/></svg>');
        background-repeat: no-repeat;
        background-size: contain;
    }
    div[data-testid="stRadio"] label:nth-of-type(5) div[data-testid="stMarkdownContainer"] p::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 18px;
        height: 18px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%231B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>');
        background-repeat: no-repeat;
        background-size: contain;
    }
    div[data-testid="stRadio"] label:nth-of-type(6) div[data-testid="stMarkdownContainer"] p::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 18px;
        height: 18px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%231B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>');
        background-repeat: no-repeat;
        background-size: contain;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(128, 128, 128, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(128, 128, 128, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────
DATA = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    daily       = pd.read_parquet(DATA / "daily_pollutants.parquet")
    daily_w     = pd.read_parquet(DATA / "daily_weather.parquet")
    stations    = pd.read_parquet(DATA / "stations.parquet")
    st_pol      = pd.read_parquet(DATA / "station_pollutant.parquet")
    hourly      = pd.read_parquet(DATA / "hourly.parquet")
    monthly     = pd.read_parquet(DATA / "monthly.parquet")
    with open(DATA / "stats.json") as f:
        stats = json.load(f)
    daily["date"]   = pd.to_datetime(daily["date"])
    daily_w["date"] = pd.to_datetime(daily_w["date"])
    return daily, daily_w, stations, st_pol, hourly, monthly, stats

daily, daily_w, stations, st_pol, hourly, monthly, stats = load_data()

# ── HELPER FUNCTIONS ─────────────────────────────────────────
def pm25_to_aqi_category(v):
    if pd.isna(v):  return ("Unknown", "#888")
    if v <= 30:     return ("Good", "#2D9C6F")
    if v <= 60:     return ("Satisfactory", "#A8D88B")
    if v <= 90:     return ("Moderate", "#F1C40F")
    if v <= 120:    return ("Poor", "#E67E22")
    if v <= 250:    return ("Very Poor", "#E74C3C")
    return ("Severe", "#922B21")

def category_css_class(cat):
    return {
        "Good": "aqi-good", "Satisfactory": "aqi-satisf",
        "Moderate": "aqi-moderate", "Poor": "aqi-poor",
        "Very Poor": "aqi-vpoor", "Severe": "aqi-severe"
    }.get(cat, "aqi-moderate")

def health_advice(cat):
    return {
        "Good": "Air quality is satisfactory and poses little to no risk. Outdoor activities are safe for everyone.",
        "Satisfactory": "Air quality is acceptable. Unusually sensitive individuals may experience minor breathing discomfort.",
        "Moderate": "People with respiratory conditions (asthma, COPD) may experience breathing discomfort. Limit prolonged outdoor exertion.",
        "Poor": "Most people may experience breathing discomfort on prolonged exposure. Sensitive groups should avoid outdoor activities.",
        "Very Poor": "Significant health impact on prolonged exposure. Avoid outdoor exertion. Wear N95 masks outdoors.",
        "Severe": "Serious health risk for the entire population. Stay indoors, use air purifiers, avoid all outdoor activities."
    }.get(cat, "")

# ── SIDEBAR NAVIGATION ───────────────────────────────────────
logo_path = Path(__file__).parent / "logo.png"
if logo_path.exists():
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        st.image(str(logo_path), width=55)
    with col2:
        st.markdown("<h2 style='margin:0; padding-top:8px; font-size:1.35rem; color:inherit;'>Delhi AQI</h2>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 10px; margin-bottom: 20px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"></path><path d="M8 12h.01"></path><path d="M12 12h.01"></path><path d="M16 12h.01"></path><path d="M8 16h.01"></path><path d="M12 16h.01"></path><path d="M16 16h.01"></path></svg>
        <span style="font-size: 1.45rem; font-weight: 700; color: inherit; vertical-align: middle;">Delhi AQI Platform</span>
    </div>
    """, unsafe_allow_html=True)
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Home",
     "AQI Dashboard",
     "PM2.5 Forecaster",
     "Alert System",
     "Health Advisory",
     "About"],
    label_visibility="collapsed"
)
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Dataset**
- Stations: **{stats['stations']}**
- Pollutants: **{stats['pollutants']}**
- Rows: **{stats['total_rows']:,}**
- Period: **{stats['date_min']} → {stats['date_max']}**
""")
st.sidebar.markdown("---")
st.sidebar.markdown("**Team Matatizo**")
st.sidebar.caption("Anuj Gautam · Ismail · Nassir")
st.sidebar.caption("[GitHub Repo](https://github.com/AnujGautam07/Delhi-Air-Quality-Analysis)")


# ═════════════════════════════════════════════════════════════
# PAGE: HOME
# ═════════════════════════════════════════════════════════════
if page == "Home":
    st.markdown('''
    <h1 class="main-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 12px;"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"></path><path d="M8 12h.01"></path><path d="M12 12h.01"></path><path d="M16 12h.01"></path><path d="M8 16h.01"></path><path d="M12 16h.01"></path><path d="M16 16h.01"></path></svg>
        Delhi Air Quality Intelligence Platform
    </h1>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Downstream application built on the Team Matatizo data engineering pipeline (2024–2025)</p>', unsafe_allow_html=True)
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{stats['total_rows']:,}", "10.4 million")
    c2.metric("Mean PM2.5", f"{stats['mean_pm25']} µg/m³", f"{(stats['mean_pm25']/25):.1f}× WHO guideline", delta_color="inverse")
    c3.metric("Mean PM10", f"{stats['mean_pm10']} µg/m³", "Most abundant pollutant")
    c4.metric("Monitoring Stations", f"{stats['stations']}", f"{stats['pollutants']} pollutants")

    st.markdown("### What this platform does")
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px; color: inherit;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                <span>AQI Dashboard</span>
            </h4>
            <p style="margin: 0; color: inherit; opacity: 0.85; font-size: 0.95rem; line-height: 1.5;">Interactive exploration of pollution levels across all 17 Delhi stations. Filter by date range, station, and pollutant. Compare trends over time.</p>
        </div>
        <div class="feature-card">
            <h4 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px; color: inherit;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5 5 3Z"></path><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1 1-2.5Z"></path></svg>
                <span>PM2.5 Forecaster</span>
            </h4>
            <p style="margin: 0; color: inherit; opacity: 0.85; font-size: 0.95rem; line-height: 1.5;">Predict next-day air quality using a regression model trained on weather + historical pollution. Enter weather conditions and get a forecast.</p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px; color: inherit;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path><path d="M22 8h-2M2 8h2M12 2v2"></path></svg>
                <span>Alert System</span>
            </h4>
            <p style="margin: 0; color: inherit; opacity: 0.85; font-size: 0.95rem; line-height: 1.5;">Real-time-style alerts when PM2.5 crosses CPCB thresholds. View which stations are currently in "Severe" or "Very Poor" category.</p>
        </div>
        <div class="feature-card">
            <h4 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px; color: inherit;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
                <span>Health Advisory Report</span>
            </h4>
            <p style="margin: 0; color: inherit; opacity: 0.85; font-size: 0.95rem; line-height: 1.5;">Generate a personalised health advisory report for any date range, location, and sensitivity level (general public vs sensitive groups).</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h3 style='text-align: center; margin-bottom: 24px; color: inherit;'>How the data engineering pipeline flows</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class="flow-container">
        <div class="flow-step">
            <div class="flow-badge">1</div>
            <div class="flow-content">
                <strong>Raw Parquet Ingest</strong>
                <p>100 MB dataset with 10.4 Million rows of hourly air quality records across Delhi.</p>
            </div>
        </div>
        <div class="flow-arrow">↓</div>
        <div class="flow-step">
            <div class="flow-badge">2</div>
            <div class="flow-content">
                <strong>Milestone 1: Data Partitioning</strong>
                <p>Splitting large dataset into 219 monthly CSV files for distributed and incremental processing.</p>
            </div>
        </div>
        <div class="flow-arrow">↓</div>
        <div class="flow-step">
            <div class="flow-badge">3</div>
            <div class="flow-content">
                <strong>Milestone 2: PostgreSQL Relational Database</strong>
                <p>Normalizing data into 3NF schema across 4 tables to maintain relational integrity and fast queries.</p>
            </div>
        </div>
        <div class="flow-arrow">↓</div>
        <div class="flow-step">
            <div class="flow-badge">4</div>
            <div class="flow-content">
                <strong>Milestone 3: Cleaning & Transformation</strong>
                <p>Outlier removal, timezone normalization, missing value imputation, and diurnal aggregations.</p>
            </div>
        </div>
        <div class="flow-arrow">↓</div>
        <div class="flow-step highlight-step">
            <div class="flow-badge highlight-badge">★</div>
            <div class="flow-content">
                <strong>Streamlit Platform (This App)</strong>
                <p>Interactive analytics dashboard, predictive forecaster, real-time alert system, and health report engine.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# PAGE: AQI DASHBOARD
# ═════════════════════════════════════════════════════════════
elif page == "AQI Dashboard":
    st.markdown('''
    <h1 class="main-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 12px;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
        AQI Dashboard
    </h1>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Explore pollution levels across stations and time</p>', unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        station_options = ["All Stations"] + sorted(stations["station_name"].tolist())
        sel_station = st.selectbox("Select Station", station_options)
    with fc2:
        pollutant_options = sorted(daily["pollutant"].unique())
        sel_pollutant = st.selectbox("Select Pollutant", pollutant_options, index=pollutant_options.index("pm25"))
    with fc3:
        date_range = st.date_input(
            "Date Range",
            value=(daily["date"].min().date(), daily["date"].max().date()),
            min_value=daily["date"].min().date(),
            max_value=daily["date"].max().date(),
        )

    # Apply filters
    filt = daily[daily["pollutant"] == sel_pollutant].copy()
    if sel_station != "All Stations":
        filt = filt[filt["station_name"] == sel_station]
    if len(date_range) == 2:
        filt = filt[(filt["date"] >= pd.to_datetime(date_range[0])) &
                    (filt["date"] <= pd.to_datetime(date_range[1]))]

    if filt.empty:
        st.warning("No data for the selected filters.")
    else:
        # Stats cards
        avg_val = filt["value"].mean()
        max_val = filt["value"].max()
        min_val = filt["value"].min()
        cat, color = pm25_to_aqi_category(avg_val) if sel_pollutant == "pm25" else (None, None)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Average", f"{avg_val:.1f} µg/m³")
        m2.metric("Maximum", f"{max_val:.1f} µg/m³")
        m3.metric("Minimum", f"{min_val:.1f} µg/m³")
        if sel_pollutant == "pm25":
            m4.markdown(f"**Avg AQI:**<br><span class='{category_css_class(cat)}'>{cat}</span>", unsafe_allow_html=True)
        else:
            m4.metric("Days", f"{filt['date'].nunique():,}")

        # Time series
        st.markdown("#### Daily Trend")
        agg = filt.groupby("date")["value"].mean().reset_index()
        fig = px.line(agg, x="date", y="value",
                      labels={"value": f"{sel_pollutant.upper()} concentration", "date": ""})
        fig.update_traces(line=dict(color="#1B8A9E", width=2))
        if sel_pollutant == "pm25":
            fig.add_hline(y=60, line_dash="dash", line_color="#E67E22",
                          annotation_text="Poor (60)", annotation_position="right")
            fig.add_hline(y=120, line_dash="dash", line_color="#E74C3C",
                          annotation_text="Very Poor (120)", annotation_position="right")
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit, sans-serif"))
        st.plotly_chart(fig, use_container_width=True)

        # Two side-by-side
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### By Station (Average)")
            station_avg = filt.groupby("station_name")["value"].mean().sort_values()
            fig2 = go.Figure(go.Bar(
                x=station_avg.values, y=station_avg.index, orientation="h",
                marker_color=["#E74C3C" if v > 120 else "#E67E22" if v > 60 else "#2D9C6F"
                              for v in station_avg.values],
                text=[f"{v:.0f}" for v in station_avg.values], textposition="outside"
            ))
            fig2.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                               xaxis_title=f"{sel_pollutant.upper()} (µg/m³)", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit, sans-serif"))
            st.plotly_chart(fig2, use_container_width=True)

        with col_b:
            st.markdown("#### Diurnal Pattern (Hour of Day)")
            h = hourly[hourly["pollutant"] == sel_pollutant]
            fig3 = px.line(h, x="hour", y="value", markers=True,
                           labels={"value": f"{sel_pollutant.upper()}", "hour": "Hour (IST)"})
            fig3.update_traces(line=dict(color="#1B8A9E", width=2.5))
            fig3.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit, sans-serif"),
                               xaxis=dict(dtick=2))
            st.plotly_chart(fig3, use_container_width=True)


# ═════════════════════════════════════════════════════════════
# PAGE: PM2.5 FORECASTER
# ═════════════════════════════════════════════════════════════
elif page == "PM2.5 Forecaster":
    st.markdown('''
    <h1 class="main-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 12px;"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5 5 3Z"></path><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1 1-2.5Z"></path></svg>
        PM2.5 Forecaster
    </h1>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Predict tomorrow\'s air quality from weather conditions</p>', unsafe_allow_html=True)

    st.markdown("""
    Enter forecasted weather conditions below. The model is a multi-variate linear regression
    trained on the cleaned dataset (weather → PM2.5), capturing the meteorological drivers
    identified in our analysis (wind speed, temperature, humidity, pressure).
    """)

    # Train a simple regression on the fly
    @st.cache_data
    def train_model():
        # Merge daily pollutants (pm25) with daily weather
        pm = daily[daily["pollutant"] == "pm25"].groupby("date")["value"].mean().reset_index()
        wx = daily_w.groupby("date")[["at_c","rh_percent","ws_m_s","bp_mmhg","sr_w_mt2"]].mean().reset_index()
        merged = pm.merge(wx, on="date").dropna()
        merged["month"] = pd.to_datetime(merged["date"]).dt.month
        merged["winter"] = merged["month"].isin([11,12,1,2]).astype(int)

        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_absolute_error
        feats = ["at_c","rh_percent","ws_m_s","bp_mmhg","sr_w_mt2","winter"]
        X = merged[feats].values
        y = merged["value"].values
        # Train/test split (chronological)
        n = len(merged)
        split = int(n * 0.8)
        m = LinearRegression()
        m.fit(X[:split], y[:split])
        pred = m.predict(X[split:])
        r2  = r2_score(y[split:], pred)
        mae = mean_absolute_error(y[split:], pred)
        return m, feats, r2, mae, merged

    model, feats, r2, mae, train_df = train_model()

    # Model performance card
    p1, p2, p3 = st.columns(3)
    p1.metric("Model R²", f"{r2:.3f}", "Test set fit")
    p2.metric("Mean Abs Error", f"{mae:.1f} µg/m³", "Avg prediction error")
    p3.metric("Training Days", f"{len(train_df):,}", "Days used")

    with st.container(border=True):
        st.markdown('''
        <h4 style="margin-top:0; color:#1B8A9E; display: flex; align-items: center; gap: 8px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path></svg>
            <span>Set Forecast Parameters</span>
        </h4>
        ''', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            at_c       = st.slider("Temperature (°C)",            0.0, 50.0, 25.0, 0.5)
            rh_percent = st.slider("Relative Humidity (%)",         0.0, 100.0, 60.0, 1.0)
        with c2:
            ws_m_s     = st.slider("Wind Speed (m/s)",              0.0, 10.0, 1.0, 0.1)
            bp_mmhg    = st.slider("Barometric Pressure (hPa)",   900.0, 1010.0, 960.0, 0.5)
        with c3:
            sr_w_mt2   = st.slider("Solar Radiation (W/m²)",        0.0, 700.0, 100.0, 10.0)
            sel_season = st.selectbox("Season", ["Winter (Nov–Feb)", "Summer (Mar–May)", "Monsoon (Jun–Sep)", "Autumn (Oct)"])
            winter     = (sel_season == "Winter (Nov–Feb)")

    # Predict
    X_new = np.array([[at_c, rh_percent, ws_m_s, bp_mmhg, sr_w_mt2, int(winter)]])
    pred  = float(model.predict(X_new)[0])
    pred  = max(0, pred)
    cat, color = pm25_to_aqi_category(pred)
    advice = health_advice(cat)

    st.markdown("---")
    st.markdown('''
    <h3 style="display: flex; align-items: center; gap: 8px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
        Forecast Result
    </h3>
    ''', unsafe_allow_html=True)
    r1, r2c = st.columns([1, 2])
    with r1:
        st.markdown(f"""
        <div style='background: {color}; color: white; padding: 24px; border-radius: 16px; text-align: center; box-shadow: 0 8px 30px rgba(0,0,0,0.12); border: 1px solid rgba(255,255,255,0.1);'>
            <div style='font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.05em;'>Predicted PM2.5</div>
            <div style='font-size: 52px; font-weight: 800; margin: 6px 0; letter-spacing: -0.02em; text-shadow: 0 2px 4px rgba(0,0,0,0.15);'>{pred:.1f}</div>
            <div style='font-size: 14px; opacity: 0.9;'>µg/m³</div>
            <div style='margin-top: 16px; padding: 8px 16px; background: rgba(255,255,255,0.25); border-radius: 8px; font-weight: 700; font-size: 1.05rem; display: inline-block;'>{cat}</div>
        </div>
        """, unsafe_allow_html=True)
    with r2c:
        st.markdown(f"#### Health Impact: {cat}")
        st.info(advice)
        # Feature importance bar chart
        st.markdown("**Why this forecast?** (Impact of weather parameters on PM2.5):")
        
        coef_df = pd.DataFrame({
            "Feature": ["Temperature", "Humidity", "Wind Speed", "Pressure", "Solar Rad", "Winter"],
            "Coefficient": model.coef_
        }).sort_values("Coefficient", key=abs, ascending=True)
        
        # Color code: green for negative coefficient (reduces pollution), red for positive (increases pollution)
        bar_colors = ["#2D9C6F" if c < 0 else "#E74C3C" for c in coef_df["Coefficient"]]
        
        fig_coef = go.Figure(go.Bar(
            x=coef_df["Coefficient"],
            y=coef_df["Feature"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{c:+.2f}" for c in coef_df["Coefficient"]],
            textposition="outside"
        ))
        fig_coef.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=5, b=5),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit, sans-serif"),
            xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        )
        st.plotly_chart(fig_coef, use_container_width=True)


# ═════════════════════════════════════════════════════════════
# PAGE: ALERT SYSTEM
# ═════════════════════════════════════════════════════════════
elif page == "Alert System":
    st.markdown('''
    <h1 class="main-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 12px;"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path><path d="M22 8h-2M2 8h2M12 2v2"></path></svg>
        Air Quality Alert System
    </h1>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time-style monitoring with configurable thresholds</p>', unsafe_allow_html=True)

    # Get latest 30 days of data
    pm_data = daily[daily["pollutant"] == "pm25"].copy()
    latest_date = pm_data["date"].max()
    recent = pm_data[pm_data["date"] >= latest_date - pd.Timedelta(days=30)]

    # User threshold
    c1, c2 = st.columns([1, 2])
    with c1:
        threshold = st.number_input("Alert Threshold (PM2.5 µg/m³)",
                                     min_value=30, max_value=300, value=120, step=10,
                                     help="Default 120 = CPCB 'Very Poor' threshold")
    with c2:
        st.markdown(f"""
        <div class="alert-banner">
            Current alert level: <strong style="color: #1B8A9E;">{pm25_to_aqi_category(threshold)[0]}</strong>
            — stations exceeding <strong>{threshold} µg/m³</strong> will be flagged below.
        </div>
        """, unsafe_allow_html=True)

    # Latest station averages (last 7 days)
    week = pm_data[pm_data["date"] >= latest_date - pd.Timedelta(days=7)]
    station_latest = week.groupby("station_name")["value"].mean().sort_values(ascending=False)

    # Alert stations
    alerts = station_latest[station_latest > threshold]
    safe   = station_latest[station_latest <= threshold]

    a1, a2, a3 = st.columns(3)
    a1.metric("Stations Above Threshold", len(alerts), f"Threshold: {threshold} µg/m³")
    a2.metric("Stations Below Threshold", len(safe))
    a3.metric("Period", "Last 7 days", str(latest_date.date()))

    st.markdown("---")

    if len(alerts) > 0:
        st.markdown(f'''
        <h3 style="display: flex; align-items: center; gap: 8px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            Active Alerts ({len(alerts)} stations)
        </h3>
        ''', unsafe_allow_html=True)
        for sname, val in alerts.items():
            cat, color = pm25_to_aqi_category(val)
            st.markdown(f"""
            <div style='background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-left: 5px solid {color}; padding: 14px 18px;
                        margin-bottom: 10px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);
                        display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='font-weight: 600; font-size: 1.05rem; color: var(--text-color);'>{sname}</div>
                    <div style='color: var(--text-color); opacity: 0.85; font-size: 13px; margin-top: 3px;'>Category: <strong style='color:{color};'>{cat}</strong></div>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 26px; font-weight: 700; color: {color};'>{val:.1f}</div>
                    <div style='font-size: 12px; color: var(--text-color); opacity: 0.6;'>µg/m³ (7-day avg)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(f"No stations currently exceed {threshold} µg/m³")

    # Safe stations
    if len(safe) > 0:
        with st.expander(f"Stations Below Threshold ({len(safe)})", expanded=False):
            badge_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;'>"
            for sname, val in safe.items():
                cat, color = pm25_to_aqi_category(val)
                badge_html += f"""
                <div style='background: rgba(128,128,128,0.08); border: 1px solid rgba(128,128,128,0.15); border-radius: 8px; padding: 6px 12px; display: inline-flex; align-items: center; gap: 8px;'>
                    <span style='width: 8px; height: 8px; border-radius: 50%; background: {color}; display: inline-block;'></span>
                    <span style='font-weight: 600; color: var(--text-color); font-size: 0.88rem;'>{sname}</span>
                    <span style='color: var(--text-color); opacity: 0.6; font-size: 0.8rem;'>{val:.1f}</span>
                </div>
                """
            badge_html += "</div>"
            st.markdown(badge_html, unsafe_allow_html=True)

    # 30-day trend chart for top 5 worst stations
    st.markdown("---")
    st.markdown('''
    <h3 style="display: flex; align-items: center; gap: 8px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M3 3v18h18"></path><path d="m18.7 9.9-5.1 5.2-2.8-2.7L7 16.2"></path></svg>
        30-Day Trend — Top 5 Polluted Stations
    </h3>
    ''', unsafe_allow_html=True)
    top5 = station_latest.head(5).index.tolist()
    trend = recent[recent["station_name"].isin(top5)]
    fig = px.line(trend, x="date", y="value", color="station_name", markers=False,
                  labels={"value": "PM2.5 (µg/m³)", "date": "", "station_name": "Station"})
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Threshold ({threshold})", annotation_position="right")
    fig.update_layout(height=420, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit, sans-serif"), margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════════════════════
# PAGE: HEALTH ADVISORY
# ═════════════════════════════════════════════════════════════
elif page == "Health Advisory":
    st.markdown('''
    <h1 class="main-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 12px;"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
        Health Advisory Report Generator
    </h1>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Personalised air quality health report for any date range</p>', unsafe_allow_html=True)

    st.markdown("Configure the parameters below and click **Generate Report**:")

    cc1, cc2 = st.columns(2)
    with cc1:
        report_station = st.selectbox("Location",
            ["All Stations"] + sorted(stations["station_name"].tolist()))
        sensitivity = st.selectbox("Risk Profile",
            ["General Public",
             "Sensitive Group (children, elderly)",
             "High Risk (asthma, heart/lung disease)"])
    with cc2:
        report_range = st.date_input(
            "Report Period",
            value=(daily["date"].max().date() - pd.Timedelta(days=30), daily["date"].max().date()),
            min_value=daily["date"].min().date(),
            max_value=daily["date"].max().date(),
        )

    if st.button("Generate Report", type="primary", use_container_width=True):
        pm_filt = daily[daily["pollutant"] == "pm25"].copy()
        if report_station != "All Stations":
            pm_filt = pm_filt[pm_filt["station_name"] == report_station]
        if len(report_range) == 2:
            pm_filt = pm_filt[(pm_filt["date"] >= pd.to_datetime(report_range[0])) &
                              (pm_filt["date"] <= pd.to_datetime(report_range[1]))]

        if pm_filt.empty:
            st.error("No data available for the selected filters.")
        else:
            avg_pm = pm_filt["value"].mean()
            max_pm = pm_filt["value"].max()
            n_days = pm_filt["date"].nunique()
            # Per-day categories
            daily_avg = pm_filt.groupby("date")["value"].mean()
            cats = daily_avg.apply(lambda v: pm25_to_aqi_category(v)[0])
            cat_counts = cats.value_counts()
            overall_cat, overall_color = pm25_to_aqi_category(avg_pm)

            # Sensitivity-adjusted advisory
            extra_advice = {
                "General Public": "",
                "Sensitive Group (children, elderly)": " For this risk group, even Moderate category requires precaution — limit outdoor time during peak hours (5–10 AM).",
                "High Risk (asthma, heart/lung disease)": " Highest care required: this group should treat Moderate category as Poor — keep rescue medication accessible, use N95 masks, avoid all outdoor activities when PM2.5 > 60 µg/m³."
            }[sensitivity]

            # Report
            st.markdown("---")
            st.markdown(f"""
            <div style='background:linear-gradient(135deg, #0F2A3D 0%, #1A4B6A 100%);
                        color:white; padding:24px; border-radius:12px; margin-bottom:20px;'>
                <h2 style='margin:0; color:white; display:flex; align-items:center; gap:10px;'>
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
                    Health Advisory Report
                </h2>
                <p style='margin:6px 0 0 0; opacity:0.9;'>
                    Location: <strong>{report_station}</strong><br>
                    Period: <strong>{report_range[0]} to {report_range[1]}</strong> ({n_days} days)<br>
                    Risk Profile: <strong>{sensitivity}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)

            r1, r2, r3 = st.columns(3)
            r1.metric("Average PM2.5", f"{avg_pm:.1f} µg/m³")
            r2.metric("Peak PM2.5", f"{max_pm:.1f} µg/m³")
            with r3:
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-top: 4px solid {overall_color}; padding: 18px 22px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); height: 100%; box-sizing: border-box;'>
                    <div style='font-size: 0.95rem; font-weight: 600; opacity: 0.8; color: var(--text-color); margin-bottom: 8px;'>Overall Category</div>
                    <span class='{category_css_class(overall_cat)}'>{overall_cat}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('''
            <h4 style="display: flex; align-items: center; gap: 8px; margin-top: 24px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                Daily Category Breakdown
            </h4>
            ''', unsafe_allow_html=True)
            order = ["Good","Satisfactory","Moderate","Poor","Very Poor","Severe"]
            ordered_counts = pd.DataFrame({
                "Category": [c for c in order if c in cat_counts.index],
                "Days":     [int(cat_counts[c]) for c in order if c in cat_counts.index],
            })
            ordered_counts["%"] = (ordered_counts["Days"] / ordered_counts["Days"].sum() * 100).round(1)
            cat_colors = {"Good":"#2D9C6F", "Satisfactory":"#A8D88B", "Moderate":"#F1C40F",
                          "Poor":"#E67E22", "Very Poor":"#E74C3C", "Severe":"#922B21"}
            fig = px.bar(ordered_counts, x="Category", y="Days",
                         color="Category", color_discrete_map=cat_colors,
                         text="Days")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=340, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit, sans-serif"),
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('''
            <h4 style="display: flex; align-items: center; gap: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5 5 0 0 0 8 8c0 1 .3 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5h4Z"></path><path d="M9 18h6M10 22h4"></path></svg>
                Health Recommendation
            </h4>
            ''', unsafe_allow_html=True)
            st.info(health_advice(overall_cat) + extra_advice)

            # Safe day list
            n_safe = (cats.isin(["Good","Satisfactory"])).sum()
            n_unsafe = (cats.isin(["Very Poor","Severe"])).sum()
            st.markdown('''
            <h4 style="display: flex; align-items: center; gap: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Summary Metrics
            </h4>
            ''', unsafe_allow_html=True)
            st.markdown(f"""
            <ul style="list-style: none; padding-left: 0; margin-top: 10px;">
                <li style="margin-bottom: 10px; display: flex; align-items: flex-start; gap: 10px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #2D9C6F; display: inline-block; margin-top: 6px; flex-shrink: 0;"></span>
                    <span style="color: var(--text-color);"><strong>Safe Air Quality</strong>: <strong>{n_safe} of {n_days} days</strong> ({n_safe/n_days*100:.0f}%) registered a status of <strong>Good</strong> or <strong>Satisfactory</strong>.</span>
                </li>
                <li style="margin-bottom: 10px; display: flex; align-items: flex-start; gap: 10px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #E74C3C; display: inline-block; margin-top: 6px; flex-shrink: 0;"></span>
                    <span style="color: var(--text-color);"><strong>Hazardous Air Quality</strong>: <strong>{n_unsafe} of {n_days} days</strong> ({n_unsafe/n_days*100:.0f}%) registered a status of <strong>Very Poor</strong> or <strong>Severe</strong>.</span>
                </li>
                <li style="margin-bottom: 10px; display: flex; align-items: flex-start; gap: 10px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #F1C40F; display: inline-block; margin-top: 6px; flex-shrink: 0;"></span>
                    <span style="color: var(--text-color);"><strong>Peak Concentration</strong>: The highest 24h average recorded was <strong>{max_pm:.1f} µg/m³</strong>, falling under the <strong>{pm25_to_aqi_category(max_pm)[0]}</strong> category.</span>
                </li>
            </ul>
            """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═════════════════════════════════════════════════════════════
elif page == "About":
    st.markdown('''
    <h1 class="main-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1B8A9E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 12px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        About This Project
    </h1>
    ''', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    ### Team Matatizo
    **Members:** Anuj Gautam · Ismail · Nassir

    ### Project: Delhi Air Quality Data Engineering Pipeline

    This downstream application is built on top of a 3-milestone data engineering pipeline:

    | Milestone | Description |
    |---|---|
    | **Milestone 1** | Ingest 100 MB Parquet (10.4M rows) → split into 219 monthly CSV chunks |
    | **Milestone 2** | Design 3NF PostgreSQL schema (4 tables) → load all data |
    | **Milestone 3** | Clean (imputation, outliers, timezone fix) → transform → 9 visualisations |
    | **This App** | Downstream application — 4 features built on the cleaned dataset |

    ### Tech Stack
    - **Backend Pipeline:** Python, pyarrow, pandas, PostgreSQL
    - **This App:** Streamlit, Plotly, scikit-learn
    - **Deployment:** Streamlit Cloud
    - **Source Code:** [GitHub](https://github.com/AnujGautam07/Delhi-Air-Quality-Analysis)

    ### Data Source
    Central Pollution Control Board (CPCB) and Delhi Pollution Control Committee (DPCC) —
    17 Continuous Ambient Air Quality Monitoring Stations across Delhi, January 2024 to December 2025.

    ### Disclaimer
    This application is for educational purposes as part of the Data Engineering & Management course.
    The forecasting model is a simple linear regression intended to demonstrate the concept;
    production air quality forecasting requires more sophisticated models (LSTM, chemical transport models).
    """)
