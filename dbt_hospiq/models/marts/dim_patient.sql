-- Patient dimension: one row per patient (latest record per mrd_no).
with ranked as (
    select
        mrd_no, age, gender, locality, age_group,
        row_number() over (partition by mrd_no order by admission_date desc) as rn
    from {{ ref('stg_admissions') }}
)
select mrd_no, age, gender, locality, age_group
from ranked
where rn = 1
