# Data Dictionary — HDHI Admission Dataset

## Source
Hero DMC Heart Institute, Ludhiana, Punjab, India
Kaggle: https://www.kaggle.com/datasets/ashishsahani/hospital-admissions-data

## Column Reference

| Original Column | Clean Name | Type | Description | Values/Range |
|-----------------|------------|------|-------------|--------------|
| SNO | sno | Integer | Serial number | 1 to 15757 |
| MRD No. | mrd_no | String | Medical record number — unique per patient | e.g. 234735 |
| D.O.A | admission_date | Date | Date of admission | Apr 2017 – Mar 2019 |
| D.O.D | discharge_date | Date | Date of discharge | Apr 2017 – Mar 2019 |
| AGE | age | Integer | Patient age in years | 4 to 110 |
| GENDER | gender | String | Patient gender | M / F |
| RURAL | locality | String | Patient locality | R=Rural / U=Urban |
| TYPE OF ADMISSION-EMERGENCY/OPD | admission_type | String | How patient was admitted | E=Emergency / O=OPD |
| month year | month_year | String | Month and year of admission | Apr-17 to Mar-19 |
| DURATION OF STAY | los_days | Integer | Length of stay in days | 1 to 98 |
| duration of intensive unit stay | icu_days | Integer | Days in ICU | 0 to 98 |
| OUTCOME | outcome | String | Patient outcome | DISCHARGE / EXPIRY / DAMA |
| SMOKING | smoking | Boolean | Smoking history | 0 / 1 |
| ALCOHOL | alcohol | Boolean | Alcohol use | 0 / 1 |
| DM | diabetes | Boolean | Diabetes Mellitus | 0 / 1 |
| HTN | hypertension | Boolean | Hypertension | 0 / 1 |
| CAD | cad | Boolean | Coronary Artery Disease | 0 / 1 |
| PRIOR CMP | prior_cmp | Boolean | Prior Cardiomyopathy | 0 / 1 |
| CKD | ckd | Boolean | Chronic Kidney Disease | 0 / 1 |
| HB | hb | Numeric | Haemoglobin level (g/dL) | 2.0 to 20.0 |
| TLC | tlc | Numeric | Total Leucocyte Count | varies |
| PLATELETS | platelets | Numeric | Platelet count | varies |
| GLUCOSE | glucose | Numeric | Blood glucose (mg/dL) | varies |
| UREA | urea | Numeric | Blood urea (mg/dL) | varies |
| CREATININE | creatinine | Numeric | Serum creatinine (mg/dL) | varies |
| BNP | bnp | Numeric | Brain Natriuretic Peptide — cardiac stress marker | 53.6% missing |
| RAISED CARDIAC ENZYMES | raised_cardiac_enzymes | Boolean | Elevated troponin/CK-MB | 0 / 1 |
| EF | ef | Numeric | Ejection Fraction % — heart pump efficiency | 5 to 85 — 9.5% missing |
| STEMI | stemi | Boolean | ST-Elevation Myocardial Infarction | 0 / 1 |
| HEART FAILURE | heart_failure | Boolean | Heart failure diagnosis | 0 / 1 |
| HFREF | hfref | Boolean | Heart Failure with Reduced EF | 0 / 1 |
| HFNEF | hfnef | Boolean | Heart Failure with Normal EF | 0 / 1 |
| CARDIOGENIC SHOCK | cardiogenic_shock | Boolean | Shock from cardiac cause | 0 / 1 |
| SHOCK | shock | Boolean | Any shock | 0 / 1 |
| PULMONARY EMBOLISM | pulmonary_embolism | Boolean | Blood clot in lung | 0 / 1 |
| CHEST INFECTION | chest_infection | Boolean | Respiratory infection | 0 / 1 |

## Engineered Features (added during cleaning)
| Feature | Description | Logic |
|---------|-------------|-------|
| age_group | Age bracket | Under 40 / 40-60 / 61-80 / Over 80 |
| season | Season of admission | Summer/Monsoon/Post-Monsoon/Winter |
| risk_score | Composite risk score | Sum of 6 clinical flags (0-6) |
| risk_category | Risk band | Low/Moderate/High/Critical |

## Null Summary
| Column | Null Count | Null % | Action |
|--------|-----------|--------|--------|
| BNP | 8,441 | 53.6% | Fill with median |
| EF | 1,505 | 9.5% | Fill with median |
| GLUCOSE | 863 | 5.5% | Fill with median |
| TLC | 286 | 1.8% | Fill with median |
| PLATELETS | 285 | 1.8% | Fill with median |
| CREATININE | 247 | 1.6% | Fill with median |
| UREA | 241 | 1.5% | Fill with median |
| HB | 252 | 1.6% | Fill with median |
