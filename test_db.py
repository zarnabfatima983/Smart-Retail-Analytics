import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Zarnab123@",      # Change this if your root user has a password
        database="smart_retail"
    )

    print("✅ Connected successfully!")
    conn.close()

except Exception as e:
    print("❌ Error:", e)