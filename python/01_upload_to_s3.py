"""
01_upload_to_s3.py — Phase 3: Upload raw data to the S3 data lake
==================================================================================
Uploads the 4 original Kaggle CSV files from data/raw/ to the S3 raw/ prefix,
then lists the bucket to verify. Raw files are never modified after upload.

Input  : data/raw/*.csv  (4 original files)
Output : s3://<S3_BUCKET>/raw/<file>.csv
Next   : 02_clean_transform.py
==================================================================================
"""

# ----------------------------------------------------------------- 1. setup
import os
import sys
import logging
from pathlib import Path

import boto3
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console is cp1252 by default
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()

# ----------------------------------------------------------- 2. configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
BUCKET = os.getenv("S3_BUCKET")
RAW_PREFIX = os.getenv("S3_RAW_PREFIX", "raw/")
PROCESSED_PREFIX = os.getenv("S3_PROCESSED_PREFIX", "processed/")

RAW_DIR = Path("data") / "raw"
RAW_FILES = [
    "HDHI Admission data.csv",
    "HDHI Mortality Data.csv",
    "HDHI Pollution Data.csv",
    "table_headings.csv",
]


# ------------------------------------------------------------ 3. upload helper
def upload_to_s3(local_path, s3_key, bucket):
    """Upload a single file to S3 with progress logging."""
    s3 = boto3.client("s3")
    file_size = Path(local_path).stat().st_size
    logger.info(f"Uploading {local_path} ({file_size / 1024 / 1024:.2f} MB)")
    s3.upload_file(str(local_path), bucket, s3_key)
    logger.info(f"Uploaded to s3://{bucket}/{s3_key}")
    return True


# ----------------------------------------------------------------- 4. main
def main():
    if not BUCKET:
        logger.error("S3_BUCKET not set in .env — aborting.")
        sys.exit(1)

    logger.info(f"Target bucket: {BUCKET} ({AWS_REGION})")
    uploaded = 0
    for fname in RAW_FILES:
        local_path = RAW_DIR / fname
        if not local_path.exists():
            logger.warning(f"Missing local file, skipping: {local_path}")
            continue
        upload_to_s3(local_path, f"{RAW_PREFIX}{fname}", BUCKET)
        uploaded += 1

    # ------------------------------------------------- 5. verify uploads
    logger.info("Verifying bucket contents ...")
    s3 = boto3.client("s3")
    resp = s3.list_objects_v2(Bucket=BUCKET)
    objects = resp.get("Contents", [])

    print("\n=== S3 BUCKET CONTENTS ===")
    print(f"{'Key':<45} {'Size (MB)':>10}  {'Last Modified':>20}")
    print("-" * 80)
    total_bytes = 0
    for obj in sorted(objects, key=lambda o: o["Key"]):
        if obj["Key"].endswith("/"):
            continue  # skip folder placeholder objects
        total_bytes += obj["Size"]
        print(f"{obj['Key']:<45} {obj['Size'] / 1024 / 1024:>10.2f}  "
              f"{obj['LastModified'].strftime('%Y-%m-%d %H:%M'):>20}")

    # ----------------------------------------------------- 6. final summary
    print("\n=== S3 UPLOAD COMPLETE ===")
    print(f"Bucket: {BUCKET}")
    print(f"Files uploaded this run: {uploaded} raw")
    print(f"Total objects in bucket: {sum(1 for o in objects if not o['Key'].endswith('/'))} "
          f"(4 raw + 1 processed expected)")
    print(f"Total data in S3: {total_bytes / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
