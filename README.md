# 🌫️ Delhi Air Quality Analysis — End-to-End Data Engineering Pipeline

**Team Matatizo** — Anuj Gautam · Ismail · Nassir
**Course:** Data Engineering & Management

---

## 📌 Project Overview

End-to-end data engineering pipeline on Delhi air quality data (2024–2025) from 17 CPCB/DPCC monitoring stations. The project covers data ingestion, relational database design, data cleaning, transformation, and a downstream Streamlit web application.

**Key Finding:** Delhi's average PM2.5 of **93.54 µg/m³** is 3.7× the WHO guideline.

---

## 📁 Project Structure

```
Delhi-Air-Quality-Analysis/
│
├── milestone1/
│   └── milestone1_split.py          # Parquet → 219 CSV chunks (50K rows each)
│
├── milestone2/
│   ├── milestone2_schema.sql        # PostgreSQL schema (4 tables, 3NF)
│   ├── milestone2_load.py           # Batch data loader (psycopg2)
│   └── milestone2_verify.sql        # Verification queries
│
├── milestone3/
│   └── milestone3_final.py          # Full cleaning + transformation + 9 graphs
│
├── streamlit_app/                   # Downstream application
│   ├── app.py                       # Main Streamlit app (6 pages, 4 features)
│   ├── requirements.txt             # Streamlit-specific dependencies
│   └── data/                        # Pre-aggregated data (~650 KB)
│       ├── daily_pollutants.parquet
│       ├── daily_weather.parquet
│       ├── hourly.parquet
│       ├── monthly.parquet
│       ├── station_pollutant.parquet
│       ├── stations.parquet
│       └── stats.json
│
├── output_plots/                    # 9 visualisations from Milestone 3
│   ├── 01_missing_values.png
│   ├── 02_pm25_monthly_trend.png
│   ├── 03_pm25_by_station.png
│   ├── 04_hourly_pattern.png
│   ├── 05_seasonal_boxplot.png
│   ├── 06_correlation_heatmap.png
│   ├── 07_aqi_pie.png
│   ├── 08_year_over_year.png
│   └── 09_station_pollutant_heatmap.png
│
├── docs/
│   ├── Team7_Final_Report_v3.docx   # Full academic report (11 sections, 9 graphs)
│   └── Team7_Presentation.pptx      # 17-slide presentation
│
├── requirements.txt                 # All Python dependencies
└── README.md                        # This file
```

---

## 🚀 Setup Instructions (VS Code)

### Step 1 — Clone and open in VS Code

```bash
git clone https://github.com/AnujGautam07/Delhi-Air-Quality-Analysis.git
cd Delhi-Air-Quality-Analysis
code .
```

### Step 2 — Create virtual environment and install dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3 — Run the Streamlit app locally

```bash
cd streamlit_app
streamlit run app.py
```

Opens at `http://localhost:8501` in your browser.

---

## 🌐 Deploy to Streamlit Cloud (Share a Link)

1. Push this repo to GitHub
2. Go to **https://share.streamlit.io** → Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository:** `AnujGautam07/Delhi-Air-Quality-Analysis`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app/app.py`
5. Click **Deploy** → wait 2-3 minutes → get a public URL

Share the URL with your professor — works in any browser, no installation needed.

---

## 📊 What Each Milestone Does

### Milestone 1 — Data Ingestion & Partitioning
- Reads 100 MB Parquet file (10.4M rows) using pyarrow row-group streaming
- Splits into 24 monthly groups, then chunks each into 50,000-row CSV files
- Output: **219 CSV files** (~9 MB each), zipped into a 93 MB archive

**Run:** `python milestone1/milestone1_split.py`

### Milestone 2 — PostgreSQL Database Design
- **Why PostgreSQL:** Structured data, TIMESTAMPTZ for timezone safety, UNIQUE constraints, ACID compliance
- **3NF Schema:** 4 tables — `stations` (17), `pollutants` (13), `weather_readings` (~800K), `pollutant_readings` (~10.4M)
- Eliminates 13× weather column redundancy from raw data

**Run:**
```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE air_quality_db;"

# 2. Create tables
psql -U postgres -d air_quality_db -f milestone2/milestone2_schema.sql

# 3. Load data (edit password in the script first)
python milestone2/milestone2_load.py

# 4. Verify
psql -U postgres -d air_quality_db -f milestone2/milestone2_verify.sql
```

### Milestone 3 — Data Cleaning & Transformation
- Drops redundant columns, converts UTC → IST, fills missing values (forward fill per station)
- Caps outliers at 99.5th percentile, removes negative sensor readings
- Adds derived features: season, weekday, aqi_category
- Generates **9 analytical graphs** saved to `output_plots/`

**Run:** `python milestone3/milestone3_final.py`

### Downstream Application — Streamlit Dashboard
4 features in one interactive web app:

| Feature | Description |
|---------|-------------|
| 📊 AQI Dashboard | Filter by station/pollutant/date → trends, station comparison, diurnal pattern |
| 🔮 PM2.5 Forecaster | Enter weather conditions → ML model predicts tomorrow's PM2.5 + health impact |
| 🚨 Alert System | Set a PM2.5 threshold → see which stations are exceeding it + 30-day trend |
| 🏥 Health Advisory | Select location + dates + risk profile → get a personalised health report |

**Run:** `cd streamlit_app && streamlit run app.py`

---

## 📈 Key Findings

| Metric | Value |
|--------|-------|
| Delhi mean PM2.5 | **93.54 µg/m³** (3.7× WHO guideline) |
| Winter mean PM2.5 | **148.7 µg/m³** (Very Poor) |
| Summer mean PM2.5 | **36.8 µg/m³** (Good) |
| Most polluted station | **Jahangirpuri** (129.1 µg/m³) |
| Strongest dispersion driver | **Wind speed** (negative correlation) |
| Very Poor + Severe readings | **25.9%** of all PM2.5 measurements |
| Total records | **10,397,242** (zero data loss after cleaning) |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Primary language |
| pyarrow | Parquet reading |
| pandas / numpy | Data manipulation |
| matplotlib / seaborn | Static visualisations (9 graphs) |
| PostgreSQL 15 | Relational database (3NF) |
| psycopg2 | Python–PostgreSQL connector |
| Streamlit | Web dashboard framework |
| Plotly | Interactive charts in dashboard |
| scikit-learn | Linear regression for PM2.5 forecaster |
| Kaggle Notebooks | Milestone execution environment |
| GitHub | Version control |

---

## 📜 License

This project is for academic purposes — Data Engineering & Management course.

---

**Team Matatizo** — Anuj Gautam · Ismail · Nassir
