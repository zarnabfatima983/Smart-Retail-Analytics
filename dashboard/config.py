"""Centralised configuration for Smart Retail Analytics."""

# Database
DB_CONFIG = {
    "host":        "localhost",
    "user":        "root",
    "password":    "Zarnab123@",          # update with your MySQL password
    "database":    "smart_retail",
    "charset":     "utf8mb4",
    "use_unicode": True,
}

# Auth
AUTH_CREDENTIALS = {
    "username": "admin",
    "password": "admin",
}

# App
CACHE_TTL_SECONDS = 300   # 5 minutes
BATCH_SIZE        = 500   # rows per MySQL insert batch

# Paths

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE_PATH = BASE_DIR / "data" / "SampleSuperstore.csv"

print("CSV_FILE_PATH =", CSV_FILE_PATH)
print("Exists =", CSV_FILE_PATH.exists())

CSV_ENCODING = "latin1"
