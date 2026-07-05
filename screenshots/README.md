# Screenshots

Dashboard screenshots from the HOSPIQ Power BI report (5 pages).

## Dashboard Pages

| File | Page | Description |
|------|------|-------------|
| 01_clinical_overview.png | Page 1 | Clinical Overview — KPI cards, monthly trend, outcomes by age group |
| 02_risk_intelligence.png | Page 2 | Risk Intelligence — condition mortality ranking, risk-tier severity |
| 03_rural_vs_urban.png | Page 3 | Rural vs Urban — 8 paired KPI cards, comparative charts |
| 04_patient_cohort_detail.png | Page 4 | Patient Cohort Detail — drill-through destination |
| 05_condition_tooltip.png | Page 5 | Condition Tooltip — custom tooltip with rank, volume, LOS, delta |

## AWS Infrastructure Proof
(located in [`docs/aws_proof/`](../docs/aws_proof/))

| File | Shows |
|------|-------|
| s3_bucket_overview.png | S3 bucket root with raw/ and processed/ folders |
| s3_processed_objects.png | processed/hdhi_admission_cleaned.csv (3.3MB) |
| s3_raw_objects.png | raw/ folder with 4 source CSVs |

## Pipeline & EDA Proof

| File | Description |
|------|-------------|
| eda_01_null_analysis.png | Missing value distribution across all columns |
| eda_02_outcome_distribution.png | Patient outcome split (Discharged/Expired/DAMA) |
| eda_03_numeric_distributions.png | Age, LOS, and EF distributions with outlier flags |
| phase2_cleaning_validation.png | Cleaning validation assertions with actual values |
| phase3_s3_bucket.png | S3 bucket contents verified |
| phase4_database_verification.png | Row counts and FK integrity for all 3 tables |
| phase5_sql_results.png | Summary of all 10 query findings with real numbers |

> Dashboard was built in Power BI Desktop and published to GitHub Pages:
> https://vitthal38.github.io/hospiq-cardiac-analytics
