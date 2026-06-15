"""
03_load_to_rds.py — Phase 4: Load cleaned data into the RDS star schema
==================================================================================
Loads data/processed/hdhi_admission_cleaned.csv (or the S3 copy) into:
  dim_patient (12,244) → dim_date (730) → fact_admissions (15,757)
Ported from the tested backup loader: drop_duplicates for patients, date-attribute
build, 0/1→bool conversion, NaT/NaN→None, batched ON CONFLICT DO NOTHING inserts.
==================================================================================
"""

import io
import os
import sys
from pathlib import Path
import logging

import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
import boto3
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

BUCKET = os.getenv("S3_BUCKET")
PROCESSED_PREFIX = os.getenv("S3_PROCESSED_PREFIX", "processed/")
REGION = os.getenv("AWS_REGION", "ap-south-1")
OUT_KEY = f"{PROCESSED_PREFIX}hdhi_admission_cleaned.csv"
LOCAL_CSV = Path("data") / "processed" / "hdhi_admission_cleaned.csv"

CAL_Q = {1: "Q1", 2: "Q1", 3: "Q1", 4: "Q2", 5: "Q2", 6: "Q2",
         7: "Q3", 8: "Q3", 9: "Q3", 10: "Q4", 11: "Q4", 12: "Q4"}
FY_Q = {4: "Q1", 5: "Q1", 6: "Q1", 7: "Q2", 8: "Q2", 9: "Q2",
        10: "Q3", 11: "Q3", 12: "Q3", 1: "Q4", 2: "Q4", 3: "Q4"}
SEASON = {3: "Summer", 4: "Summer", 5: "Summer",
          6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
          10: "Post-Monsoon", 11: "Post-Monsoon",
          12: "Winter", 1: "Winter", 2: "Winter"}

# fact_admissions columns in schema order
FACT_COLS = [
    "sno", "mrd_no", "admission_date", "discharge_date", "admission_type",
    "los_days", "icu_days", "outcome", "smoking", "alcohol", "diabetes",
    "hypertension", "cad", "prior_cmp", "ckd", "hb", "tlc", "platelets",
    "glucose", "urea", "creatinine", "bnp", "raised_cardiac_enzymes", "ef",
    "severe_anaemia", "anaemia", "stable_angina", "acs", "stemi",
    "atypical_chest_pain", "heart_failure", "hfref", "hfnef", "valvular", "chb",
    "sss", "aki", "cva_infract", "cva_bleed", "af", "vt", "psvt", "congenital",
    "uti", "neuro_cardiogenic_syncope", "orthostatic", "infective_endocarditis",
    "dvt", "cardiogenic_shock", "shock", "pulmonary_embolism", "chest_infection",
    "risk_score", "risk_category",
]
BOOL_COLS = {
    "smoking", "alcohol", "diabetes", "hypertension", "cad", "prior_cmp", "ckd",
    "raised_cardiac_enzymes", "severe_anaemia", "anaemia", "stable_angina", "acs",
    "stemi", "atypical_chest_pain", "heart_failure", "hfref", "hfnef", "valvular",
    "chb", "sss", "aki", "cva_infract", "cva_bleed", "af", "vt", "psvt",
    "congenital", "uti", "neuro_cardiogenic_syncope", "orthostatic",
    "infective_endocarditis", "dvt", "cardiogenic_shock", "shock",
    "pulmonary_embolism", "chest_infection",
}
INT_COLS = {"sno", "los_days", "icu_days", "risk_score"}
FLOAT_COLS = {"hb", "tlc", "platelets", "glucose", "urea", "creatinine", "bnp", "ef"}
DATE_COLS = {"admission_date", "discharge_date"}


def get_connection():
    return psycopg2.connect(
        host=os.getenv("RDS_HOST"),
        port=int(os.getenv("RDS_PORT", 5432)),
        database=os.getenv("RDS_DATABASE"),
        user=os.getenv("RDS_USERNAME"),
        password=os.getenv("RDS_PASSWORD"),
        connect_timeout=15,
    )


def load_clean_df():
    """Load cleaned CSV from S3, fall back to local."""
    try:
        if not BUCKET:
            raise RuntimeError("S3_BUCKET not set")
        s3 = boto3.client("s3", region_name=REGION)
        obj = s3.get_object(Bucket=BUCKET, Key=OUT_KEY)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()),
                         parse_dates=["admission_date", "discharge_date"])
        logger.info(f"Loaded from S3: s3://{BUCKET}/{OUT_KEY}  shape={df.shape}")
    except Exception as e:
        logger.warning(f"S3 load failed ({e}); using local file")
        df = pd.read_csv(LOCAL_CSV, parse_dates=["admission_date", "discharge_date"])
        logger.info(f"Loaded from local: {LOCAL_CSV}  shape={df.shape}")
    return df


def _date(x):
    return None if pd.isna(x) else pd.Timestamp(x).date()


def _int(x):
    return None if pd.isna(x) else int(x)


def _float(x):
    return None if pd.isna(x) else float(x)


def cell(col, value):
    if col in DATE_COLS:
        return _date(value)
    if col in BOOL_COLS:
        return None if pd.isna(value) else bool(int(value))
    if col in INT_COLS:
        return _int(value)
    if col in FLOAT_COLS:
        return _float(value)
    return None if pd.isna(value) else str(value)


def run_schema(conn):
    logger.info("Creating schema from sql/01_schema.sql ...")
    with conn.cursor() as cur, open("sql/01_schema.sql", encoding="utf-8") as f:
        cur.execute(f.read())
    conn.commit()
    logger.info("Schema created: dim_patient, dim_date, fact_admissions")


def insert_batched(cur, sql, rows, batch):
    for i in range(0, len(rows), batch):
        execute_values(cur, sql, rows[i:i + batch], page_size=batch)


def main():
    df = load_clean_df()
    conn = get_connection()
    conn.autocommit = False
    try:
        run_schema(conn)
        cur = conn.cursor()

        # ---- dim_patient (unique by mrd_no, keep first) ----
        dp = df.drop_duplicates(subset="mrd_no", keep="first")
        patient_rows = [(str(r.mrd_no), _int(r.age), r.age_group, r.gender, r.locality)
                        for r in dp.itertuples(index=False)]
        insert_batched(cur,
                       "INSERT INTO dim_patient (mrd_no, age, age_group, gender, locality) "
                       "VALUES %s ON CONFLICT (mrd_no) DO NOTHING", patient_rows, 500)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM dim_patient")
        n_patient = cur.fetchone()[0]
        logger.info(f"dim_patient: {n_patient} rows")
        assert n_patient == 12244, f"dim_patient count wrong: {n_patient}"

        # ---- dim_date (unique admission dates) ----
        dates = pd.to_datetime(pd.Series(df["admission_date"].dropna().unique())).sort_values()
        date_rows = []
        for ts in dates:
            d = ts.date()
            date_rows.append((d, d.strftime("%A"), d.strftime("%B"), d.month, d.year,
                              CAL_Q[d.month], FY_Q[d.month], SEASON[d.month], d.weekday() >= 5))
        insert_batched(cur,
                       "INSERT INTO dim_date (date_id, day_name, month_name, month_num, year, "
                       "quarter, fiscal_quarter, season, is_weekend) VALUES %s "
                       "ON CONFLICT (date_id) DO NOTHING", date_rows, 100)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM dim_date")
        n_date = cur.fetchone()[0]
        logger.info(f"dim_date: {n_date} rows")
        assert n_date == 730, f"dim_date count wrong: {n_date}"

        # ---- fact_admissions (all columns) ----
        fact_rows = [tuple(cell(c, getattr(r, c)) for c in FACT_COLS)
                     for r in df.itertuples(index=False)]
        cols = ", ".join(FACT_COLS)
        insert_batched(cur,
                       f"INSERT INTO fact_admissions ({cols}) VALUES %s "
                       f"ON CONFLICT (sno) DO NOTHING", fact_rows, 500)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM fact_admissions")
        n_fact = cur.fetchone()[0]
        logger.info(f"fact_admissions: {n_fact} rows")
        assert n_fact == 15757, f"fact_admissions count wrong: {n_fact}"

        # ---- FK integrity ----
        cur.execute("SELECT COUNT(*) FROM fact_admissions f "
                    "LEFT JOIN dim_patient p ON f.mrd_no = p.mrd_no WHERE p.mrd_no IS NULL")
        orphan_patient = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM fact_admissions f "
                    "LEFT JOIN dim_date d ON f.admission_date = d.date_id WHERE d.date_id IS NULL")
        orphan_date = cur.fetchone()[0]
        assert orphan_patient == 0, f"Orphaned patient FKs: {orphan_patient}"
        assert orphan_date == 0, f"Orphaned date FKs: {orphan_date}"
        logger.info(f"FK integrity: patient orphans={orphan_patient}, date orphans={orphan_date}")

        # ---- outcome verification ----
        cur.execute("SELECT outcome, COUNT(*) FROM fact_admissions GROUP BY outcome ORDER BY COUNT(*) DESC")
        outcomes = dict(cur.fetchall())
        assert outcomes.get("Discharged") == 13756, f"Discharged wrong: {outcomes}"
        assert outcomes.get("Expired") == 1105, f"Expired wrong: {outcomes}"
        assert outcomes.get("DAMA") == 896, f"DAMA wrong: {outcomes}"

        cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print("\n=== PHASE 4 LOADING COMPLETE ===")
    print(f"dim_patient:      {n_patient:,} rows")
    print(f"dim_date:            {n_date:,} rows")
    print(f"fact_admissions: {n_fact:,} rows")
    print("FK integrity:    PASSED")
    print("Outcome counts:  PASSED")


if __name__ == "__main__":
    main()
