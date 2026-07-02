# dbt_hospiq — HOSPIQ Transformation Layer

A dbt project that rebuilds the HOSPIQ star schema as version-controlled, tested
transformations on top of the loaded PostgreSQL warehouse.

## Layers
- **staging/** — `stg_admissions`: one standardised row per admission (renames, casts, derived `is_expired` / `is_dama`).
- **marts/** — `dim_patient`, `dim_date`, `fact_admissions`, plus reporting marts `mart_mortality_by_condition` and `mart_rural_urban`.
- **tests/** — schema tests (`not_null`, `accepted_values`, `relationships`, `unique`) + a custom `assert_mortality_bounds` test that fails if the overall mortality rate leaves the 6.5–7.5% band.

## Run it
```bash
# 1. Configure credentials (never committed)
cp profiles.yml.example profiles.yml   # then fill in your RDS values

cd dbt_hospiq
dbt deps                 # install packages (if any)
dbt run                  # materialise staging (views) + marts (tables)
dbt test                 # run schema + custom tests
dbt docs generate && dbt docs serve   # browse model lineage
```

> `profiles.yml` is git-ignored — only `profiles.yml.example` is committed. The
> raw source (`hospiq_raw.hdhi_admission_cleaned`) maps to the cleaned dataset
> loaded by the Python pipeline.
