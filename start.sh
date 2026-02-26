#!/bin/bash
source venv/bin/activate
echo "--- Naprawa i Start Systemu Kopert (v1.4) ---"

# 1. Zatrzymaj stare procesy
echo "Zamykanie starych procesów..."
pkill -f api_server.py
sleep 2

# 2. Sprawdź bazę danych
echo "Sprawdzanie integralności bazy danych..."
if [ -f "koperty_system.db" ]; then
    DB_CHECK=$(python3 -c "import sqlite3; c = sqlite3.connect('koperty_system.db'); r = c.execute('PRAGMA integrity_check').fetchone()[0]; print(r)")
    echo "Status Bazy: $DB_CHECK"
    if [ "$DB_CHECK" != "ok" ]; then
        echo "BŁĄD: Baza danych jest uszkodzona lub zablokowana!"
        exit 1
    fi
else
    echo "UWAGA: Baza danych nie istnieje (zostanie utworzona)."
fi

# 3. Sprawdź biblioteki
echo "Weryfikacja środowiska Python..."
python3 -c "import flask, flask_cors, sqlite3, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Brak wymaganych bibliotek. Próba instalacji..."
    pip install -r requirements.txt
else
    echo "Środowisko OK."
fi

# 4. Wyczyść stare logi
rm -f api_server.log

# 5. Uruchom serwer
echo "Uruchamianie serwera API..."
nohup python3 api_server.py > api_server.log 2>&1 &
SERVER_PID=$!
echo "Serwer działa w tle (PID: $SERVER_PID)"

# 6. Weryfikacja startu
echo "Oczekiwanie na start..."
sleep 3
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ SUKCES: Serwer aktywny."
    echo "Logi serwera:"
    head -n 5 api_server.log
    
    # Opcjonalne otwarcie przeglądarki
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5000 &
    fi
else
    echo "❌ BŁĄD: Serwer nie wystartował."
    cat api_server.log
    exit 1
fi
