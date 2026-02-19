# Replit: uruchomienie z GitHub

## Co jest już przygotowane

- `api_server.py` uruchamia się na porcie z `PORT` (wymagane na Replit).
- `.replit` ustawia komendę startową: `bash run_replit.sh`.
- `run_replit.sh`:
  - tworzy `.venv` (jeśli brak),
  - instaluje zależności z `requirements.txt`,
  - startuje `api_server.py`.
- `replit.nix` dodaje Python + sqlite.

## 1. Wypchnij repo na GitHub

W tym katalogu:

```bash
git add .
git commit -m "Prepare project for Replit deployment"
git push -u origin main
```

## 2. Import do Replit

1. Wejdź na Replit.
2. `Create Repl` -> `Import from GitHub`.
3. Wklej URL repo: `https://github.com/harig8977-hub/koperty.git`.
4. Utwórz repl.

## 3. Uruchom

- Kliknij `Run`.
- Aplikacja wystartuje i poda publiczny URL Replit.

## 4. Co otworzyć

- API / frontend główny: `/` (serwuje `prototype.html`)
- Generator QR: `/generator-qr.html`

## 5. Dane

- Baza SQLite: `koperty_system.db` (plik w repo).
- Replit zapisuje zmiany w plikach projektu, więc dane zostają po restarcie repl.

