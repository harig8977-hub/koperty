
import sqlite3
import os

DB_NAME = "koperty_system.db"

def check_logs():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n--- Checking Error Logs (Last 5) ---")
        cursor.execute("SELECT * FROM error_logs ORDER BY created_at DESC LIMIT 5")
        logs = cursor.fetchall()
        if not logs:
            print("No errors found in error_logs table.")
        for log in logs:
            print(f"[{log['created_at']}] {log['error_code']} - {log['barcode']} (User: {log['user_id']})")
            
        print("\n--- Checking Events (Last 5) ---")
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 5")
        events = cursor.fetchall()
        if not events:
            print("No events found.")
        for event in events:
            print(f"[{event['timestamp']}] {event['operation']} {event['envelope_key']} ({event['from_status']} -> {event['to_status']})")
            
        conn.close()
    except Exception as e:
        print(f"❌ Error querying logs: {e}")

if __name__ == "__main__":
    check_logs()
