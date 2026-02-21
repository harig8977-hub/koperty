const TRANSLATIONS = {
    'pl': {
        // Roles
        'role_warehouse': 'MAGAZYNIER',
        'role_warehouse_desc': 'Przyjęcia, Wydania, Sortowanie',
        'role_operator': 'OPERATOR',
        'role_operator_desc': 'Produkcja, Ustawienia, Baza Wiedzy',

        // Titles & Headers
        'system_title': 'SYSTEM KOPERT v2.0',
        'select_machine': 'WYBIERZ MASZYNĘ',
        'enter_pin': 'PODAJ PIN MASZYNY',
        'machine_name': 'NAZWA MASZYNY',
        'login_required': '🔒 WYMAGANE LOGOWANIE',

        // Warehouse Screen
        'search_envelope': '🔍 WYSZUKAJ KOPERTĘ',
        'search_placeholder': 'Wpisz liczby...',
        'search_hint': 'Wpisz dowolne liczby z numeru koperty:',
        'filter_shop_floor': 'Tylko na Hali (SHOP FLOOR)',
        'empty_search': 'Wpisz liczby aby wyszukać...',
        'no_results': 'Brak wyników',

        // Operations
        'btn_generator': '🖨️ GENERATOR QR',
        'btn_admin': '⚙️ PANEL ADMINA',
        'btn_machines': '⚙️ MASZYNY',
        'btn_user': '👥 USER',
        'btn_logout': 'WYLOGUJ',

        // Issue / Receive
        'header_issue': '⭡ WYDANIE (OUT)',
        'header_receive': '⭣ PRZYJĘCIE (RET)',
        'active_cart': 'Aktywny Wózek:',
        'manual_placeholder': 'Wpisz nr koperty...',
        'tap_scan': 'TAPNIJ BY ZESKANOWAĆ',
        'history_cart_out': '📜 HISTORIA (NA WÓZKU)',
        'history_cart_in': '📜 HISTORIA (Z WÓZKA)',
        'btn_confirm_out': 'ZATWIERDZ WÓZEK',
        'btn_finish_in': 'ZAKOŃCZ PRZYJĘCIE',
        'target_zone_label': 'DOCELOWA STREFA MAGAZYNOWA',
        'cart_return_label': 'NA WÓZKU ZWROTNYM',

        // Operator Screen
        'current_task': 'AKTUALNE ZADANIE',
        'task_none': 'BRAK / OCZEKIWANIE',
        'product_label': 'PRODUKT:',
        'status_label': 'STATUS:',
        'last_op_label': 'OSTATNI OPERATOR:',
        'btn_release': 'ZWOLNIJ KOPERTĘ',
        'btn_release_pallet': 'ZAKOŃCZ PALETĘ',

        // Alerts & Messages
        'error_pin': 'BŁĘDNY PIN!',
        'warning_irreversible': 'Uwaga: Ta operacja jest nieodwracalna.',
        'confirm_release': 'Czy na pewno chcesz zwolnić kopertę?',
        'envelope_released': 'Koperta zwolniona pomyślnie!',
        'envelope_loaded': 'Koperta załadowana pomyślnie!',
        'error_server': 'Błąd serwera',
        'error_network': 'Błąd połączenia',

        // Admin Panel
        'header_add_product': '🏭 DODAJ PRODUKT',
        'header_product_list': '📋 LISTA PRODUKTÓW',
        'label_company': 'Nazwa Firmy',
        'label_product': 'Nazwa Produktu',
        'label_rcs': 'Identyfikator RCS',
        'btn_add_product': 'DODAJ PRODUKT',
        'btn_import_csv': '📤 Importuj CSV',
        'btn_import_excel': '📊 Importuj Excel',
        'btn_refresh': '🔄 Odśwież',
        'btn_template_csv': '📥 Szablon CSV',
        'placeholder_search_product': 'Szukaj produktu...',
        'products_loading': 'Ładowanie produktów...',

        // Admin - Envelopes
        'header_register_envelope': '📝 REJESTRACJA NOWEJ KOPERTY',
        'label_choose_product': 'Wybierz Produkt (wpisz nazwę lub RCS)',
        'placeholder_search': 'Szukaj...',
        'label_selected_product': 'WYBRANY PRODUKT',
        'label_warehouse_section': 'Sekcja Magazynowa',
        'option_section': 'Sekcja {0}',
        'btn_create_envelope': 'UTWÓRZ KOPERTĘ',
        'header_envelope_history': '🔍 HISTORIA KOPERTY',
        'placeholder_envelope_id': 'Wpisz ID koperty...',
        'btn_search': 'SZUKAJ',
        'history_results_empty': 'Wpisz ID aby zobaczyć historię',
        'header_delete_envelope': '🗑️ USUWANIE KOPERTY',
        'placeholder_delete_id': 'ID koperty do usunięcia...',
        'btn_delete_permanent': 'USUŃ TRWALE',
        'warning_delete_caution': 'Ostrożnie! Tej operacji nie można cofnąć.',

        // User Panel
        'header_add_user': '👥 DODAJ UŻYTKOWNIKA',
        'label_username': 'Nazwa użytkownika',
        'label_fullname': 'Imię i nazwisko',
        'label_pin': 'PIN (4 cyfry)',
        'label_role': 'Rola',
        'option_role_operator': 'Operator',
        'option_role_warehouse': 'Magazynier',
        'option_role_admin': 'Administrator',
        'label_shift': 'Zmiana (opcjonalnie)',
        'option_shift_none': '-- Brak --',
        'option_shift_A': 'Zmiana A',
        'option_shift_B': 'Zmiana B',
        'option_shift_day': 'Dzień',
        'btn_add_user': 'DODAJ UŻYTKOWNIKA',
        'header_user_list': '📋 LISTA UŻYTKOWNIKÓW',
        'users_loading': 'Ładowanie użytkowników...',

        // Dynamic JS
        'confirm_delete_product': 'Czy na pewno chcesz usunąć produkt {0}?',
        'product_updated': '✅ Produkt zaktualizowany pomyślnie!',
        'product_deleted': '✅ Produkt usunięty pomyślnie!',
        'error_general': '❌ Błąd: {0}',
        'edit_product': '✏️ Edytuj Produkt',
        'btn_save': '💾 Zapisz',
        'btn_cancel': 'Anuluj',
        'all_fields_required': 'Wszystkie pola są wymagane!',
        'no_products_db': 'Brak produktów w bazie',
        'products_load_error': 'Błąd ładowania produktów',
        'no_results_search': 'Brak wyników',
        'search_error': 'Błąd wyszukiwania',
        'import_status_error': 'Błąd importu!',
        'error_details': 'Szczegóły błędów:',
        'import_status_finished': 'Import zakończony!',

        // Warehouse - New
        'today_searched': '🔍 DZIŚ SZUKANE',
        'add_btn': '+ Dodaj',
        'import_btn': '📋 Import',
        'return_cart_title': '📦 DO ZWROTU',
        'no_scanned': 'Brak zeskanowanych kopert',
        'no_envelopes': 'Brak kopert',

        // Operator - New
        'close_camera': 'ZAMKNIJ KAMERĘ',
        'load_btn': 'ZAŁADUJ',
        'no_entries': 'Brak wpisów',
        'finish_btn': 'ZAKOŃCZ',
        'new_entry_pallet': '➕ NOWY WPIS (PALETYZACJA)',
        'pressure_label': '⚖️ NACISK (BAR)',
        'layers_label': '📚 ILOŚĆ WARSTW',
        'pallet_type_label': '🧱 RODZAJ PALETY',
        'packs_label': '📦 ILE PAKSÓW',
        'save_settings': '💾 ZAPISZ USTAWIENIA',
        'pallet_euro': 'EURO',
        'pallet_chep': 'CHEP (Niebieska)',
        'pallet_industrial': 'PRZEMYSŁOWA',
        'pallet_dhp': 'DHP',
        'param_placeholder': 'Prędkość: 5000\nFider: 30%',
        'notes_placeholder': 'Na co zwracać uwagę...',
        'summary_placeholder': 'Krótkie podsumowanie zmiany...',

        // Operator - Extra
        'machineLabel': 'MASZYNA',
        'envelopeSelect': '📋 WYBIERZ KOPERTĘ DO PRACY',
        'scan_btn': '📡 SKANUJ',
        'shift_None': 'Zmiana: BRAK',
        'shift_A': 'Zmiana: A',
        'shift_B': 'Zmiana: B',
        'shift_Day': 'Zmiana: Dzień',
        'params_label': '⚙️ PARAMETRY',
        'attention_label': '⚠️ UWAGI',
        'summary_label': '📋 PODSUMOWANIE',
        'save_board_btn': '💾 ZAPISZ DO TABLICY',
        'history_log_title': '📜 HISTORIA WPISÓW',
        'new_entry_title': '➕ NOWY WPIS',
        'slot_label': '📦 SLOT {0}',

        // General - New
        'connecting': 'Łączenie...',
        'loading': '⏳ Ładowanie...',
        'history_error': '❌ Błąd pobierania historii',
        'server_error': '❌ Błąd połączenia z serwerem',
        'enter_id_history': 'Wpisz ID koperty aby zobaczyć historię...',
        'no_users': 'Brak użytkowników',
        'users_load_error': 'Błąd ładowania użytkowników',
        'import_success': '✅ Import zakończony pomyślnie!',
        'skipped': 'Pominięto',
        'errors_label': 'Błędy',
        'connection_error_label': '❌ Błąd połączenia',
        
        // Modals - New
        'btn_cancel_modal': 'Anuluj',
        'edit_product_title': '✏️ Edytuj Produkt',
        'import_products_title': '📤 Import Produktów',
        'file_format_label': 'Format pliku:',
        'file_format_search_hint': 'Jedna koperta na linię (CSV lub Excel z 1 kolumną)',
        'btn_import': '📤 Importuj',
        'add_to_search_title': '🔍 Dodaj do listy szukanych',
        'envelope_id_label': 'ID Koperty:',
        'envelope_placeholder': 'np. RCS044761/A',
        'btn_add': '✅ Dodaj',
        'import_search_title': '📤 Import Listy Szukanych',

        // Alerts - Specific
        'fill_pallet_params': 'Wypełnij pola parametrów paletyzacji!',
        'settings_saved': 'Zapisano ustawienia paletyzacji!',
        'logout_success': 'Wylogowano pomyślnie.',
        'fill_one_field': 'Wypełnij przynajmniej jedno pole!',
        'note_saved': '✅ Notatka zapisana!',
        'no_active_envelope_finish': '⚠️ Brak aktywnej koperty do zakończenia!',
        'load_envelope_first': '⚠️ Najpierw załaduj kopertę do slotu!',
        'envelope_location_error': '⛔ Koperta niedostępna dla operatora (Zła lokalizacja)',
        'enter_note_content': 'Wpisz treść notatki!',
        'error_operator_name': '❌ Błąd: nie można pobrać nazwy operatora',
        'error_note_save': '❌ Błąd zapisu notatki! Sprawdź konsolę przeglądarki (F12).',
        'enter_envelope_number': 'Wpisz numer koperty!',
        'envelope_not_found_db': '❌ Koperta nie znaleziona w bazie!',
        'semaphore_busy': '⛔ SEMAFOR: Koperta zajęta przez: {0}',
        'error_machine': '⛔ {0}\nMaszyna: {1}',
        'no_envelopes_warehouse': 'Brak dostępnych kopert w magazynie!',
        'fill_product_fields': 'Wypełnij wszystkie pola produktu!',
        'product_added_success': '✅ Sukces! Dodano produkt: {0} | {1}',
        'select_product': 'Wybierz produkt!',
        'delete_envelope_prompt': 'Wpisz ID koperty do usunięcia.',
        'delete_cancelled': 'Anulowano usunięcie.',
        'envelope_deleted_success': '✅ SUKCES: Koperta {0} została usunięta.',
        'delete_error': '❌ BŁĄD: {0}',
        'fill_required_user': 'Uzupełnij wymagane pola: nazwa użytkownika, PIN i rola.',
        'pin_4_digits': 'PIN musi składać się z 4 cyfr.',
        'user_added_success': '✅ Użytkownik {0} został dodany!',
        'user_not_found': 'Nie znaleziono użytkownika',
        'user_updated_success': '✅ Użytkownik zaktualizowany!',
        'pin_changed_success': '✅ PIN dla {0} został zmieniony na: {1}',
        'user_deleted_success': '✅ Użytkownik {0} został usunięty (dezaktywowany).',
        'enter_envelope_code': 'Wpisz kod koperty!',
        'envelope_not_found_base': '❌ Koperta nie istnieje w bazie!',
        'enter_envelope_id': 'Podaj ID koperty!',
        'added_to_list': '✅ Dodano do listy!',
        'error_connection': '❌ Błąd połączenia',
        'choose_file': 'Wybierz plik!',
        'error_delete': '❌ Błąd usuwania',
        'error_clear': '❌ Błąd czyszczenia listy',
        'cart_empty_warning': '⚠️ Wózek jest pusty! Dodaj koperty przed zatwierdzeniem.',
        'no_envelopes_receive': '⚠️ Brak kopert do przyjęcia! Zeskanuj koperty przed zakończeniem.',
        'select_zone_first': '⚠️ WYBIERZ NAJPIERW STREFĘ MAGAZYNU (A-R)!',
        'camera_blocked': '⚠️ KAMERA ZABLOKOWANA PRZEZ PRZEGLĄDARKĘ!\n\nPrzeglądarki blokują kamerę na stronach nieszyfrowanych (HTTP).\nUżyj localhost lub HTTPS.',
        'camera_secure_context_hint': 'Dla adresu LAN po HTTP kamera może być blokowana. Użyj HTTPS albo localhost/127.0.0.1.',
        'camera_lib_missing': 'Brak biblioteki skanera (html5-qrcode). Sprawdź połączenie z internetem lub lokalny plik vendor.',
        'camera_start_error': 'Błąd uruchomienia kamery.',
        'camera_permission_denied': 'Brak uprawnień do kamery. Sprawdź ustawienia przeglądarki.',
        'camera_not_found': 'Nie znaleziono kamery.',
        'camera_in_use': 'Kamera jest zajęta przez inną aplikację.',
        'camera_unknown_error': 'Nieznany błąd kamery.',
        'lib_init_error': 'Błąd inicjalizacji biblioteki: ',
        'go_to_op_panel': 'Przejdź do panelu operatora!',
        'confirm_delete_product_text': 'Czy na pewno chcesz usunąć produkt {0}?\n\nUwaga: Ta operacja jest nieodwracalna.',
        'choose_import_file': 'Wybierz plik do importu!',
        'importing_status': 'Importowanie...',
        'import_total': 'Razem',
        'import_added': 'Dodano',
        'import_skipped': 'Pominięto (zduplikowane)',
        'import_errors': 'Błędy',
        'import_error_details': 'Szczegóły błędów:',
        'import_row_error': 'Wiersz {0}: {1}',
        'btn_logout': 'WYLOGUJ',
        'envelope_number_label': 'Numer koperty (RCS#wersja#nr):',
        'slot_note_placeholder': 'Notatka...',
        'slot_envelope_placeholder': 'Nr koperty...'
    },
    'en': {
        // Roles
        'role_warehouse': 'WAREHOUSE',
        'role_warehouse_desc': 'Receive, Issue, Sort',
        'role_operator': 'PRODUCTION',
        'role_operator_desc': 'Production, Settings, Knowledge Base',

        // Titles & Headers
        'system_title': 'ENVELOPE SYSTEM v2.0',
        'select_machine': 'SELECT MACHINE',
        'enter_pin': 'ENTER MACHINE PIN',
        'machine_name': 'MACHINE NAME',
        'login_required': '🔒 LOGIN REQUIRED',

        // Warehouse Screen
        'search_envelope': '🔍 SEARCH ENVELOPE',
        'search_placeholder': 'Enter numbers...',
        'search_hint': 'Enter any digits from envelope ID:',
        'filter_shop_floor': 'Shop Floor Only',
        'empty_search': 'Type numbers to search...',
        'no_results': 'No results found',

        // Operations
        'btn_generator': '🖨️ QR GENERATOR',
        'btn_admin': '⚙️ ADMIN PANEL',
        'btn_machines': '⚙️ MACHINES',
        'btn_user': '👥 USER',
        'btn_logout': 'LOGOUT',

        // Issue / Receive
        'header_issue': '⭡ ISSUE (OUT)',
        'header_receive': '⭣ RECEIVE (RET)',
        'active_cart': 'Active Cart:',
        'manual_placeholder': 'Envelope ID...',
        'tap_scan': 'TAP TO SCAN',
        'history_cart_out': '📜 HISTORY (ON CART)',
        'history_cart_in': '📜 HISTORY (FROM CART)',
        'btn_confirm_out': 'CONFIRM CART',
        'btn_finish_in': 'FINISH RECEIVE',
        'target_zone_label': 'TARGET WAREHOUSE ZONE',
        'cart_return_label': 'ON RETURN CART',
        'today_searched': '🔍 SEARCHED TODAY',
        'add_btn': '+ Add',
        'import_btn': '📋 Import',
        'return_cart_title': '📦 TO RETURN',
        'no_scanned': 'No envelopes scanned',
        'no_envelopes': 'No envelopes',

        // Operator Screen
        'current_task': 'CURRENT TASK',
        'task_none': 'NONE / WAITING',
        'product_label': 'PRODUCT:',
        'status_label': 'STATUS:',
        'last_op_label': 'LAST OPERATOR:',
        'btn_release': 'RELEASE ENVELOPE',
        'btn_release_pallet': 'FINISH PALLET',
        'close_camera': 'CLOSE CAMERA',
        'load_btn': 'LOAD',
        'no_entries': 'No entries',
        'finish_btn': 'FINISH',
        'new_entry_pallet': '➕ NEW ENTRY (PALLETIZING)',
        'pressure_label': '⚖️ PRESSURE (BAR)',
        'layers_label': '📚 LAYERS COUNT',
        'pallet_type_label': '🧱 PALLET TYPE',
        'packs_label': '📦 PACKS COUNT',
        'save_settings': '💾 SAVE SETTINGS',
        'pallet_euro': 'EURO',
        'pallet_chep': 'CHEP (Blue)',
        'pallet_industrial': 'INDUSTRIAL',
        'pallet_dhp': 'DHP',
        'param_placeholder': 'Speed: 5000\nFeeder: 30%',
        'notes_placeholder': 'What to pay attention to...',
        'summary_placeholder': 'Brief summary of changes...',

        // Operator - Extra
        'machineLabel': 'MACHINE',
        'envelopeSelect': '📋 SELECT ENVELOPE',
        'scan_btn': '📡 SCAN',
        'shift_None': 'Shift: NONE',
        'shift_A': 'Shift: A',
        'shift_B': 'Shift: B',
        'shift_Day': 'Shift: Day',
        'params_label': '⚙️ PARAMETRY',
        'attention_label': '⚠️ ATTENTION',
        'summary_label': '📋 SUMMARY',
        'save_board_btn': '💾 SAVE TO BOARD',
        'history_log_title': '📜 HISTORY LOG',
        'new_entry_title': '➕ NEW ENTRY',
        'slot_label': '📦 SLOT {0}',

        // Alerts & Messages
        'error_pin': 'WRONG PIN!',
        'warning_irreversible': 'Warning: This operation is irreversible.',
        'confirm_release': 'Are you sure you want to release this envelope?',
        'envelope_released': 'Envelope released successfully!',
        'envelope_loaded': 'Envelope loaded successfully!',
        'error_server': 'Server Error',
        'error_network': 'Connection Error',
        'connecting': 'Connecting...',
        'loading': '⏳ Loading...',
        'history_error': '❌ Error loading history',
        'server_error': '❌ Server connection error',
        'enter_id_history': 'Enter envelope ID to view history...',
        'no_users': 'No users',
        'users_load_error': 'Error loading users',
        'import_success': '✅ Import finished successfully!',
        'skipped': 'Skipped',
        'errors_label': 'Errors',
        'connection_error_label': '❌ Connection Error',

        // Admin Panel
        'header_add_product': '🏭 ADD PRODUCT',
        'header_product_list': '📋 PRODUCT LIST',
        'label_company': 'Company Name',
        'label_product': 'Product Name',
        'label_rcs': 'RCS ID',
        'btn_add_product': 'ADD PRODUCT',
        'btn_import_csv': '📤 Import CSV',
        'btn_import_excel': '📊 Import Excel',
        'btn_refresh': '🔄 Refresh',
        'btn_template_csv': '📥 CSV Template',
        'placeholder_search_product': 'Search product...',
        'products_loading': 'Loading products...',

        // Admin - Envelopes
        'header_register_envelope': '📝 REGISTER NEW ENVELOPE',
        'label_choose_product': 'Choose Product (name or RCS)',
        'placeholder_search': 'Search...',
        'label_selected_product': 'SELECTED PRODUCT',
        'label_warehouse_section': 'Warehouse Section',
        'option_section': 'Section {0}',
        'btn_create_envelope': 'CREATE ENVELOPE',
        'header_envelope_history': '🔍 ENVELOPE HISTORY',
        'placeholder_envelope_id': 'Enter envelope ID...',
        'btn_search': 'SEARCH',
        'history_results_empty': 'Enter ID to view history',
        'header_delete_envelope': '🗑️ DELETE ENVELOPE',
        'placeholder_delete_id': 'Envelope ID to delete...',
        'btn_delete_permanent': 'DELETE PERMANENTLY',
        'warning_delete_caution': 'Caution! This operation cannot be undone.',

        // Admin - Modals
        'btn_cancel_modal': 'Cancel',
        'edit_product_title': '✏️ Edit Product',
        'import_products_title': '📤 Import Products',
        'file_format_label': 'File format:',
        'file_format_search_hint': 'One envelope per line (CSV or Excel with 1 column)',
        'btn_import': '📤 Import',
        'add_to_search_title': '🔍 Add to search list',
        'envelope_id_label': 'Envelope ID:',
        'envelope_placeholder': 'e.g. RCS044761/A',
        'btn_add': '✅ Add',
        'import_search_title': '📤 Import Search List',

        // Alerts - Specific
        'fill_pallet_params': 'Fill pallet parameters!',
        'settings_saved': 'Settings saved!',
        'logout_success': 'Logged out successfully.',
        'fill_one_field': 'Fill at least one field!',
        'note_saved': '✅ Note saved!',
        'no_active_envelope_finish': '⚠️ No active envelope to finish!',
        'load_envelope_first': '⚠️ Load envelope into slot first!',
        'envelope_location_error': '⛔ Envelope not available for operator (Wrong Location)',
        'enter_note_content': 'Enter note content!',
        'error_operator_name': '❌ Error: Cannot get operator name',
        'error_note_save': '❌ Error saving note! Check console (F12).',
        'enter_envelope_number': 'Enter envelope number!',
        'envelope_not_found_db': '❌ Envelope not found in database!',
        'semaphore_busy': '⛔ SEMAPHORE: Envelope busy by: {0}',
        'error_machine': '⛔ {0}\nMachine: {1}',
        'no_envelopes_warehouse': 'No envelopes available in warehouse!',
        'fill_product_fields': 'Fill all product fields!',
        'product_added_success': '✅ Success! Product added: {0} | {1}',
        'select_product': 'Select product!',
        'delete_envelope_prompt': 'Enter envelope ID to delete.',
        'delete_cancelled': 'Deletion cancelled.',
        'envelope_deleted_success': '✅ SUCCESS: Envelope {0} deleted.',
        'delete_error': '❌ ERROR: {0}',
        'fill_required_user': 'Fill required fields: username, PIN, role.',
        'pin_4_digits': 'PIN must be 4 digits.',
        'user_added_success': '✅ User {0} added!',
        'user_not_found': 'User not found',
        'user_updated_success': '✅ User updated!',
        'pin_changed_success': '✅ PIN for {0} changed to: {1}',
        'user_deleted_success': '✅ User {0} deleted (deactivated).',
        'enter_envelope_code': 'Enter envelope code!',

        // User Panel
        'header_add_user': '👥 ADD USER',
        'label_username': 'Username',
        'label_fullname': 'Full Name',
        'label_pin': 'PIN (4 digits)',
        'label_role': 'Role',
        'option_role_operator': 'Operator',
        'option_role_warehouse': 'Warehouse',
        'option_role_admin': 'Administrator',
        'label_shift': 'Shift (optional)',
        'option_shift_none': '-- None --',
        'option_shift_A': 'Shift A',
        'option_shift_B': 'Shift B',
        'option_shift_day': 'Day',
        'btn_add_user': 'ADD USER',
        'header_user_list': '📋 USER LIST',
        'users_loading': 'Loading users...',

        // Dynamic JS
        'confirm_delete_product': 'Are you sure you want to delete product {0}?',
        'product_updated': '✅ Product updated successfully!',
        'product_deleted': '✅ Product deleted successfully!',
        'error_general': '❌ Error: {0}',
        'edit_product': '✏️ Edit Product',
        'btn_save': '💾 Save',
        'btn_cancel': 'Cancel',
        'all_fields_required': 'All fields are required!',
        'no_products_db': 'No products in database',
        'products_load_error': 'Error loading products',
        'no_results_search': 'No results',
        'search_error': 'Search error',
        'import_status_error': 'Import error!',
        'error_details': 'Error details:',
        'import_status_finished': 'Import finished!',
        'enter_envelope_code': 'Enter envelope code!',
        'envelope_not_found_base': '❌ Envelope does not exist in database!',
        'enter_envelope_id': 'Enter envelope ID!',
        'added_to_list': '✅ Added to list!',
        'error_connection': '❌ Connection error',
        'choose_file': 'Choose file!',
        'error_delete': '❌ Delete error',
        'error_clear': '❌ List clear error',
        'cart_empty_warning': '⚠️ Cart is empty! Add envelopes before confirming.',
        'no_envelopes_receive': '⚠️ No envelopes to receive! Scan envelopes before finishing.',
        'select_zone_first': '⚠️ SELECT WAREHOUSE ZONE (A-R) FIRST!',
        'camera_blocked': '⚠️ CAMERA BLOCKED BY BROWSER!\n\nBrowsers block camera on non-secure sites (HTTP).\nUse localhost or HTTPS.',
        'camera_secure_context_hint': 'Camera may be blocked on LAN HTTP addresses. Use HTTPS or localhost/127.0.0.1.',
        'camera_lib_missing': 'Scanner library (html5-qrcode) is missing. Check internet access or local vendor file.',
        'camera_start_error': 'Camera start error.',
        'camera_permission_denied': 'Camera permission denied. Check browser settings.',
        'camera_not_found': 'No camera found.',
        'camera_in_use': 'Camera is already in use by another application.',
        'camera_unknown_error': 'Unknown camera error.',
        'lib_init_error': 'Library init error: ',
        'go_to_op_panel': 'Go to operator panel!',
        'confirm_delete_product_text': 'Are you sure you want to delete product {0}?\n\nCaution: This operation cannot be undone.',
        'choose_import_file': 'Choose file to import!',
        'importing_status': 'Importing...',
        'import_total': 'Total',
        'import_added': 'Added',
        'import_skipped': 'Skipped (duplicate)',
        'import_errors': 'Errors',
        'import_error_details': 'Error details:',
        'import_row_error': 'Row {0}: {1}',
        'btn_logout': 'LOGOUT',
        'envelope_number_label': 'Envelope number (RCS#version#nr):',
        'slot_note_placeholder': 'Note...',
        'slot_envelope_placeholder': 'Envelope nr...'
    },
};

let currentLang = localStorage.getItem('app_lang') || 'pl';

function t(key, ...args) {
    let str = TRANSLATIONS[currentLang][key] || key;
    args.forEach((arg, i) => {
        str = str.replace(`{${i}}`, arg);
    });
    return str;
}

function setLanguage(lang) {
    if (!TRANSLATIONS[lang]) return;

    currentLang = lang;
    localStorage.setItem('app_lang', lang);

    // Update HTML elements
    // Update HTML elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const argsAttr = el.getAttribute('data-i18n-args');
        let args = [];

        if (argsAttr) {
            try {
                args = JSON.parse(argsAttr);
            } catch (e) {
                console.error('Error parsing data-i18n-args', e);
            }
        }

        if (TRANSLATIONS[lang][key]) {
            let text = TRANSLATIONS[lang][key];

            // Replace placeholders {0}, {1}, etc.
            if (args.length > 0) {
                args.forEach((arg, i) => {
                    text = text.replace(`{${i}}`, arg);
                });
            }

            if ((el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') && el.getAttribute('placeholder')) {
                el.placeholder = text;
            } else {
                el.innerHTML = text;
            }
        }
    });

    // Update active button state if exists
    updateLangButtons();
}

function updateLangButtons() {
    const btnPl = document.getElementById('btn-lang-pl');
    const btnEn = document.getElementById('btn-lang-en');

    if (btnPl && btnEn) {
        if (currentLang === 'pl') {
            btnPl.classList.add('active-lang');
            btnEn.classList.remove('active-lang');
        } else {
            btnPl.classList.remove('active-lang');
            btnEn.classList.add('active-lang');
        }
    }
}

// Init on load
document.addEventListener('DOMContentLoaded', () => {
    setLanguage(currentLang);
});
