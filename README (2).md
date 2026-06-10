# 🌫️ Delhi Air Quality & Weather Analysis (2024–2025)
**Data Engineering & Management — Team 7 Project**

---

## 📌 Project Overview

This project performs end-to-end data engineering on a real-world air quality and weather dataset collected from **17 CPCB/DPCC monitoring stations across Delhi, India**, covering **January 2024 to December 2025**.

The dataset contains over **10.4 million rows** of 15-minute interval readings across **13 pollutants** and **9 weather parameters**.

---

## 👥 Team 7

| Name | Role |
|------|------|
| *(Add your names here)* | Data Engineering |

---

## 📁 Repository Structure

```
├── data/
│   └── monthly_csvs/              # 219 CSV files (split from parquet, per month per chunk)
│       ├── data_2024_01_part01.csv
│       ├── data_2024_01_part02.csv
│       └── ... (219 files total)
│
├── milestone1_split.py            # M1: Load parquet → split into 219 CSVs
│
├── milestone2_schema.sql          # M2: PostgreSQL schema (CREATE TABLEs, indexes)
├── milestone2_load.py             # M2: Load all CSVs into PostgreSQL
├── milestone2_verify.sql          # M2: Verification queries
│
├── milestone3_final.py            # M3: Full cleaning, transformation & visualization
│
├── output_plots/                  # 9 generated graphs (PNG)
│   ├── 01_missing_values.png
│   ├── 02_pm25_monthly_trend.png
│   ├── 03_pm25_by_station.png
│   ├── 04_hourly_pattern.png
│   ├── 05_seasonal_boxplot.png
│   ├── 06_correlation_heatmap.png
│   ├── 07_aqi_distribution.png
│   ├── 08_year_over_year.png
│   └── 09_station_pollutant_heatmap.png
│
└── README.md
```

---

## 🗂️ Dataset Details

| Property | Value |
|----------|-------|
| Source | CPCB / DPCC Delhi Monitoring Stations |
| Format | `.parquet` → split into `.csv` |
| Total Rows | 10,397,242 |
| Columns | 22 |
| Date Range | Jan 2024 – Dec 2025 |
| Frequency | 15-minute intervals |
| Stations | 17 |
| Pollutants | 13 (PM2.5, PM10, NO2, NO, NH3, SO2, CO, Ozone, Benzene, Toluene, Xylene, Ethyl Benzene, M/P Xylene) |
| Weather Params | 9 (Temperature, Humidity, Wind Speed/Direction, Rainfall, Solar Radiation, Pressure, Vertical Wind) |

---

## 🏁 Milestone 1 — Data Loading & Splitting

**Goal:** Load the raw `.parquet` file and split it into small manageable CSV files for version control.

**Approach:**
- Loaded the 100 MB parquet file using `pyarrow` (row-group by row-group to avoid memory crash)
- Grouped data by `year` and `month` → 24 monthly groups
- Split each month into chunks of 50,000 rows → **219 CSV files** (~9–10 MB each)
- Zipped all files into one downloadable archive

**Script:** `milestone1_split.py`

**Output:** 219 CSV files → `data_YYYY_MM_partXX.csv`

---

## 🗄️ Milestone 2 — Database Design & Loading (PostgreSQL)

**Goal:** Design a normalized relational database and load all data into PostgreSQL.

### Schema Design (3NF Normalization)

The raw data has redundancy — weather columns repeat identically across all 13 pollutant rows for the same station-timestamp. We fix this with 3-table normalization:

```
stations            → 17 rows  (dimension table)
pollutants          → 13 rows  (lookup table)
weather_readings    → ~800,000 rows  (one per station × timestamp)
pollutant_readings  → ~10,400,000 rows  (one per station × timestamp × pollutant)
```

**Key design decisions:**
- `station_id` as natural primary key (stable CPCB ID)
- `UNIQUE` constraints on composite keys prevent duplicate readings
- `TIMESTAMPTZ` preserves UTC timezone info
- Indexes on `reading_time` and `pollutant_code` for fast queries

**Scripts:** `milestone2_schema.sql` → `milestone2_load.py` → `milestone2_verify.sql`

**How to run:**
```bash
# 1. Create database in pgAdmin
CREATE DATABASE air_quality_db;

# 2. Run schema
psql -U postgres -d air_quality_db -f milestone2_schema.sql

# 3. Load data
pip install psycopg2-binary pandas
python milestone2_load.py

# 4. Verify
psql -U postgres -d air_quality_db -f milestone2_verify.sql
```

---

## 🧹 Milestone 3 — Data Cleaning, Transformation & Analysis

**Goal:** Clean raw data, apply transformations, and generate analytical visualizations.

### Problems Found in Raw Data

| Issue | Details |
|-------|---------|
| Missing weather values | `vws_m_s`: 81%, `at_c`: 44%, `bp_mmhg`: 43%, `rf_mm`: 41% |
| Redundant columns | `timestamp` duplicates `datetime`; `station` duplicates `station_name` |
| Outliers | Extreme spikes in NO, SO2, Toluene readings |
| Wrong timezone | Datetime stored as UTC but data is from Delhi (IST = UTC+5:30) |

### Cleaning Steps Applied

1. **Dropped** 6 redundant columns (`timestamp`, `station`, `year`, `month`, `day`, `hour`)
2. **Converted** datetime UTC → IST (`Asia/Kolkata`)
3. **Removed** duplicate rows
4. **Filled** missing weather values using forward fill + backward fill per station
5. **Capped** outliers at 99.5th percentile per pollutant
6. **Removed** negative sensor readings (set to NaN)
7. **Standardized** text columns (strip whitespace, fix casing)

### Transformations Applied

1. Re-extracted `year`, `month`, `day`, `hour`, `weekday` from clean IST datetime
2. Added **`season`** column (Winter/Spring/Summer/Autumn)
3. Added **`aqi_category`** using India CPCB PM2.5 standard
4. Created **wide-format** pivot table (one row per station-timestamp, one column per pollutant)

**Script:** `milestone3_final.py`

---

## 📊 Key Findings

### PM2.5 Air Quality
- Delhi's average PM2.5 = **93.54 µg/m³** — more than 3.7× WHO guideline (25 µg/m³)
- **Jahangirpuri** is the most polluted station (129.1 µg/m³ avg)
- **Nehru Nagar** second (113.5 µg/m³), **Dwarka-Sector 8** third (105.8 µg/m³)

### Seasonal Pattern
| Season | Avg PM2.5 |
|--------|-----------|
| Winter | 148.7 µg/m³ |
| Autumn | 115.9 µg/m³ |
| Spring | 70.4 µg/m³ |
| Summer | 36.8 µg/m³ |

Winter is **~4× worse** than summer due to temperature inversion and crop burning.

### Year-over-Year
- A modest improvement in PM2.5 is observed from 2024 to 2025, most pronounced in winter months

### AQI Distribution
- **20.6%** of readings fall in "Good" category
- **25.9%** fall in "Very Poor" or "Severe" — serious public health concern

### Diurnal Pattern
- Peak pollution at **5 AM** (111.3 µg/m³) — overnight accumulation + morning traffic
- Lowest at **10 PM** (69.6 µg/m³)

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Data processing |
| pandas / numpy | Data manipulation |
| pyarrow | Reading parquet files |
| matplotlib / seaborn | Visualizations |
| PostgreSQL | Relational database |
| psycopg2 | Python–PostgreSQL connector |
| Kaggle Notebooks | Execution environment |
| GitHub | Version control |

---

## ▶️ How to Run (Kaggle Notebooks)

```python
# Step 1: Upload team_7.parquet to Kaggle input dataset
# Step 2: Install dependencies (pre-installed on Kaggle)
pip install pyarrow pandas matplotlib seaborn

# Step 3: Run milestone scripts in order
# Milestone 1 — split parquet into 219 CSVs
python milestone1_split.py

# Milestone 3 — cleaning, transformation & graphs
python milestone3_final.py
```

---

## 📜 License
This project is for academic purposes — Data Engineering & Management course.
