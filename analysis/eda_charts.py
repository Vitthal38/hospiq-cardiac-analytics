"""
04_eda_charts.py — Phase 1: Generate EDA visualisations
==================================================================================
Standalone script that reproduces the 3 exploratory charts from
notebooks/01_eda_exploration.ipynb directly from the raw dataset.

Input  : s3://<S3_BUCKET>/raw/HDHI Admission data.csv  (fallback: data/raw/)
Output : assets/screenshots/eda_01_null_analysis.png
         assets/screenshots/eda_02_outcome_distribution.png
         assets/screenshots/eda_03_numeric_distributions.png
Dependencies : pandas, numpy, matplotlib, boto3, python-dotenv
==================================================================================
"""

import io
import os
import sys
from pathlib import Path

import pandas as pd
import boto3
from dotenv import load_dotenv

import matplotlib
matplotlib.use("Agg")  # headless backend — must be set before pyplot import
import matplotlib.pyplot as plt  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

BUCKET = os.getenv("S3_BUCKET")
RAW_PREFIX = os.getenv("S3_RAW_PREFIX", "raw/")
REGION = os.getenv("AWS_REGION", "ap-south-1")
RAW_KEY = f"{RAW_PREFIX}HDHI Admission data.csv"
LOCAL_RAW = Path("data") / "raw" / "HDHI Admission data.csv"
OUT = Path("assets") / "screenshots"
DPI = 150


def load_raw():
    """Load the raw CSV from S3, fall back to local."""
    try:
        if not BUCKET:
            raise RuntimeError("S3_BUCKET not set")
        s3 = boto3.client("s3", region_name=REGION)
        obj = s3.get_object(Bucket=BUCKET, Key=RAW_KEY)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        print(f"Loaded from S3: s3://{BUCKET}/{RAW_KEY}")
    except Exception as e:
        print(f"S3 load failed ({e}); using local file")
        df = pd.read_csv(LOCAL_RAW)
    return df


def chart_null_analysis(df):
    null_df = pd.DataFrame({
        "null_count": df.isnull().sum(),
        "null_pct": (df.isnull().sum() / len(df) * 100).round(2),
    }).sort_values("null_pct", ascending=False)
    null_df = null_df[null_df["null_count"] > 0]

    fig, ax = plt.subplots(figsize=(10, 4))
    null_df["null_pct"].plot(kind="bar", color="#E63946", ax=ax)
    ax.set_title("Missing Value % by Column", fontsize=14, fontweight="bold")
    ax.set_ylabel("Missing %")
    ax.set_xlabel("Column")
    ax.axhline(y=20, color="orange", linestyle="--", label="20% threshold")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(OUT / "eda_01_null_analysis.png", dpi=DPI)
    plt.close(fig)
    print("Saved: eda_01_null_analysis.png")


def chart_outcome_distribution(df):
    counts = df["OUTCOME"].value_counts()
    pct = (df["OUTCOME"].value_counts(normalize=True) * 100).round(2)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        counts.values,
        labels=[f"{o}\n{c:,} ({p:.1f}%)" for o, c, p in zip(counts.index, counts.values, pct.values)],
        colors=["#2DC653", "#E63946", "#F5A623"],
        startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=2),
    )
    ax.set_title("Patient Outcome Distribution\n15,757 Real Cardiac Admissions",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(OUT / "eda_02_outcome_distribution.png", dpi=DPI)
    plt.close(fig)
    print("Saved: eda_02_outcome_distribution.png")


def chart_numeric_distributions(df):
    age = pd.to_numeric(df["AGE"], errors="coerce")
    los = pd.to_numeric(df["DURATION OF STAY"], errors="coerce").dropna()
    ef = pd.to_numeric(df["EF"], errors="coerce").dropna()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].hist(age.dropna(), bins=20, color="#00B4D8", edgecolor="white")
    axes[0].axvline(age.mean(), color="red", linestyle="--", label=f"Mean: {age.mean():.1f}")
    axes[0].axvline(age.median(), color="orange", linestyle="--", label=f"Median: {age.median():.1f}")
    axes[0].set_title("Patient Age Distribution")
    axes[0].set_xlabel("Age (years)")
    axes[0].set_ylabel("Count")
    axes[0].legend()

    los_capped = los[los <= 30]
    axes[1].hist(los_capped, bins=30, color="#2DC653", edgecolor="white")
    axes[1].set_title("Length of Stay (capped at 30 days)")
    axes[1].set_xlabel("Days")
    axes[1].set_ylabel("Count")
    axes[1].text(0.7, 0.9, f"Max: {los.max():.0f} days\n{(los > 30).sum()} records > 30d",
                 transform=axes[1].transAxes, bbox=dict(boxstyle="round", facecolor="wheat"))

    axes[2].hist(ef, bins=20, color="#F5A623", edgecolor="white")
    axes[2].axvline(40, color="red", linestyle="--", label="EF < 40% = High Risk")
    axes[2].set_title("Ejection Fraction Distribution")
    axes[2].set_xlabel("EF %")
    axes[2].set_ylabel("Count")
    axes[2].legend()

    plt.suptitle("Key Numeric Variable Distributions — HDHI Dataset", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(OUT / "eda_03_numeric_distributions.png", dpi=DPI)
    plt.close(fig)
    print("Saved: eda_03_numeric_distributions.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_raw()
    print(f"Loaded raw data: {df.shape[0]} rows x {df.shape[1]} cols")
    chart_null_analysis(df)
    chart_outcome_distribution(df)
    chart_numeric_distributions(df)
    print("All 3 EDA charts generated.")


if __name__ == "__main__":
    main()
