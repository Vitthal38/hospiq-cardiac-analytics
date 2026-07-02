# Changelog

## v1.0.0 — 2026-07-02

### Pipeline
- AWS S3 raw zone ingestion → Python ETL →
  PostgreSQL star schema (dim_patient, dim_date, fact_admissions)
- Date format disambiguation: M/D vs D/M conflict
  resolved across 3,767 rows
- "EMPTY" string coerced to true nulls across
  8 lab columns (840 occurrences)
- Clinically-aware median imputation
  (never zero-fill on clinical values)

### Analysis
- 10 analytical SQL queries across mortality,
  risk, capacity, and equity dimensions
- 3 PostgreSQL views: v_clinical_overview,
  v_monthly_summary, v_risk_summary
- Statistical significance testing:
  chi-square + correlation analysis
  (analysis/statistical_findings.md)

### Dashboard
- 5-page Power BI dashboard with drill-through
  and custom tooltip pages
- DAX: ALL()-based cohort benchmark,
  RANKX condition severity, MoM delta measure

### Quality
- 15-point data quality assertion suite
- GitHub Actions CI: lint + quality checks
- Architecture diagram added to docs/
