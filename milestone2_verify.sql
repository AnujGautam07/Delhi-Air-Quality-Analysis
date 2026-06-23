-- ============================================================
-- MILESTONE 2 : Verification Queries
-- Run after loading to confirm everything worked
-- ============================================================

SET search_path TO air_quality, public;

-- 1. Row counts
SELECT 'stations'           AS table_name, COUNT(*) AS total_rows FROM stations
UNION ALL
SELECT 'pollutants',                        COUNT(*) FROM pollutants
UNION ALL
SELECT 'weather_readings',                  COUNT(*) FROM weather_readings
UNION ALL
SELECT 'pollutant_readings',                COUNT(*) FROM pollutant_readings;

-- 2. List all stations
SELECT station_id, station_name, city, state
FROM stations ORDER BY station_name;

-- 3. All pollutants
SELECT * FROM pollutants ORDER BY pollutant_code;

-- 4. Top 5 most polluted stations (avg PM2.5)
SELECT
    s.station_name,
    ROUND(AVG(pr.value)::numeric, 2) AS avg_pm25
FROM pollutant_readings pr
JOIN stations s USING (station_id)
WHERE pr.pollutant_code = 'pm25'
GROUP BY s.station_name
ORDER BY avg_pm25 DESC
LIMIT 5;

-- 5. Monthly average PM2.5 trend
SELECT
    TO_CHAR(reading_time, 'YYYY-MM') AS month,
    ROUND(AVG(value)::numeric, 2)    AS avg_pm25
FROM pollutant_readings
WHERE pollutant_code = 'pm25'
GROUP BY month ORDER BY month;

-- 6. Data completeness per station
SELECT
    s.station_name,
    COUNT(*)                                       AS total,
    COUNT(pr.value)                                AS non_null,
    ROUND(100.0 * COUNT(pr.value) / COUNT(*), 1)   AS completeness_pct
FROM pollutant_readings pr
JOIN stations s USING (station_id)
WHERE pr.pollutant_code = 'pm25'
GROUP BY s.station_name
ORDER BY completeness_pct DESC;
