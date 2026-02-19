
import sqlite3
import os

DB_NAME = "koperty_system.db"

print(f"Checking database: {DB_NAME}")
if not os.path.exists(DB_NAME):
    print("❌ API Error: Database file not found!")
    exit(1)

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM envelopes")
    count = cursor.fetchone()[0]
    print(f"✅ Connection successful. Envelopes count: {count}")
    
    cursor.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    print(f"ℹ️ Journal Mode: {mode}")

    conn.close()
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
