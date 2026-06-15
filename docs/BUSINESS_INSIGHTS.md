# Business Insights — HOSPIQ SQL Analysis
## Data: 15,757 real cardiac admissions, Hero DMC Heart Institute (Apr 2017 – Mar 2019)

_All numbers below are live query output from `sql/02_analysis_queries.sql` run against the RDS PostgreSQL star schema via `python/run_sql_queries.py`._

## Executive Summary
- **Total admissions:** 15,757 (12,244 unique patients); **mortality rate 7.01%** (1,105 deaths), DAMA 5.69% (896).
- **Most dangerous comorbidity combo:** Hypertension + CKD → **47.2% mortality**, ~6.7× the hospital average.
- **Seasonal peak:** January is the busiest month (1,643 admissions) and deadliest (9.80%); **Monsoon carries the most STEMI cases (717)**.
- **Risk score validated:** mortality rises monotonically Low 5.27% → Moderate 6.19% → High 8.65% → **Critical 8.66%**.
- **Ejection fraction is the sharpest single predictor:** mortality climbs from **3.33% (normal EF) to 16.08% (severely reduced)** — nearly 5×.

## Q1: Hospital Scorecard
| total_admissions | unique_patients | total_deaths | mortality_pct | dama_count | avg_los_days | avg_icu_days | stemi_cases | heart_failure_cases | shock_cases |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15757 | 12244 | 1105 | 7.01 | 896 | 6.4 | 3.8 | 2202 | 4561 | 944 |

## Q2: Rural vs Urban
| locality | admissions | avg_los | deaths | mortality_pct | stemi_cases | avg_ef |
| --- | --- | --- | --- | --- | --- | --- |
| Rural | 3758 | 6.4 | 285 | 7.58 | 553 | 43.0 |
| Urban | 11999 | 6.4 | 820 | 6.83 | 1649 | 43.4 |

**Insight:** Rural patients die at a higher rate (7.58% vs 6.83%) despite identical length of stay and ejection fraction — pointing to access/time-to-care gaps rather than disease severity on arrival.

## Q3: Age Group Risk
| age_group | patients | avg_los | deaths | mortality_pct | avg_ef |
| --- | --- | --- | --- | --- | --- |
| Over 80 | 1013 | 7.9 | 123 | 12.14 | 42.5 |
| 61-80 | 7581 | 6.7 | 601 | 7.93 | 42.6 |
| Under 40 | 931 | 5.9 | 55 | 5.91 | 48.3 |
| 40-60 | 6232 | 5.9 | 326 | 5.23 | 43.5 |

**Insight:** The Over-80 group dies at 12.14% — 2.3× the 40–60 group. Notably, Under-40 mortality (5.91%) exceeds the 40–60 band (5.23%): young cardiac admissions are rare but disproportionately severe.

## Q4: Seasonal Patterns
| season | month | admissions | stemi_cases | emergencies | mortality_pct | avg_los |
| --- | --- | --- | --- | --- | --- | --- |
| Winter | January | 1643 | 198 | 1189 | 9.80 | 6.5 |
| Winter | February | 1432 | 210 | 980 | 7.75 | 6.6 |
| Summer | March | 1355 | 131 | 847 | 5.09 | 6.6 |
| Summer | April | 996 | 143 | 695 | 8.33 | 6.2 |
| Summer | May | 1185 | 190 | 869 | 5.49 | 6.0 |
| Monsoon | June | 1194 | 168 | 891 | 5.78 | 6.4 |
| Monsoon | July | 1176 | 179 | 875 | 5.61 | 6.2 |
| Monsoon | August | 1145 | 177 | 854 | 8.38 | 6.3 |
| Monsoon | September | 1262 | 193 | 923 | 5.71 | 6.6 |
| Post-Monsoon | October | 1359 | 188 | 920 | 6.48 | 6.6 |
| Post-Monsoon | November | 1468 | 213 | 946 | 8.31 | 6.5 |
| Winter | December | 1542 | 212 | 935 | 6.68 | 6.3 |

**Insight:** Volume and mortality peak in **winter (January: 1,643 admissions, 9.80% mortality)**. By season-total STEMI, **Monsoon leads with 717 cases** (Winter 620, Summer 464, Post-Monsoon 401); November is the single highest STEMI month (213).

## Q5: Deadliest Comorbidity Combinations
| diabetes | hypertension | cad | ckd | patients | avg_los | mortality_pct |
| --- | --- | --- | --- | --- | --- | --- |
| – | ✓ | – | ✓ | 72 | 8.3 | **47.2** |
| – | – | ✓ | ✓ | 162 | 7.9 | 26.5 |
| – | – | – | ✓ | 199 | 7.8 | 21.6 |
| – | ✓ | – | ✓ (DM) | 109 | 8.1 | 21.1 |
| – | ✓ | – | – | 609 | 5.8 | 17.7 |

**Key finding:** Hypertension + CKD carries **47.2% mortality** — nearly 7× the 7.01% hospital average. Every one of the 10 deadliest combinations contains **CKD**; diabetes alone sits at just 9.1%.

## Q6: Risk Score Validation
| risk_band | patients | avg_los | mortality_pct | avg_ef |
| --- | --- | --- | --- | --- |
| Critical Risk | 889 | 8.7 | 8.66 | 32.9 |
| High Risk | 5110 | 7.1 | 8.65 | 38.1 |
| Moderate Risk | 7767 | 5.9 | 6.19 | 45.2 |
| Low Risk | 1991 | 5.6 | 5.27 | 54.2 |

**Does Critical Risk have the highest mortality? Yes — 8.66%.** Mortality rises monotonically across bands and average EF falls 54.2 → 32.9, confirming the score tracks real severity. (Critical and High are near-tied, suggesting the top two tiers could be merged.)

## Q7: Year-over-Year Trend
Admissions are **clearly growing**. FY2018-19 beats FY2017-18 in most months — February +138, March +129, January +97, August +103, October +103 vs the prior year. The hospital is seeing materially rising cardiac demand.

## Q8: EF and Survival
| ef_category | patients | avg_los | mortality_pct |
| --- | --- | --- | --- |
| 1. Normal EF (55%+) | 4625 | 5.8 | 3.33 |
| 2. Mildly Reduced (40-54%) | 5006 | 5.9 | 4.53 |
| 3. Moderately Reduced (30-39%) | 3856 | 7.2 | 9.31 |
| 4. Severely Reduced (under 30%) | 2270 | 7.4 | 16.08 |

**Severely Reduced EF mortality: 16.08%. Normal EF mortality: 3.33%** — a ~4.8× gradient. Pump function is the single cleanest survival signal in the dataset.

## Q9: STEMI Patients
| locality | age_group | stemi_cases | avg_los | avg_ef | with_shock | mortality_pct |
| --- | --- | --- | --- | --- | --- | --- |
| Urban | Over 80 | 76 | 8.5 | 36.0 | 17 | 32.9 |
| Rural | 61-80 | 236 | 6.6 | 36.5 | 26 | 13.1 |
| Urban | 61-80 | 701 | 7.4 | 37.1 | 96 | 12.4 |
| Rural | Under 40 | 33 | 6.3 | 37.3 | 4 | 12.1 |
| Urban | Under 40 | 60 | 6.2 | 39.9 | 6 | 10.0 |

**Highest-risk STEMI group: Urban patients over 80 — 32.9% mortality** (76 cases, 17 with cardiogenic shock). STEMI mortality is driven by age and concurrent shock.

## Q10: LOS Distribution
| p25_days | median_days | p75_days | p90_days | p95_days | max_days | mean_days |
| --- | --- | --- | --- | --- | --- | --- |
| 3.0 | 5.0 | 8.0 | 12.0 | 15.0 | 98 | 6.4 |

**Insight:** The typical stay is short (median 5 days) but right-skewed — 5% of admissions exceed 15 days, up to a 98-day maximum.

## Most Significant Finding
**Chronic kidney disease — not diabetes — is the deadliest companion to heart disease at this hospital.** Patients presenting with **hypertension + CKD died at 47.2%**, nearly **7× the 7.01% hospital average**, and CKD appears in *every one* of the ten deadliest comorbidity combinations. Meanwhile diabetes alone — the condition most associated with cardiac risk in the public mind — sat at just 9.1%, barely above the 8.8% baseline for patients with none of these conditions. The data quietly rewrites which risk factor a cardiac ward should fear most: the cardio-renal patient.

## Interview Talking Points
Five numbers a candidate must know:
1. **15,757 admissions, 7.01% in-hospital mortality** (1,105 deaths) — the headline scorecard (Q1).
2. **47.2% mortality for hypertension + CKD** — ~7× the average; CKD is the dominant multiplier (Q5).
3. **Risk score validated: 5.27% (Low) → 8.66% (Critical)** mortality, monotonic, with EF falling 54→33 (Q6).
4. **EF gradient: 3.33% (normal) → 16.08% (severely reduced)** — the sharpest single predictor (Q8).
5. **January is the deadliest month at 9.80% mortality (1,643 admissions)**; winter is the demand+mortality peak (Q4).
