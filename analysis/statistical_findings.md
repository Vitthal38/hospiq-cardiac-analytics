# Statistical Analysis — HOSPIQ Cardiac Admissions

## 1. Rural vs Urban Mortality Gap
- Rural mortality: **7.55%** · Urban mortality: **6.85%**
- Chi-square test of independence: chi2 = 2.053, p = 0.1519, dof = 1
- Effect size (Cramer's V) = 0.011 (small)
- **Interpretation:** the rural–urban difference is NOT statistically significant at alpha 0.05, so the observed gap may be attributable to chance.

## 2. Correlation with Mortality
Pearson correlation of each variable with `is_expired` (|r| > 0.15 flagged as notable):

| Variable | Pearson r | Notable? |
| --- | --- | --- |
| ef | -0.167 | ✅ notable |
| creatinine | 0.134 | — |
| age | 0.067 | — |
| los_days | -0.059 | — |
| risk_score | 0.047 | — |

## 3. Age Group Mortality (ANOVA)
- Group mortality — Under 40: 5.89% · 40-60: 5.14% · 61-80: 7.98% · Over 80: 12.14%
- One-way ANOVA: F = 29.489, p = 0.0000
- **Interpretation:** mortality rates across age groups **differ significantly** (alpha 0.05).

## 4. Emergency vs OPD Mortality
- Emergency mortality: **9.86%** · OPD mortality: **0.58%**
- Chi-square: chi2 = 441.043, p = 0.0000
- Odds ratio (Emergency vs OPD death odds) = **18.77**
- **Interpretation:** the difference is significant; emergency-route patients face 18.8x the odds of in-hospital death versus planned/OPD admissions.

## 5. Length of Stay by Outcome
| Outcome | Mean LOS | Median LOS | Std | 90th pct |
| --- | --- | --- | --- | --- |
| Discharged | 6.59 | 6 | 4.77 | 12 |
| Expired | 5.34 | 3 | 6.89 | 13 |
| DAMA | 5.07 | 3 | 5.46 | 11 |

- Mann-Whitney U (Expired vs Discharged LOS) = 4779268, p = 0.0000
- **Interpretation:** Expired and Discharged length-of-stay distributions are **significantly different** (non-parametric test used because LOS is right-skewed).

## Key Takeaway
- Emergency-route admissions carry meaningfully higher death odds (18.8x vs OPD) — the pathway where clinical risk concentrates.
- Ejection fraction and creatinine are the variables most correlated with death, confirming pump function and kidney stress as the clearest bedside warning signs.
- The rural–urban mortality gap is not statistically robust, pointing to access factors worth a targeted operational review rather than a broad clinical overhaul.
