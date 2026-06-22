# 🌫️ Delhi Air Quality Intelligence Platform

**Downstream application** built on the Team Matatizo data engineering pipeline.

## What This App Does

Four integrated tools, all powered by the cleaned dataset from Milestones 1–3:

| Feature | What it does |
|---------|--------------|
| 📊 **AQI Dashboard** | Interactive exploration of pollution across 17 stations × 13 pollutants × 2 years |
| 🔮 **PM2.5 Forecaster** | Linear regression model predicts PM2.5 from weather inputs |
| 🚨 **Alert System** | Flags stations crossing user-defined PM2.5 thresholds, 30-day trend chart |
| 🏥 **Health Advisory** | Generates personalised health reports by location, date range, and risk profile |

---

## 📁 Folder Structure

```
streamlit_app/
├── app.py              ← main Streamlit application
├── requirements.txt    ← Python dependencies
├── data/               ← pre-aggregated parquet files (~650 KB total)
│   ├── daily_pollutants.parquet
│   ├── daily_weather.parquet
│   ├── stations.parquet
│   ├── station_pollutant.parquet
│   ├── hourly.parquet
│   ├── monthly.parquet
│   └── stats.json
└── README.md
```

---

## 🚀 Deploy to Streamlit Cloud (FREE)

### Step 1 — Push to GitHub
Copy the entire `streamlit_app/` folder into your repo at:
```
https://github.com/AnujGautam07/Delhi-Air-Quality-Analysis
```

github repo structure :
```
Delhi-Air-Quality-Analysis/
├── milestone1_split.py
├── milestone2_schema.sql
├── milestone2_load.py
├── milestone3_final.py
├── README.md
└── streamlit_app/          ← this whole folder
    ├── app.py
    ├── requirements.txt
    └── data/
        ├── daily_pollutants.parquet
        ├── daily_weather.parquet
        ├── hourly.parquet
        ├── monthly.parquet
        ├── station_pollutant.parquet
        ├── stations.parquet
        └── stats.json
```

Then commit & push:
```bash
git add streamlit_app/
git commit -m "Add downstream application — Streamlit dashboard"
git push origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to **https://share.streamlit.io**
2. Sign in with your **GitHub account** (free)
3. Click **"New app"**
4. Fill in:
   - **Repository:** `AnujGautam07/Delhi-Air-Quality-Analysis`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app/app.py`
5. Click **"Deploy"**

Wait 2–3 minutes for the first deployment. You'll get a URL like:
```
https://anujgautam07-delhi-air-quality-analysis-streamlit-appapp-xxxx.streamlit.app
```

Share that link with your professor — he opens it in any browser, no installation needed.

---

## 💻 Run Locally (Optional)

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 📊 Data Source

The app reads **pre-aggregated parquet files** derived from the cleaned dataset (Milestone 3 output):

- **daily_pollutants.parquet** — Daily averages per (station × pollutant) — ~49k rows
- **daily_weather.parquet** — Daily weather averages per station — ~5k rows
- **hourly.parquet** — Hourly diurnal pattern per pollutant — 312 rows
- **monthly.parquet** — Monthly averages per pollutant — 312 rows
- **station_pollutant.parquet** — Per-station per-pollutant averages — 221 rows
- **stations.parquet** — Station metadata — 17 rows
- **stats.json** — Top-level dataset statistics

Total data footprint: **~650 KB** (well under Streamlit Cloud's 1 GB limit).

These were computed by running the milestone 3 cleaning pipeline on a sample of the dataset (every 3rd CSV chunk = ~3.4M rows), then aggregating to daily/hourly/monthly granularity. All headline numbers (mean PM2.5, station rankings, AQI distribution) match the milestone 3 output.

---

## 🛠️ Tech Stack

- **Streamlit 1.31** — web framework
- **Plotly** — interactive charts
- **scikit-learn** — linear regression for PM2.5 forecaster
- **pandas + pyarrow** — data loading
- **NumPy** — numerical operations

---

## 👥 Team Matatizo
Anuj Gautam · Ismail · Nassir

**Course:** Data Engineering & Management
