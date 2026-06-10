-- ============================================================
-- MILESTONE 2 : Schema
-- Team 7 — Delhi Air Quality Dataset (2024–2025)
-- Database : PostgreSQL
-- ============================================================

-- Create a dedicated schema
CREATE SCHEMA IF NOT EXISTS air_quality;
SET search_path TO air_quality, public;

-- Drop tables if re-running (order matters due to foreign keys)
DROP TABLE IF EXISTS pollutant_readings CASCADE;
DROP TABLE IF EXISTS weather_readings   CASCADE;
DROP TABLE IF EXISTS pollutants         CASCADE;
DROP TABLE IF EXISTS stations           CASCADE;


-- ------------------------------------------------------------
-- TABLE 1 : stations
-- Stores info about each monitoring station (only 17 unique)
-- Instead of repeating this on every row in the CSV
-- ------------------------------------------------------------
CREATE TABLE stations (
    station_id    VARCHAR(20)  PRIMARY KEY,
    station_name  VARCHAR(150) NOT NULL,
    city          VARCHAR(100) NOT NULL,
    state         VARCHAR(100) NOT NULL
);


-- ------------------------------------------------------------
-- TABLE 2 : pollutants
-- Lookup table for the 13 pollutant types
-- ------------------------------------------------------------
CREATE TABLE pollutants (
    pollutant_code VARCHAR(20)  PRIMARY KEY,
    pollutant_name VARCHAR(100) NOT NULL,
    unit           VARCHAR(20)
);


-- ------------------------------------------------------------
-- TABLE 3 : weather_readings
-- One row per (station + timestamp)
-- Weather does NOT depend on which pollutant we're measuring
-- ------------------------------------------------------------
CREATE TABLE weather_readings (
    id            BIGSERIAL    PRIMARY KEY,
    station_id    VARCHAR(20)  NOT NULL,
    reading_time  TIMESTAMPTZ  NOT NULL,
    at_c          NUMERIC(6,2),   -- air temperature °C
    rh_percent    NUMERIC(6,2),   -- relative humidity %
    ws_m_s        NUMERIC(6,2),   -- wind speed m/s
    wd_deg        NUMERIC(6,2),   -- wind direction degrees
    rf_mm         NUMERIC(6,2),   -- rainfall mm
    tot_rf_mm     NUMERIC(8,2),   -- cumulative rainfall mm
    sr_w_mt2      NUMERIC(7,2),   -- solar radiation W/m²
    bp_mmhg       NUMERIC(7,2),   -- barometric pressure mmHg
    vws_m_s       NUMERIC(6,2),   -- vertical wind speed m/s

    FOREIGN KEY (station_id) REFERENCES stations(station_id),
    UNIQUE (station_id, reading_time)
);


-- ------------------------------------------------------------
-- TABLE 4 : pollutant_readings
-- One row per (station + timestamp + pollutant)
-- ------------------------------------------------------------
CREATE TABLE pollutant_readings (
    id             BIGSERIAL    PRIMARY KEY,
    station_id     VARCHAR(20)  NOT NULL,
    pollutant_code VARCHAR(20)  NOT NULL,
    reading_time   TIMESTAMPTZ  NOT NULL,
    value          NUMERIC(10,3),

    FOREIGN KEY (station_id)     REFERENCES stations(station_id),
    FOREIGN KEY (pollutant_code) REFERENCES pollutants(pollutant_code),
    UNIQUE (station_id, pollutant_code, reading_time)
);


-- ============================================================
-- INDEXES — speeds up queries on large tables
-- ============================================================
CREATE INDEX idx_weather_time         ON weather_readings  (reading_time);
CREATE INDEX idx_weather_station      ON weather_readings  (station_id);
CREATE INDEX idx_pollutant_time       ON pollutant_readings(reading_time);
CREATE INDEX idx_pollutant_station    ON pollutant_readings(station_id);
CREATE INDEX idx_pollutant_code       ON pollutant_readings(pollutant_code);


-- ============================================================
-- SEED DATA — fill pollutants lookup table
-- ============================================================
INSERT INTO pollutants (pollutant_code, pollutant_name, unit) VALUES
    ('pm25',        'Particulate Matter < 2.5µm',  'µg/m³'),
    ('pm10',        'Particulate Matter < 10µm',   'µg/m³'),
    ('no',          'Nitric Oxide',                'µg/m³'),
    ('no2',         'Nitrogen Dioxide',            'µg/m³'),
    ('nh3',         'Ammonia',                     'µg/m³'),
    ('so2',         'Sulfur Dioxide',              'µg/m³'),
    ('co',          'Carbon Monoxide',             'mg/m³'),
    ('ozone',       'Ozone',                       'µg/m³'),
    ('benzene',     'Benzene',                     'µg/m³'),
    ('toluene',     'Toluene',                     'µg/m³'),
    ('xylene',      'Xylene',                      'µg/m³'),
    ('eth_benzene', 'Ethyl Benzene',               'µg/m³'),
    ('mp_xylene',   'Meta/Para Xylene',            'µg/m³');

