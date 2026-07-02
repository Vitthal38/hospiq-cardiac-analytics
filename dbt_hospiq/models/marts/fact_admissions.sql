-- Fact table: one row per admission, with FKs to dim_patient and dim_date.
select
    sno                        as fact_admission_id,
    mrd_no,
    admission_date,
    discharge_date,
    admission_type,
    outcome,
    is_expired,
    is_dama,
    los_days,
    icu_days,
    diabetes,
    hypertension,
    cad,
    ckd,
    stemi,
    heart_failure,
    cardiogenic_shock,
    ef,
    creatinine,
    risk_score,
    risk_category
from {{ ref('stg_admissions') }}
