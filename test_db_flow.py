
import sqlite3
import os
import random

DB_NAME = "koperty_system.db"

def test_flow():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Pick a random envelope in MAGAZYN
        cursor.execute("SELECT unique_key FROM envelopes WHERE status = 'MAGAZYN' LIMIT 1")
        row = cursor.fetchone()
        if not row:
            print("❌ No envelopes in MAGAZYN to test with.")
            # Create one
            env_id = f"TEST-{random.randint(1000,9999)}"
            cursor.execute("INSERT INTO envelopes (unique_key, rcs_id, status, current_holder_id, current_holder_type, is_green) VALUES (?, ?, 'MAGAZYN', 'MAGAZYN_A', 'WAREHOUSE', 1)", (env_id, env_id))
            conn.commit()
            print(f"✅ Created test envelope: {env_id}")
            row = {'unique_key': env_id}
        
        env_id = row['unique_key']
        print(f"👉 Testing with envelope: {env_id}")
        
        # 2. Issue from Warehouse (MAGAZYN -> SHOP_FLOOR)
        print("   Attempting ISSUE (MAGAZYN -> SHOP_FLOOR)...")
        # Ensure is_green is 1
        cursor.execute("UPDATE envelopes SET is_green = 1 WHERE unique_key = ?", (env_id,))
        conn.commit()
        
        # Transaction for ISSUE
        cursor.execute("BEGIN IMMEDIATE")
        try:
            cursor.execute("SELECT status FROM envelopes WHERE unique_key = ?", (env_id,))
            current = cursor.fetchone()['status']
            if current != 'MAGAZYN':
                print(f"   ⚠️ Status is {current}, forcing set to MAGAZYN for test")
                cursor.execute("UPDATE envelopes SET status='MAGAZYN', current_holder_id='MAGAZYN_A' WHERE unique_key=?", (env_id,))
            
            cursor.execute("""
                UPDATE envelopes 
                SET status = 'SHOP_FLOOR', 
                    current_holder_id = 'CART-OUT-TEST',
                    current_holder_type = 'CART_OUT',
                    warehouse_section = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE unique_key = ?
            """, (env_id,))
            
            cursor.execute("""
                INSERT INTO events (envelope_key, user_id, from_status, to_status, from_holder, to_holder, operation)
                VALUES (?, 'TEST_USER', 'MAGAZYN', 'SHOP_FLOOR', 'MAGAZYN', 'CART-OUT-TEST', 'ISSUE')
            """, (env_id,))
            conn.commit()
            print("   ✅ ISSUE successful.")
        except Exception as e:
            conn.rollback()
            print(f"   ❌ ISSUE failed: {e}")
            return

        # 3. Bind to Machine (SHOP_FLOOR -> W_PRODUKCJI)
        print("   Attempting BIND (SHOP_FLOOR -> W_PRODUKCJI)...")
        cursor.execute("BEGIN IMMEDIATE")
        try:
            cursor.execute("""
                UPDATE envelopes 
                SET status = 'W_PRODUKCJI', 
                    current_holder_id = 'TEST_MACHINE',
                    current_holder_type = 'MACHINE',
                    updated_at = CURRENT_TIMESTAMP
                WHERE unique_key = ?
            """, (env_id,))
            conn.commit()
            print("   ✅ BIND successful.")
        except Exception as e:
            conn.rollback()
            print(f"   ❌ BIND failed: {e}")
            return
            
        # 4. Verify Final State
        cursor.execute("SELECT status, current_holder_id FROM envelopes WHERE unique_key = ?", (env_id,))
        final = cursor.fetchone()
        print(f"   🏁 Final state: {final['status']} at {final['current_holder_id']}")

        # Cleanup
        print("   Cleaning up test envelope...")
        cursor.execute("DELETE FROM envelopes WHERE unique_key = ? AND unique_key LIKE 'TEST-%'", (env_id,))
        if env_id.startswith("TEST-"):
           conn.commit()
        else:
           # Revert to MAGAZYN
           cursor.execute("UPDATE envelopes SET status='MAGAZYN', current_holder_id='MAGAZYN_A', current_holder_type='WAREHOUSE' WHERE unique_key=?", (env_id,))
           conn.commit()

        conn.close()
        
    except Exception as e:
        print(f"❌ Error during test flow: {e}")

if __name__ == "__main__":
    test_flow()
