"""
02_clean_transform.py — Phase 2: Data Cleaning
==================================================================================
Cleans the raw HDHI cardiac admission data into an analysis-ready dataset.

Key issues handled (identified in Phase 1 EDA):
  1. D.O.A mixes M/D/YYYY (early) and D/M/YYYY (late) — disambiguated using the
     reliable 'month year' column (ported, tested logic).
  2. Lab columns store the literal string "EMPTY" instead of NaN.
  3. BNP (53.57% null) and EF (9.55% null) plus other labs — median-filled.

Input  : s3://<S3_BUCKET>/raw/HDHI Admission data.csv  (fallback: data/raw/)
Output : data/processed/hdhi_admission_cleaned.csv  (+ S3 processed/ if available)
Next   : 03_load_to_rds.py
==================================================================================
"""

# ---------------------------------------------------------------- Step 1: setup
import io
import os
import sys
import logging

# Ensure UTF-8 console output (Windows defaults to cp1252, which cannot print ✅).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd
import numpy as np
import boto3
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s — %(levelname)s — %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

BUCKET = os.getenv("S3_BUCKET")
RAW_PREFIX = os.getenv("S3_RAW_PREFIX", "raw/")
PROCESSED_PREFIX = os.getenv("S3_PROCESSED_PREFIX", "processed/")
REGION = os.getenv("AWS_REGION", "ap-south-1")

RAW_KEY = f"{RAW_PREFIX}HDHI Admission data.csv"
OUT_KEY = f"{PROCESSED_PREFIX}hdhi_admission_cleaned.csv"
LOCAL_RAW = os.path.join("data", "raw", "HDHI Admission data.csv")
LOCAL_OUT = os.path.join("data", "processed", "hdhi_admission_cleaned.csv")

LAB_COLS_RAW = ["HB", "TLC", "PLATELETS", "GLUCOSE", "UREA", "CREATININE", "BNP", "EF"]
LAB_COLS = ["hb", "tlc", "platelets", "glucose", "urea", "creatinine", "bnp", "ef"]

# Binary clinical flag columns (post-rename) — coerced to clean 0/1.
FLAG_COLS = [
    "smoking", "alcohol", "diabetes", "hypertension", "cad", "prior_cmp", "ckd",
    "raised_cardiac_enzymes", "severe_anaemia", "anaemia", "stable_angina", "acs",
    "stemi", "atypical_chest_pain", "heart_failure", "hfref", "hfnef", "valvular",
    "chb", "sss", "aki", "cva_infract", "cva_bleed", "af", "vt", "psvt",
    "congenital", "uti", "neuro_cardiogenic_syncope", "orthostatic",
    "infective_endocarditis", "dvt", "cardiogenic_shock", "shock",
    "pulmonary_embolism", "chest_infection",
]

COLUMN_MAP = {
    'SNO': 'sno', 'MRD No.': 'mrd_no', 'D.O.A': 'admission_date',
    'D.O.D': 'discharge_date', 'AGE': 'age', 'GENDER': 'gender', 'RURAL': 'locality',
    'TYPE OF ADMISSION-EMERGENCY/OPD': 'admission_type', 'month year': 'month_year',
    'DURATION OF STAY': 'los_days', 'duration of intensive unit stay': 'icu_days',
    'OUTCOME': 'outcome', 'SMOKING ': 'smoking', 'ALCOHOL': 'alcohol', 'DM': 'diabetes',
    'HTN': 'hypertension', 'CAD': 'cad', 'PRIOR CMP': 'prior_cmp', 'CKD': 'ckd',
    'HB': 'hb', 'TLC': 'tlc', 'PLATELETS': 'platelets', 'GLUCOSE': 'glucose',
    'UREA': 'urea', 'CREATININE': 'creatinine', 'BNP': 'bnp',
    'RAISED CARDIAC ENZYMES': 'raised_cardiac_enzymes', 'EF': 'ef',
    'SEVERE ANAEMIA': 'severe_anaemia', 'ANAEMIA': 'anaemia',
    'STABLE ANGINA': 'stable_angina', 'ACS': 'acs', 'STEMI': 'stemi',
    'ATYPICAL CHEST PAIN': 'atypical_chest_pain', 'HEART FAILURE': 'heart_failure',
    'HFREF': 'hfref', 'HFNEF': 'hfnef', 'VALVULAR': 'valvular', 'CHB': 'chb',
    'SSS': 'sss', 'AKI': 'aki', 'CVA INFRACT': 'cva_infract', 'CVA BLEED': 'cva_bleed',
    'AF': 'af', 'VT': 'vt', 'PSVT': 'psvt', 'CONGENITAL': 'congenital', 'UTI': 'uti',
    'NEURO CARDIOGENIC SYNCOPE': 'neuro_cardiogenic_syncope', 'ORTHOSTATIC': 'orthostatic',
    'INFECTIVE ENDOCARDITIS': 'infective_endocarditis', 'DVT': 'dvt',
    'CARDIOGENIC SHOCK': 'cardiogenic_shock', 'SHOCK': 'shock',
    'PULMONARY EMBOLISM': 'pulmonary_embolism', 'CHEST INFECTION': 'chest_infection',
}

SEASON_BY_MONTH = {3: "Summer", 4: "Summer", 5: "Summer",
                   6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
                   10: "Post-Monsoon", 11: "Post-Monsoon",
                   12: "Winter", 1: "Winter", 2: "Winter"}


# ----------------------------------------------- ported tested date-parse logic
def parse_admission_date(doa_raw, month_year):
    """D.O.A mixes M/D/YYYY (early) and D/M/YYYY (late). Use the reliable
    'month year' label (e.g. 'Apr-17') to pick the correct parse per row.
    Returns (series, n_dayfirst_false, n_fallback_true, n_failed)."""
    ref = pd.to_datetime(month_year, format="%b-%y", errors="coerce")
    pf = pd.to_datetime(doa_raw, format="mixed", dayfirst=False, errors="coerce")
    pt = pd.to_datetime(doa_raw, format="mixed", dayfirst=True, errors="coerce")
    matches = (pf.dt.year == ref.dt.year) & (pf.dt.month == ref.dt.month)
    result = pf.where(matches, pt)
    n_false = int(matches.sum())                 # rows the simple parse got right
    n_fallback = int((~matches).sum())           # rows that needed the D/M fallback
    n_failed = int(result.isna().sum())          # rows still unparseable
    return result, n_false, n_fallback, n_failed


def parse_discharge_date(dod_raw, admission_date):
    """D.O.D has the same mixed-format issue but no reference column; choose the
    parse that lands on/after admission."""
    a = pd.to_datetime(dod_raw, format="mixed", dayfirst=False, errors="coerce")
    b = pd.to_datetime(dod_raw, format="mixed", dayfirst=True, errors="coerce")
    return a.where(a >= admission_date, b)


# --------------------------------------------------------- Step 2: load (S3 → local)
def load_data():
    try:
        if not BUCKET:
            raise RuntimeError("S3_BUCKET not set in .env")
        s3 = boto3.client("s3", region_name=REGION)
        obj = s3.get_object(Bucket=BUCKET, Key=RAW_KEY)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        logger.info(f"Loaded from S3: s3://{BUCKET}/{RAW_KEY}")
        return df
    except Exception as e:
        logger.warning(f"S3 load failed ({e}); falling back to local file")
        df = pd.read_csv(LOCAL_RAW)
        logger.info(f"Loaded from local: {LOCAL_RAW}")
        return df


def main():
    df = load_data()

    # ------------------------------------------------ Step 3: pre-cleaning snapshot
    logger.info("=== PRE-CLEANING SNAPSHOT ===")
    logger.info(f"Shape: {df.shape}")
    snap_cols = ["BNP", "EF", "HB", "TLC", "PLATELETS", "UREA", "CREATININE", "GLUCOSE"]
    logger.info("Null counts (raw):")
    for c in snap_cols:
        logger.info(f"  {c}: {int(df[c].isnull().sum())} nulls")
    logger.info(f"Sample D.O.A values: {df['D.O.A'].head(5).tolist()}")
    logger.info(f"OUTCOME value counts: {df['OUTCOME'].value_counts().to_dict()}")
    logger.info(f"RURAL value counts: {df['RURAL'].value_counts().to_dict()}")

    # ----------------------------- Step 4: fix lab columns containing "EMPTY" string
    logger.info("=== STEP 4: fix 'EMPTY' strings in lab columns ===")
    total_empty = 0
    for c in LAB_COLS_RAW:
        n_empty = int((df[c].astype(str).str.strip().str.upper() == "EMPTY").sum())
        total_empty += n_empty
        df[c] = df[c].replace(r'^\s*EMPTY\s*$', np.nan, regex=True)
        df[c] = pd.to_numeric(df[c], errors="coerce")
        if n_empty:
            logger.info(f"  {c}: replaced {n_empty} 'EMPTY' strings -> NaN, coerced numeric")
    logger.info(f"Total 'EMPTY' strings replaced across lab columns: {total_empty}")

    # ----------------------------------------- Step 5: mixed-format date parsing
    logger.info("=== STEP 5: date parsing (mixed-format fix) ===")
    df["admission_date"], n_simple, n_fallback, n_failed = parse_admission_date(
        df["D.O.A"], df["month year"])
    logger.info(f"  D.O.A: {n_simple} rows parsed by simple (M/D) match, "
                f"{n_fallback} needed D/M fallback, {n_failed} failed (NaT)")
    naive_fail = int(pd.to_datetime(df['D.O.A'], dayfirst=True, errors='coerce').isna().sum())
    logger.info(f"  (For reference: naive dayfirst=True alone would fail on {naive_fail} rows)")
    df["discharge_date"] = parse_discharge_date(df["D.O.D"], df["admission_date"])
    logger.info(f"  D.O.D failed (NaT): {int(df['discharge_date'].isna().sum())}")

    # LOS cross-check: calculated vs reported DURATION OF STAY
    calc_los = (df["discharge_date"] - df["admission_date"]).dt.days
    reported = pd.to_numeric(df["DURATION OF STAY"], errors="coerce")
    mismatch = int((calc_los != reported).sum())
    pct = mismatch / len(df) * 100
    logger.info(f"  LOS mismatch (calculated vs reported): {mismatch} ({pct:.1f}%)")
    if pct > 5:
        logger.info("  -> Using reported DURATION OF STAY as authoritative los_days")

    df = df.drop(columns=["D.O.A", "D.O.D"])  # parsed versions now exist

    # -------------------------------------------------- Step 6: rename to snake_case
    logger.info("=== STEP 6: rename columns to snake_case ===")
    unmapped = [c for c in df.columns if c not in COLUMN_MAP
                and c not in ("admission_date", "discharge_date")]
    if unmapped:
        logger.warning(f"  Columns in data not in mapping: {unmapped}")
    df = df.rename(columns=COLUMN_MAP)

    # ------------------------------------------------- Step 7: map categorical values
    logger.info("=== STEP 7: map categorical values ===")
    df["locality"] = df["locality"].astype(str).str.strip().str.upper().map(
        {"R": "Rural", "U": "Urban"})
    df["admission_type"] = df["admission_type"].astype(str).str.strip().str.upper().map(
        {"E": "Emergency", "O": "OPD"})
    df["outcome"] = df["outcome"].astype(str).str.strip().str.upper().map(
        {"DISCHARGE": "Discharged", "EXPIRY": "Expired", "DAMA": "DAMA"})
    df["gender"] = df["gender"].astype(str).str.strip().str.upper().map(
        {"M": "Male", "F": "Female"})

    # numeric coercion for age / los / icu
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["los_days"] = pd.to_numeric(df["los_days"], errors="coerce")
    df["icu_days"] = pd.to_numeric(df["icu_days"], errors="coerce")

    # ----------------------------------------------- Step 8: fill nulls with median
    logger.info("=== STEP 8: median-fill numeric labs ===")
    medians = {}
    for c in LAB_COLS:
        med = df[c].median()
        n_missing = int(df[c].isna().sum())
        df[c] = df[c].fillna(med)
        medians[c] = med
        logger.info(f"  {c}: filled {n_missing} nulls with median={med:.2f}")

    # ------------------------------- coerce binary flag columns to clean 0/1 integers
    for c in FLAG_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int).clip(0, 1)

    # ------------------------------------------------- Step 9: engineer new features
    logger.info("=== STEP 9: feature engineering ===")
    df["age_group"] = pd.cut(df["age"], bins=[0, 39, 60, 80, 200],
                             labels=["Under 40", "40-60", "61-80", "Over 80"]).astype("object")
    df["season"] = df["admission_date"].dt.month.map(SEASON_BY_MONTH)
    df["risk_score"] = (
        df["diabetes"] + df["hypertension"] + df["cad"] + df["ckd"]
        + (df["ef"] < 40).astype(int)
        + (df["creatinine"] > 1.5).astype(int)
    ).astype(int)

    def risk_cat(s):
        if s == 0:
            return "Low Risk"
        if s <= 2:
            return "Moderate Risk"
        if s <= 4:
            return "High Risk"
        return "Critical Risk"
    df["risk_category"] = df["risk_score"].apply(risk_cat)

    df_clean = df

    # ------------------------------------------------ Step 10: validation (5 checks)
    logger.info("=== STEP 10: validation ===")
    assert len(df_clean) == 15757, f"Row count wrong: {len(df_clean)}"
    print("✅ Row count: 15,757")

    discharged = int((df_clean['outcome'] == 'Discharged').sum())
    expired = int((df_clean['outcome'] == 'Expired').sum())
    dama = int((df_clean['outcome'] == 'DAMA').sum())
    assert discharged == 13756, f"Discharged count wrong: {discharged}"
    assert expired == 1105, f"Expired count wrong: {expired}"
    assert dama == 896, f"DAMA count wrong: {dama}"
    print("✅ Outcome counts verified: 13756 / 1105 / 896")

    critical_cols = ['outcome', 'locality', 'admission_type', 'gender', 'age', 'los_days']
    for col in critical_cols:
        null_count = int(df_clean[col].isnull().sum())
        assert null_count == 0, f"Nulls found in {col}: {null_count}"
    print("✅ No nulls in critical columns")

    assert df_clean['risk_score'].between(0, 6).all(), "Risk score out of range"
    print("✅ Risk scores all in range 0-6")

    assert 'R' not in df_clean['locality'].values, "Raw locality values remain"
    assert 'E' not in df_clean['admission_type'].values, "Raw type values remain"
    assert 'DISCHARGE' not in df_clean['outcome'].values, "Raw outcome values remain"
    print("✅ All categorical mappings applied")

    # ------------------------------------------------- Step 11: post-clean summary
    print("\n=== CLEANING COMPLETE ===")
    print(f"Shape: {df_clean.shape}")
    print(f"\nOutcome distribution:")
    print(df_clean['outcome'].value_counts())
    print(f"\nLocality distribution:")
    print(df_clean['locality'].value_counts())
    print(f"\nAge group distribution:")
    print(df_clean['age_group'].value_counts())
    print(f"\nSeason distribution:")
    print(df_clean['season'].value_counts())
    print(f"\nRisk category distribution:")
    print(df_clean['risk_category'].value_counts())
    print(f"\nMedian values used for null filling:")
    for c, m in medians.items():
        print(f"  {c}: {m:.2f}")
    print(f"\nRemaining nulls:")
    remaining = df_clean.isnull().sum()
    remaining = remaining[remaining > 0]
    print("None" if len(remaining) == 0 else remaining.to_string())

    # ----------------------------------------------------------- Step 12: save
    os.makedirs(os.path.dirname(LOCAL_OUT), exist_ok=True)
    df_clean.to_csv(LOCAL_OUT, index=False)
    size_mb = os.path.getsize(LOCAL_OUT) / 1024 / 1024
    print(f"\n✅ Saved local: {LOCAL_OUT} ({size_mb:.2f} MB)")

    try:
        if not BUCKET:
            raise RuntimeError("S3_BUCKET not set")
        s3 = boto3.client("s3", region_name=REGION)
        buf = io.StringIO()
        df_clean.to_csv(buf, index=False)
        s3.put_object(Bucket=BUCKET, Key=OUT_KEY, Body=buf.getvalue().encode("utf-8"))
        print(f"✅ Uploaded to S3: s3://{BUCKET}/{OUT_KEY}")
    except Exception as e:
        print(f"⚠️  S3 upload skipped ({e}). Local copy is saved.")


if __name__ == "__main__":
    main()
