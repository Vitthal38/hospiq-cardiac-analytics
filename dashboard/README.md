# Dashboard — HOSPIQ Cardiac Analytics (Power BI)

The Power BI report (`hospiq_cardiac.pbix`) is a large binary and is **git-ignored**; it is available on request. Rendered proof of every page lives in [`../screenshots/`](../screenshots/).

## Pages
1. **Clinical Overview** — 5 KPI cards (Total Admissions, Mortality Rate, STEMI Count, Emergency Rate, Avg LOS), monthly admissions trend with an average reference line, outcomes by age group, Emergency vs OPD donut.
2. **Risk Intelligence** — cardiogenic-shock / CKD / critical-risk / diabetes mortality cards, mortality by risk tier (severity gradient), mortality by clinical condition (cardiogenic shock highlighted), mortality trend by risk score.
3. **Rural vs Urban** — 8 comparison cards + 3 comparative charts across mortality, DAMA, LOS, and emergency share.
4. **Patient Cohort Detail** — drill-through destination (right-click any risk-tier bar on page 2) showing patient-level rows.
5. **Condition Tooltip** — custom report-page tooltip surfacing condition mortality rank, count, avg LOS, and delta vs cohort average.

## Connection
Built on the cleaned dataset in [`../data/processed/hdhi_admission_cleaned.csv`](../data/processed/). During development the source was PostgreSQL on AWS RDS (views `v_clinical_overview`, `v_monthly_summary`, `v_risk_summary`); the flat cleaned CSV is the portable equivalent.

## Key DAX measures
```dax
Patient Count        = COUNTROWS(hdhi_admission_cleaned)
Cohort Avg Mortality = CALCULATE([Mortality Rate], ALL(hdhi_admission_cleaned))
Mortality vs Cohort  = [Mortality Rate] - [Cohort Avg Mortality]
Condition Mortality Rank =
    RANKX(
        FILTER(ALL(Conditions[Condition]), NOT ISBLANK([Condition Mortality])),
        [Condition Mortality], , DESC, DENSE
    )
```

## Data Model Notes

### Conditions Table
The `Conditions` table used in the `Condition Mortality Rank` RANKX measure is a
calculated table in Power BI that unpivots the six boolean condition flags from
`hdhi_admission_cleaned` into a single column:

```dax
Conditions = UNION(
    ROW("Condition", "Cardiogenic Shock"),
    ROW("Condition", "STEMI"),
    ROW("Condition", "AKI"),
    ROW("Condition", "Atrial Fibrillation"),
    ROW("Condition", "Heart Failure"),
    ROW("Condition", "CKD")
)
```

This table is joined to the fact table via a DAX measure that filters
`hdhi_admission_cleaned` by each condition flag. It exists only in the Power BI
data model and has no SQL equivalent — it is the source of the
`Condition Mortality Rank` column on the Risk Intelligence page.
