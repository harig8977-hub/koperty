INSTRUKCJA INSTALACJI I URUCHOMIENIA
====================================

Wymagania:
- System operacyjny Linux/macOS (lub Windows z WSL/Python)
- Zainstalowany Python 3

Instrukcja:
1. Skopiuj cały folder 'start1.2' na nowy komputer.
2. Otwórz terminal w tym folderze.
3. Nadaj uprawnienia do uruchamiania skryptu startowego:
   chmod +x start.sh
4. Uruchom system:
   ./start.sh

Skrypt automatycznie:
- Stworzy wirtualne środowisko Python (venv)
- Zainstaluje wymagane biblioteki (flask, flask-cors)
- Uruchomi serwer API

Po uruchomieniu:
- Otwórz przeglądarkę i wpisz adres: http://localhost:5000
- Powinien pojawić się interfejs systemu (prototype.html)

Uwagi:
- Baza danych 'koperty_system.db' zawiera aktualny stan systemu.
- Wszystkie dane są zapisywane lokalnie w tym pliku.
