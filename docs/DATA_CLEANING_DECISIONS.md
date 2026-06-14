# Data Cleaning Decisions

_Phase 2 reference. Every decision below is grounded in the Phase 1 findings in `EDA_REPORT.md`. Format for each: **Problem → Options considered → Decision → Why → Downstream impact.**_

---

## Decision 1 — Column Renaming Strategy
- **Problem:** Raw columns are inconsistent: spaces (`MRD No.`), trailing spaces (`SMOKING `), slashes (`TYPE OF ADMISSION-EMERGENCY/OPD`), and mixed case.
- **Options:** (a) keep as-is; (b) lowercase only; (c) full `snake_case` rename.
- **Decision:** Rename every column to `snake_case` (e.g. `MRD No.` → `mrd_no`, `DURATION OF STAY` → `los_days`).
- **Why:** SQL identifiers and Python attribute access both break on spaces/slashes; `snake_case` is the professional convention and avoids quoting columns everywhere.
- **Impact:** All downstream SQL, Python, and Power BI reference clean names; the mapping is recorded in `DATA_DICTIONARY.md`.

## Decision 2 — Date Parsing (mixed-format, NOT naive dayfirst)
- **Problem:** EDA proved `D.O.A` mixes formats — early rows are M/D/YYYY (`4/1/2017` = 1 Apr, confirmed by `month year=Apr-17`), later rows are D/M/YYYY (`31/03/2019`). Naive `dayfirst=True` failed on 3,767 rows and mismatched 15,734 LOS values.
- **Options:** (a) `dayfirst=True` (rejected — fails on ~3,800 rows); (b) `dayfirst=False` (fails on the late D/M rows); (c) disambiguate using the reliable `month year` label.
- **Decision:** Parse with both day-first and month-first, then for each row choose the parse whose (year, month) matches the `month year` column.
- **Why:** `month year` (`Apr-17` … `Mar-19`) is unambiguous and present for every row, so it resolves which interpretation is correct.
- **Impact:** `admission_date` is correct for season/fiscal-quarter/trend analysis and `dim_date`. (LOS itself comes from the reported `DURATION OF STAY` column, not date subtraction, so it is unaffected.)
- **Run result (Phase 2):** 12,268 rows parsed correctly by the simple (M/D) match, **3,489 required the D/M fallback**, **0 failed**. For reference, naive `dayfirst=True` alone fails on **3,767 rows**. Calculated-vs-reported LOS mismatch was **15,738 (99.9%)**, confirming date subtraction is unreliable — reported `DURATION OF STAY` is kept authoritative. (1 discharge_date remained NaT.)

## Decision 3 — BNP Null Handling
- **Problem:** BNP is 53.6% missing (8,441), and missingness is informative (ordered selectively for suspected heart failure).
- **Options:** (a) drop the column; (b) drop rows (loses 8,441); (c) mean-fill; (d) median-fill.
- **Decision:** Median-fill (**470.50**), and **exclude BNP from correlation/regression**.
- **Why:** Dropping the missing rows destroys the dataset; mean (817.8) is skewed by extremes up to 5,000; median is robust. Keeping the column lets it contribute to risk scoring without pretending it's analysis-grade.
- **Run result (Phase 2):** the column also contained **640 `EMPTY` strings**; after coercion, **9,081 values total were median-filled** (8,441 raw nulls + 640 EMPTY).
- **Impact:** Usable as a soft risk signal only; explicitly flagged as not correlation-safe.

## Decision 4 — EF Null Handling
- **Problem:** Ejection Fraction is 9.5% missing (1,505) but clinically central (drives risk_score and mortality stratification).
- **Options:** (a) drop rows; (b) mean-fill; (c) median-fill.
- **Decision:** Median-fill (**42.00**).
- **Why:** 9.5% is too much to drop, EF is too important to discard, and median resists skew.
- **Run result (Phase 2):** EF also contained **94 `EMPTY` strings**; **1,599 values total were median-filled** (1,505 raw nulls + 94 EMPTY).
- **Impact:** EF available for all rows in `risk_score` (`ef < 40` flag) and EF-band mortality analysis; imputation noted as a caveat.

## Decision 5 — Other Lab Null Handling (HB, TLC, PLATELETS, GLUCOSE, UREA, CREATININE)
- **Problem:** Each has low missingness (1.5–5.5%) plus literal `EMPTY` string markers.
- **Options:** (a) drop rows; (b) zero-fill; (c) median-fill after coercion.
- **Decision:** Coerce to numeric (turning `EMPTY` → NaN), then median-fill each column independently.
- **Why:** Zero-filling a lab value is clinically wrong (0 creatinine ≠ missing); median preserves distribution; missingness is low enough that imputation barely moves aggregates.
- **Run result (Phase 2):** `EMPTY` strings replaced — GLUCOSE 82, PLATELETS 9, HB 4, CREATININE 4, TLC 4, UREA 3 (BNP 640 + EF 94 above = **840 total EMPTY across all labs**). Medians used and total values filled (incl. EMPTY): HB **12.40** (256), TLC **10.10** (290), PLATELETS **226.00** (294), GLUCOSE **136.00** (945), UREA **35.00** (244), CREATININE **1.00** (251).
- **Impact:** Complete numeric columns for SQL aggregates without distorting means.

## Decision 6 — Age Outlier Handling
- **Problem:** Age ranges 4–110; 34 patients <15 and 2 >100.
- **Options:** (a) clip to a "normal" band; (b) drop; (c) keep and flag.
- **Decision:** Keep all; bucket into `age_group` (Under 40 / 40-60 / 61-80 / Over 80).
- **Why:** Paediatric and centenarian cardiac admissions are clinically real, not data errors; removing them would bias mortality analysis.
- **Impact:** Full age range retained; `age_group` enables cohort comparison.

## Decision 7 — Length-of-Stay Outlier Handling
- **Problem:** LOS ranges 1–98 days; only 2 records exceed 60.
- **Options:** (a) cap values at a threshold; (b) drop long stays; (c) keep all, cap only chart display.
- **Decision:** Keep all values in calculations; cap **charts** at 30 days for readability.
- **Why:** Long stays are genuine complex admissions and matter for cost/capacity analysis; only the visual would be distorted by the tail.
- **Impact:** Accurate percentile/mean LOS; readable distributions.

## Decision 8 — RURAL Mapping
- **Problem:** `RURAL` stores `R`/`U`.
- **Decision:** Map `R` → `Rural`, `U` → `Urban` (column renamed `locality`).
- **Why:** Self-documenting values for SQL output and Power BI legends.
- **Impact:** Rural-vs-urban analysis reads clearly with no decoding.

## Decision 9 — OUTCOME Mapping
- **Problem:** `OUTCOME` stores `DISCHARGE` / `EXPIRY` / `DAMA`.
- **Decision:** Map → `Discharged` / `Expired` / `DAMA`.
- **Why:** Consistent, presentation-ready labels; `DAMA` kept as the recognised clinical acronym.
- **Impact:** Clean labels across every query and dashboard.

## Decision 10 — Repeat Admission Handling
- **Problem:** 12,244 patients produced 15,757 rows (3,513 repeats; one patient 17 times).
- **Options:** (a) deduplicate to one row per patient; (b) keep all admissions.
- **Decision:** Keep every admission row; `dim_patient` holds one row per `mrd_no`, `fact_admissions` holds every admission.
- **Why:** Each admission is a distinct clinical event; deduplicating would discard real outcomes and understate volume.
- **Impact:** Star schema correctly separates patient identity (dimension) from admission events (fact).

## Decision 11 — Risk Score Construction
- **Problem:** Need a single, explainable severity indicator.
- **Options:** (a) black-box model; (b) transparent additive flag score.
- **Decision:** `risk_score` = sum of 6 flags: diabetes + hypertension + cad + ckd + (ef < 40) + (creatinine > 1.5); banded into `risk_category` (0 = Low, 1-2 = Moderate, 3-4 = High, 5+ = Critical).
- **Why:** Transparent and clinically defensible; can be explained to non-technical stakeholders and recomputed by hand.
- **Impact:** Drives risk-stratification analysis; validated against mortality in Phase 5.

## Decision 12 — Why Median over Mean for Imputation
- **Problem:** Choosing a central-tendency fill for skewed clinical labs.
- **Decision:** Use the **median** for every imputed column.
- **Why:** Lab values (BNP, creatinine, glucose) are right-skewed — means are dragged up by extreme cases (e.g. BNP mean 817.8 vs median 470.5). The median represents a typical patient far better.
- **Impact:** Imputation does not inflate averages or distort risk thresholds.

## Decision 13 — Boolean Flag Coercion
- **Problem:** Clinical flags are `0`/`1` integers, but `CHEST INFECTION` contains a stray `\` value.
- **Decision:** Coerce all flag columns to numeric (invalid → 0), then to boolean.
- **Why:** Clean boolean typing is required for PostgreSQL `BOOLEAN` columns and reliable `WHERE flag = TRUE` filters.
- **Impact:** No type errors on load; correct condition counts in SQL.
