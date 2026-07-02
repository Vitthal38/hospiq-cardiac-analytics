-- Staging: standardise raw admissions — rename, cast dates, cast flags to 0/1,
-- derive outcome flags, add load timestamp. One row per admission.
with source as (
    select * from {{ source('hospiq_raw', 'hdhi_admission_cleaned') }}
)
select
    sno,
    mrd_no,
    cast(admission_date as date)                              as admission_date,
    cast(discharge_date as date)                              as discharge_date,
    age,
    age_group,
    gender,
    locality,
    admission_type,
    outcome,
    case when outcome = 'Expired' then 1 else 0 end           as is_expired,
    case when outcome = 'DAMA'    then 1 else 0 end           as is_dama,
    los_days,
    icu_days,
    cast(diabetes          as integer)                        as diabetes,
    cast(hypertension      as integer)                        as hypertension,
    cast(cad               as integer)                        as cad,
    cast(ckd               as integer)                        as ckd,
    cast(stemi             as integer)                        as stemi,
    cast(heart_failure     as integer)                        as heart_failure,
    cast(cardiogenic_shock as integer)                        as cardiogenic_shock,
    ef,
    creatinine,
    risk_score,
    risk_category,
    current_timestamp                                         as loaded_at
from source
