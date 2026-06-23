"""
Milestone 1 — Load & Split
Reads the source .parquet file and splits it into 219 monthly CSV files.
Each month is further chunked into 50,000-row parts (~9 MB each).

Usage:
    python milestone1_split.py

Output: ./monthly_csvs/data_YYYY_MM_partXX.csv  (219 files)
        ./air_quality_csvs.zip                   (~93 MB)
"""

import pyarrow.parquet as pq
import pandas as pd
import os
import zipfile

# ── CONFIG ──────────────────────────────────────────────────
FILE_PATH  = "team_7 (1).parquet"   # path to source parquet file
OUTPUT_DIR = "./monthly_csvs"
ZIP_PATH   = "./air_quality_csvs.zip"
CHUNK_ROWS = 50_000                  # rows per CSV file (~9 MB each)
# ────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pf = pq.ParquetFile(FILE_PATH)
    print(f"Source file : {FILE_PATH}")
    print(f"Total rows  : {pf.metadata.num_rows:,}")
    print(f"Row groups  : {pf.num_row_groups}")
    print(f"Chunk size  : {CHUNK_ROWS:,} rows per file")
    print(f"Output dir  : {OUTPUT_DIR}")
    print()

    # Step 1: Read row-group by row-group and bucket by (year, month)
    monthly_buffers = {}

    for i in range(pf.num_row_groups):
        print(f"  Reading row group {i + 1}/{pf.num_row_groups}...", end=" ", flush=True)
        df = pf.read_row_group(i).to_pandas()

        for (yr, mo), grp in df.groupby(["year", "month"]):
            key = (int(yr), int(mo))
            if key not in monthly_buffers:
                monthly_buffers[key] = []
            monthly_buffers[key].append(grp)

        print(f"{len(df):,} rows")

    # Step 2: Write chunked CSVs
    print(f"\nWriting chunked CSV files...\n")
    all_files = []
    total_files = 0

    for (yr, mo) in sorted(monthly_buffers.keys()):
        combined = pd.concat(monthly_buffers[(yr, mo)], ignore_index=True)

        for part, start in enumerate(range(0, len(combined), CHUNK_ROWS), start=1):
            chunk    = combined.iloc[start : start + CHUNK_ROWS]
            filename = f"data_{yr}_{mo:02d}_part{part:02d}.csv"
            out_path = os.path.join(OUTPUT_DIR, filename)
            chunk.to_csv(out_path, index=False)
            size_mb  = os.path.getsize(out_path) / (1024 * 1024)
            print(f"  {filename}  |  {len(chunk):>6,} rows  |  {size_mb:.1f} MB")
            all_files.append(out_path)
            total_files += 1

        print(f"  └─ {yr}-{mo:02d}: {part} parts, {len(combined):,} rows total\n")

    # Step 3: Zip everything
    print(f"Zipping {total_files} files → {ZIP_PATH} ...")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in all_files:
            zf.write(fpath, arcname=os.path.basename(fpath))

    zip_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"\n✓ Done! {total_files} CSV files zipped.")
    print(f"  Zip size : {zip_mb:.1f} MB")


if __name__ == "__main__":
    main()
