import hashlib
import json
import secrets
import sqlite3
from typing import List, Dict, Optional, Any

DB_NAME = "koperty_system.db"
DEFAULT_OPERATOR_MACHINES = [
    'PRINTER MAIN',
    'PRINTER 2',
    'VISON',
    'ETERNA',
    'CUTER',
    'ST2',
    'VERSOR',
    'BOOBST 1',
    'BOOBST 2',
    'PALLETIZING'
]

class Database:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        # OPTYMALIZACJA: WAL, FK, Timeout
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=5000')
        
        # To pozwala odwoływać się do kolumn po nazwie (row["status"]) a nie indeksie
        conn.row_factory = sqlite3.Row 
        return conn

    def _create_tables(self):
        """Tworzy strukturę tabel, jeśli nie istnieją."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # OPTYMALIZACJA: Indeksy dla wydajności (tworzone przed tabelami lub po - tutaj sprawdzamy if not exists)
        # Indeks statusu (dla filtrowania)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_envelopes_status ON envelopes(status)')
        # Indeks maszyny (dla sprawdzania zajętości)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_envelopes_holder ON envelopes(current_holder_id)')
        # Indeks RCS (dla szybkiego wyszukiwania) - choć unique_key jest Primary Key, to warto mieć też na rcs_id jeśli szukamy po nim
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_envelopes_rcs ON envelopes(rcs_id)')

        # 1. Tabela KOPERT (rozszerzona wg specyfikacji v2.0)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS envelopes (
                unique_key TEXT PRIMARY KEY,
                rcs_id TEXT NOT NULL,
                product_version TEXT,              -- DEPRECATED
                additional_number INTEGER,         -- DEPRECATED
                status TEXT NOT NULL,
                current_holder_id TEXT NOT NULL,   -- np. "BOOBST 1", "CART-RET", "MAGAZYN"
                current_holder_type TEXT NOT NULL, -- np. "MACHINE", "WAREHOUSE"
                creation_reason TEXT,
                warehouse_section TEXT,            -- np. "A", "B" (tylko gdy w magazynie)
                is_green INTEGER DEFAULT 1,        -- Status kompletności (1=Zielona, 0=Czerwona)
                last_operator_id TEXT,             -- ID ostatniego użytkownika operującego kopertą
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migracja: dodaj kolumny jeśli nie istnieją (dla istniejących baz)
        try:
            cursor.execute('ALTER TABLE envelopes ADD COLUMN is_green INTEGER DEFAULT 1')
        except:
            pass  # Kolumna już istnieje
        try:
            cursor.execute('ALTER TABLE envelopes ADD COLUMN last_operator_id TEXT')
        except:
            pass  # Kolumna już istnieje

        # 2. Tabela ZDARZEŃ (Historia/Logi)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                envelope_key TEXT NOT NULL,
                user_id TEXT,
                from_status TEXT,
                to_status TEXT,
                from_holder TEXT,
                to_holder TEXT,
                operation TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                comment TEXT,
                FOREIGN KEY(envelope_key) REFERENCES envelopes(unique_key)
            )
        ''')
        
        # Migracja: dodaj kolumnę operation jeśli nie istnieje (dla istniejących baz)
        try:
            cursor.execute('ALTER TABLE events ADD COLUMN operation TEXT')
        except:
            pass  # Kolumna już istnieje

        # 3. Tabela NOTATEK MASZYNOWYCH (Baza wiedzy) - STARA, zachowana dla kompatybilności
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machine_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                operator_name TEXT,
                glue_length TEXT,
                machine_speed TEXT,
                width TEXT,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 4. NOWA Tabela NOTATEK PRODUKT + MASZYNA
        # Klucz: para (product_code, machine_id)
        # product_code = np. "333444555#1.3" (bez numeru kopii)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_machine_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT NOT NULL,
                machine_id TEXT NOT NULL,
                note_content TEXT,
                note_type TEXT DEFAULT 'specific',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                modified_by TEXT,
                is_active INTEGER DEFAULT 1,
                UNIQUE(product_code, machine_id, note_type)
            )
        ''')

        # 5. Tabela HISTORII NOTATEK
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                product_code TEXT,
                machine_id TEXT,
                old_content TEXT,
                new_content TEXT,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                changed_by TEXT,
                operation_type TEXT,
                FOREIGN KEY(note_id) REFERENCES product_machine_notes(id)
            )
        ''')

        # 5.1 Notatki operatora (zastępują localStorage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operator_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                envelope_id TEXT NOT NULL,
                machine_id TEXT NOT NULL,
                note_kind TEXT NOT NULL CHECK(note_kind IN ('standard', 'pallet', 'slot')),
                note_data_json TEXT NOT NULL,
                created_by TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # 5.2 Obrazy notatek (scope: operator_note lub product_machine_note)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_scope TEXT NOT NULL CHECK(note_scope IN ('operator_note', 'product_machine_note')),
                note_id INTEGER NOT NULL,
                storage_path TEXT NOT NULL,
                original_filename TEXT,
                mime_type TEXT NOT NULL,
                width INTEGER,
                height INTEGER,
                size_bytes INTEGER,
                sha256 TEXT,
                annotations_json TEXT,
                order_index INTEGER DEFAULT 0,
                revision INTEGER DEFAULT 1,
                created_by TEXT,
                modified_by TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')

        try:
            cursor.execute('ALTER TABLE note_images ADD COLUMN modified_by TEXT')
        except:
            pass

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operator_notes_cursor ON operator_notes(envelope_id, machine_id, created_at, id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operator_notes_created ON operator_notes(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_note_images_scope_note ON note_images(note_scope, note_id, is_active, order_index)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_note_images_created ON note_images(created_at)')

        # 6. Tabela ERROR_LOGS (Audyt Błędów - wg specyfikacji v2.0)
        # Rejestruje próby złamania procesu (duplikaty, bypass magazynu, itp.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                error_code TEXT NOT NULL,      -- np. 'DUPLICATE_ATTEMPT', 'NOT_ISSUED', 'BYPASS_ATTEMPT'
                user_id TEXT,                  -- Kto próbował wykonać operację
                location_id TEXT,              -- Gdzie? (Magazyn, BOOBST 1, itp.)
                conflict_details TEXT,         -- JSON: snapshot stanu (kto ma oryginał, jaka maszyna)
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 7. Tabela PRODUKTÓW (Firma, Produkt, RCS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,       -- Nazwa firmy np. "PROTEGA GLOBAL LTD"
                product_name TEXT NOT NULL,       -- Nazwa produktu np. "T22684 OXED (NEW FSC)"
                rcs_id TEXT NOT NULL UNIQUE,      -- Identyfikator RCS np. "RCS044563/C"
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # Migracja: dodaj kolumnę product_id do envelopes jeśli nie istnieje
        try:
            cursor.execute('ALTER TABLE envelopes ADD COLUMN product_id INTEGER REFERENCES products(id)')
        except:
            pass  # Kolumna już istnieje

        # 8. Tabela UŻYTKOWNIKÓW (Operatorzy, Magazynierzy, Administratorzy)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                pin TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('OPERATOR', 'WAREHOUSE', 'ADMIN')),
                full_name TEXT,
                shift TEXT,                        -- Zmiana: A, B, Dzień (opcjonalne)
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # 9. Tabela PIN dla maszyn operatora
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machines_auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_name TEXT UNIQUE NOT NULL,
                pin_hash TEXT NOT NULL,
                pin_salt TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_machines_auth_active ON machines_auth(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_machines_auth_name ON machines_auth(machine_name)')

        # 10. Tabela LISTY WYSZUKIWANIA (Warehouse Search List)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,                      -- NULL = wspólna lista, lub konkretny user_id
                envelope_id TEXT NOT NULL,         -- ID koperty do znalezienia
                priority TEXT DEFAULT 'normal',    -- 'normal', 'high'
                found INTEGER DEFAULT 0,           -- 0 = nie znaleziono, 1 = znaleziono
                found_at DATETIME,                 -- Kiedy znaleziono
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                date TEXT NOT NULL                 -- YYYY-MM-DD dla filtrowania dzisiejszych
            )
        ''')

        conn.commit()
        
        # Seed domyślnych użytkowników
        self._seed_default_users(conn)
        # Migracja: operatorzy nie są już logowani przez users
        self._remove_operator_users(conn)
        # Seed domyślnych maszyn operatora (PIN 1001+)
        self._seed_default_machines(conn)
        
        conn.close()


    def get_envelope_history(self, envelope_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Pobiera historię zdarzeń dla danej koperty."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, from_status, to_status, from_holder, to_holder, timestamp, comment
            FROM events
            WHERE envelope_key = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (envelope_id, limit))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append(dict(row))
            
        conn.close()
        return history

    def get_envelopes_paginated(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Pobiera koperty z paginacją."""
        offset = (page - 1) * limit
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Pobierz całkowitą liczbę
        cursor.execute("SELECT COUNT(*) FROM envelopes")
        total_count = cursor.fetchone()[0]
        
        # Pobierz dane
        cursor.execute("""
            SELECT e.unique_key, e.rcs_id, e.status, 
                   e.current_holder_id, e.current_holder_type, e.warehouse_section,
                   e.is_green, e.last_operator_id, e.product_id,
                   p.company_name, p.product_name
            FROM envelopes e
            LEFT JOIN products p ON e.product_id = p.id
            ORDER BY e.updated_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            if row['product_id'] and row['company_name']:
                product_display = f"{row['company_name']} | {row['product_name']}"
            else:
                product_display = f"KOPERTA {row['rcs_id']}"
            
            results.append({
                "id": row['unique_key'],
                "rcs_id": row['rcs_id'],
                "product": product_display,
                "company_name": row['company_name'],
                "product_name": row['product_name'],
                "status": row['status'],
                "machine": row['current_holder_id'] if row['current_holder_id'] else None,
                "location": row['warehouse_section'] if row['status'] == 'MAGAZYN' else None
            })
            
        return {
            "data": results,
            "meta": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit
            }
        }

    def get_machine_status(self, machine_id: str) -> Dict[str, Any]:
        """Sprawdza status maszyny (czy ma przypisaną kopertę)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT unique_key, rcs_id, product_version, status, 
                   current_holder_id, last_operator_id, product_id
            FROM envelopes 
            WHERE current_holder_id = ? AND status = 'W_PRODUKCJI'
            LIMIT 1
        """, (machine_id,))
        
        row = cursor.fetchone()
        
        result = None
        if row:
            # Pobierz nazwę produktu
            product_name = f"Koperta {row['rcs_id']}"
            if row['product_id']:
                cursor.execute("SELECT company_name, product_name FROM products WHERE id = ?", (row['product_id'],))
                prod_row = cursor.fetchone()
                if prod_row:
                    product_name = f"{prod_row['company_name']} | {prod_row['product_name']}"

            result = {
                "id": row['unique_key'],
                "rcs_id": row['rcs_id'],
                "product": product_name,
                "status": row['status'],
                "operator": row['last_operator_id']
            }
            
        conn.close()
        return result

    # ========================
    # METODY DLA PRODUKTÓW
    # ========================

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Pobiera wszystkie aktywne produkty."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, company_name, product_name, rcs_id, created_at
            FROM products
            WHERE is_active = 1
            ORDER BY company_name, product_name
        ''')
        
        rows = cursor.fetchall()
        products = [dict(row) for row in rows]
        conn.close()
        return products

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Pobiera produkt po ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, company_name, product_name, rcs_id, created_at
            FROM products
            WHERE id = ? AND is_active = 1
        ''', (product_id,))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_product_by_rcs(self, rcs_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera produkt po identyfikatorze RCS."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, company_name, product_name, rcs_id, created_at
            FROM products
            WHERE rcs_id = ? AND is_active = 1
        ''', (rcs_id,))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Wyszukuje produkty po fragmencie nazwy firmy, produktu lub RCS."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT id, company_name, product_name, rcs_id, created_at
            FROM products
            WHERE is_active = 1 AND (
                company_name LIKE ? OR
                product_name LIKE ? OR
                rcs_id LIKE ?
            )
            ORDER BY company_name, product_name
            LIMIT 20
        ''', (search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        products = [dict(row) for row in rows]
        conn.close()
        return products

    def create_product(self, company_name: str, product_name: str, rcs_id: str) -> Dict[str, Any]:
        """Tworzy nowy produkt. Zwraca utworzony produkt lub błąd."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (company_name, product_name, rcs_id)
                VALUES (?, ?, ?)
            ''', (company_name, product_name, rcs_id))
            
            product_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "id": product_id,
                "company_name": company_name,
                "product_name": product_name,
                "rcs_id": rcs_id
            }
        except sqlite3.IntegrityError as e:
            conn.close()
            return {"success": False, "error": f"RCS '{rcs_id}' już istnieje w bazie"}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}

    def update_product(self, product_id: int, company_name: str = None, 
                       product_name: str = None, rcs_id: str = None) -> Dict[str, Any]:
        """Aktualizuje dane produktu."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if company_name:
            updates.append("company_name = ?")
            values.append(company_name)
        if product_name:
            updates.append("product_name = ?")
            values.append(product_name)
        if rcs_id:
            updates.append("rcs_id = ?")
            values.append(rcs_id)
        
        if not updates:
            conn.close()
            return {"success": False, "error": "Brak danych do aktualizacji"}
        
        values.append(product_id)
        
        try:
            cursor.execute(f'''
                UPDATE products SET {", ".join(updates)}
                WHERE id = ? AND is_active = 1
            ''', values)
            
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            
            if affected > 0:
                return {"success": True, "message": "Produkt zaktualizowany"}
            else:
                return {"success": False, "error": "Produkt nie znaleziony"}
        except sqlite3.IntegrityError:
            conn.close()
            return {"success": False, "error": f"RCS '{rcs_id}' już istnieje"}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}

    def delete_product_soft(self, product_id: int) -> Dict[str, Any]:
        """
        Soft delete produktu (ustawia is_active = 0).
        Sprawdza czy produkt nie jest używany przez aktywne koperty.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Sprawdź czy produkt istnieje
            cursor.execute('SELECT id, rcs_id FROM products WHERE id = ? AND is_active = 1', (product_id,))
            product = cursor.fetchone()
            
            if not product:
                conn.close()
                return {"success": False, "error": "Produkt nie znaleziony", "status": 404}
            
            # Sprawdź czy produkt jest używany przez koperty
            cursor.execute('''
                SELECT COUNT(*) as count FROM envelopes 
                WHERE product_id = ? AND status != 'MAGAZYN'
            ''', (product_id,))
            envelope_count = cursor.fetchone()[0]
            
            if envelope_count > 0:
                conn.close()
                return {
                    "success": False, 
                    "error": f"Nie można usunąć produktu. Jest używany przez {envelope_count} kopert(y) w produkcji.",
                    "status": 409
                }
            
            # Soft delete
            cursor.execute('UPDATE products SET is_active = 0 WHERE id = ?', (product_id,))
            conn.commit()
            conn.close()
            
            return {"success": True, "message": f"Produkt {product['rcs_id']} został usunięty"}
            
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e), "status": 500}

    def import_products_batch(self, products_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Importuje wiele produktów naraz.
        
        Args:
            products_list: Lista słowników z kluczami: company_name, product_name, rcs_id
            
        Returns:
            Dict ze statystykami: total, added, skipped, errors + lista błędów
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {
            "total": len(products_list),
            "added": 0,
            "skipped": 0,
            "errors": 0
        }
        
        error_details = []
        
        for idx, product in enumerate(products_list, start=1):
            try:
                company_name = product.get('company_name', '').strip()
                product_name = product.get('product_name', '').strip()
                rcs_id = product.get('rcs_id', '').strip()
                
                # Walidacja
                if not all([company_name, product_name, rcs_id]):
                    stats["errors"] += 1
                    error_details.append({
                        "row": idx,
                        "error": "Brak wymaganych pól (company_name, product_name, rcs_id)"
                    })
                    continue
                
                # Sprawdź czy produkt już istnieje
                cursor.execute('SELECT id FROM products WHERE rcs_id = ?', (rcs_id,))
                existing = cursor.fetchone()
                
                if existing:
                    stats["skipped"] += 1
                    error_details.append({
                        "row": idx,
                        "error": f"Produkt o RCS '{rcs_id}' już istnieje",
                        "type": "duplicate"
                    })
                    continue
                
                # Dodaj produkt
                cursor.execute('''
                    INSERT INTO products (company_name, product_name, rcs_id)
                    VALUES (?, ?, ?)
                ''', (company_name, product_name, rcs_id))
                
                stats["added"] += 1
                
            except Exception as e:
                stats["errors"] += 1
                error_details.append({
                    "row": idx,
                    "error": str(e)
                })
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "stats": stats,
            "error_details": error_details[:20]  # Ogranicz do 20 pierwszych błędów
        }

# Helper do szybkiego użycia
    # ========================
    # LOGIKA BIZNESOWA (TRANSAKCJE)
    # ========================

    def log_error(self, barcode, error_code, user_id=None, location_id=None, conflict_details=None):
        """Loguje błąd do tabeli error_logs (audyt)."""
        import json
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO error_logs (barcode, error_code, user_id, location_id, conflict_details)
                VALUES (?, ?, ?, ?, ?)
            """, (barcode, error_code, user_id, location_id, 
                  json.dumps(conflict_details) if conflict_details else None))
            conn.commit()
        except:
            pass # Nie chcemy żeby błąd logowania wywalił aplikację
        finally:
            conn.close()

    def issue_envelope(self, envelope_id: str, cart_id: str, user_id: str) -> Dict[str, Any]:
        """
        Wydaje kopertę z magazynu na wózek (MAGAZYN -> SHOP_FLOOR).
        Atomiczna transakcja z walidacją.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN IMMEDIATE")
            
            # 1. Pobierz stan
            cursor.execute("""
                SELECT status, current_holder_id, is_green, last_operator_id, updated_at 
                FROM envelopes WHERE unique_key = ?
            """, (envelope_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.rollback()
                self.log_error(envelope_id, 'ERR_NOT_FOUND', user_id, 'MAGAZYN')
                return {"success": False, "error_code": "ERR_NOT_FOUND", "status": 404}
                
            current_status = row['status']
            is_green = row['is_green']
            
            # 2. Walidacja Statusu
            if current_status != 'MAGAZYN':
                conn.rollback()
                error_code = 'ERR_DUPLICATE_ACTIVE' if current_status == 'W_PRODUKCJI' else 'ERR_INVALID_STATUS'
                self.log_error(envelope_id, error_code, user_id, 'MAGAZYN', {
                    "current_status": current_status, "holder": row['current_holder_id']
                })
                return {
                    "success": False, 
                    "error_code": error_code, 
                    "status": 409,
                    "current_status": current_status,
                    "holder": row['current_holder_id']
                }

            # 3. Walidacja Koloru
            if not is_green:
                conn.rollback()
                self.log_error(envelope_id, 'ERR_WRONG_COLOR', user_id, 'MAGAZYN')
                return {"success": False, "error_code": "ERR_WRONG_COLOR", "status": 409}
            
            # 4. Update
            cursor.execute("""
                UPDATE envelopes 
                SET status = 'SHOP_FLOOR', 
                    current_holder_id = ?, 
                    current_holder_type = 'CART_OUT',
                    warehouse_section = NULL,
                    last_operator_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE unique_key = ?
            """, (cart_id, user_id, envelope_id))
            
            # 5. Log Event
            cursor.execute("""
                INSERT INTO events (envelope_key, user_id, from_status, to_status, from_holder, to_holder, operation)
                VALUES (?, ?, 'MAGAZYN', 'SHOP_FLOOR', 'MAGAZYN', ?, 'ISSUE')
            """, (envelope_id, user_id, cart_id))
            
            conn.commit()
            return {"success": True, "status": "SHOP_FLOOR"}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()

    def bind_envelope_to_machine(self, envelope_id: str, machine_id: str, user_id: str) -> Dict[str, Any]:
        """
        Przypisuje kopertę do maszyny.
        Obsługuje:
        - SHOP_FLOOR -> W_PRODUKCJI (LOAD)
        - W_PRODUKCJI(A) -> W_PRODUKCJI(B) (TRANSFER_AUTO)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN IMMEDIATE")
            
            cursor.execute("SELECT status, current_holder_id FROM envelopes WHERE unique_key = ?", (envelope_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.rollback()
                self.log_error(envelope_id, 'ERR_NOT_FOUND', user_id, machine_id)
                return {"success": False, "error_code": "ERR_NOT_FOUND", "status": 404}
            
            current_status = row['status']
            current_holder = row['current_holder_id']
            
            # Walidacje
            if current_status == 'MAGAZYN':
                conn.rollback()
                self.log_error(envelope_id, 'ERR_NOT_ISSUED', user_id, machine_id)
                return {"success": False, "error_code": "ERR_NOT_ISSUED", "status": 409}
                
            if current_status == 'W_PRODUKCJI':
                if str(current_holder) == str(machine_id):
                    # Idempotentny przypadek - koperta już na tej maszynie.
                    conn.commit()
                    return {
                        "success": True,
                        "status": "W_PRODUKCJI",
                        "operation": "ALREADY_ON_MACHINE",
                        "from_machine": current_holder,
                        "to_machine": machine_id
                    }

                # Automatyczny transfer między maszynami.
                cursor.execute("""
                    UPDATE envelopes 
                    SET status = 'W_PRODUKCJI', 
                        current_holder_id = ?, 
                        current_holder_type = 'MACHINE',
                        last_operator_id = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE unique_key = ?
                """, (machine_id, user_id, envelope_id))

                cursor.execute("""
                    INSERT INTO events (envelope_key, user_id, from_status, to_status, from_holder, to_holder, operation)
                    VALUES (?, ?, 'W_PRODUKCJI', 'W_PRODUKCJI', ?, ?, 'TRANSFER_AUTO')
                """, (envelope_id, user_id, current_holder, machine_id))

                conn.commit()
                return {
                    "success": True,
                    "status": "W_PRODUKCJI",
                    "operation": "TRANSFER_AUTO",
                    "from_machine": current_holder,
                    "to_machine": machine_id
                }
                
            if current_status != 'SHOP_FLOOR':
                conn.rollback()
                return {"success": False, "error_code": "ERR_INVALID_STATUS", "status": 409}
            
            # Update
            cursor.execute("""
                UPDATE envelopes 
                SET status = 'W_PRODUKCJI', 
                    current_holder_id = ?, 
                    current_holder_type = 'MACHINE',
                    last_operator_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE unique_key = ?
            """, (machine_id, user_id, envelope_id))
            
            # Log Event - dodane logowanie historii
            cursor.execute("""
                INSERT INTO events (envelope_key, user_id, from_status, to_status, from_holder, to_holder, operation)
                VALUES (?, ?, ?, 'W_PRODUKCJI', ?, ?, 'LOAD')
            """, (envelope_id, user_id, current_status, current_holder, machine_id))
            
            conn.commit()
            return {
                "success": True,
                "status": "W_PRODUKCJI",
                "operation": "LOAD",
                "from_machine": current_holder,
                "to_machine": machine_id
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()

    def delete_envelope(self, envelope_id: str) -> Dict[str, Any]:
        """Usuwa kopertę z bazy danych (ADMIN)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            with conn: # Transakcja
                # Sprawdź czy koperta istnieje
                cursor.execute("SELECT unique_key FROM envelopes WHERE unique_key = ?", (envelope_id,))
                if not cursor.fetchone():
                    return {"success": False, "error": "Koperta nie znaleziona", "status": 404}
                
                # Usuń powiązane zdarzenia (Events) - musi być pierwsze bo FK
                cursor.execute("DELETE FROM events WHERE envelope_key = ?", (envelope_id,))
                
                # Usuń kopertę
                cursor.execute("DELETE FROM envelopes WHERE unique_key = ?", (envelope_id,))
                
                # Loguj usunięcie
                self.log_error(envelope_id, 'INFO_DELETED', 'ADMIN', 'WAREHOUSE', {'action': 'manual_delete'})
                
            return {"success": True, "message": f"Koperta {envelope_id} została usunięta"}
            
        except sqlite3.Error as e:
            return {"success": False, "error": f"Błąd bazy danych: {e}", "status": 500}
        finally:
            conn.close()

    def release_envelope(self, envelope_id: str) -> Dict[str, Any]:
        """
        Zwalnia kopertę z maszyny (W_PRODUKCJI -> SHOP_FLOOR / CART-RET).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN IMMEDIATE")
            
            cursor.execute("SELECT status, current_holder_id, last_operator_id FROM envelopes WHERE unique_key = ?", (envelope_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.rollback()
                return {"success": False, "error": "Not found", "status": 404}
                
            current_status = row['status']
            current_holder = str(row['current_holder_id']).upper()
            operator = row['last_operator_id'] or 'SYSTEM'
            
            # Logika Paletyzacja vs Reszta
            if 'PALLET' in current_holder:
                new_status = 'CART-RET-05'
                new_holder = 'CART-RET-05'
                new_type = 'CART_IN'
            else:
                new_status = 'SHOP_FLOOR'
                new_holder = 'SHOP_FLOOR'
                new_type = 'FLOOR'
            
            cursor.execute("""
                UPDATE envelopes 
                SET status = ?, current_holder_id = ?, current_holder_type = ?, updated_at = CURRENT_TIMESTAMP
                WHERE unique_key = ?
            """, (new_status, new_holder, new_type, envelope_id))
            
            # Log Event - dodane logowanie historii
            cursor.execute("""
                INSERT INTO events (envelope_key, user_id, from_status, to_status, from_holder, to_holder, operation)
                VALUES (?, ?, ?, ?, ?, ?, 'RELEASE')
            """, (envelope_id, operator, current_status, new_status, current_holder, new_holder))
            
            conn.commit()
            return {
                "success": True, 
                "new_status": new_status, 
                "new_holder": new_holder
            }
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()

    def return_to_warehouse(self, envelope_id: str, location: str) -> Dict[str, Any]:
        """
        Przyjmuje kopertę na magazyn (ANY -> MAGAZYN).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN IMMEDIATE")
            
            cursor.execute("SELECT status, current_holder_id, last_operator_id FROM envelopes WHERE unique_key = ?", (envelope_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.rollback()
                return {"success": False, "error": "Not found", "status": 404}
            
            current_status = row['status']
            current_holder = row['current_holder_id']
            operator = row['last_operator_id'] or 'WAREHOUSE'
            
            if current_status == 'W_PRODUKCJI' and not str(current_holder).startswith('CART'):
                conn.rollback()
                return {"success": False, "error": "Koperta na maszynie", "status": 409}
            
            cursor.execute("""
                UPDATE envelopes 
                SET status = 'MAGAZYN', 
                    current_holder_id = 'MAGAZYN',
                    current_holder_type = 'WAREHOUSE',
                    warehouse_section = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE unique_key = ?
            """, (location, envelope_id))
            
            # Log Event - dodane logowanie historii
            cursor.execute("""
                INSERT INTO events (envelope_key, user_id, from_status, to_status, from_holder, to_holder, operation)
                VALUES (?, ?, ?, 'MAGAZYN', ?, 'WAREHOUSE', 'RETURN')
            """, (envelope_id, operator, current_status, current_holder))
            
            conn.commit()
            return {"success": True, "status": "MAGAZYN"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()

    # ========================
    # ZARZĄDZANIE MASZYNAMI (PIN OPERATORA)
    # ========================

    def _hash_pin(self, pin: str, salt_hex: str = None) -> tuple[str, str]:
        """Zwraca (hash_hex, salt_hex) dla PIN."""
        salt_hex = salt_hex or secrets.token_hex(16)
        pin_hash = hashlib.pbkdf2_hmac(
            'sha256',
            pin.encode('utf-8'),
            bytes.fromhex(salt_hex),
            120000
        ).hex()
        return pin_hash, salt_hex

    def _verify_pin_hash(self, pin: str, pin_hash: str, salt_hex: str) -> bool:
        """Weryfikuje PIN względem hash + salt."""
        candidate_hash, _ = self._hash_pin(pin, salt_hex)
        return secrets.compare_digest(candidate_hash, pin_hash)

    def _is_valid_pin(self, pin: str) -> bool:
        return isinstance(pin, str) and pin.isdigit() and len(pin) == 4

    def _seed_default_machines(self, conn):
        """Uzupełnia domyślne maszyny operatora (PIN 1001+)."""
        cursor = conn.cursor()
        cursor.execute("SELECT machine_name FROM machines_auth")
        existing = {row[0] for row in cursor.fetchall()}

        inserted = 0
        for idx, machine_name in enumerate(DEFAULT_OPERATOR_MACHINES, start=1):
            if machine_name in existing:
                continue

            default_pin = f"{1000 + idx:04d}"
            pin_hash, pin_salt = self._hash_pin(default_pin)
            cursor.execute('''
                INSERT INTO machines_auth (machine_name, pin_hash, pin_salt, is_active)
                VALUES (?, ?, ?, 1)
            ''', (machine_name, pin_hash, pin_salt))
            inserted += 1

        if inserted:
            conn.commit()

    def get_active_machines_auth(self) -> List[Dict[str, Any]]:
        """Pobiera listę aktywnych maszyn operatora."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, machine_name
            FROM machines_auth
            WHERE is_active = 1
            ORDER BY machine_name
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "machine": row["machine_name"]} for row in rows]

    def get_all_machines_auth(self) -> List[Dict[str, Any]]:
        """Pobiera wszystkie maszyny operatora (admin)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, machine_name, is_active, created_at, updated_at
            FROM machines_auth
            ORDER BY machine_name
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": row["id"],
            "machine": row["machine_name"],
            "is_active": row["is_active"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        } for row in rows]

    def verify_machine_auth(self, machine_name: str, pin: str) -> Dict[str, Any]:
        """Weryfikuje PIN wybranej maszyny operatora."""
        if not machine_name:
            return {"success": False, "error": "Brak nazwy maszyny", "status": 400}
        if not self._is_valid_pin(pin):
            return {"success": False, "error": "PIN musi składać się z 4 cyfr", "status": 400}

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, machine_name, pin_hash, pin_salt, is_active
            FROM machines_auth
            WHERE machine_name = ?
            LIMIT 1
        ''', (machine_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {"success": False, "error": "Maszyna nie istnieje", "status": 404}
        if not row["is_active"]:
            return {"success": False, "error": "Maszyna jest nieaktywna", "status": 403}
        if not self._verify_pin_hash(pin, row["pin_hash"], row["pin_salt"]):
            return {"success": False, "error": "Nieprawidłowy PIN", "status": 401}

        return {
            "success": True,
            "machine": {
                "id": row["id"],
                "machine": row["machine_name"],
                "is_active": row["is_active"]
            }
        }

    def create_machine_auth(self, machine_name: str, pin: str) -> Dict[str, Any]:
        """Dodaje nową maszynę operatora."""
        machine_name = (machine_name or "").strip()
        if not machine_name:
            return {"success": False, "error": "Nazwa maszyny jest wymagana", "status": 400}
        if not self._is_valid_pin(pin):
            return {"success": False, "error": "PIN musi składać się z 4 cyfr", "status": 400}

        pin_hash, pin_salt = self._hash_pin(pin)
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO machines_auth (machine_name, pin_hash, pin_salt, is_active)
                VALUES (?, ?, ?, 1)
            ''', (machine_name, pin_hash, pin_salt))
            conn.commit()
            return {
                "success": True,
                "machine_id": cursor.lastrowid,
                "machine": machine_name,
                "status": 201
            }
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Maszyna o tej nazwie już istnieje", "status": 409}
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()

    def update_machine_auth(self, machine_id: int, machine_name: str = None, is_active: int = None) -> Dict[str, Any]:
        """Aktualizuje nazwę i/lub status aktywności maszyny operatora."""
        updates = []
        params = []

        if machine_name is not None:
            clean_name = machine_name.strip()
            if not clean_name:
                return {"success": False, "error": "Nazwa maszyny nie może być pusta", "status": 400}
            updates.append("machine_name = ?")
            params.append(clean_name)

        if is_active is not None:
            normalized = 1 if int(is_active) else 0
            updates.append("is_active = ?")
            params.append(normalized)

        if not updates:
            return {"success": False, "error": "Brak danych do aktualizacji", "status": 400}

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(machine_id)

        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f"UPDATE machines_auth SET {', '.join(updates)} WHERE id = ?", params)
            if cursor.rowcount == 0:
                return {"success": False, "error": "Maszyna nie znaleziona", "status": 404}
            conn.commit()
            return {"success": True, "machine_id": machine_id}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Maszyna o tej nazwie już istnieje", "status": 409}
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()

    def change_machine_pin(self, machine_id: int, new_pin: str) -> Dict[str, Any]:
        """Zmienia PIN maszyny operatora."""
        if not self._is_valid_pin(new_pin):
            return {"success": False, "error": "PIN musi składać się z 4 cyfr", "status": 400}

        pin_hash, pin_salt = self._hash_pin(new_pin)
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE machines_auth
                SET pin_hash = ?, pin_salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (pin_hash, pin_salt, machine_id))
            if cursor.rowcount == 0:
                return {"success": False, "error": "Maszyna nie znaleziona", "status": 404}
            conn.commit()
            return {"success": True, "machine_id": machine_id}
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()

    # ========================
    # ZARZĄDZANIE UŻYTKOWNIKAMI
    # ========================

    def _remove_operator_users(self, conn):
        """Czyści operatorów z tabeli users po migracji na PIN maszyn."""
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE role = 'OPERATOR'")
        if cursor.rowcount:
            conn.commit()

    def _seed_default_users(self, conn):
        """Tworzy domyślnych użytkowników magazynu/admin."""
        cursor = conn.cursor()
        default_users = [
            ('admin', '9999', 'ADMIN', 'Administrator Systemu', None),
            ('magazynier1', '5555', 'WAREHOUSE', 'Magazynier Testowy', 'A'),
        ]

        inserted = 0
        for user in default_users:
            cursor.execute("SELECT id FROM users WHERE username = ?", (user[0],))
            if cursor.fetchone():
                continue
            cursor.execute('''
                INSERT INTO users (username, pin, role, full_name, shift)
                VALUES (?, ?, ?, ?, ?)
            ''', user)
            inserted += 1

        if inserted:
            conn.commit()
    
    def create_user(self, username: str, pin: str, role: str, full_name: str = None, shift: str = None) -> Dict[str, Any]:
        """Tworzy nowego użytkownika."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Walidacja PIN (4 cyfry)
            if not pin.isdigit() or len(pin) != 4:
                return {"success": False, "error": "PIN musi składać się z 4 cyfr", "status": 400}
            
            # Walidacja roli (operatorzy zarządzani osobno przez machines_auth)
            if role not in ['WAREHOUSE', 'ADMIN']:
                return {"success": False, "error": "Dozwolone role: WAREHOUSE, ADMIN", "status": 400}
            
            cursor.execute('''
                INSERT INTO users (username, pin, role, full_name, shift)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, pin, role, full_name, shift))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "status": 201
            }
            
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Użytkownik o tej nazwie już istnieje", "status": 409}
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Pobiera wszystkich użytkowników."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, pin, role, full_name, shift, created_at, is_active
            FROM users
            WHERE role IN ('WAREHOUSE', 'ADMIN')
            ORDER BY role, username
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row['id'],
                "username": row['username'],
                "pin": row['pin'],
                "role": row['role'],
                "full_name": row['full_name'],
                "shift": row['shift'],
                "created_at": row['created_at'],
                "is_active": row['is_active']
            })
        
        conn.close()
        return users
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Pobiera użytkownika po ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, pin, role, full_name, shift, created_at, is_active
            FROM users
            WHERE id = ? AND role IN ('WAREHOUSE', 'ADMIN')
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row['id'],
                "username": row['username'],
                "pin": row['pin'],
                "role": row['role'],
                "full_name": row['full_name'],
                "shift": row['shift'],
                "created_at": row['created_at'],
                "is_active": row['is_active']
            }
        return None
    
    def update_user(self, user_id: int, full_name: str = None, role: str = None, shift: str = None, is_active: int = None) -> Dict[str, Any]:
        """Aktualizuje dane użytkownika."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Przygotuj zapytanie dynamicznie
            updates = []
            params = []
            
            if full_name is not None:
                updates.append("full_name = ?")
                params.append(full_name)
            
            if role is not None:
                if role not in ['WAREHOUSE', 'ADMIN']:
                    return {"success": False, "error": "Dozwolone role: WAREHOUSE, ADMIN", "status": 400}
                updates.append("role = ?")
                params.append(role)
            
            if shift is not None:
                updates.append("shift = ?")
                params.append(shift)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            if not updates:
                return {"success": False, "error": "Brak danych do aktualizacji", "status": 400}
           
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                conn.close()
                return {"success": False, "error": "Użytkownik nie znaleziony", "status": 404}
            
            conn.commit()
            conn.close()
            
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e), "status": 500}
    
    def change_user_pin(self, user_id: int, new_pin: str) -> Dict[str, Any]:
        """Zmienia PIN użytkownika."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Walidacja PIN
            if not new_pin.isdigit() or len(new_pin) != 4:
                return {"success": False, "error": "PIN musi składać się z 4 cyfr", "status": 400}
            
            cursor.execute('''
                UPDATE users 
                SET pin = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_pin, user_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return {"success": False, "error": "Użytkownik nie znaleziony", "status": 404}
            
            conn.commit()
            conn.close()
            
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e), "status": 500}
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Usuwa użytkownika (soft delete - ustawia is_active = 0)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                return {"success": False, "error": "Użytkownik nie znaleziony", "status": 404}
            
            conn.commit()
            conn.close()
            
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e), "status": 500}
    
    def verify_user(self, pin: str, role: str = None) -> Optional[Dict[str, Any]]:
        """Weryfikuje użytkownika po PIN (i opcjonalnie roli)."""
        if role == 'OPERATOR':
            return None

        conn = self.get_connection()
        cursor = conn.cursor()
        
        if role:
            cursor.execute('''
                SELECT id, username, pin, role, full_name, shift, is_active
                FROM users
                WHERE pin = ? AND role = ? AND is_active = 1
                LIMIT 1
            ''', (pin, role))
        else:
            cursor.execute('''
                SELECT id, username, pin, role, full_name, shift, is_active
                FROM users
                WHERE pin = ? AND role IN ('WAREHOUSE', 'ADMIN') AND is_active = 1
                LIMIT 1
            ''', (pin,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row['id'],
                "username": row['username'],
                "pin": row['pin'],
                "role": row['role'],
                "full_name": row['full_name'],
                "shift": row['shift'],
                "is_active": row['is_active']
            }
        return None

    # ========================
    # WAREHOUSE SEARCH LIST
    # ========================
    
    def get_todays_search_list(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Pobiera dzisiejszą listę wyszukiwania."""
        from datetime import date
        today = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT id, envelope_id, priority, found, found_at, created_at
                FROM search_lists
                WHERE date = ? AND (user_id = ? OR user_id IS NULL)
                ORDER BY priority DESC, created_at ASC
            ''', (today, user_id))
        else:
            # Wspólna lista
            cursor.execute('''
                SELECT id, envelope_id, priority, found, found_at, created_at
                FROM search_lists
                WHERE date = ? AND user_id IS NULL
                ORDER BY priority DESC, created_at ASC
            ''', (today,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_to_search_list(self, envelope_id: str, user_id: str = None, priority: str = 'normal') -> Dict[str, Any]:
        """Dodaje kopertę do listy wyszukiwania."""
        from datetime import date
        today = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Sprawdź czy już istnieje
            cursor.execute('''
                SELECT id FROM search_lists
                WHERE envelope_id = ? AND date = ? AND (user_id = ? OR (user_id IS NULL AND ? IS NULL))
            ''', (envelope_id, today, user_id, user_id))
            
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Koperta już jest na liście", "status": 409}
            
            cursor.execute('''
                INSERT INTO search_lists (envelope_id, user_id, priority, date)
                VALUES (?, ?, ?, ?)
            ''', (envelope_id, user_id, priority, today))
            
            conn.commit()
            item_id = cursor.lastrowid
            conn.close()
            
            return {"success": True, "id": item_id}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e), "status": 500}
    
    def bulk_add_to_search_list(self, envelope_ids: List[str], user_id: str = None) -> Dict[str, Any]:
        """Dodaje wiele kopert do listy (bulk import)."""
        from datetime import date
        today = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        added = 0
        skipped = 0
        errors = 0
        error_details = []
        
        for idx, env_id in enumerate(envelope_ids, 1):
            try:
                # Sprawdź duplikat
                cursor.execute('''
                    SELECT id FROM search_lists
                    WHERE envelope_id = ? AND date = ? AND (user_id = ? OR (user_id IS NULL AND ? IS NULL))
                ''', (env_id, today, user_id, user_id))
                
                if cursor.fetchone():
                    skipped += 1
                    continue
                
                cursor.execute('''
                    INSERT INTO search_lists (envelope_id, user_id, date)
                    VALUES (?, ?, ?)
                ''', (env_id, user_id, today))
                
                added += 1
            except Exception as e:
                errors += 1
                error_details.append({"row": idx, "envelope": env_id, "error": str(e)})
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total": len(envelope_ids),
                "added": added,
                "skipped": skipped,
                "errors": errors
            },
            "error_details": error_details
        }
    
    def mark_search_item_found(self, envelope_id: str) -> Dict[str, Any]:
        """Oznacza kopertę jako znalezioną."""
        from datetime import date, datetime
        today = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE search_lists
            SET found = 1, found_at = ?
            WHERE envelope_id = ? AND date = ? AND found = 0
        ''', (datetime.now().isoformat(), envelope_id, today))
        
        updated = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {"success": True, "updated": updated}
    
    def delete_search_item(self, item_id: int) -> Dict[str, Any]:
        """Usuwa element z listy wyszukiwania."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM search_lists WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    def clear_todays_search_list(self, user_id: str = None) -> Dict[str, Any]:
        """Czyści dzisiejszą listę wyszukiwania."""
        from datetime import date
        today = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('DELETE FROM search_lists WHERE date = ? AND user_id = ?', (today, user_id))
        else:
            cursor.execute('DELETE FROM search_lists WHERE date = ? AND user_id IS NULL', (today,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {"success": True, "deleted": deleted}

    # ========================
    # NOTATKI OPERATORA + ZDJECIA
    # ========================

    def create_operator_note(self, envelope_id: str, machine_id: str, note_kind: str, note_data: Dict[str, Any], author: str) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            payload = json.dumps(note_data, ensure_ascii=False)
            cursor.execute(
                '''
                INSERT INTO operator_notes (envelope_id, machine_id, note_kind, note_data_json, created_by, modified_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''',
                (envelope_id, machine_id, note_kind, payload, author)
            )
            note_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {"success": True, "note_id": note_id}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e), "status": 500}

    def get_operator_notes_paginated(self, envelope_id: str, machine_id: str, limit: int = 20, cursor_token: Optional[str] = None) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        limit = max(1, min(limit, 100))

        where_sql = "WHERE envelope_id = ? AND machine_id = ? AND is_active = 1"
        params: list[Any] = [envelope_id, machine_id]

        if cursor_token:
            try:
                cursor_ts, cursor_id = cursor_token.split(",", 1)
                cursor_id_int = int(cursor_id)
                where_sql += " AND (created_at < ? OR (created_at = ? AND id < ?))"
                params.extend([cursor_ts, cursor_ts, cursor_id_int])
            except Exception:
                conn.close()
                return {"success": False, "error": "Nieprawidlowy cursor", "status": 400}

        params.append(limit + 1)
        cursor.execute(
            f'''
            SELECT id, envelope_id, machine_id, note_kind, note_data_json, created_by, created_at, modified_at
            FROM operator_notes
            {where_sql}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            ''',
            params
        )

        rows = cursor.fetchall()
        conn.close()

        has_next = len(rows) > limit
        rows = rows[:limit]
        notes: list[Dict[str, Any]] = []
        for row in rows:
            try:
                note_data = json.loads(row["note_data_json"]) if row["note_data_json"] else {}
            except Exception:
                note_data = {}
            notes.append(
                {
                    "id": row["id"],
                    "envelope_id": row["envelope_id"],
                    "machine_id": row["machine_id"],
                    "note_kind": row["note_kind"],
                    "note_data": note_data,
                    "created_by": row["created_by"],
                    "created_at": row["created_at"],
                    "modified_at": row["modified_at"],
                }
            )

        next_cursor = None
        if has_next and rows:
            last = rows[-1]
            next_cursor = f'{last["created_at"]},{last["id"]}'

        return {"success": True, "notes": notes, "next_cursor": next_cursor}

    def soft_delete_operator_note(self, note_id: int) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE operator_notes SET is_active = 0, modified_at = CURRENT_TIMESTAMP WHERE id = ?", (note_id,))
        updated = cursor.rowcount
        conn.commit()
        conn.close()
        if updated == 0:
            return {"success": False, "error": "Notatka nie istnieje", "status": 404}
        return {"success": True}

    def note_exists(self, note_scope: str, note_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        if note_scope == "operator_note":
            cursor.execute("SELECT id FROM operator_notes WHERE id = ? AND is_active = 1", (note_id,))
        else:
            cursor.execute("SELECT id FROM product_machine_notes WHERE id = ? AND is_active = 1", (note_id,))
        row = cursor.fetchone()
        conn.close()
        return bool(row)

    def get_note_images(self, note_scope: str, note_id: int) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT id, note_scope, note_id, storage_path, original_filename, mime_type, width, height, size_bytes,
                   sha256, annotations_json, order_index, revision, created_by, modified_by, created_at, modified_at
            FROM note_images
            WHERE note_scope = ? AND note_id = ? AND is_active = 1
            ORDER BY order_index ASC, id ASC
            ''',
            (note_scope, note_id)
        )
        rows = cursor.fetchall()
        conn.close()
        images: list[Dict[str, Any]] = []
        for row in rows:
            try:
                annotations = json.loads(row["annotations_json"]) if row["annotations_json"] else {"objects": []}
            except Exception:
                annotations = {"objects": []}
            images.append(
                {
                    "id": row["id"],
                    "note_scope": row["note_scope"],
                    "note_id": row["note_id"],
                    "storage_path": row["storage_path"],
                    "original_filename": row["original_filename"],
                    "mime_type": row["mime_type"],
                    "width": row["width"],
                    "height": row["height"],
                    "size_bytes": row["size_bytes"],
                    "sha256": row["sha256"],
                    "annotations_json": annotations,
                    "order_index": row["order_index"],
                    "revision": row["revision"],
                    "created_by": row["created_by"],
                    "modified_by": row["modified_by"],
                    "created_at": row["created_at"],
                    "modified_at": row["modified_at"],
                }
            )
        return images

    def get_note_image_by_id(self, image_id: int) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT id, note_scope, note_id, storage_path, original_filename, mime_type, width, height, size_bytes,
                   sha256, annotations_json, order_index, revision, created_by, modified_by, created_at, modified_at, is_active
            FROM note_images
            WHERE id = ?
            ''',
            (image_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        try:
            annotations = json.loads(row["annotations_json"]) if row["annotations_json"] else {"objects": []}
        except Exception:
            annotations = {"objects": []}
        return {
            "id": row["id"],
            "note_scope": row["note_scope"],
            "note_id": row["note_id"],
            "storage_path": row["storage_path"],
            "original_filename": row["original_filename"],
            "mime_type": row["mime_type"],
            "width": row["width"],
            "height": row["height"],
            "size_bytes": row["size_bytes"],
            "sha256": row["sha256"],
            "annotations_json": annotations,
            "order_index": row["order_index"],
            "revision": row["revision"],
            "created_by": row["created_by"],
            "modified_by": row["modified_by"],
            "created_at": row["created_at"],
            "modified_at": row["modified_at"],
            "is_active": row["is_active"],
        }

    def create_note_image(
        self,
        note_scope: str,
        note_id: int,
        storage_path: str,
        original_filename: str,
        mime_type: str,
        width: int,
        height: int,
        size_bytes: int,
        sha256_hex: str,
        annotations_json: Dict[str, Any],
        order_index: int,
        created_by: str,
    ) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if not self.note_exists(note_scope, note_id):
                conn.close()
                return {"success": False, "error": "Notatka nie istnieje", "status": 404}

            cursor.execute(
                "SELECT COUNT(*) FROM note_images WHERE note_scope = ? AND note_id = ? AND is_active = 1",
                (note_scope, note_id),
            )
            active_count = cursor.fetchone()[0]
            if active_count >= 3:
                conn.close()
                return {"success": False, "error": "Limit 3 zdjec na notatke", "status": 400}

            payload = json.dumps(annotations_json or {"objects": []}, ensure_ascii=False)
            cursor.execute(
                '''
                INSERT INTO note_images (
                    note_scope, note_id, storage_path, original_filename, mime_type, width, height,
                    size_bytes, sha256, annotations_json, order_index, revision, created_by, modified_by, modified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, CURRENT_TIMESTAMP)
                ''',
                (
                    note_scope,
                    note_id,
                    storage_path,
                    original_filename,
                    mime_type,
                    width,
                    height,
                    size_bytes,
                    sha256_hex,
                    payload,
                    order_index,
                    created_by,
                    created_by,
                ),
            )
            image_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {"success": True, "image_id": image_id}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e), "status": 500}

    def update_note_image_annotations(
        self,
        image_id: int,
        annotations_json: Dict[str, Any],
        modified_by: str,
        expected_revision: int,
    ) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT revision, annotations_json
            FROM note_images
            WHERE id = ? AND is_active = 1
            ''',
            (image_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"success": False, "error": "Obraz nie istnieje", "status": 404}

        current_revision = int(row["revision"] or 1)
        if current_revision != int(expected_revision):
            try:
                current_annotations = json.loads(row["annotations_json"]) if row["annotations_json"] else {"objects": []}
            except Exception:
                current_annotations = {"objects": []}
            conn.close()
            return {
                "success": False,
                "error": "Conflict",
                "status": 409,
                "current_revision": current_revision,
                "current_annotations_json": current_annotations,
            }

        payload = json.dumps(annotations_json or {"objects": []}, ensure_ascii=False)
        next_revision = current_revision + 1
        cursor.execute(
            '''
            UPDATE note_images
            SET annotations_json = ?, revision = ?, modified_by = ?, modified_at = CURRENT_TIMESTAMP
            WHERE id = ? AND is_active = 1
            ''',
            (payload, next_revision, modified_by, image_id),
        )
        conn.commit()
        conn.close()
        return {"success": True, "revision": next_revision}

    def soft_delete_note_image(self, image_id: int) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE note_images SET is_active = 0, modified_at = CURRENT_TIMESTAMP WHERE id = ? AND is_active = 1",
            (image_id,),
        )
        updated = cursor.rowcount
        conn.commit()
        conn.close()
        if updated == 0:
            return {"success": False, "error": "Obraz nie istnieje", "status": 404}
        return {"success": True}

# Helper do szybkiego użycia
db = Database()
