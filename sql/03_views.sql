-- ============================================================
-- HOSPIQ — Power BI Views
-- v_clinical_overview · v_monthly_summary · v_risk_summary
-- ============================================================

CREATE OR REPLACE VIEW v_clinical_overview AS
SELECT
    f.sno, f.admission_date, f.discharge_date,
    f.admission_type, f.los_days, f.icu_days, f.outcome,
    f.diabetes, f.hypertension, f.cad, f.ckd, f.prior_cmp,
    f.smoking, f.alcohol,
    f.hb, f.tlc, f.ef, f.bnp, f.creatinine,
    f.raised_cardiac_enzymes,
    f.stemi, f.heart_failure, f.hfref, f.hfnef,
    f.cardiogenic_shock, f.shock, f.pulmonary_embolism,
    f.chest_infection, f.aki, f.af,
    f.risk_score, f.risk_category,
    p.age, p.age_group, p.gender, p.locality,
    d.day_name, d.month_name, d.month_num, d.year,
    d.quarter, d.fiscal_quarter, d.season, d.is_weekend
FROM fact_admissions f
JOIN dim_patient p ON f.mrd_no=p.mrd_no
JOIN dim_date d ON f.admission_date=d.date_id;

CREATE OR REPLACE VIEW v_monthly_summary AS
SELECT
    d.year, d.month_name, d.month_num,
    d.fiscal_quarter, d.season,
    COUNT(*) AS admissions,
    SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END) AS deaths,
    ROUND(SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),2) AS mortality_pct,
    SUM(CASE WHEN f.stemi=TRUE THEN 1 ELSE 0 END) AS stemi_cases,
    SUM(CASE WHEN f.heart_failure=TRUE THEN 1 ELSE 0 END) AS heart_failure_cases,
    SUM(CASE WHEN f.admission_type='Emergency' THEN 1 ELSE 0 END) AS emergencies,
    ROUND(AVG(f.los_days),1) AS avg_los
FROM fact_admissions f
JOIN dim_date d ON f.admission_date=d.date_id
GROUP BY d.year, d.month_name, d.month_num, d.fiscal_quarter, d.season;

CREATE OR REPLACE VIEW v_risk_summary AS
SELECT
    f.risk_category,
    COUNT(*) AS patients,
    ROUND(AVG(f.los_days),1) AS avg_los,
    ROUND(SUM(CASE WHEN f.outcome='Expired' THEN 1 ELSE 0 END)
          *100.0/COUNT(*),2) AS mortality_pct,
    ROUND(AVG(f.ef),1) AS avg_ef,
    SUM(CASE WHEN f.stemi=TRUE THEN 1 ELSE 0 END) AS stemi_cases,
    SUM(CASE WHEN f.ckd=TRUE AND f.hypertension=TRUE
             THEN 1 ELSE 0 END) AS ckd_htn_patients
FROM fact_admissions f
GROUP BY f.risk_category;
