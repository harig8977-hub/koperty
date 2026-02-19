// =====================================================
// ZARZĄDZANIE PRODUKTAMI - Funkcje edycji, usuwania i importu
// =====================================================

let currentImportType = 'csv';

// Aktualizuj funkcję loadProductsList aby pokazywała przyciski edycji/usuwania
// Aktualizuj funkcję loadProductsList aby pokazywała przyciski edycji/usuwania

window.loadProductsList = async function () {
    const container = document.getElementById('products-list');
    try {
        const response = await fetch(`${API_BASE}/products`);
        if (response.ok) {
            const products = await response.json();

            if (products.length === 0) {
                container.innerHTML = '<div style="color: #555; text-align: center; padding: 20px;">Brak produktów w bazie</div>';
                return;
            }

            container.innerHTML = products.map(p => {
                const companyEsc = (p.company_name || '').replace(/'/g, "\\'");
                const productEsc = (p.product_name || '').replace(/'/g, "\\'");
                const rcsEsc = (p.rcs_id || '').replace(/'/g, "\\'");

                return `
                    <div style="background: #252525; padding: 10px; margin-bottom: 8px; border-radius: 6px; border-left: 3px solid var(--accent-orange); display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="font-weight: bold; color: #fff;">${p.company_name}</div>
                            <div style="color: #aaa; font-size: 0.9rem;">${p.product_name}</div>
                            <div style="color: #888; font-size: 0.8rem;">RCS: ${p.rcs_id}</div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button onclick="editProduct(${p.id}, '${companyEsc}', '${productEsc}', '${rcsEsc}')" 
                                class="btn" style="padding: 5px 10px; font-size: 0.8rem; background: #555;">
                                ✏️
                            </button>
                            <button onclick="deleteProduct(${p.id}, '${rcsEsc}')" 
                                class="btn" style="padding: 5px 10px; font-size: 0.8rem; background: var(--accent-red);">
                                ❌
                            </button>
                        </div>
                    </div>
                `}).join('');
        }
    } catch (err) {
        container.innerHTML = '<div style="color: var(--accent-red);">Błąd ładowania produktów</div>';
    }
};

// Override searchProductsAdmin
window.searchProductsAdmin = async function () {
    const query = document.getElementById('search-product-input').value.trim();
    const container = document.getElementById('products-list');

    if (query.length < 2) {
        loadProductsList();
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/products/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            const products = await response.json();

            if (products.length === 0) {
                container.innerHTML = '<div style="color: #555; text-align: center; padding: 20px;">Brak wyników</div>';
                return;
            }

            container.innerHTML = products.map(p => {
                const companyEsc = (p.company_name || '').replace(/'/g, "\\'");
                const productEsc = (p.product_name || '').replace(/'/g, "\\'");
                const rcsEsc = (p.rcs_id || '').replace(/'/g, "\\'");

                return `
                    <div style="background: #252525; padding: 10px; margin-bottom: 8px; border-radius: 6px; border-left: 3px solid var(--accent-orange); display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="font-weight: bold; color: #fff;">${p.company_name}</div>
                            <div style="color: #aaa; font-size: 0.9rem;">${p.product_name}</div>
                            <div style="color: #888; font-size: 0.8rem;">RCS: ${p.rcs_id}</div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button onclick="editProduct(${p.id}, '${companyEsc}', '${productEsc}', '${rcsEsc}')" 
                                class="btn" style="padding: 5px 10px; font-size: 0.8rem; background: #555;">
                                ✏️
                            </button>
                            <button onclick="deleteProduct(${p.id}, '${rcsEsc}')" 
                                class="btn" style="padding: 5px 10px; font-size: 0.8rem; background: var(--accent-red);">
                                ❌
                            </button>
                        </div>
                    </div>
                `}).join('');
        }
    } catch (err) {
        container.innerHTML = '<div style="color: var(--accent-red);">Błąd wyszukiwania</div>';
    }
};

// Edycja produktu
window.editProduct = function (id, company, product, rcs) {
    document.getElementById('edit-product-id').value = id;
    document.getElementById('edit-product-company').value = company;
    document.getElementById('edit-product-name').value = product;
    document.getElementById('edit-product-rcs').value = rcs;
    document.getElementById('edit-product-modal').classList.remove('hidden');
};

window.closeEditProductModal = function () {
    document.getElementById('edit-product-modal').classList.add('hidden');
};

window.saveProductChanges = async function () {
    const id = document.getElementById('edit-product-id').value;
    const company = document.getElementById('edit-product-company').value.trim();
    const product = document.getElementById('edit-product-name').value.trim();
    const rcs = document.getElementById('edit-product-rcs').value.trim();

    if (!company || !product || !rcs) {
        alert(t('all_fields_required'));
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/products/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                company_name: company,
                product_name: product,
                rcs_id: rcs
            })
        });

        const result = await response.json();

        if (result.success) {
            alert(t('product_updated'));
            closeEditProductModal();
            loadProductsList();
        } else {
            alert(t('error_general', result.error));
        }
    } catch (err) {
        alert(t('error_network'));
    }
};

// Usuwanie produktu
window.deleteProduct = async function (id, rcs) {
    if (!confirm(t('confirm_delete_product_text', rcs))) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/products/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            alert(t('product_deleted'));
            loadProductsList();
        } else {
            alert(t('error_general', result.error));
        }
    } catch (err) {
        alert(t('error_network'));
    }
};

// Import produktów
window.showImportModal = function (type) {
    currentImportType = type;
    const title = type === 'csv' ? t('btn_import_csv') : t('btn_import_excel');
    const accept = type === 'csv' ? '.csv' : '.xlsx,.xls';

    document.getElementById('import-modal-title').textContent = title;
    document.getElementById('import-file-input').setAttribute('accept', accept);
    document.getElementById('import-file-input').value = '';
    document.getElementById('import-progress').classList.add('hidden');
    document.getElementById('import-results').classList.add('hidden');
    document.getElementById('import-btn').disabled = false;

    document.getElementById('import-modal').classList.remove('hidden');
};

window.closeImportModal = function () {
    document.getElementById('import-modal').classList.add('hidden');
};

window.executeImport = async function () {
    const fileInput = document.getElementById('import-file-input');
    const file = fileInput.files[0];

    if (!file) {
        alert(t('choose_import_file'));
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const endpoint = currentImportType === 'csv' ? '/products/import-csv' : '/products/import-excel';

    // Pokaż progress
    document.getElementById('import-progress').classList.remove('hidden');
    document.getElementById('import-progress-bar').style.width = '50%';
    document.getElementById('import-status').textContent = t('importing_status');
    document.getElementById('import-btn').disabled = true;

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        document.getElementById('import-progress-bar').style.width = '100%';

        if (result.success) {
            const stats = result.stats;
                    document.getElementById('import-status').textContent = t('import_finished_status');

            // Pokaż wyniki
            let resultsHTML = `
                <div style="color: var(--accent-green); font-weight: bold; margin-bottom: 10px;">
                    ${t('import_success_msg')}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <div style="background: #1a1a1a; padding: 10px; border-radius: 4px;">
                        <div style="color: #888; font-size: 0.8rem;">${t('import_total')}</div>
                        <div style="color: #fff; font-size: 1.2rem; font-weight: bold;">${stats.total}</div>
                    </div>
                    <div style="background: #1a1a1a; padding: 10px; border-radius: 4px;">
                        <div style="color: #888; font-size: 0.8rem;">${t('import_added')}</div>
                        <div style="color: var(--accent-green); font-size: 1.2rem; font-weight: bold;">${stats.added}</div>
                    </div>
                    <div style="background: #1a1a1a; padding: 10px; border-radius: 4px;">
                        <div style="color: #888; font-size: 0.8rem;">${t('import_skipped')}</div>
                        <div style="color: var(--accent-orange); font-size: 1.2rem; font-weight: bold;">${stats.skipped}</div>
                    </div>
                    <div style="background: #1a1a1a; padding: 10px; border-radius: 4px;">
                        <div style="color: #888; font-size: 0.8rem;">${t('import_errors')}</div>
                        <div style="color: var(--accent-red); font-size: 1.2rem; font-weight: bold;">${stats.errors}</div>
                    </div>
                </div>
            `;

            if (result.error_details && result.error_details.length > 0) {
                resultsHTML += `<div style="color: #888; font-size: 0.9rem; margin-top: 10px;">${t('import_error_details')}</div>`;
                resultsHTML += '<div style="max-height: 150px; overflow-y: auto; margin-top: 5px;">';
                result.error_details.forEach(err => {
                    resultsHTML += `<div style="color: var(--accent-red); font-size: 0.85rem; padding: 3px 0;">
                        ${t('import_row_error', err.row, err.error)}
                    </div>`;
                });
                resultsHTML += '</div>';
            }

            document.getElementById('import-results').innerHTML = resultsHTML;
            document.getElementById('import-results').classList.remove('hidden');

            // Odśwież listę produktów
            loadProductsList();
        } else {
            document.getElementById('import-status').textContent = t('import_error_status');
            document.getElementById('import-results').innerHTML = `
                <div style="color: var(--accent-red);">
                    ❌ ${result.error}
                </div>
            `;
            document.getElementById('import-results').classList.remove('hidden');
        }
    } catch (err) {
        document.getElementById('import-status').textContent = t('error_general', 'Error');
        document.getElementById('import-results').innerHTML = `
            <div style="color: var(--accent-red);">
                ❌ Błąd połączenia z serwerem
            </div>
        `;
        document.getElementById('import-results').classList.remove('hidden');
    } finally {
        document.getElementById('import-btn').disabled = false;
    }
};

// Pobierz szablon CSV
window.downloadCSVTemplate = function () {
    const csv = 'company_name,product_name,rcs_id\nPROTEGA GLOBAL LTD,T22684 OXED (NEW FSC),RCS044563/C\nExample Company,Example Product,RCS000001';
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'products_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
};
