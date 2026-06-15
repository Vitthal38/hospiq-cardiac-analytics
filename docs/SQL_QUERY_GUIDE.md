# SQL Query Guide — Plain English Explanations

## What is SQL?
SQL (Structured Query Language) is the language used to ask questions of data stored in a database. Instead of scrolling through 15,757 rows by hand, you write a short instruction — "count how many patients died, grouped by age" — and the database returns the answer in milliseconds. Every query in this project simply asks a clear business question and lets the database do the counting, averaging, and grouping. No programming loops, just declarative questions.

## The 10 Business Questions We Asked

### Q1: Hospital Overall Scorecard
**What we asked:** What are the headline numbers for this hospital?
**What we found:** 15,757 admissions from 12,244 unique patients; 1,105 deaths (7.01% mortality); 896 DAMA; average stay 6.4 days; 2,202 STEMI; 4,561 heart-failure cases; 944 cardiogenic-shock cases.
**Why it matters:** This is the single-slide summary a hospital director needs — overall scale, mortality, and the burden of the most serious conditions, all in one row.

### Q2: Rural vs Urban Outcomes
**What we asked:** Do patients from rural areas have worse outcomes?
**What we found:** Rural mortality 7.58% vs urban 6.83%, despite identical average stay (6.4 days) and ejection fraction (~43%).
**Why it matters:** Equal disease severity but unequal survival suggests an access-to-care gap — rural patients may arrive later — which is a healthcare-equity issue worth investigating.

### Q3: Age Group Risk
**What we asked:** Which age group faces the highest mortality?
**What we found:** Over-80 patients die at 12.14% — more than double the 40–60 group (5.23%). Even Under-40 (5.91%) slightly exceeds 40–60.
**Why it matters:** It tells the hospital where to concentrate intensive monitoring and which cohorts drive the most deaths and longest stays — directly informing resource allocation.

### Q4: Seasonal Patterns
**What we asked:** Do cardiac emergencies follow seasonal patterns?
**What we found:** January is the busiest month (1,643 admissions) and deadliest (9.80%). By season, Monsoon has the most STEMI cases (717), ahead of Winter (620).
**Why it matters:** Predictable seasonal peaks let the hospital staff up cardiology and ICU capacity ahead of winter and monsoon surges instead of reacting after the fact.

### Q5: Deadliest Combinations
**What we asked:** Which combination of existing conditions is most dangerous?
**What we found:** Hypertension + CKD = 47.2% mortality — about 6.7× the hospital average. CKD appears in every one of the ten deadliest combinations.
**Why it matters:** It flags exactly which patients need the most aggressive early intervention on arrival — the cardio-renal patient, not the diabetic, is the red flag.

### Q6: Risk Score Validation
**What we asked:** Does our risk score actually predict mortality?
**What we found:** Mortality rises steadily with the score — Low 5.27%, Moderate 6.19%, High 8.65%, Critical 8.66% — and average ejection fraction falls from 54% to 33% across the same bands.
**Why it matters:** A validated, simple score can be used at the bedside to triage patients the moment they are admitted — clinical decision support that any nurse can apply.

### Q7: Year-over-Year Trend
**What we asked:** Is the hospital seeing more cardiac patients each year?
**What we found:** Yes — FY2018-19 beat the prior year in most months (e.g. February +138, March +129, January +97 admissions).
**Why it matters:** Rising demand is the evidence base for capacity planning, hiring, and bed expansion decisions.

### Q8: Heart Pump Function and Survival
**What we asked:** How does the heart's pumping efficiency (ejection fraction) predict survival?
**What we found:** Severely Reduced EF (under 30%) = 16.08% mortality vs 3.33% for Normal EF — nearly a 5× difference.
**Why it matters:** EF is the single clearest survival signal in the data, so a low EF on admission should automatically raise a patient's monitoring priority.

### Q9: STEMI Patient Profile
**What we asked:** Who are the highest-risk heart-attack (STEMI) patients?
**What we found:** Urban patients over 80 have the worst STEMI mortality at 32.9% (76 cases, 17 with cardiogenic shock).
**Why it matters:** Knowing the highest-risk profile lets the ER apply the fastest STEMI protocol (door-to-balloon time) to exactly the patients who benefit most.

### Q10: How Long Do Patients Stay?
**What we asked:** What does a typical cardiac hospital stay look like?
**What we found:** Median 5 days; 75th percentile 8 days; 90th percentile 12 days; 95th percentile 15 days; maximum 98 days (mean 6.4).
**Why it matters:** Most stays are short, but a small tail of very long stays consumes disproportionate bed capacity — essential for bed-planning and cost forecasting.

## Three SQL Techniques Worth Understanding

### CTEs (used in Q6)
A CTE ("Common Table Expression") lets you break a complex question into clear, named steps instead of one tangled block. For the risk-score validation we did it in three steps: (1) join each admission to its patient, (2) label each patient Low/Moderate/High/Critical based on their risk score, (3) count the death rate within each label. Reading top to bottom, it tells a story — join, label, summarise — which anyone can follow even without knowing SQL.

### Window Functions (used in Q7)
A window function compares each row to *other related rows* without collapsing the table. For the year-over-year trend, it let us place each month's admissions right next to the same month from the previous year — so "January 2019: 870" sits beside "January 2018: 773," and we can show the +97 change. It's the database equivalent of looking left to last year while reading across the calendar.

### Percentiles (used in Q10)
A percentile tells you the value below which a given share of patients fall — the median (50th percentile) is the "typical" stay. We prefer the median over the average for length of stay because a handful of 98-day admissions drag the average upward and make a typical stay look longer than it is. The median (5 days) honestly represents the middle patient; the average (6.4 days) is pulled up by the long tail. Showing both, plus the 90th/95th percentiles, gives the full picture.
