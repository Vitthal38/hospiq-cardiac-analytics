# AWS Infrastructure Evidence

## S3 Bucket
File: s3_bucket_overview.png
Shows: hospiq-cardiac-analytics bucket with raw/ and processed/ prefixes visible

File: s3_processed_objects.png
Shows: hdhi_admission_cleaned.csv in processed/ with file size and last modified date

## RDS PostgreSQL
File: rds_instance.png
Shows: hospiq-db RDS instance (PostgreSQL 15, db.t3.micro free tier)
Note: Instance deleted post-project to avoid billing. Screenshot taken before deletion.

## How AWS was used
- Raw CSV uploaded to S3 raw/ via pipeline/01_extract_load.py (boto3)
- Cleaned CSV uploaded to S3 processed/ via pipeline/02_clean_transform.py
- Star schema loaded to RDS PostgreSQL via pipeline/03_load_postgres.py (psycopg2)
- Power BI connected to RDS via PostgreSQL connector (DirectQuery mode)
- RDS deleted after the dashboard was published to Power BI Service to eliminate
  ongoing billing (~$15/month free tier cap)
