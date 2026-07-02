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
CREATE SCHEMA IF NOT EXISTS AC_HOL_DB.AC_HOL_UAT;  -- simulates UAT environment

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

-- Seed data: 10,000 rows using deterministic index-based random selection
INSERT INTO AC_HOL_DB.OPERATIONS.FLIGHTS (
    flight_id, departure_airport, arrival_airport,
    scheduled_departure, actual_departure,
    scheduled_arrival, actual_arrival,
    aircraft_type, status, delay_minutes, delay_reason,
    passengers_boarded, capacity
)
WITH airports AS (
    SELECT column1 AS code, ROW_NUMBER() OVER (ORDER BY column1) AS idx FROM (VALUES
        ('YYZ'),('YVR'),('YUL'),('YYC'),('YEG'),
        ('YOW'),('YHZ'),('YWG'),('YQR'),('YXE'),
        ('LAX'),('JFK'),('ORD'),('LHR'),('CDG'),
        ('FRA'),('AMS'),('NRT'),('MEX'),('CUN')
    ) t
),
aircraft AS (
    SELECT column1 AS atype, ROW_NUMBER() OVER (ORDER BY column1) AS idx FROM (VALUES
        ('B737'),('B787'),('A319'),('A320'),('A321'),('E190'),('CRJ9')
    ) t
),
base AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY SEQ8()) AS rn,
        DATEADD('minute', (UNIFORM(0, 87600, RANDOM()))::INT, '2024-07-01'::TIMESTAMP_NTZ) AS sched_dep,
        UNIFORM(1, 20, RANDOM()) AS dep_idx,
        UNIFORM(1, 20, RANDOM()) AS arr_idx,
        UNIFORM(1, 7, RANDOM()) AS ac_idx,
        CASE
            WHEN UNIFORM(1, 100, RANDOM()) <= 70 THEN 'ON_TIME'
            WHEN UNIFORM(1, 100, RANDOM()) <= 85 THEN 'DELAYED'
            ELSE 'CANCELLED'
        END AS status
    FROM TABLE(GENERATOR(ROWCOUNT => 10000))
)
SELECT
    'AC' || LPAD(rn::VARCHAR, 5, '0') AS flight_id,
    dep.code AS departure_airport,
    arr.code AS arrival_airport,
    b.sched_dep AS scheduled_departure,
    DATEADD('minute', (UNIFORM(-5, 180, RANDOM()))::INT, b.sched_dep) AS actual_departure,
    DATEADD('minute', (UNIFORM(60, 600, RANDOM()))::INT, b.sched_dep) AS scheduled_arrival,
    DATEADD('minute', (UNIFORM(90, 660, RANDOM()))::INT, b.sched_dep) AS actual_arrival,
    ac.atype AS aircraft_type,
    b.status,
    CASE b.status
        WHEN 'ON_TIME' THEN 0
        WHEN 'DELAYED' THEN UNIFORM(15, 240, RANDOM())::INT
        ELSE NULL
    END AS delay_minutes,
    -- Intentional DQ issue: ~8% of DELAYED flights have NULL delay_reason (~200 rows)
    CASE
        WHEN b.status = 'DELAYED' AND UNIFORM(1, 100, RANDOM()) <= 8 THEN NULL
        WHEN b.status = 'DELAYED' THEN
            CASE UNIFORM(1, 7, RANDOM())
                WHEN 1 THEN 'WEATHER'
                WHEN 2 THEN 'ATC_DELAY'
                WHEN 3 THEN 'CREW'
                WHEN 4 THEN 'MAINTENANCE'
                WHEN 5 THEN 'LATE_ARRIVAL'
                WHEN 6 THEN 'FUELING'
                ELSE 'CATERING'
            END
        ELSE NULL
    END AS delay_reason,
    UNIFORM(50, 180, RANDOM())::INT AS passengers_boarded,
    CASE ac.atype
        WHEN 'B787' THEN 298
        WHEN 'B737' THEN 168
        WHEN 'A321' THEN 182
        WHEN 'A320' THEN 150
        WHEN 'A319' THEN 120
        WHEN 'E190' THEN 97
        ELSE 75
    END AS capacity
FROM base b
JOIN airports dep ON dep.idx = b.dep_idx
JOIN airports arr ON arr.idx = CASE WHEN b.arr_idx = b.dep_idx THEN MOD(b.arr_idx, 20) + 1 ELSE b.arr_idx END
JOIN aircraft ac ON ac.idx = b.ac_idx;

-- Inject ~50 duplicate flight_ids (same flight_id, different rows — simulates pipeline bug)
INSERT INTO AC_HOL_DB.OPERATIONS.FLIGHTS (
    flight_id, departure_airport, arrival_airport,
    scheduled_departure, actual_departure,
    scheduled_arrival, actual_arrival,
    aircraft_type, status, delay_minutes, delay_reason,
    passengers_boarded, capacity
)
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
WITH flights_indexed AS (
    SELECT flight_id, ROW_NUMBER() OVER (ORDER BY flight_id) - 1 AS idx
    FROM (SELECT DISTINCT flight_id FROM AC_HOL_DB.OPERATIONS.FLIGHTS)
),
base AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY SEQ8()) AS rn,
        'BK' || LPAD((UNIFORM(1000000, 9999999, RANDOM()))::VARCHAR, 8, '0') AS booking_id,
        DATEADD('day', -(UNIFORM(1, 365, RANDOM()))::INT, CURRENT_DATE) AS booking_date,
        ABS(HASH(RANDOM())) AS rand_val,
        (UNIFORM(0, 1, RANDOM()) = 1) AS is_aeroplan
    FROM TABLE(GENERATOR(ROWCOUNT => 25000))
)
SELECT
    b.booking_id,
    f.flight_id,
    -- Ensure Aeroplan members have customer_id in range 1-5000 (matches LOYALTY table)
    CASE WHEN b.is_aeroplan THEN UNIFORM(1, 5000, RANDOM())::INT
         ELSE UNIFORM(5001, 2000000, RANDOM())::INT
    END AS customer_id,
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
    b.is_aeroplan AS is_aeroplan_member
FROM base b
JOIN flights_indexed f ON f.idx = MOD(b.rand_val, (SELECT COUNT(DISTINCT flight_id) FROM AC_HOL_DB.OPERATIONS.FLIGHTS));

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
    preferred_seat   VARCHAR(10),
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
CREATE OR REPLACE TABLE AC_HOL_DB.AC_HOL_UAT.FLIGHTS (
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

INSERT INTO AC_HOL_DB.AC_HOL_UAT.FLIGHTS (
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
SELECT 'OPERATIONS.FLIGHTS'           AS tbl, COUNT(*) AS row_count FROM AC_HOL_DB.OPERATIONS.FLIGHTS
UNION ALL
SELECT 'BOOKINGS.RESERVATIONS',        COUNT(*) FROM AC_HOL_DB.BOOKINGS.RESERVATIONS
UNION ALL
SELECT 'LOYALTY.AEROPLAN_MEMBERS',     COUNT(*) FROM AC_HOL_DB.LOYALTY.AEROPLAN_MEMBERS
UNION ALL
SELECT 'AC_HOL_UAT.FLIGHTS',           COUNT(*) FROM AC_HOL_DB.AC_HOL_UAT.FLIGHTS
UNION ALL
SELECT 'OPERATIONS.FLIGHT_ROUTES',     COUNT(*) FROM AC_HOL_DB.OPERATIONS.FLIGHT_ROUTES;
