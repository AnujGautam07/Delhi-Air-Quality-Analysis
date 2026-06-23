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
    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        color: #0F2A3D;
        padding: 0;
        margin-bottom: 0;
    }
    .sub-header {
        color: #1B8A9E;
        font-size: 1.05rem;
        margin-top: 0;
    }
    .metric-card {
        background: #F7FAFB;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1B8A9E;
    }
    .aqi-good     { background:#2D9C6F; color:white; padding:8px 14px; border-radius:6px; font-weight:600; display:inline-block; }
    .aqi-satisf   { background:#A8D88B; color:white; padding:8px 14px; border-radius:6px; font-weight:600; display:inline-block; }
    .aqi-moderate { background:#F1C40F; color:white; padding:8px 14px; border-radius:6px; font-weight:600; display:inline-block; }
    .aqi-poor     { background:#E67E22; color:white; padding:8px 14px; border-radius:6px; font-weight:600; display:inline-block; }
    .aqi-vpoor    { background:#E74C3C; color:white; padding:8px 14px; border-radius:6px; font-weight:600; display:inline-block; }
    .aqi-severe   { background:#922B21; color:white; padding:8px 14px; border-radius:6px; font-weight:600; display:inline-block; }
    .stMetric { background: white; padding: 0.5rem; border-radius: 6px; }
    div[data-testid="metric-container"] {
        background-color: #F7FAFB;
        border: 1px solid #E1ECF2;
        padding: 12px;
        border-radius: 8px;
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
st.sidebar.markdown("## 🌫️ Delhi AQI Platform")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home",
     "📊 AQI Dashboard",
     "🔮 PM2.5 Forecaster",
     "🚨 Alert System",
     "🏥 Health Advisory",
     "ℹ️ About"],
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
if page == "🏠 Home":
    st.markdown('<h1 class="main-header">Delhi Air Quality Intelligence Platform</h1>', unsafe_allow_html=True)
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
        #### 📊 AQI Dashboard
        Interactive exploration of pollution levels across all 17 Delhi stations.
        Filter by date range, station, and pollutant. Compare trends over time.

        #### 🔮 PM2.5 Forecaster
        Predict next-day air quality using a regression model trained on
        weather + historical pollution. Enter weather conditions and get a forecast.
        """)
    with f2:
        st.markdown("""
        #### 🚨 Alert System
        Real-time-style alerts when PM2.5 crosses CPCB thresholds. View which
        stations are currently in "Severe" or "Very Poor" category.

        #### 🏥 Health Advisory Report
        Generate a personalised health advisory report for any date range,
        location, and sensitivity level (general public vs sensitive groups).
        """)

    st.markdown("---")
    st.markdown("### How the data flows")
    st.markdown("""
    ```
    Raw Parquet (100 MB, 10.4M rows)
            ↓
    Milestone 1: Split into 219 CSVs
            ↓
    Milestone 2: PostgreSQL Database (3NF)
            ↓
    Milestone 3: Cleaning + Transformation
            ↓
    Pre-aggregated Tables  ← (this app reads these)
            ↓
    Streamlit Dashboard
    ```
    """)


# ═════════════════════════════════════════════════════════════
# PAGE: AQI DASHBOARD
# ═════════════════════════════════════════════════════════════
elif page == "📊 AQI Dashboard":
    st.markdown('<h1 class="main-header">📊 AQI Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Explore pollution levels across stations and time</p>', unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        station_options = ["All Stations"] + sorted(stations["station_name"].tolist())
        sel_station = st.selectbox("📍 Select Station", station_options)
    with fc2:
        pollutant_options = sorted(daily["pollutant"].unique())
        sel_pollutant = st.selectbox("🧪 Select Pollutant", pollutant_options, index=pollutant_options.index("pm25"))
    with fc3:
        date_range = st.date_input(
            "📅 Date Range",
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
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
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
                               xaxis_title=f"{sel_pollutant.upper()} (µg/m³)", plot_bgcolor="white")
            st.plotly_chart(fig2, use_container_width=True)

        with col_b:
            st.markdown("#### Diurnal Pattern (Hour of Day)")
            h = hourly[hourly["pollutant"] == sel_pollutant]
            fig3 = px.line(h, x="hour", y="value", markers=True,
                           labels={"value": f"{sel_pollutant.upper()}", "hour": "Hour (IST)"})
            fig3.update_traces(line=dict(color="#1B8A9E", width=2.5))
            fig3.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
                               xaxis=dict(dtick=2))
            st.plotly_chart(fig3, use_container_width=True)


# ═════════════════════════════════════════════════════════════
# PAGE: PM2.5 FORECASTER
# ═════════════════════════════════════════════════════════════
elif page == "🔮 PM2.5 Forecaster":
    st.markdown('<h1 class="main-header">🔮 PM2.5 Forecaster</h1>', unsafe_allow_html=True)
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

    st.markdown("---")
    st.markdown("### 🌤️ Enter Tomorrow's Weather Forecast")

    c1, c2, c3 = st.columns(3)
    with c1:
        at_c       = st.slider("🌡️ Temperature (°C)",            0.0, 50.0, 25.0, 0.5)
        rh_percent = st.slider("💧 Relative Humidity (%)",         0.0, 100.0, 55.0, 1.0)
    with c2:
        ws_m_s     = st.slider("💨 Wind Speed (m/s)",              0.0, 10.0, 2.0, 0.1)
        bp_mmhg    = st.slider("📊 Barometric Pressure (mmHg)",  720.0, 780.0, 750.0, 0.5)
    with c3:
        sr_w_mt2   = st.slider("☀️ Solar Radiation (W/m²)",        0.0, 1000.0, 200.0, 10.0)
        winter     = st.selectbox("❄️ Season", ["Winter (Nov–Feb)", "Other"]) == "Winter (Nov–Feb)"

    # Predict
    X_new = np.array([[at_c, rh_percent, ws_m_s, bp_mmhg, sr_w_mt2, int(winter)]])
    pred  = float(model.predict(X_new)[0])
    pred  = max(0, pred)
    cat, color = pm25_to_aqi_category(pred)
    advice = health_advice(cat)

    st.markdown("---")
    st.markdown("### 🎯 Forecast Result")
    r1, r2c = st.columns([1, 2])
    with r1:
        st.markdown(f"""
        <div style='background:{color}; color:white; padding:24px; border-radius:12px; text-align:center;'>
            <div style='font-size:14px; opacity:0.9;'>Predicted PM2.5</div>
            <div style='font-size:48px; font-weight:700; margin:8px 0;'>{pred:.1f}</div>
            <div style='font-size:16px;'>µg/m³</div>
            <div style='margin-top:14px; padding:6px 12px; background:rgba(255,255,255,0.2); border-radius:6px; font-weight:600;'>{cat}</div>
        </div>
        """, unsafe_allow_html=True)
    with r2c:
        st.markdown(f"#### Health Impact: {cat}")
        st.info(advice)
        # Feature importance
        st.markdown("**Why this forecast?** Model coefficients:")
        coef_df = pd.DataFrame({
            "Feature": ["Temperature", "Humidity", "Wind Speed", "Pressure", "Solar Radiation", "Winter Season"],
            "Coefficient": model.coef_
        }).sort_values("Coefficient", key=abs, ascending=False)
        st.dataframe(coef_df, use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════════════════════
# PAGE: ALERT SYSTEM
# ═════════════════════════════════════════════════════════════
elif page == "🚨 Alert System":
    st.markdown('<h1 class="main-header">🚨 Air Quality Alert System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time-style monitoring with configurable thresholds</p>', unsafe_allow_html=True)

    # Get latest 30 days of data
    pm_data = daily[daily["pollutant"] == "pm25"].copy()
    latest_date = pm_data["date"].max()
    recent = pm_data[pm_data["date"] >= latest_date - pd.Timedelta(days=30)]

    # User threshold
    c1, c2 = st.columns([1, 2])
    with c1:
        threshold = st.number_input("⚠️ Alert Threshold (PM2.5 µg/m³)",
                                     min_value=30, max_value=300, value=120, step=10,
                                     help="Default 120 = CPCB 'Very Poor' threshold")
    with c2:
        st.markdown(f"""
        <div style='padding:12px; background:#F7FAFB; border-radius:8px; margin-top:24px;'>
            Current alert level: <strong>{pm25_to_aqi_category(threshold)[0]}</strong>
            — stations exceeding {threshold} µg/m³ will be flagged below.
        </div>
        """, unsafe_allow_html=True)

    # Latest station averages (last 7 days)
    week = pm_data[pm_data["date"] >= latest_date - pd.Timedelta(days=7)]
    station_latest = week.groupby("station_name")["value"].mean().sort_values(ascending=False)

    # Alert stations
    alerts = station_latest[station_latest > threshold]
    safe   = station_latest[station_latest <= threshold]

    a1, a2, a3 = st.columns(3)
    a1.metric("🔴 Stations Above Threshold", len(alerts), f"Threshold: {threshold} µg/m³")
    a2.metric("🟢 Stations Below Threshold", len(safe))
    a3.metric("📅 Period", "Last 7 days", str(latest_date.date()))

    st.markdown("---")

    if len(alerts) > 0:
        st.markdown(f"### 🚨 Active Alerts ({len(alerts)} stations)")
        for sname, val in alerts.items():
            cat, color = pm25_to_aqi_category(val)
            st.markdown(f"""
            <div style='background:white; border-left:5px solid {color}; padding:14px 18px;
                        margin-bottom:10px; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.06);
                        display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <div style='font-weight:600; font-size:15px; color:#0F2A3D;'>{sname}</div>
                    <div style='color:#666; font-size:13px; margin-top:3px;'>Category: <strong style='color:{color};'>{cat}</strong></div>
                </div>
                <div style='text-align:right;'>
                    <div style='font-size:26px; font-weight:700; color:{color};'>{val:.1f}</div>
                    <div style='font-size:12px; color:#888;'>µg/m³ (7-day avg)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(f"✅ No stations currently exceed {threshold} µg/m³")

    # Safe stations
    if len(safe) > 0:
        with st.expander(f"🟢 Stations Below Threshold ({len(safe)})", expanded=False):
            for sname, val in safe.items():
                cat, color = pm25_to_aqi_category(val)
                st.markdown(f"- **{sname}** — {val:.1f} µg/m³  ({cat})")

    # 30-day trend chart for top 5 worst stations
    st.markdown("---")
    st.markdown("### 📈 30-Day Trend — Top 5 Polluted Stations")
    top5 = station_latest.head(5).index.tolist()
    trend = recent[recent["station_name"].isin(top5)]
    fig = px.line(trend, x="date", y="value", color="station_name", markers=False,
                  labels={"value": "PM2.5 (µg/m³)", "date": "", "station_name": "Station"})
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Threshold ({threshold})", annotation_position="right")
    fig.update_layout(height=420, plot_bgcolor="white", margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════════════════════
# PAGE: HEALTH ADVISORY
# ═════════════════════════════════════════════════════════════
elif page == "🏥 Health Advisory":
    st.markdown('<h1 class="main-header">🏥 Health Advisory Report Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Personalised air quality health report for any date range</p>', unsafe_allow_html=True)

    st.markdown("Configure the parameters below and click **Generate Report**:")

    cc1, cc2 = st.columns(2)
    with cc1:
        report_station = st.selectbox("📍 Location",
            ["All Stations"] + sorted(stations["station_name"].tolist()))
        sensitivity = st.selectbox("👤 Risk Profile",
            ["General Public",
             "Sensitive Group (children, elderly)",
             "High Risk (asthma, heart/lung disease)"])
    with cc2:
        report_range = st.date_input(
            "📅 Report Period",
            value=(daily["date"].max().date() - pd.Timedelta(days=30), daily["date"].max().date()),
            min_value=daily["date"].min().date(),
            max_value=daily["date"].max().date(),
        )

    if st.button("📋 Generate Report", type="primary", use_container_width=True):
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
                <h2 style='margin:0; color:white;'>🏥 Health Advisory Report</h2>
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
            r3.markdown(f"**Overall Category**<br><span class='{category_css_class(overall_cat)}'>{overall_cat}</span>", unsafe_allow_html=True)

            st.markdown("#### 📊 Daily Category Breakdown")
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
            fig.update_layout(height=340, showlegend=False, plot_bgcolor="white",
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### 💡 Health Recommendation")
            st.info(health_advice(overall_cat) + extra_advice)

            # Safe day list
            n_safe = (cats.isin(["Good","Satisfactory"])).sum()
            n_unsafe = (cats.isin(["Very Poor","Severe"])).sum()
            st.markdown(f"""
            #### 📋 Summary
            - **{n_safe} of {n_days} days** ({n_safe/n_days*100:.0f}%) had safe air quality (Good or Satisfactory)
            - **{n_unsafe} of {n_days} days** ({n_unsafe/n_days*100:.0f}%) had hazardous air quality (Very Poor or Severe)
            - Peak day registered **{max_pm:.0f} µg/m³** — {pm25_to_aqi_category(max_pm)[0]} category
            """)


# ═════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═════════════════════════════════════════════════════════════
elif page == "ℹ️ About":
    st.markdown('<h1 class="main-header">ℹ️ About This Project</h1>', unsafe_allow_html=True)
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
