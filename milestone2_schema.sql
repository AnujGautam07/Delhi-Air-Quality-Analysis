-- ============================================================
-- MILESTONE 2 : PostgreSQL Schema
-- Team Matatizo — Delhi Air Quality Dataset (2024–2025)
-- ============================================================

CREATE SCHEMA IF NOT EXISTS air_quality;
SET search_path TO air_quality, public;

DROP TABLE IF EXISTS pollutant_readings CASCADE;
DROP TABLE IF EXISTS weather_readings   CASCADE;
DROP TABLE IF EXISTS pollutants         CASCADE;
DROP TABLE IF EXISTS stations           CASCADE;

-- Table 1: stations (dimension)
CREATE TABLE stations (
    station_id    VARCHAR(20)  PRIMARY KEY,
    station_name  VARCHAR(150) NOT NULL,
    city          VARCHAR(100) NOT NULL,
    state         VARCHAR(100) NOT NULL
);

-- Table 2: pollutants (lookup)
CREATE TABLE pollutants (
    pollutant_code VARCHAR(20)  PRIMARY KEY,
    pollutant_name VARCHAR(100) NOT NULL,
    unit           VARCHAR(20)
);

-- Table 3: weather_readings
CREATE TABLE weather_readings (
    id            BIGSERIAL    PRIMARY KEY,
    station_id    VARCHAR(20)  NOT NULL,
    reading_time  TIMESTAMPTZ  NOT NULL,
    at_c          NUMERIC(6,2),
    rh_percent    NUMERIC(6,2),
    ws_m_s        NUMERIC(6,2),
    wd_deg        NUMERIC(6,2),
    rf_mm         NUMERIC(6,2),
    tot_rf_mm     NUMERIC(8,2),
    sr_w_mt2      NUMERIC(7,2),
    bp_mmhg       NUMERIC(7,2),
    vws_m_s       NUMERIC(6,2),

    FOREIGN KEY (station_id) REFERENCES stations(station_id),
    UNIQUE (station_id, reading_time)
);

-- Table 4: pollutant_readings
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

-- Indexes
CREATE INDEX idx_weather_time         ON weather_readings  (reading_time);
CREATE INDEX idx_weather_station      ON weather_readings  (station_id);
CREATE INDEX idx_pollutant_time       ON pollutant_readings(reading_time);
CREATE INDEX idx_pollutant_station    ON pollutant_readings(station_id);
CREATE INDEX idx_pollutant_code       ON pollutant_readings(pollutant_code);

-- Seed pollutants
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
