"""MySQL connection helpers for Smart Retail Analytics."""

import logging
from typing import Optional

import mysql.connector
import pandas as pd
from mysql.connector import Error

from config import DB_CONFIG

logger = logging.getLogger(__name__)


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print("❌ MySQL connection failed:", e)
        logger.error("MySQL connection failed: %s", e)
    return None


def execute_query(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Run a SQL query and return results as a DataFrame."""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    try:
        return pd.read_sql(query, conn, params=params)
    except Error as e:
        logger.error("Query failed: %s", e)
        return pd.DataFrame()
    finally:
        if conn.is_connected():
            conn.close()


def test_connection() -> bool:
    """Return True if a MySQL connection can be established."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        logger.info("Connected to MySQL %s", version[0])
        cursor.close()
        return True
    except Error as e:
        logger.error("Connection test failed: %s", e)
        return False
    finally:
        if conn.is_connected():
            conn.close()
