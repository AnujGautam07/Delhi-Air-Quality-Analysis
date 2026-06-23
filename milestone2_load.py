"""
Milestone 2 — Data Loader
Loads all 219 CSV files from the zip into PostgreSQL.

Usage:
    pip install psycopg2-binary pandas
    python milestone2_load.py
"""

import zipfile, io, os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# ── CONFIG — change these ────────────────────────────────────
ZIP_PATH = "../milestone1/air_quality_csvs.zip"
DB = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "air_quality_db",
    "user":     "postgres",
    "password": "your_password_here",   # ← CHANGE THIS
}
SCHEMA     = "air_quality"
BATCH_SIZE = 5000
# ─────────────────────────────────────────────────────────────


def get_conn():
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    return conn


def load_stations(cur, df):
    rows = (
        df[["station_id", "station_name", "city", "state"]]
        .dropna(subset=["station_id"])
        .drop_duplicates("station_id")
        .values.tolist()
    )
    execute_values(cur, f"""
        INSERT INTO {SCHEMA}.stations (station_id, station_name, city, state)
        VALUES %s ON CONFLICT (station_id) DO NOTHING
    """, rows)


def load_weather(cur, df):
    cols = ["station_id","datetime","at_c","rh_percent","ws_m_s",
            "wd_deg","rf_mm","tot_rf_mm","sr_w_mt2","bp_mmhg","vws_m_s"]
    w = (df[cols].dropna(subset=["station_id","datetime"])
         .drop_duplicates(["station_id","datetime"]))
    w = w.astype(object).where(pd.notna(w), None)
    execute_values(cur, f"""
        INSERT INTO {SCHEMA}.weather_readings
            (station_id, reading_time, at_c, rh_percent, ws_m_s,
             wd_deg, rf_mm, tot_rf_mm, sr_w_mt2, bp_mmhg, vws_m_s)
        VALUES %s ON CONFLICT (station_id, reading_time) DO NOTHING
    """, list(w.itertuples(index=False, name=None)), page_size=BATCH_SIZE)


def load_pollutants(cur, df):
    p = (df[["station_id","pollutant","datetime","value"]]
         .dropna(subset=["station_id","pollutant","datetime"]))
    p = p.astype(object).where(pd.notna(p), None)
    execute_values(cur, f"""
        INSERT INTO {SCHEMA}.pollutant_readings
            (station_id, pollutant_code, reading_time, value)
        VALUES %s ON CONFLICT (station_id, pollutant_code, reading_time) DO NOTHING
    """, list(p.itertuples(index=False, name=None)), page_size=BATCH_SIZE)


def main():
    conn = get_conn()
    zf   = zipfile.ZipFile(ZIP_PATH)
    files = sorted(zf.namelist())
    print(f"Found {len(files)} CSV files in zip\n")

    for i, fname in enumerate(files, 1):
        print(f"[{i:>3}/{len(files)}] {fname} ...", end=" ", flush=True)
        df = pd.read_csv(io.BytesIO(zf.read(fname)), parse_dates=["datetime"])

        with conn.cursor() as cur:
            load_stations(cur, df)
            load_weather(cur, df)
            load_pollutants(cur, df)
        conn.commit()
        print(f"{len(df):,} rows ✓")

    conn.close()
    print("\n✅ All data loaded successfully!")


if __name__ == "__main__":
    main()
