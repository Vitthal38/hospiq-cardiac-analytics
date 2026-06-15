# EDA Report — HDHI Cardiac Admission Dataset

_Phase 1 of 7 — Exploratory Data Analysis. All figures below are produced by `notebooks/01_eda_exploration.ipynb` on the **raw** dataset (no transformations applied)._

## 1. Dataset Overview

| Attribute | Value |
|---|---|
| Source | Hero DMC Heart Institute, Ludhiana, Punjab, India |
| Kaggle | https://www.kaggle.com/datasets/ashishsahani/hospital-admissions-data |
| Rows | 15,757 |
| Columns | 56 |
| Memory (deep) | ~18,410 KB (~18 MB) |
| Data period | April 2017 – March 2019 (2 fiscal years) |
| Unique patients | 12,244 |

## 2. Null Analysis

Eight columns contain missing values. **BNP is the critical issue at 53.6% missing.**

| Column | Null Count | Null % | Severity |
|---|---|---|---|
| BNP | 8,441 | 53.57% | 🔴 Critical (>20%) |
| EF | 1,505 | 9.55% | 🟠 Moderate |
| GLUCOSE | 863 | 5.48% | 🟡 Minor |
| TLC | 286 | 1.82% | 🟡 Minor |
| PLATELETS | 285 | 1.81% | 🟡 Minor |
| HB | 252 | 1.60% | 🟡 Minor |
| CREATININE | 247 | 1.57% | 🟡 Minor |
| UREA | 241 | 1.53% | 🟡 Minor |

> Note: lab columns also contain the literal string `EMPTY` as a missing marker (e.g. BNP has 7,316 non-null cells raw, but only 6,676 are numerically valid after coercion). These must be coerced to NaN before any numeric work. **Phase 2 confirmed 840 `EMPTY` strings across the 8 lab columns** (BNP 640, EF 94, GLUCOSE 82, PLATELETS 9, HB 4, TLC 4, CREATININE 4, UREA 3) — invisible to `isnull()`.

Chart: `assets/screenshots/eda_01_null_analysis.png`

## 3. Duplicate Analysis

| Metric | Value |
|---|---|
| True duplicate rows (all columns identical) | 0 |
| Total rows | 15,757 |
| Unique patients (MRD No.) | 12,244 |
| Patients with multiple admissions | 2,598 |
| Extra admission records from repeats | 3,513 |
| Average admissions per patient | 1.29 |
| Most admissions by one patient | 17 |

**Conclusion:** there are no true duplicates. The 3,513 "extra" records are legitimate repeat admissions — each is a distinct clinical event. **Do not deduplicate by MRD No.**

## 4. Categorical Distributions

**Outcome (target variable)**

| Outcome | Count | % |
|---|---|---|
| DISCHARGE | 13,756 | 87.30% |
| EXPIRY | 1,105 | 7.01% |
| DAMA | 896 | 5.69% |

**Demographics & admission**

| Variable | Breakdown |
|---|---|
| Gender | Male 9,990 (63.4%) · Female 5,767 (36.6%) |
| Locality | Urban 12,077 (76.6%) · Rural 3,680 (23.4%) |
| Admission type | Emergency 10,924 (69.3%) · OPD 4,833 (30.7%) |

**Comorbidity prevalence**

| Condition | Count | % |
|---|---|---|
| Coronary Artery Disease (CAD) | 10,551 | 67.0% |
| Hypertension (HTN) | 7,656 | 48.6% |
| Diabetes (DM) | 5,097 | 32.3% |
| Prior Cardiomyopathy | 2,434 | 15.4% |
| Chronic Kidney Disease (CKD) | 1,550 | 9.8% |
| Alcohol Use | 1,021 | 6.5% |
| Smoking | 793 | 5.0% |

**Cardiac conditions**

| Condition | Count | % |
|---|---|---|
| Heart Failure | 4,561 | 28.9% |
| STEMI | 2,202 | 14.0% |
| Cardiogenic Shock | 944 | 6.0% |
| Pulmonary Embolism | 242 | 1.5% |

Chart: `assets/screenshots/eda_02_outcome_distribution.png`

## 5. Numeric Outliers

| Column | Min | Max | Mean | Median | Nulls |
|---|---|---|---|---|---|
| AGE | 4 | 110 | 61.4 | 62 | 0 |
| DURATION OF STAY | 1 | 98 | 6.4 | 5 | 0 |
| EF | 14 | 60 | — | — | 1,505 |
| CREATININE | — | 15.63 | — | — | 247 |
| GLUCOSE | — | 888 | — | — | 863 |
| HB | 3.0 | 26.5 | — | — | 252 |

**Outlier flags raised**

| Flag | Count | Examples / Note |
|---|---|---|
| AGE < 15 | 34 | Paediatric cardiac cases — clinically valid |
| AGE > 100 | 2 | Centenarian admissions — valid |
| LOS > 60 days | 2 | Genuine long admissions (max 98) |
| CREATININE > 15 | 2 | Severe renal failure — valid |
| HB > 20 | 14 | High haemoglobin (max 26.5) — review but plausible |
| EF > 85 | 0 | None |
| GLUCOSE > 1000 | 0 | None |

Chart: `assets/screenshots/eda_03_numeric_distributions.png`

## 6. Date Validation

Parsing `D.O.A` / `D.O.D` with `dayfirst=True` (the assumed Indian DD/MM/YYYY convention) **fails badly**, which is itself the key finding:

| Check | Result |
|---|---|
| D.O.A parse failures | 3,767 |
| D.O.D parse failures | 3,770 |
| D.O.A range (as parsed) | 2017-01-04 → 2019-12-03 (artefacts visible) |
| Impossible dates (D.O.D < D.O.A) | 13 |
| LOS mismatch (calculated vs reported) | 15,734 of 15,757 |

**Conclusion:** the `D.O.A` column is **not uniformly DD/MM/YYYY**. Early records are M/D/YYYY (e.g. `4/1/2017` = 1 Apr, confirmed by `month year = Apr-17`) while later records are D/M/YYYY (e.g. `31/03/2019`). A naive `dayfirst=True` mis-parses ~3,800 rows and corrupts almost every calculated LOS. **The cleaning phase must disambiguate using the reliable `month year` column, not a single dayfirst flag.** (See `DATA_CLEANING_DECISIONS.md`, Decision 2.)

> **Phase 2 outcome:** the `month year`-referenced parser resolved this cleanly — **12,268 rows parsed by the simple match, 3,489 needed the day-first fallback, 0 failed.**

## 7. BNP Deep Dive

BNP (Brain Natriuretic Peptide) is a cardiac-stress marker and the dataset's worst quality issue.

- **Missing rate:** 53.6% (8,441 of 15,757).
- **Where present:** ~6,676 numerically valid values; median **470.5**, mean **817.8** (right-skewed by extremes up to 5,000), max 5,000.
- **Missingness is not random:** presence varies by outcome and admission type (BNP is ordered selectively, typically for suspected heart failure), so the missingness is *informative*, not purely random.
- **Decision:** fill with **median (470.5)** for risk-scoring purposes only.
- **Limitation:** because it is >50% imputed and missing-not-at-random, **BNP must be excluded from any correlation/regression analysis.**

## 8. Key Findings

1. **Outcome imbalance** — 87.30% discharged, 7.01% expired (1,105), 5.69% DAMA (896). 12.7% of admissions had an unfavourable outcome.
2. **The BNP problem** — 53.6% missing (8,441). Usable for median-filled risk scoring only; excluded from correlation work.
3. **Repeat admissions are real** — 12,244 unique patients produced 15,757 admissions (3,513 repeats; one patient admitted 17 times). Keep all rows; do not deduplicate.
4. **Age outliers are clinically valid** — 34 patients under 15 and 2 over 100. Range 4–110. Keep and flag, don't remove.
5. **Length-of-stay tail** — max 98 days; only 2 records exceed 60. Keep all; cap charts at 30 days for readability.
6. **Emergency dominance** — 69.3% emergency admissions; this is an acute tertiary cardiac unit, important context for all findings.
7. **Heavy comorbidity burden** — CAD 67.0%, HTN 48.6%, DM 32.3%. These reflect India's chronic-disease epidemic in cardiac populations, not data errors.

## 9. Cleaning Recommendations

| Issue | Recommended Action | Reason |
|---|---|---|
| BNP 53.6% missing | Median-fill; exclude from correlation | Too many rows to drop; missing-not-at-random |
| EF 9.5% missing | Median-fill | Clinically important, moderate missingness |
| Other labs (<6% missing) | Median-fill per column | Low missingness, preserves row count |
| `D.O.A` mixed date format | Disambiguate via `month year` column | `dayfirst=True` fails on 3,767 rows |
| AGE / LOS / CREAT outliers | Keep, flag | Clinically plausible extremes |
| RURAL `R`/`U` | Map → Rural / Urban | Readability |
| GENDER `M`/`F` | Map → Male / Female | Readability |
| OUTCOME codes | Map → Discharged / Expired / DAMA | Standardise |
| Admission `E`/`O` | Map → Emergency / OPD | Readability |
| Boolean flags (0/1, stray `\`) | Coerce → boolean | Clean typing for SQL |
| Repeat admissions | Keep all rows | Each admission is a valid event |
| Column names | Rename → snake_case | Professional convention |
