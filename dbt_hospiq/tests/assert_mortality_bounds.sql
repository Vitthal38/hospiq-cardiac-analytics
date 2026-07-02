-- Custom singular test: fails (returns rows) if the overall mortality rate
-- falls outside the expected 6.5%–7.5% band. Zero rows = pass.
with rate as (
    select 100.0 * sum(is_expired) / count(*) as mortality_pct
    from {{ ref('fact_admissions') }}
)
select mortality_pct
from rate
where mortality_pct < 6.5 or mortality_pct > 7.5
