-- Date dimension: one row per unique admission date with calendar attributes.
with dates as (
    select distinct admission_date as date_id
    from {{ ref('stg_admissions') }}
    where admission_date is not null
)
select
    date_id,
    extract(year  from date_id)::int                          as year,
    extract(month from date_id)::int                           as month_num,
    trim(to_char(date_id, 'Month'))                            as month_name,
    'Q' || extract(quarter from date_id)::int                  as quarter,
    case
        when extract(month from date_id) in (3, 4, 5)      then 'Summer'
        when extract(month from date_id) in (6, 7, 8, 9)   then 'Monsoon'
        when extract(month from date_id) in (10, 11)       then 'Post-Monsoon'
        else 'Winter'
    end                                                        as season,
    trim(to_char(date_id, 'Day'))                              as day_of_week,
    extract(dow from date_id) in (0, 6)                        as is_weekend
from dates
