# SYSTEM HISTORII OBIEGU KOPERT

## Opis
System automatycznie generuje szczegółowe raporty w formacie TXT zawierające kompletną historię przepływu kopert przez system produkcyjny.

## Zawartość raportu
Każdy raport zawiera:
- **Numer RCS** - kod produktu
- **Dane produktu** - firma, nazwa produktu
- **Aktualny status** - gdzie obecnie znajduje się koperta
- **Pełną historię przepływu**:
  - Data i czas każdego zdarzenia
  - Operacja (ISSUE, LOAD, RELEASE, RETURN)
  - Zmiana statusu (MAGAZYN → SHOP_FLOOR → W_PRODUKCJI)
  - Zmiana lokalizacji (maszyna, wózek, magazyn)
  - Użytkownik: ID, imię i nazwisko, rola (operator, magazynier)
  - **Informacja o notatkach**: Czy dla danej maszyny została utworzona notatka (TAK/NIE)
- **Podsumowanie notatek** - agregacja wszystkich notatek dla produktu

## Przykład wpisu w historii:
```
  [2026-02-01 14:30:15] ISSUE
    Status: MAGAZYN → SHOP_FLOOR
    Lokalizacja: MAGAZYN → CART-OUT-1
    Użytkownik: Jan Kowalski (ID: jan.kowalski, Rola: WAREHOUSE)
    ✓ NOTATKA: Nie

  [2026-02-01 14:35:22] LOAD
    Status: SHOP_FLOOR → W_PRODUKCJI
    Lokalizacja: SHOP_FLOOR → PRINTER MAIN
    Użytkownik: Anna Nowak (ID: anna.nowak, Rola: OPERATOR)
    ✓ NOTATKA: Tak
       Autor: Anna Nowak
       Data: 2026-02-01 14:36:10
```

## Użycie

### 1. Przez API (z aplikacji)
```javascript
// Pobierz historię dla konkretnego RCS jako plik TXT
window.open(`${API_BASE}/circulation-history/111222333`);

// Pobierz historię jako JSON
const response = await fetch(`${API_BASE}/circulation-history/111222333/view`);
const data = await response.json();

// Generuj historie dla wszystkich RCS
const response = await fetch(`${API_BASE}/circulation-history/generate-all`, {
    method: 'POST'
});
```

### 2. Przez wiersz poleceń
```bash
# Generuj historię dla konkretnego RCS
python3 circulation_history.py 111222333

# Generuj historie dla wszystkich RCS w systemie
python3 circulation_history.py
```

### 3. Programatycznie w Pythonie
```python
from circulation_history import save_circulation_history, save_all_circulation_histories

# Pojedyncza historia
filepath = save_circulation_history('111222333')
print(f"Zapisano: {filepath}")

# Wszystkie historie
files = save_all_circulation_histories()
print(f"Wygenerowano {len(files)} plików")
```

## Lokalizacja plików
Wszystkie wygenerowane raporty są zapisywane w katalogu:
```
circulation_history/circulation_history_{RCS}_{TIMESTAMP}.txt
```

Przykład:
```
circulation_history/circulation_history_111222333_20260201_145530.txt
```

## Automatyczne logowanie
System automatycznie rejestruje każde zdarzenie w tabeli `events` bazy danych:
- Wydanie z magazynu (ISSUE)
- Załadowanie na maszynę (LOAD)
- Zwolnienie z maszyny (RELEASE)
- Powrót do magazynu (RETURN)

## Endpointy API

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `/api/circulation-history/<rcs_id>` | GET | Pobiera plik TXT z historią |
| `/api/circulation-history/<rcs_id>/view` | GET | Zwraca historię jako JSON |
| `/api/circulation-history/generate-all` | POST | Generuje pliki dla wszystkich RCS |

## Struktura bazy danych

### Tabela `events`
Rejestruje wszystkie zdarzenia w systemie:
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    envelope_key TEXT,
    user_id TEXT,
    from_status TEXT,
    to_status TEXT,
    from_holder TEXT,
    to_holder TEXT,
    operation TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    comment TEXT
)
```

### Tabela `product_machine_notes`
Przechowuje notatki dla par (produkt, maszyna):
```sql
CREATE TABLE product_machine_notes (
    id INTEGER PRIMARY KEY,
    product_code TEXT,
    machine_id TEXT,
    note_content TEXT,
    created_at DATETIME,
    modified_at DATETIME,
    created_by TEXT,
    modified_by TEXT,
    is_active INTEGER DEFAULT 1
)
```

## Funkcje

### `get_envelope_circulation_history(rcs_id)`
Pobiera kompletną historię obiegu koperty z bazy danych.

**Parametry:**
- `rcs_id` - numer RCS kodoperty

**Zwraca:**
- Lista słowników z danymi kopert, zdarzeń i notatek lub `None` jeśli nie znaleziono

### `format_circulation_history_txt(rcs_id, history_data)`
Formatuje historię do czytelnego formatu tekstowego.

**Parametry:**
- `rcs_id` - numer RCS
- `history_data` - dane z `get_envelope_circulation_history()`

**Zwraca:**
- String z sformatowaną historią

### `save_circulation_history(rcs_id)`
Główna funkcja - pobiera historię i zapisuje do pliku.

**Parametry:**
- `rcs_id` - numer RCS

**Zwraca:**
- Ścieżka do zapisanego pliku lub `None` w przypadku błędu

### `save_all_circulation_histories()`
Generuje pliki historii dla wszystkich RCS w systemie.

**Zwraca:**
- Lista ścieżek do wygenerowanych plików

## Przykłady użycia

### Automatyczne generowanie po zakończeniu produkcji
```python
# W kodzie obsługi zwolnienia koperty z PALLETIZING
from circulation_history import save_circulation_history

def release_from_palletizing(envelope_id):
    # ... logika zwalniania ...
    
    # Wydobądź RCS z envelope_id
    rcs_id = envelope_id.split('#')[0]
    
    # Wygeneruj raport
    save_circulation_history(rcs_id)
```

### Eksport wszystkich historii do backupu
```bash
#!/bin/bash
# backup_histories.sh
python3 circulation_history.py
tar -czf histories_backup_$(date +%Y%m%d).tar.gz circulation_history/
```

## Uwagi
- Pliki są generowne z kodowaniem UTF-8
- Każdyuruchomienie tworzy nowy plik z timestampem
- System automatycznie tworzy katalog `circulation_history/` jeśli nie istnieje
- Historie zawierają tylko aktywne notatki (`is_active = 1`)
