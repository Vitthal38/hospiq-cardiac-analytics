"""
test_rds_connection.py
==================================================================================
Purpose      : Quick smoke test that the RDS PostgreSQL instance is reachable
               using the credentials in .env. Prints the server version on
               success, or a clear error message on failure.
Input        : .env  (RDS_HOST, RDS_PORT, RDS_DATABASE, RDS_USERNAME, RDS_PASSWORD)
Output        : "Connection successful" + PostgreSQL version, or the error.
Dependencies : psycopg2-binary, python-dotenv
Run          : python python/test_rds_connection.py
==================================================================================
"""

import os
import sys

from dotenv import load_dotenv
import psycopg2

load_dotenv()

host = os.getenv("RDS_HOST")
port = os.getenv("RDS_PORT", "5432")
database = os.getenv("RDS_DATABASE")
user = os.getenv("RDS_USERNAME")
password = os.getenv("RDS_PASSWORD")

missing = [k for k, v in {
    "RDS_HOST": host,
    "RDS_DATABASE": database,
    "RDS_USERNAME": user,
    "RDS_PASSWORD": password,
}.items() if not v or v.startswith("your")]

if missing:
    print(f"[ABORT] These .env values are still placeholders/blank: {', '.join(missing)}")
    print("        Fill them in after the RDS instance is created (Task 7), then re-run.")
    sys.exit(1)

print(f"Connecting to {host}:{port}/{database} as {user} ...")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password,
        connect_timeout=10,
    )
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
    conn.close()
    print("Connection successful")
    print(f"Server: {version}")
except Exception as exc:
    print("Connection FAILED")
    print(f"Error: {exc}")
    sys.exit(1)
