"""
data_quality_checks.py — Data quality assertion suite for HOSPIQ.

Runs 15 assertions against the cleaned admissions dataset and prints PASS/FAIL
for each. Exits with code 1 if any check fails so CI (GitHub Actions) can gate on it.

Usage:
    python pipeline/data_quality_checks.py
Data path can be overridden with the HOSPIQ_DATA environment variable.
"""

import os
import sys

import pandas as pd

DATA_PATH = os.environ.get(
    "HOSPIQ_DATA", os.path.join("data", "processed", "hdhi_admission_cleaned.csv")
)

VALID_OUTCOMES = {"Discharged", "Expired", "DAMA"}
VALID_ADMISSION_TYPES = {"Emergency", "OPD"}
VALID_LOCALITIES = {"Rural", "Urban"}
VALID_RISK_CATEGORIES = {"Low Risk", "Moderate Risk", "High Risk", "Critical Risk"}


def _load():
    return pd.read_csv(DATA_PATH)


def _expired(df):
    return (df["outcome"] == "Expired").astype(int)


def check_01_row_count(df):
    return len(df) == 15757, f"rows={len(df)} (expected 15757)"


def check_02_unique_patients(df):
    n = df["mrd_no"].nunique()
    return n == 12244, f"unique mrd_no={n} (expected 12244)"


def check_03_outcome_domain(df):
    vals = set(df["outcome"].dropna().unique())
    return vals <= VALID_OUTCOMES, f"outcome values={sorted(vals)}"


def check_04_admission_type_domain(df):
    vals = set(df["admission_type"].dropna().unique())
    return vals <= VALID_ADMISSION_TYPES, f"admission_type values={sorted(vals)}"


def check_05_locality_domain(df):
    vals = set(df["locality"].dropna().unique())
    return vals <= VALID_LOCALITIES, f"locality values={sorted(vals)}"


def check_06_los_positive(df):
    bad = int((df["los_days"] < 1).sum())
    return bad == 0, f"rows with los_days < 1: {bad}"


def check_07_age_bounds(df):
    bad = int((~df["age"].between(1, 115)).sum())
    return bad == 0, f"rows with age outside 1-115: {bad}"


def check_08_ef_bounds(df):
    ef = df["ef"].dropna()
    bad = int((~ef.between(5, 85)).sum())
    return bad == 0, f"non-null ef outside 5-85: {bad}"


def check_09_risk_score_bounds(df):
    bad = int((~df["risk_score"].between(0, 6)).sum())
    return bad == 0, f"rows with risk_score outside 0-6: {bad}"


def check_10_risk_category_domain(df):
    vals = set(df["risk_category"].dropna().unique())
    return vals <= VALID_RISK_CATEGORIES, f"risk_category values={sorted(vals)}"


def check_11_unique_admission_grain(df):
    # sno is the admission-level primary key. (mrd_no, admission_date) is NOT unique
    # because same-day repeat records exist, so uniqueness is asserted on sno.
    dupes = int(df.duplicated(subset=["sno"]).sum())
    return dupes == 0, f"duplicate sno rows: {dupes}"


def check_12_mortality_rate(df):
    rate = _expired(df).mean() * 100
    return 6.5 <= rate <= 7.5, f"mortality rate={rate:.2f}% (bound 6.5-7.5)"


def check_13_emergency_rate(df):
    rate = (df["admission_type"] == "Emergency").mean() * 100
    return 68 <= rate <= 71, f"emergency rate={rate:.2f}% (bound 68-71)"


def check_14_cardiogenic_shock_mortality(df):
    shock = df[df["cardiogenic_shock"] == 1]
    rate = (shock["outcome"] == "Expired").mean() * 100 if len(shock) else 0
    return 45 <= rate <= 50, f"cardiogenic shock mortality={rate:.2f}% (bound 45-50)"


def check_15_expired_count(df):
    total = int(_expired(df).sum())
    return total == 1105, f"is_expired sum={total} (expected 1105)"


CHECKS = [
    ("CHECK 01: Row count == 15757", check_01_row_count),
    ("CHECK 02: Unique patients == 12244", check_02_unique_patients),
    ("CHECK 03: outcome domain", check_03_outcome_domain),
    ("CHECK 04: admission_type domain", check_04_admission_type_domain),
    ("CHECK 05: locality domain", check_05_locality_domain),
    ("CHECK 06: los_days >= 1", check_06_los_positive),
    ("CHECK 07: age in 1-115", check_07_age_bounds),
    ("CHECK 08: ef in 5-85 (non-null)", check_08_ef_bounds),
    ("CHECK 09: risk_score in 0-6", check_09_risk_score_bounds),
    ("CHECK 10: risk_category domain", check_10_risk_category_domain),
    ("CHECK 11: unique admission grain (sno)", check_11_unique_admission_grain),
    ("CHECK 12: mortality rate 6.5-7.5%", check_12_mortality_rate),
    ("CHECK 13: emergency rate 68-71%", check_13_emergency_rate),
    ("CHECK 14: cardiogenic shock mortality 45-50%", check_14_cardiogenic_shock_mortality),
    ("CHECK 15: is_expired sum == 1105", check_15_expired_count),
]


def run_all_checks():
    df = _load()
    passed = 0
    print(f"Running {len(CHECKS)} data quality checks on {DATA_PATH}\n")
    for name, fn in CHECKS:
        ok, detail = fn(df)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name:<48} {detail}")
        passed += int(ok)
    print(f"\n{passed}/{len(CHECKS)} checks passed.")
    if passed != len(CHECKS):
        sys.exit(1)


if __name__ == "__main__":
    run_all_checks()
