-- ============================================================
-- HOSPIQ Database Schema
-- Hero DMC Heart Institute Cardiac Analytics
-- Star Schema: 2 dimension tables + 1 fact table
-- ============================================================

-- Drop in reverse FK order (fact first then dims)
DROP TABLE IF EXISTS fact_admissions;
DROP TABLE IF EXISTS dim_patient;
DROP TABLE IF EXISTS dim_date;

-- ============================================================
-- DIMENSION TABLE 1: dim_patient
-- One row per unique patient (by MRD No.)
-- Expected rows: 12,244
-- ============================================================
CREATE TABLE dim_patient (
    mrd_no          VARCHAR(20) PRIMARY KEY,
    age             INTEGER,
    age_group       VARCHAR(20),
    gender          VARCHAR(10),
    locality        VARCHAR(10)
);

-- ============================================================
-- DIMENSION TABLE 2: dim_date
-- One row per unique admission date
-- Expected rows: 730
-- Covers April 2017 to March 2019 (2 Indian fiscal years)
-- ============================================================
CREATE TABLE dim_date (
    date_id         DATE PRIMARY KEY,
    day_name        VARCHAR(10),
    month_name      VARCHAR(10),
    month_num       INTEGER,
    year            INTEGER,
    quarter         VARCHAR(5),
    fiscal_quarter  VARCHAR(5),
    season          VARCHAR(20),
    is_weekend      BOOLEAN
);

-- ============================================================
-- FACT TABLE: fact_admissions
-- One row per cardiac admission
-- Expected rows: 15,757
-- ============================================================
CREATE TABLE fact_admissions (
    sno                       INTEGER PRIMARY KEY,
    mrd_no                    VARCHAR(20) REFERENCES dim_patient(mrd_no),
    admission_date            DATE REFERENCES dim_date(date_id),
    discharge_date            DATE,
    admission_type            VARCHAR(20),
    los_days                  INTEGER,
    icu_days                  INTEGER,
    outcome                   VARCHAR(20),
    smoking                   BOOLEAN,
    alcohol                   BOOLEAN,
    diabetes                  BOOLEAN,
    hypertension              BOOLEAN,
    cad                       BOOLEAN,
    prior_cmp                 BOOLEAN,
    ckd                       BOOLEAN,
    hb                        NUMERIC(6,2),
    tlc                       NUMERIC(10,2),
    platelets                 NUMERIC(10,2),
    glucose                   NUMERIC(8,2),
    urea                      NUMERIC(8,2),
    creatinine                NUMERIC(6,2),
    bnp                       NUMERIC(10,2),
    raised_cardiac_enzymes    BOOLEAN,
    ef                        NUMERIC(6,2),
    severe_anaemia            BOOLEAN,
    anaemia                   BOOLEAN,
    stable_angina             BOOLEAN,
    acs                       BOOLEAN,
    stemi                     BOOLEAN,
    atypical_chest_pain       BOOLEAN,
    heart_failure             BOOLEAN,
    hfref                     BOOLEAN,
    hfnef                     BOOLEAN,
    valvular                  BOOLEAN,
    chb                       BOOLEAN,
    sss                       BOOLEAN,
    aki                       BOOLEAN,
    cva_infract               BOOLEAN,
    cva_bleed                 BOOLEAN,
    af                        BOOLEAN,
    vt                        BOOLEAN,
    psvt                      BOOLEAN,
    congenital                BOOLEAN,
    uti                       BOOLEAN,
    neuro_cardiogenic_syncope BOOLEAN,
    orthostatic               BOOLEAN,
    infective_endocarditis    BOOLEAN,
    dvt                       BOOLEAN,
    cardiogenic_shock         BOOLEAN,
    shock                     BOOLEAN,
    pulmonary_embolism        BOOLEAN,
    chest_infection           BOOLEAN,
    risk_score                INTEGER,
    risk_category             VARCHAR(20)
);
