# Changelog — 2026-02-26

## 1. Magazyn — podział dashboardu
- Sekcja "Wydanie" (ISSUE) i "Przyjęcie" (RECEIVE) rozdzielone na dwa osobne widoki
- Dodano przycisk przełączania w górnym pasku (`RECEIVE` / `ISSUE`)
- Domyślnie wyświetlane są Wydania

## 2. Poprawki UI
- Zmniejszono szerokość pola wyszukiwania kopert (`#search-envelope-input`) do 95%
- Zmieniono szerokość pola historii kopert (`#main-screen-history-search`) na 90%
- Przetłumaczono etykiety przycisków na angielski (`RECEIVE`, `ISSUE`)
- Ujednolicono wielkość przycisków w górnym pasku magazynu (140×45px)

## 3. Baza danych — powiązanie notatek z RCS
- Dodano kolumnę `rcs_id` do tabeli `operator_notes`
- Automatyczne rozwiązywanie `rcs_id` z tabeli `envelopes` przy tworzeniu notatki
- Backfill istniejących notatek przy starcie serwera
- Dodano indeks na `rcs_id` dla szybkiego wyszukiwania
- API (`GET` i `POST` `/api/operator-notes/`) zwraca pole `rcs_id`

### Zmienione pliki
- `prototype.html` — layout, przyciski, toggle
- `database.py` — migracja, backfill, create/get operator notes
- `api_server.py` — rcs_id w odpowiedziach API
