-- =============================================================================
-- Air Canada CoCo HOL — Setup Script
-- Creates AC_HOL_DB with synthetic flight operations, booking, and loyalty data
-- Intentional data quality issues seeded for lab discovery exercises
-- =============================================================================

USE ROLE ACCOUNTADMIN;

-- ---------------------------------------------------------------------------
-- 1. Database and Schemas
-- ---------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS AC_HOL_DB;
CREATE SCHEMA IF NOT EXISTS AC_HOL_DB.OPERATIONS;
CREATE SCHEMA IF NOT EXISTS AC_HOL_DB.BOOKINGS;
CREATE SCHEMA IF NOT EXISTS AC_HOL_DB.LOYALTY;
CREATE SCHEMA IF NOT EXISTS AC_HOL_UAT;  -- simulates UAT environment

-- ---------------------------------------------------------------------------
-- 2. OPERATIONS.FLIGHTS
--    ~10,000 rows | DQ issues: NULL delay_reason (DELAYED flights), dup flight_ids
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE AC_HOL_DB.OPERATIONS.FLIGHTS (
    flight_id        VARCHAR(10),
    departure_airport CHAR(3),
    arrival_airport   CHAR(3),
    scheduled_departure TIMESTAMP_NTZ,
    actual_departure    TIMESTAMP_NTZ,
    scheduled_arrival   TIMESTAMP_NTZ,
    actual_arrival      TIMESTAMP_NTZ,
    aircraft_type    VARCHAR(10),
    status           VARCHAR(20),   -- ON_TIME, DELAYED, CANCELLED
    delay_minutes    NUMBER(5),
    delay_reason     VARCHAR(50),   -- intentional NULLs for ~200 DELAYED rows
    passengers_boarded NUMBER(4),
    capacity         NUMBER(4),
    load_date        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);

-- Seed data: 10 000 rows using Snowflake generator
INSERT INTO AC_HOL_DB.OPERATIONS.FLIGHTS (
    flight_id, departure_airport, arrival_airport,
    scheduled_departure, actual_departure,
    scheduled_arrival,   actual_arrival,
    aircraft_type, status, delay_minutes, delay_reason,
    passengers_boarded, capacity
)
WITH airports AS (
    SELECT column1 AS code FROM (VALUES
        ('YYZ'),('YVR'),('YUL'),('YYC'),('YEG'),
        ('YOW'),('YHZ'),('YWG'),('YQR'),('YXE'),
        ('LAX'),('JFK'),('ORD'),('LHR'),('CDG'),
        ('FRA'),('AMS'),('NRT'),('MEX'),('CUN')
    ) t
),
aircraft AS (
    SELECT column1 AS atype FROM (VALUES
        ('B737'),('B787'),('A319'),('A320'),('A321'),('E190'),('CRJ9')
    ) t
),
reasons AS (
    SELECT column1 AS reason FROM (VALUES
        ('WEATHER'),('ATC_DELAY'),('CREW'),('MAINTENANCE'),
        ('LATE_ARRIVAL'),('FUELING'),('CATERING')
    ) t
),
base AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY SEQ8()) AS rn,
        DATEADD('minute', (UNIFORM(0, 87600, RANDOM()))::INT, '2024-07-01'::TIMESTAMP_NTZ) AS sched_dep
    FROM TABLE(GENERATOR(ROWCOUNT => 10000))
),
raw AS (
    SELECT
        rn,
        'AC' || LPAD((UNIFORM(100, 9999, RANDOM()))::VARCHAR, 4, '0') AS flight_id,
        dep.code AS dep_ap,
        arr.code AS arr_ap,
        sched_dep,
        DATEADD('minute', (UNIFORM(-5, 180, RANDOM()))::INT, sched_dep) AS act_dep,
        DATEADD('minute', (UNIFORM(60, 600, RANDOM()))::INT, sched_dep) AS sched_arr,
        ac.atype AS aircraft_type,
        CASE
            WHEN UNIFORM(1, 10, RANDOM()) <= 7 THEN 'ON_TIME'
            WHEN UNIFORM(1, 10, RANDOM()) <= 9 THEN 'DELAYED'
            ELSE 'CANCELLED'
        END AS status,
        UNIFORM(1, 5, RANDOM()) AS dep_idx,
        UNIFORM(1, 5, RANDOM()) AS arr_idx,
        UNIFORM(1, 7, RANDOM()) AS ac_idx,
        UNIFORM(1, 7, RANDOM()) AS reason_idx
    FROM base
    JOIN airports dep ON dep.code = (SELECT code FROM airports ORDER BY RANDOM() LIMIT 1)
    JOIN airports arr ON arr.code != dep.code AND arr.code = (SELECT code FROM airports ORDER BY RANDOM() LIMIT 1)
    JOIN aircraft  ac  ON ac.atype = (SELECT atype FROM aircraft ORDER BY RANDOM() LIMIT 1)
)
SELECT
    r.flight_id,
    r.dep_ap,
    r.arr_ap,
    r.sched_dep,
    r.act_dep,
    r.sched_arr,
    DATEADD('minute', DATEDIFF('minute', r.sched_dep, r.act_dep) + (UNIFORM(30, 60, RANDOM()))::INT, r.sched_arr) AS act_arr,
    r.aircraft_type,
    r.status,
    CASE r.status
        WHEN 'ON_TIME'   THEN 0
        WHEN 'DELAYED'   THEN UNIFORM(15, 240, RANDOM())::INT
        ELSE NULL
    END AS delay_minutes,
    -- Intentional DQ issue: ~200 DELAYED flights have NULL delay_reason
    CASE
        WHEN r.status = 'DELAYED' AND UNIFORM(1, 10, RANDOM()) > 8 THEN NULL
        WHEN r.status = 'DELAYED' THEN (SELECT reason FROM (VALUES('WEATHER'),('ATC_DELAY'),('CREW'),('MAINTENANCE'),('LATE_ARRIVAL'),('FUELING'),('CATERING')) t(reason) ORDER BY RANDOM() LIMIT 1)
        ELSE NULL
    END AS delay_reason,
    UNIFORM(50, 180, RANDOM())::INT AS passengers_boarded,
    CASE r.aircraft_type
        WHEN 'B787' THEN 298
        WHEN 'B737' THEN 168
        WHEN 'A321' THEN 182
        WHEN 'A320' THEN 150
        WHEN 'A319' THEN 120
        WHEN 'E190' THEN 97
        ELSE 75
    END AS capacity
FROM raw r;

-- Inject ~50 duplicate flight_ids (same flight_id, different rows — simulates pipeline bug)
INSERT INTO AC_HOL_DB.OPERATIONS.FLIGHTS
SELECT
    flight_id,
    departure_airport,
    arrival_airport,
    DATEADD('hour', 1, scheduled_departure),
    DATEADD('hour', 1, actual_departure),
    DATEADD('hour', 1, scheduled_arrival),
    DATEADD('hour', 1, actual_arrival),
    aircraft_type,
    status,
    delay_minutes,
    delay_reason,
    passengers_boarded,
    capacity
FROM AC_HOL_DB.OPERATIONS.FLIGHTS
LIMIT 50;

-- ---------------------------------------------------------------------------
-- 3. BOOKINGS.RESERVATIONS
--    ~25,000 rows | DQ issue: ~100 NULL cabin_class
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE AC_HOL_DB.BOOKINGS.RESERVATIONS (
    booking_id         VARCHAR(15),
    flight_id          VARCHAR(10),
    customer_id        NUMBER(8),
    booking_date       TIMESTAMP_NTZ,
    cabin_class        VARCHAR(10),    -- ECONOMY, PREMIUM, BUSINESS | ~100 NULLs
    ticket_price       NUMBER(10,2),
    ancillary_revenue  NUMBER(8,2),
    check_in_status    VARCHAR(20),
    baggage_weight_kg  NUMBER(5,1),
    is_aeroplan_member BOOLEAN,
    load_date          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO AC_HOL_DB.BOOKINGS.RESERVATIONS (
    booking_id, flight_id, customer_id, booking_date, cabin_class,
    ticket_price, ancillary_revenue, check_in_status,
    baggage_weight_kg, is_aeroplan_member
)
WITH flights_sample AS (
    SELECT DISTINCT flight_id FROM AC_HOL_DB.OPERATIONS.FLIGHTS LIMIT 2000
),
base AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY SEQ8()) AS rn,
        'BK' || LPAD((UNIFORM(1000000, 9999999, RANDOM()))::VARCHAR, 8, '0') AS booking_id,
        UNIFORM(1, 2000000, RANDOM())::INT AS customer_id,
        DATEADD('day', -(UNIFORM(1, 365, RANDOM()))::INT, CURRENT_DATE) AS booking_date
    FROM TABLE(GENERATOR(ROWCOUNT => 25000))
)
SELECT
    b.booking_id,
    (SELECT flight_id FROM flights_sample ORDER BY RANDOM() LIMIT 1) AS flight_id,
    b.customer_id,
    b.booking_date,
    -- Intentional DQ issue: ~100 NULL cabin_class
    CASE
        WHEN UNIFORM(1, 250, RANDOM()) = 1 THEN NULL
        WHEN UNIFORM(1, 10, RANDOM()) <= 7 THEN 'ECONOMY'
        WHEN UNIFORM(1, 10, RANDOM()) <= 9 THEN 'PREMIUM'
        ELSE 'BUSINESS'
    END AS cabin_class,
    CASE
        WHEN UNIFORM(1, 10, RANDOM()) <= 7 THEN ROUND(UNIFORM(180, 650, RANDOM())::FLOAT, 2)
        WHEN UNIFORM(1, 10, RANDOM()) <= 9 THEN ROUND(UNIFORM(650, 1800, RANDOM())::FLOAT, 2)
        ELSE ROUND(UNIFORM(1800, 5500, RANDOM())::FLOAT, 2)
    END AS ticket_price,
    ROUND(UNIFORM(0, 250, RANDOM())::FLOAT, 2) AS ancillary_revenue,
    CASE UNIFORM(1, 4, RANDOM())
        WHEN 1 THEN 'CHECKED_IN'
        WHEN 2 THEN 'NOT_CHECKED_IN'
        WHEN 3 THEN 'BOARDED'
        ELSE 'NO_SHOW'
    END AS check_in_status,
    ROUND(UNIFORM(5, 32, RANDOM())::FLOAT, 1) AS baggage_weight_kg,
    (UNIFORM(0, 1, RANDOM()) = 1) AS is_aeroplan_member
FROM base b;

-- ---------------------------------------------------------------------------
-- 4. LOYALTY.AEROPLAN_MEMBERS
--    ~5,000 rows | DQ issue: ~30 rows with negative points_balance
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE AC_HOL_DB.LOYALTY.AEROPLAN_MEMBERS (
    customer_id      NUMBER(8) PRIMARY KEY,
    member_since     DATE,
    tier             VARCHAR(20),
    points_balance   NUMBER(10),   -- intentional ~30 negative values
    lifetime_miles   NUMBER(12),
    preferred_seat   VARCHAR(5),
    email_opted_in   BOOLEAN,
    load_date        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO AC_HOL_DB.LOYALTY.AEROPLAN_MEMBERS (
    customer_id, member_since, tier,
    points_balance, lifetime_miles, preferred_seat, email_opted_in
)
WITH base AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY SEQ8()) AS rn
    FROM TABLE(GENERATOR(ROWCOUNT => 5000))
)
SELECT
    rn AS customer_id,
    DATEADD('day', -(UNIFORM(1, 7300, RANDOM()))::INT, CURRENT_DATE) AS member_since,
    CASE UNIFORM(1, 10, RANDOM())
        WHEN 1 THEN 'SUPER_ELITE'
        WHEN 2 THEN 'ALTITUDE_75K'
        WHEN 3 THEN 'ALTITUDE_50K'
        WHEN 4 THEN 'ALTITUDE_35K'
        WHEN 5 THEN 'ALTITUDE_25K'
        ELSE 'STANDARD'
    END AS tier,
    -- Intentional DQ issue: ~30 rows with negative points_balance
    CASE
        WHEN UNIFORM(1, 170, RANDOM()) = 1 THEN -1 * UNIFORM(100, 50000, RANDOM())::INT
        ELSE UNIFORM(0, 500000, RANDOM())::INT
    END AS points_balance,
    UNIFORM(0, 2000000, RANDOM())::INT AS lifetime_miles,
    CASE UNIFORM(1, 6, RANDOM())
        WHEN 1 THEN 'WINDOW'
        WHEN 2 THEN 'AISLE'
        WHEN 3 THEN 'MIDDLE'
        WHEN 4 THEN 'EXIT'
        WHEN 5 THEN 'BULKHEAD'
        ELSE NULL
    END AS preferred_seat,
    (UNIFORM(0, 1, RANDOM()) = 1) AS email_opted_in
FROM base;

-- ---------------------------------------------------------------------------
-- 5. AC_HOL_UAT schema — simulates UAT pipeline (intentional differences)
--    - 2 columns removed (aircraft_type, delay_reason dropped)
--    - ~9,500 rows instead of 10,050 (pipeline lag)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE AC_HOL_UAT.FLIGHTS (
    flight_id          VARCHAR(10),
    departure_airport  CHAR(3),
    arrival_airport    CHAR(3),
    scheduled_departure TIMESTAMP_NTZ,
    actual_departure    TIMESTAMP_NTZ,
    scheduled_arrival   TIMESTAMP_NTZ,
    actual_arrival      TIMESTAMP_NTZ,
    -- NOTE: aircraft_type and delay_reason columns removed in UAT (simulates schema drift)
    status             VARCHAR(20),
    delay_minutes      NUMBER(5),
    passengers_boarded NUMBER(4),
    capacity           NUMBER(4),
    load_date          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO AC_HOL_UAT.FLIGHTS (
    flight_id, departure_airport, arrival_airport,
    scheduled_departure, actual_departure,
    scheduled_arrival, actual_arrival,
    status, delay_minutes, passengers_boarded, capacity
)
SELECT
    flight_id, departure_airport, arrival_airport,
    scheduled_departure, actual_departure,
    scheduled_arrival, actual_arrival,
    status, delay_minutes, passengers_boarded, capacity
FROM AC_HOL_DB.OPERATIONS.FLIGHTS
LIMIT 9500;  -- 500+ fewer rows than PROD to simulate pipeline lag

-- ---------------------------------------------------------------------------
-- 6. OPERATIONS.FLIGHT_ROUTES (lookup / reference table)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE AC_HOL_DB.OPERATIONS.FLIGHT_ROUTES (
    route_id    NUMBER AUTOINCREMENT,
    origin      CHAR(3),
    destination CHAR(3),
    distance_km NUMBER(5),
    avg_duration_min NUMBER(4)
);

INSERT INTO AC_HOL_DB.OPERATIONS.FLIGHT_ROUTES (origin, destination, distance_km, avg_duration_min) VALUES
    ('YYZ','YVR',3360,295),('YYZ','YUL',540,90),('YYZ','YYC',2700,245),
    ('YYZ','LAX',4400,325),('YYZ','JFK',560,90),('YYZ','LHR',5700,470),
    ('YYZ','CDG',6200,490),('YYZ','FRA',6340,500),('YYZ','NRT',11200,830),
    ('YVR','YYZ',3360,295),('YVR','LAX',1750,155),('YVR','NRT',8200,600),
    ('YUL','YYZ',540,90),('YUL','CDG',5530,430),('YUL','LHR',5250,415),
    ('YYC','YYZ',2700,245),('YYC','YVR',680,80),('YEG','YYZ',2800,250),
    ('YOW','YYZ',350,65),('YHZ','YYZ',1280,145);

-- ---------------------------------------------------------------------------
-- 7. Verify row counts
-- ---------------------------------------------------------------------------
SELECT 'OPERATIONS.FLIGHTS'           AS tbl, COUNT(*) AS rows FROM AC_HOL_DB.OPERATIONS.FLIGHTS
UNION ALL
SELECT 'BOOKINGS.RESERVATIONS',        COUNT(*) FROM AC_HOL_DB.BOOKINGS.RESERVATIONS
UNION ALL
SELECT 'LOYALTY.AEROPLAN_MEMBERS',     COUNT(*) FROM AC_HOL_DB.LOYALTY.AEROPLAN_MEMBERS
UNION ALL
SELECT 'AC_HOL_UAT.FLIGHTS',           COUNT(*) FROM AC_HOL_UAT.FLIGHTS
UNION ALL
SELECT 'OPERATIONS.FLIGHT_ROUTES',     COUNT(*) FROM AC_HOL_DB.OPERATIONS.FLIGHT_ROUTES;
