# Instrukcja Instalacji Systemu Kopert (v1.5) na Linux

Ten dokument opisuje proces instalacji i uruchomienia aplikacji na "czystym" systemie Linux (np. Ubuntu, Debian).

## 1. Wymagania Systemowe

Upewnij się, że masz zainstalowany:

- **Python 3.8+** (zwykle domyślnie w systemie)
- **pip** (menedżer pakietów Python)

Aby zainstalować brakujące składniki, otwórz terminal i wpisz:

```bash
sudo apt update
sudo apt install python3 python3-pip sqlite3
```

_(Pakiet `sqlite3` to narzędzie do ręcznego podglądu bazy danych, opcjonalne ale zalecane)._

## 2. Przygotowanie Aplikacji

1. Skopiuj folder `start_1.5` na nowy komputer (np. do katalogu domowego `~/projekty/koperty/start_1.5`).
2. Wejdź do katalogu projektu:
   ```bash
   cd ~/projekty/koperty/start_1.5
   ```

## 3. Instalacja Zależności (Biblioteki Python)

Aplikacja wymaga kilku bibliotek (Flask, Flask-CORS). Możesz je zainstalować globalnie dla użytkownika lub w wirtualnym środowisku.

**Opcja A (Najprostsza - dla jednego użytkownika):**

```bash
pip3 install flask flask-cors
```

**Opcja B (Zalecana - izolowane środowisko):**

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
```

_(Jeśli użyjesz Opcji B, pamiętaj by aktywować środowisko `source venv/bin/activate` przed każdym uruchomieniem)._

## 4. Baza Danych (SQLite)

System używa bazy danych **SQLite**, która jest przechowywana w jednym pliku: `koperty_system.db`.

**WAŻNE:**

- **Nie musisz instalować serwera bazy danych** (jak MySQL czy PostgreSQL).
- Baza danych zostanie **automatycznie utworzona** przy pierwszym uruchomieniu aplikacji, jeśli plik `koperty_system.db` nie istnieje.
- Jeśli przenosisz dane ze starego komputera, po prostu skopiuj plik `koperty_system.db` do katalogu `start_1.5`.

**Zarządzanie bazą (opcjonalne):**
Aby ręcznie sprawdzić zawartość bazy, użyj zainstalowanego narzędzia `sqlite3`:

```bash
sqlite3 koperty_system.db
# Wewnątrz konsoli sqlite:
.tables          # Pokaż tabele
select * from envelopes limit 5;  # Pokaż 5 kopert
.quit            # Wyjście
```

## 5. Uruchomienie Systemu

Najprostszy sposób uruchomienia to skorzystanie z dołączonego skryptu:

```bash
chmod +x start.sh   # Raz, aby nadać uprawnienia wykonywania
./start.sh          # Uruchomienie
```

Skrypt ten:

1. Sprawdzi poprawność bazy danych.
2. Zainstaluje brakujące biblioteki (jeśli masz uprawnienia).
3. Uruchomi serwer w tle.
4. Wyświetli adres, pod którym dostępna jest aplikacja (zwykle `http://localhost:5000`).

## 6. Dostęp do Aplikacji (Frontend)

Otwórz plik `prototype.html` w przeglądarce internetowej (Chrome/Firefox).

Jeśli uruchamiasz to na serwerze i chcesz łączyć się z innego komputera, musisz edytować plik `api_server.py` i zmienić linię na końcu pliku:
`app.run(host='0.0.0.0', port=5000)`
Wtedy aplikacja będzie dostępna pod adresem IP komputera, np. `http://192.168.1.15:5000`.
