Model danych
OPERATOR (np. Grunwald)
└── MASZYNA 1
│ └── RCS029837 → Notatka A (ustawienia dla maszyny 1)
│ └── RCS029838 → Notatka B
└── MASZYNA 2
└── RCS029837 → Notatka C (inne ustawienia dla maszyny 2)
└── RCS029838 → Notatka D
Klucz unikalny notatki: operator_id + machine_id + order_number

Struktura bazy danych
sql
Copy
-- Operatorzy
CREATE TABLE operators (
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL, -- np. "Grunwald"
login VARCHAR(50) UNIQUE NOT NULL
);

-- Maszyny
CREATE TABLE machines (
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL, -- np. "CNC-01"
type VARCHAR(50)
);

-- Przypisanie operatorów do maszyn (wiele-do-wielu)
CREATE TABLE operator_machines (
operator_id INT REFERENCES operators(id),
machine_id INT REFERENCES machines(id),
PRIMARY KEY (operator_id, machine_id)
);

-- Notatki ustawień (serce systemu)
CREATE TABLE machine_notes (
id SERIAL PRIMARY KEY,
operator_id INT REFERENCES operators(id),
machine_id INT REFERENCES machines(id),
order_number VARCHAR(50) NOT NULL, -- np. "RCS029837"
settings_note TEXT NOT NULL, -- treść notatki z ustawieniami
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW(),
UNIQUE(operator_id, machine_id, order_number)
);
Plan implementacji (krok po kroku)
Faza 1 — Backend (tydzień 1-2)
Krok Zadanie Szczegóły
1.1 Setup projektu API (Node.js/Python/C#), baza PostgreSQL
1.2 CRUD operatorów Rejestracja, logowanie, lista operatorów
1.3 CRUD maszyn Dodawanie maszyn, przypisywanie do operatorów
1.4 CRUD notatek Tworzenie/edycja/odczyt notatek per zlecenie+maszyna
1.5 Endpoint wyszukiwania GET /notes?order=RCS029837&machine=3 → zwraca notatkę
Faza 2 — Frontend (tydzień 2-3)
Krok Zadanie Szczegóły
2.1 Ekran logowania Operator wybiera siebie / loguje się
2.2 Pole wyszukiwania Wpisanie numeru zlecenia (np. RCS029837)
2.3 Wybór maszyny Po wpisaniu numeru → lista maszyn operatora
2.4 Wyświetlenie notatki Notatka ustawień dla danej kombinacji
2.5 Edytor notatki Tworzenie/edycja ustawień (rich text lub formularz)
Faza 3 — Logika biznesowa (tydzień 3-4)
Krok Zadanie Szczegóły
3.1 Widoczność notatek Notatka widoczna tylko po wpisaniu numeru zlecenia
3.2 Izolacja per maszyna Grunwald na maszynie 1 widzi inne notatki niż na maszynie 2
3.3 Historia zmian Logowanie kto i kiedy zmienił ustawienia
3.4 Walidacja Sprawdzanie formatu numeru zlecenia (regex: RCS\d{6})
Faza 4 — Testy i wdrożenie (tydzień 4-5)
Krok Zadanie
4.1 Testy jednostkowe i integracyjne
4.2 Testy z operatorami (UAT)
4.3 Wdrożenie na produkcję
Flow użytkownika

1. Grunwald loguje się
2. Wybiera maszynę (np. CNC-01)
3. Wpisuje numer zlecenia: RCS029837
4. System szuka notatki dla: Grunwald + CNC-01 + RCS029837
5. Jeśli istnieje → wyświetla ustawienia
6. Jeśli nie → pusty formularz do stworzenia notatki
7. Grunwald przełącza na maszynę CNC-02
8. Wpisuje ten sam numer RCS029837 → widzi INNE ustawienia
