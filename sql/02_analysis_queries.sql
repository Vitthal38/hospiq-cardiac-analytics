-- ============================================================
-- HOSPIQ — 10 Business Analysis Queries
-- Run against the star schema (dim_patient, dim_date, fact_admissions)
-- 15,757 cardiac admissions, Hero DMC Heart Institute (Apr 2017 – Mar 2019)
-- ============================================================

-- Q1: Hospital Overall Scorecard
-- Business question: What are the headline KPIs for this hospital?
-- Plain English: one row of top-line totals — admissions, patients, deaths,
-- mortality %, DAMA, average stay/ICU, and key condition counts.
SELECT
    COUNT(*) AS total_admissions,
    COUNT(DISTINCT mrd_no) AS unique_patients,
    SUM(CASE WHEN outcome='Expired' THEN 1 ELSE 0 END) AS total_deaths,
    ROUND(SUM(CASE WHEN outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),2) AS mortality_pct,
    SUM(CASE WHEN outcome='DAMA' THEN 1 ELSE 0 END) AS dama_count,
    ROUND(AVG(los_days),1) AS avg_los_days,
    ROUND(AVG(icu_days),1) AS avg_icu_days,
    SUM(CASE WHEN stemi=TRUE THEN 1 ELSE 0 END) AS stemi_cases,
    SUM(CASE WHEN heart_failure=TRUE THEN 1 ELSE 0 END) AS heart_failure_cases,
    SUM(CASE WHEN cardiogenic_shock=TRUE THEN 1 ELSE 0 END) AS shock_cases
FROM fact_admissions;

-- Q2: Rural vs Urban Outcomes
-- Business question: Does where you live affect your survival?
-- Plain English: compare mortality, stay and severity between rural and urban patients.
SELECT
    p.locality,
    COUNT(*) AS admissions,
    ROUND(AVG(f.los_days),1) AS avg_los,
    SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END) AS deaths,
    ROUND(SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),2) AS mortality_pct,
    SUM(CASE WHEN f.stemi=TRUE THEN 1 ELSE 0 END) AS stemi_cases,
    ROUND(AVG(f.ef),1) AS avg_ef
FROM fact_admissions f
JOIN dim_patient p ON f.mrd_no=p.mrd_no
GROUP BY p.locality
ORDER BY mortality_pct DESC;

-- Q3: Age Group Mortality
-- Business question: Which age group has the highest cardiac mortality?
-- Plain English: mortality and average stay by age band.
SELECT
    p.age_group,
    COUNT(*) AS patients,
    ROUND(AVG(f.los_days),1) AS avg_los,
    SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END) AS deaths,
    ROUND(SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),2) AS mortality_pct,
    ROUND(AVG(f.ef),1) AS avg_ef
FROM fact_admissions f
JOIN dim_patient p ON f.mrd_no=p.mrd_no
GROUP BY p.age_group
ORDER BY mortality_pct DESC;

-- Q4: Seasonal Patterns
-- Business question: Do cardiac emergencies spike in certain seasons?
-- Plain English: admissions, STEMI, emergencies and mortality by month/season.
SELECT
    d.season,
    d.month_name,
    d.month_num,
    COUNT(*) AS admissions,
    SUM(CASE WHEN f.stemi=TRUE THEN 1 ELSE 0 END) AS stemi_cases,
    SUM(CASE WHEN f.admission_type='Emergency' THEN 1 ELSE 0 END) AS emergencies,
    ROUND(SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),2) AS mortality_pct,
    ROUND(AVG(f.los_days),1) AS avg_los
FROM fact_admissions f
JOIN dim_date d ON f.admission_date=d.date_id
GROUP BY d.season, d.month_name, d.month_num
ORDER BY d.month_num;

-- Q5: Comorbidity Combinations (top 10 deadliest)
-- Business question: Which combination of existing conditions is most deadly?
-- Plain English: mortality for each diabetes/hypertension/cad/ckd combination.
SELECT
    diabetes, hypertension, cad, ckd,
    COUNT(*) AS patients,
    ROUND(AVG(los_days),1) AS avg_los,
    ROUND(SUM(CASE WHEN outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),1) AS mortality_pct
FROM fact_admissions
GROUP BY diabetes, hypertension, cad, ckd
ORDER BY mortality_pct DESC
LIMIT 10;

-- Q6: Risk Score Validation (3 CTEs chained)
-- Business question: Does our composite risk score actually predict mortality?
-- Plain English: band patients by risk_score, then check mortality rises with risk.
WITH base AS (
    SELECT f.*, p.age_group, p.locality
    FROM fact_admissions f
    JOIN dim_patient p ON f.mrd_no=p.mrd_no
),
scored AS (
    SELECT *,
        CASE
            WHEN risk_score>=5 THEN 'Critical Risk'
            WHEN risk_score>=3 THEN 'High Risk'
            WHEN risk_score>=1 THEN 'Moderate Risk'
            ELSE 'Low Risk'
        END AS risk_band
    FROM base
),
summary AS (
    SELECT
        risk_band,
        COUNT(*) AS patients,
        ROUND(AVG(los_days),1) AS avg_los,
        ROUND(SUM(CASE WHEN outcome='Expired' THEN 1 ELSE 0 END)
              *100.0/COUNT(*),2) AS mortality_pct,
        ROUND(AVG(ef),1) AS avg_ef
    FROM scored
    GROUP BY risk_band
)
SELECT * FROM summary
ORDER BY mortality_pct DESC;

-- Q7: Year-over-Year Monthly Trend (window function)
-- Business question: Is the hospital seeing more admissions year on year?
-- Plain English: per-month admissions with the same month's prior-year count via LAG.
SELECT
    d.year,
    d.month_name,
    d.month_num,
    COUNT(*) AS admissions,
    SUM(CASE WHEN f.stemi=TRUE THEN 1 ELSE 0 END) AS stemi_cases,
    LAG(COUNT(*)) OVER (
        PARTITION BY d.month_num ORDER BY d.year
    ) AS prev_year_count,
    COUNT(*) - LAG(COUNT(*)) OVER (
        PARTITION BY d.month_num ORDER BY d.year
    ) AS yoy_change
FROM fact_admissions f
JOIN dim_date d ON f.admission_date=d.date_id
GROUP BY d.year, d.month_name, d.month_num
ORDER BY d.year, d.month_num;

-- Q8: Ejection Fraction Risk Stratification
-- Business question: How does heart pump function predict survival?
-- Plain English: mortality by EF band (normal → severely reduced).
SELECT
    CASE
        WHEN ef>=55 THEN '1. Normal EF (55%+)'
        WHEN ef>=40 THEN '2. Mildly Reduced (40-54%)'
        WHEN ef>=30 THEN '3. Moderately Reduced (30-39%)'
        WHEN ef<30  THEN '4. Severely Reduced (under 30%)'
        ELSE '5. Not Measured'
    END AS ef_category,
    COUNT(*) AS patients,
    ROUND(AVG(los_days),1) AS avg_los,
    ROUND(SUM(CASE WHEN outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),2) AS mortality_pct
FROM fact_admissions
GROUP BY ef_category
ORDER BY ef_category;

-- Q9: STEMI Patient Deep Dive
-- Business question: Who are the highest-risk STEMI patients?
-- Plain English: among STEMI cases, mortality by locality and age group.
SELECT
    p.locality,
    p.age_group,
    COUNT(*) AS stemi_cases,
    ROUND(AVG(f.los_days),1) AS avg_los,
    ROUND(AVG(f.ef),1) AS avg_ef,
    SUM(CASE WHEN f.cardiogenic_shock=TRUE THEN 1 ELSE 0 END) AS with_shock,
    ROUND(SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),1) AS mortality_pct
FROM fact_admissions f
JOIN dim_patient p ON f.mrd_no=p.mrd_no
WHERE f.stemi=TRUE
GROUP BY p.locality, p.age_group
ORDER BY mortality_pct DESC;

-- Q10: LOS Percentile Distribution
-- Business question: What does a typical cardiac hospital stay look like?
-- Plain English: percentile spread of length of stay (excludes 0-day rows).
SELECT
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP
          (ORDER BY los_days)::NUMERIC,1) AS p25_days,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP
          (ORDER BY los_days)::NUMERIC,1) AS median_days,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP
          (ORDER BY los_days)::NUMERIC,1) AS p75_days,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP
          (ORDER BY los_days)::NUMERIC,1) AS p90_days,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP
          (ORDER BY los_days)::NUMERIC,1) AS p95_days,
    MAX(los_days) AS max_days,
    ROUND(AVG(los_days)::NUMERIC,1) AS mean_days
FROM fact_admissions
WHERE los_days>0;
