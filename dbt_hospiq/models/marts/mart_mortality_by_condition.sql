-- Mortality mart: one row per clinical condition with mortality rate and avg LOS.
with f as (
    select * from {{ ref('fact_admissions') }}
),
conditions as (
    select 'Cardiogenic Shock' as condition_name, is_expired, los_days from f where cardiogenic_shock = 1
    union all
    select 'STEMI',            is_expired, los_days from f where stemi = 1
    union all
    select 'CKD',              is_expired, los_days from f where ckd = 1
    union all
    select 'Heart Failure',    is_expired, los_days from f where heart_failure = 1
    union all
    select 'Diabetes',         is_expired, los_days from f where diabetes = 1
    union all
    select 'Hypertension',     is_expired, los_days from f where hypertension = 1
)
select
    condition_name,
    count(*)                                              as admissions,
    sum(is_expired)                                       as deaths,
    round(100.0 * sum(is_expired) / count(*), 2)          as mortality_pct,
    round(avg(los_days), 2)                               as avg_los
from conditions
group by condition_name
order by mortality_pct desc
