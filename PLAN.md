# HOSPIQ — Project Plan

## Project Context

### Problem Statement
India has the highest rate of cardiovascular deaths globally.
Most Indian hospitals — particularly tier-2 institutions —
collect patient data but never analyse it systematically.
Ward managers make decisions based on experience, not data.
This project demonstrates what becomes visible when 2 years
of real cardiac admissions are structured, cleaned, and analysed.

### Business Questions This Project Answers
1. What is the true mortality rate and how does it vary by patient profile?
2. Do rural patients have worse cardiac outcomes than urban patients?
3. Which age group faces the highest cardiac mortality risk?
4. Do cardiac emergencies follow seasonal patterns?
5. Which combination of existing conditions is most deadly?
6. Does a composite risk score accurately predict patient mortality?
7. Is the hospital seeing more admissions year on year?
8. How does ejection fraction predict patient survival?
9. Who are the highest-risk STEMI patients?
10. What does a typical cardiac hospital stay look like?

### Dataset Details
Source:   Hero DMC Heart Institute, Ludhiana, Punjab, India
Period:   April 2017 to March 2019 (2 fiscal years)
Rows:     15,757 admission records
Patients: 12,244 unique (3,513 repeat admissions)
Columns:  56 clinical and demographic variables

Known data quality issues:
- BNP column: 53.6% missing (8,441 nulls) — highest missing rate
- EF column: 9.5% missing (1,505 nulls)
- Age range: 4 to 110 — extreme values need investigation
- LOS range: 1 to 98 days — outliers present
- Date format: inconsistencies in D.O.A column
- Repeat admissions: same patient appears multiple times

### Tech Stack Decision Rationale
Why AWS S3: Industry standard data lake — shows cloud literacy
Why RDS PostgreSQL: Production-grade DB — not just local SQLite
Why SQL views: Power BI connects to views not raw tables — professional pattern
Why Jupyter: Shows exploratory thinking — not just pipeline coding
Why Power BI: Most in-demand BI tool in Indian job market

## Phase-by-Phase Plan

### Phase 1 — Data Exploration
Objective: Understand the data completely before writing any code.
Deliverables:
  - notebooks/01_eda_exploration.ipynb
  - docs/EDA_REPORT.md
Commit message: "Phase 1: EDA complete — notebook and findings report"

Steps:
  1.1 Load raw CSV into pandas
  1.2 Check shape, dtypes, memory usage
  1.3 Null analysis — count and % per column
  1.4 Duplicate analysis — by MRD No.
  1.5 Categorical value distributions
  1.6 Numeric outlier detection
  1.7 Date format validation
  1.8 Document every finding
  1.9 Create 3 EDA charts
  1.10 Write EDA_REPORT.md

### Phase 2 — Data Cleaning
Objective: Fix every issue with documented justification.
Deliverables:
  - python/02_clean_transform.py
  - docs/DATA_CLEANING_DECISIONS.md
Commit message: "Phase 2: Cleaning pipeline and decisions documented"

Steps:
  2.1 Rename columns to snake_case
  2.2 Parse dates with dayfirst=True
  2.3 Map categorical values
  2.4 Handle nulls — one decision per column
  2.5 Handle outliers — one decision per column
  2.6 Engineer features: age_group, season, risk_score, risk_category
  2.7 Validate output against known totals
  2.8 Write DATA_CLEANING_DECISIONS.md

### Phase 3 — AWS Infrastructure
Objective: Set up cloud pipeline.
Deliverables:
  - S3 bucket with raw and processed data
  - RDS PostgreSQL instance running
  - docs/ARCHITECTURE.md
  - python/01_upload_to_s3.py
Commit message: "Phase 3: AWS S3 and RDS infrastructure ready"

Steps:
  3.1 Create S3 bucket
  3.2 Upload raw CSVs to S3 raw/
  3.3 Upload cleaned CSV to S3 processed/
  3.4 Create RDS PostgreSQL 15 free tier instance
  3.5 Configure security group port 5432
  3.6 Test connection
  3.7 Write ARCHITECTURE.md

### Phase 4 — Database Design and Loading
Objective: Build star schema and load clean data.
Deliverables:
  - sql/01_schema.sql
  - python/03_load_to_rds.py
Commit message: "Phase 4: Star schema created, 15757 rows loaded"

Tables:
  dim_patient     — 12,244 unique patients
  dim_date        — 730 unique dates
  fact_admissions — 15,757 admission records

Steps:
  4.1 Write CREATE TABLE statements
  4.2 Load dim_patient
  4.3 Load dim_date
  4.4 Load fact_admissions
  4.5 Verify FK integrity
  4.6 Verify row counts

### Phase 5 — SQL Analysis
Objective: Answer 10 business questions with SQL.
Deliverables:
  - sql/02_analysis_queries.sql
  - sql/03_views.sql
  - docs/BUSINESS_INSIGHTS.md
  - docs/SQL_QUERY_GUIDE.md
Commit message: "Phase 5: 10 SQL queries, 3 views, business insights"

Business questions: Q1 through Q10 (listed above)
Views: v_clinical_overview, v_monthly_summary, v_risk_summary

### Phase 6 — Power BI Dashboard
Objective: Build 3-page dashboard connected to RDS.
Deliverables:
  - powerbi/HOSPIQ_Dashboard.pbix
  - assets/screenshots/ (3 page screenshots)
Commit message: "Phase 6: Power BI dashboard complete — 3 pages live"

Pages:
  Page 1 — Clinical Overview
  Page 2 — Risk Intelligence
  Page 3 — Rural vs Urban Disparity

### Phase 7 — Final Documentation
Objective: Portfolio-ready documentation.
Deliverables:
  - docs/INTERVIEW_PREP.md
  - docs/SQL_QUERY_GUIDE.md
  - Updated README with real numbers
Commit message: "Phase 7: Final documentation — project complete"

## Real Numbers Reference
Total admissions:      15,757
Unique patients:       12,244
Mortality:              1,105  (7.01%)
DAMA:                     896  (5.69%)
Discharged:            13,756  (87.30%)
Emergency:             10,924  (69.33%)
STEMI:                  2,202  (13.97%)
Heart failure:          4,561  (28.94%)
Cardiogenic shock:        944   (5.99%)
Rural:                  3,680  (23.35%)
Urban:                 12,077  (76.65%)
Avg LOS:                  6.4  days
HTN + CKD mortality:    47.2%  (6.7x average)

## Current Status
Phase 1 — Data Exploration    : ⏳ IN PROGRESS (START HERE)
Phase 2 — Data Cleaning       : ⏳ PENDING
Phase 3 — AWS Infrastructure  : ⏳ PENDING
Phase 4 — Database Loading    : ⏳ PENDING
Phase 5 — SQL Analysis        : ⏳ PENDING
Phase 6 — Power BI Dashboard  : ⏳ PENDING
Phase 7 — Documentation       : ⏳ PENDING
