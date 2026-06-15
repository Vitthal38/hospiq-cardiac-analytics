# Interview Preparation Guide — HOSPIQ Project

## Numbers to Memorise Before Any Interview
- Total admissions: 15,757
- Unique patients: 12,244
- Mortality rate: 7.01% (1,105 deaths)
- DAMA rate: 5.69% (896 patients)
- Emergency admissions: 69.3% (10,924)
- STEMI cases: 2,202 (14%)
- Heart failure: 4,561 (28.9%)
- HTN + CKD mortality: 47.2% — 6.7x average
- Critical Risk mortality: 8.66%
- Severely Reduced EF mortality: 16.08%
- Monsoon STEMI cases: 717 (highest season)
- BNP missing: 53.57% (8,441 nulls)
- Mixed date format rows fixed: 3,489
- EMPTY strings in lab columns: 840

## Data Modeling Questions

**Q1: Why did you use a star schema instead of keeping one flat table?**
A star schema separates facts from dimensions. dim_patient holds each patient once (12,244 rows). dim_date holds each date once (730 rows). fact_admissions holds each admission (15,757 rows). Without this, patient attributes would repeat 15,757 times. The star schema enables efficient GROUP BY and JOIN operations, maps directly to Power BI relationships, and is the standard data warehouse pattern interviewers expect to see.

**Q2: Why did you mark dim_date as a Date Table in Power BI?**
Without marking it, Power BI creates hidden auto-date tables per column that cannot be shared between visuals. Marking it enables DATESMTD, DATESYTD, SAMEPERIODLASTYEAR to work correctly. Without it, time intelligence DAX silently returns wrong results on partial years.

**Q3: You have 15,757 rows but 12,244 unique patients. How did you handle this in the schema?**
Each admission is a valid clinical event, so all 15,757 rows stay in fact_admissions. The dim_patient table holds one row per unique MRD number using drop_duplicates(keep='first'). This means the fact table can have multiple rows per patient (repeat admissions) all referencing the same dim_patient row. FK integrity was verified — zero orphaned fact rows.

## Data Cleaning Questions

**Q4: BNP has 53.57% missing. How did you handle that and what are the limitations?**
Filled with median (470.5). Could not drop — losing 8,441 rows would severely reduce dataset size. Limitation: BNP is excluded from correlation analysis. It is only used in the composite risk score where the missing value is replaced by median before calculation. The cleaning decision is documented in DATA_CLEANING_DECISIONS.md.

**Q5: You mentioned the date column had mixed formats. What was the problem and how did you fix it?**
D.O.A had two formats mixed: M/D/YYYY in early records and D/M/YYYY in later records. Using dayfirst=True alone failed on 3,767 rows. The fix: parse with the month_year column as reference. Extract month from month_year (e.g. Apr-17 = month 4). Try parsing D.O.A with dayfirst=False first. Where parsed month differs from reference month, try dayfirst=True instead. Result: 12,268 parsed simply, 3,489 needed the fallback, 0 failed. This would have corrupted LOS calculations for nearly the entire dataset if not caught in EDA.

**Q6: You found 840 EMPTY strings in lab columns. Why is this a problem and how did you catch it?**
pandas isnull() returns False for the string "EMPTY". It is not a null — it is a string that looks like missing data. Standard null analysis in EDA would miss it entirely. Caught it by converting each lab column with pd.to_numeric using errors='coerce', which converts non-numeric strings to NaN. Then treated as a regular null. Total affected: 840 values across 8 lab columns. BNP had the most (640 EMPTY strings + 7,801 true nulls = 8,441 total missing).

## SQL Questions

**Q7: Explain your most complex SQL query.**
Q6 — Patient Risk Score Validation uses 3 chained CTEs. CTE 1 (base): joins fact_admissions to dim_patient. CTE 2 (scored): adds risk_band category from risk_score. CTE 3 (summary): aggregates mortality % per risk band. This validates that the engineered risk_score actually predicts mortality — Critical Risk patients had 8.66% mortality vs 5.27% for Low Risk, confirming the score works.

**Q8: What is the difference between a CTE and a subquery?**
A CTE (WITH clause) is named and can be referenced multiple times in the same query. A subquery is anonymous and can only be used once. CTEs improve readability — the 3-CTE chain in Q6 reads as three clear steps rather than nested subqueries. For performance they are often equivalent, but some databases materialise CTEs which can be faster or slower depending on the query plan.

**Q9: Why did you create views for Power BI instead of connecting directly to the fact table?**
Three reasons. First: v_clinical_overview pre-joins all 3 tables, so Power BI gets a flat view without needing to manage relationships in the query layer. Second: if the schema changes, I update the view — not the Power BI file. This is a maintainability pattern. Third: views control what columns Power BI sees, hiding internal columns not needed for reporting.

**Q10: The HTN + CKD combination had 47.2% mortality. Walk me through how you found that.**
Q5 groups fact_admissions by the four boolean flags: diabetes, hypertension, cad, ckd. It calculates mortality % for each combination. The combination hypertension=TRUE, ckd=TRUE, diabetes=FALSE, cad=FALSE had 72 patients and 47.2% mortality — 6.7x the hospital average of 7.01%. This is the most clinically significant finding because CKD dramatically reduces the heart's ability to compensate under stress, and hypertension compounds the cardiac workload. Together they create a disproportionately dangerous clinical profile.

## AWS Questions

**Q11: Why did you use AWS RDS instead of a local PostgreSQL?**
RDS is a managed cloud database — no setup, patching, or backup management required. Power BI connects to it directly from anywhere without needing a local database running. It demonstrates cloud literacy — most analytics roles at mid-to-large companies use cloud databases. Free tier (db.t3.micro) meant zero cost for this project.

**Q12: Why did you use S3 as a data lake?**
S3 decouples storage from compute. The raw data persists regardless of whether RDS is running or has been deleted. The cleaned CSV is stored in S3 processed/ folder — it can be reloaded into RDS at any time without re-running the cleaning pipeline. This is the production pattern: raw zone and processed zone in S3, database as the query layer.

**Q13: Your RDS instance kept getting deleted. How would you handle this in production?**
In production, RDS would never be deleted between uses. It would have automated backups enabled, multi-AZ failover, and be accessed through a VPC with private subnet — not publicly accessible. For this portfolio project, I stopped/started the instance to manage free tier costs and deleted it when not needed, relying on S3 as the persistent storage layer.

## Business Understanding Questions

**Q14: You found that Monsoon has the highest STEMI cases (717). Why might that be?**
Monsoon season in India (June-September) brings high humidity, temperature fluctuations, and increased respiratory infections. Studies link cold-to-warm transitions and pollution spikes during monsoon onset with platelet aggregation and vasoconstriction — both STEMI risk factors. Additionally, the dataset includes a pollution file (HDHI Pollution Data.csv) — a natural extension of this project would correlate AQI with STEMI rates by month to validate this hypothesis.

**Q15: DAMA (Discharged Against Medical Advice) is 5.69%. Why does this matter analytically?**
DAMA patients left before completing treatment. They are neither a clinical success nor a mortality. Including them in mortality calculations would understate the true death rate. Excluding them would bias the discharged count upward. For this project, DAMA is kept as a separate outcome category in all analyses so the 3-way split is always visible: 87.30% discharged / 7.01% expired / 5.69% DAMA.

## Power BI / DAX Questions

**Q16: What DAX measures did you build?**
Core measures:
- Mortality Rate % = DIVIDE(CALCULATE(COUNTROWS, outcome="Expired"), COUNTROWS)
- STEMI Count = CALCULATE(COUNTROWS, stemi=TRUE)
- Avg LOS Days = AVERAGE(fact_admissions[los_days])
- Rural Mortality % = DIVIDE with locality filter
- Critical Risk Count = CALCULATE with risk_category filter
- CKD+HTN Mortality % = DIVIDE with two boolean filters

**Q17: Why did you connect Power BI directly to RDS instead of importing a CSV?**
Direct connection means the dashboard reflects the current database state — if data is updated, the dashboard refreshes automatically. Importing a CSV creates a static snapshot that goes stale immediately. The v_clinical_overview view handles the JOIN logic so Power BI only needs one table to build all visuals.

## Project-Level Questions

**Q18: What was the most surprising thing you found?**
The mixed date format in D.O.A. Early records used M/D/YYYY and later ones D/M/YYYY. A simple dayfirst=True parse — which most analysts would use for Indian data — failed on 3,489 rows and would have corrupted LOS calculations for essentially the entire dataset. The fix required using the month_year column as a reference to disambiguate which format to apply. This is the kind of issue that only surfaces during thorough EDA — not during pipeline building.

**Q19: This dataset only has 2 years of data from one hospital. What are the limitations?**
Three key limitations. First: single-hospital data from a tertiary cardiac centre in Punjab — findings may not generalise to other regions or hospital types. Second: BNP is missing for 53.57% of patients, limiting its use as a predictive variable. Third: no socioeconomic data — rural vs urban differences in outcome could reflect access to care, transportation time, or income level, but the data cannot distinguish between these. Any analysis should be presented as hypothesis-generating, not conclusive.

**Q20: If you had 6 more months, what would you add?**
Three things in priority order. First: time-series analysis correlating STEMI rates with the pollution data already in the dataset (HDHI Pollution Data.csv is unused). Second: survival analysis using actual admission and discharge dates to calculate time-to-event, not just a binary expired/discharged outcome. Third: a patient readmission prediction model using the 3,513 repeat admissions as the training signal — the risk_score is a simple proxy, but a logistic regression on the full clinical feature set would be more robust.
