# HOSPIQ — Architecture Document

## Pipeline Overview

```
Raw CSV (Kaggle)
    ↓
AWS S3 Raw Folder
(hospiq-cardiac-data/raw/)
    ↓
Python pandas (02_clean_transform.py)
- Column renaming
- Date parsing
- Null handling
- Feature engineering
    ↓
AWS S3 Processed Folder
(hospiq-cardiac-data/processed/)
    ↓
Python psycopg2 (03_load_to_rds.py)
- dim_patient load
- dim_date load
- fact_admissions load
    ↓
AWS RDS PostgreSQL 15
- Star schema
- 3 analytical views
    ↓
Power BI Desktop
- Direct RDS connection
- 3-page dashboard
```

## AWS Resources

| Resource | Name | Type | Cost |
|----------|------|------|------|
| S3 Bucket | hospiq-cardiac-data-935140613339 | Standard | ~$0.00/month |
| RDS Instance | hospiq-db | db.t3.micro PostgreSQL 15 | Free tier |
| Region | ap-south-1 (Mumbai) | — | — |

## Database Schema

```
dim_patient (12,244 rows)
  mrd_no VARCHAR(20) PK
  age INTEGER
  age_group VARCHAR(20)
  gender VARCHAR(10)
  locality VARCHAR(10)

dim_date (730 rows)
  date_id DATE PK
  day_name VARCHAR(10)
  month_name VARCHAR(10)
  month_num INTEGER
  year INTEGER
  quarter VARCHAR(5)
  fiscal_quarter VARCHAR(5)
  season VARCHAR(20)
  is_weekend BOOLEAN

fact_admissions (15,757 rows)
  sno INTEGER PK
  mrd_no FK → dim_patient
  admission_date FK → dim_date
  [all clinical columns]
```

## Security Notes
- AWS credentials stored in .env (gitignored)
- RDS accessible on port 5432 from specific IPs only
- No sensitive patient data in GitHub
- Raw CSVs gitignored
