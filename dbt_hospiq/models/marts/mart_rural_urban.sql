-- Equity mart: mortality, DAMA, LOS and emergency rate by locality.
select
    p.locality,
    count(*)                                                          as admissions,
    round(100.0 * sum(f.is_expired) / count(*), 2)                    as mortality_pct,
    round(100.0 * sum(f.is_dama)    / count(*), 2)                    as dama_pct,
    round(avg(f.los_days), 2)                                         as avg_los,
    round(100.0 * sum(case when f.admission_type = 'Emergency'
                           then 1 else 0 end) / count(*), 2)          as emergency_rate_pct
from {{ ref('fact_admissions') }} f
join {{ ref('dim_patient') }} p on f.mrd_no = p.mrd_no
group by p.locality
order by p.locality
