"""
Moduł do generowania historii obiegu kopert w formacie TXT.
Zapisuje szczegółowe informacje o przepływie kopert przez system.
"""

import sqlite3
from datetime import datetime
import os

DB_NAME = "koperty_system.db"
HISTORY_DIR = "circulation_history"

def ensure_history_dir():
    """Tworzy katalog na pliki historii jeśli nie istnieje."""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def get_envelope_circulation_history(rcs_id):
    """
    Pobiera kompletną historię obiegu koperty po numerze RCS.
    Zwraca listę zdarzeń z pełnymi informacjami.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Pobierz wszystkie koperty dla danego RCS
    cursor.execute("""
        SELECT e.unique_key, e.rcs_id, e.status, e.current_holder_id,
               e.warehouse_section, e.last_operator_id, e.updated_at,
               p.company_name, p.product_name
        FROM envelopes e
        LEFT JOIN products p ON e.product_id = p.id
        WHERE e.rcs_id = ?
        ORDER BY e.unique_key
    """, (rcs_id,))

    
    envelopes = cursor.fetchall()
    
    if not envelopes:
        conn.close()
        return None
    
    history_data = []
    
    for envelope in envelopes:
        envelope_id = envelope['unique_key']
        
        # Pobierz zdarzenia dla tej koperty wraz z danymi użytkownika/maszyny
        cursor.execute("""
            SELECT e.id, e.envelope_key, e.user_id, e.from_status, e.to_status,
                   e.from_holder, e.to_holder, e.operation, e.timestamp, e.comment,
                   u.full_name, u.role, m.machine_name
            FROM events e
            LEFT JOIN users u ON e.user_id = u.username
            LEFT JOIN machines_auth m ON e.user_id = m.machine_name
            WHERE e.envelope_key = ?
            ORDER BY e.timestamp ASC
        """, (envelope_id,))
        
        events = cursor.fetchall()
        
        # Sprawdź czy były notatki dla produktów na maszynach
        product_code = '#'.join(envelope_id.split('#')[:2])  # "123456#1.0"
        
        cursor.execute("""
            SELECT pmn.machine_id, pmn.note_content, pmn.created_at, pmn.created_by,
                   pmn.modified_at, pmn.modified_by
            FROM product_machine_notes pmn
            WHERE pmn.product_code = ? AND pmn.is_active = 1
        """, (product_code,))
        
        notes = {row['machine_id']: dict(row) for row in cursor.fetchall()}
        
        history_data.append({
            'envelope': dict(envelope),
            'events': [dict(e) for e in events],
            'notes': notes
        })
    
    conn.close()
    return history_data

def format_circulation_history_txt(rcs_id, history_data):
    """
    Formatuje historię obiegu do czytelnego formatu TXT.
    """
    if not history_data:
        return f"Brak danych dla RCS: {rcs_id}\n"
    
    lines = []
    lines.append("=" * 80)
    lines.append(f"HISTORIA OBIEGU KOPERTY - RCS: {rcs_id}")
    lines.append("=" * 80)
    lines.append(f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    for idx, envelope_data in enumerate(history_data, 1):
        envelope = envelope_data['envelope']
        events = envelope_data['events']
        notes = envelope_data['notes']
        
        lines.append("-" * 80)
        lines.append(f"KOPERTA #{idx}: {envelope['unique_key']}")
        lines.append("-" * 80)
        
        # Informacje o produkcie
        if envelope['company_name'] and envelope['product_name']:
            lines.append(f"Produkt: {envelope['company_name']} | {envelope['product_name']}")
        else:
            lines.append(f"Produkt: KOPERTA {envelope['rcs_id']}")
        
        # Aktualny status
        lines.append(f"Aktualny status: {envelope['status']}")
        if envelope['current_holder_id']:
            lines.append(f"Aktualna lokalizacja: {envelope['current_holder_id']}")
        if envelope['warehouse_section']:
            lines.append(f"Sekcja magazynowa: {envelope['warehouse_section']}")
        if envelope['last_operator_id']:
            lines.append(f"Ostatni operator: {envelope['last_operator_id']}")
        
        lines.append("")
        lines.append("HISTORIA PRZEPŁYWU:")
        lines.append("")
        
        if not events:
            lines.append("  (Brak zarejestrowanych zdarzeń)")
        else:
            for event in events:
                timestamp = event['timestamp']
                operation = event['operation'] or 'OPERACJA'
                from_status = event['from_status'] or '---'
                to_status = event['to_status'] or '---'
                from_holder = event['from_holder'] or '---'
                to_holder = event['to_holder'] or '---'
                user_id = event['user_id'] or 'SYSTEM'
                if event['full_name']:
                    full_name = event['full_name']
                    role = event['role'] or '---'
                elif event['machine_name']:
                    full_name = f"Maszyna {event['machine_name']}"
                    role = 'MACHINE'
                else:
                    full_name = user_id
                    role = '---'
                comment = event['comment'] or ''
                
                lines.append(f"  [{timestamp}] {operation}")
                lines.append(f"    Status: {from_status} → {to_status}")
                lines.append(f"    Lokalizacja: {from_holder} → {to_holder}")
                lines.append(f"    Użytkownik: {full_name} (ID: {user_id}, Rola: {role})")
                
                # Sprawdź czy była notatka dla tej maszyny
                machine_id = to_holder if 'MACHINE' in str(operation) else None
                if machine_id and machine_id in notes:
                    note_info = notes[machine_id]
                    lines.append(f"    ✓ NOTATKA: Tak")
                    lines.append(f"       Autor: {note_info['created_by']}")
                    lines.append(f"       Data: {note_info['created_at']}")
                    if note_info['modified_at'] != note_info['created_at']:
                        lines.append(f"       Zmodyfikowano: {note_info['modified_at']} przez {note_info['modified_by']}")
                else:
                    lines.append(f"    ✓ NOTATKA: Nie")
                
                if comment:
                    lines.append(f"    Komentarz: {comment}")
                
                lines.append("")
        
        # Podsumowanie notatek
        if notes:
            lines.append("NOTATKI PRODUKTU NA MASZYNACH:")
            lines.append("")
            for machine_id, note_info in notes.items():
                lines.append(f"  Maszyna: {machine_id}")
                lines.append(f"    Treść: {note_info['note_content'][:100]}...")
                lines.append(f"    Utworzył: {note_info['created_by']} ({note_info['created_at']})")
                lines.append(f"    Zmodyfikował: {note_info['modified_by']} ({note_info['modified_at']})")
                lines.append("")
    
    lines.append("=" * 80)
    lines.append("KONIEC RAPORTU")
    lines.append("=" * 80)
    
    return "\n".join(lines)

def save_circulation_history(rcs_id):
    """
    Główna funkcja - pobiera historię i zapisuje do pliku TXT.
    
    Args:
        rcs_id: Numer RCS koperty
        
    Returns:
        Ścieżka do zapisanego pliku lub None jeśli błąd
    """
    ensure_history_dir()
    
    # Pobierz dane
    history_data = get_envelope_circulation_history(rcs_id)
    
    if not history_data:
        print(f"Brak danych dla RCS: {rcs_id}")
        return None
    
    # Formatuj do TXT
    txt_content = format_circulation_history_txt(rcs_id, history_data)
    
    # Zapisz do pliku
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"circulation_history_{rcs_id}_{timestamp}.txt"
    filepath = os.path.join(HISTORY_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print(f"✅ Historia zapisana: {filepath}")
    return filepath

def save_all_circulation_histories():
    """
    Generuje pliki historii dla wszystkich RCS w systemie.
    Przydatne do backupu lub analizy.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT rcs_id FROM envelopes ORDER BY rcs_id")
    rcs_list = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"\nGeneruję historię dla {len(rcs_list)} produktów RCS...")
    
    saved_files = []
    for rcs_id in rcs_list:
        filepath = save_circulation_history(rcs_id)
        if filepath:
            saved_files.append(filepath)
    
    print(f"\n✅ Wygenerowano {len(saved_files)} plików historii w katalogu: {HISTORY_DIR}/")
    return saved_files

# Automatyczne logowanie przy każdej zmianie statusu
def auto_log_event(envelope_id, user_id, operation, from_status, to_status, from_holder, to_holder, comment=None):
    """
    Funkcja pomocnicza do logowania zdarzeń.
    Może być wywołana automatycznie przy każdej zmianie statusu.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO events (envelope_key, user_id, from_status, to_status, from_holder, to_holder, operation, comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (envelope_id, user_id, from_status, to_status, from_holder, to_holder, operation, comment))
    
    conn.commit()
    conn.close()

# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        rcs_id = sys.argv[1]
        print(f"\nGeneruję historię dla RCS: {rcs_id}")
        save_circulation_history(rcs_id)
    else:
        print("\nUżycie:")
        print("  python circulation_history.py [RCS_ID]     - generuje historię dla konkretnego RCS")
        print("\nLub zaimportuj w kodzie:")
        print("  from circulation_history import save_circulation_history")
        print("  save_circulation_history('123456789')")
        print("\nGeneruję historię dla wszystkich RCS...")
        save_all_circulation_histories()
