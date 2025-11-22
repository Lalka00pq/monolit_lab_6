// JS ОСТАВЛЕН БЕЗ ИЗМЕНЕНИЙ
const searchBtn = document.getElementById('searchBtn');
const searchInput = document.getElementById('searchInput');
const refreshBtn = document.getElementById('refreshBtn');
const clearBtn = document.getElementById('clearBtn');
const filesList = document.getElementById('filesList');
const statusMessage = document.getElementById('statusMessage');

// Modal elements
const modal = document.getElementById('analysisModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const textArticle = document.getElementById('textArticle');
const textAnnotation = document.getElementById('textAnnotation');
const textSummary = document.getElementById('textSummary');

// === INIT ===
document.addEventListener('DOMContentLoaded', loadFiles);

refreshBtn.addEventListener('click', loadFiles);
searchBtn.addEventListener('click', handleSearch);

closeModalBtn.addEventListener('click', () => modal.style.display = 'none');
modal.addEventListener('click', (e) => { if(e.target === modal) modal.style.display = 'none'; });

if(clearBtn) {
    clearBtn.addEventListener('click', async () => {
        if(confirm('Удалить все файлы?')) {
            await fetch('/api/v1/files/clear', {method: 'DELETE'});
            loadFiles();
        }
    });
}

// === LOAD LIBRARY ===
async function loadFiles() {
    filesList.innerHTML = '<div class="empty-placeholder"><p>Загрузка...</p></div>';
    try {
        const res = await fetch('/api/v1/library');
        const json = await res.json();
        renderGrid(json.data);
    } catch (e) {
        filesList.innerHTML = `<p style="color:red; text-align:center">Ошибка: ${e.message}</p>`;
    }
}

function renderGrid(items) {
    if(!items || items.length === 0) {
        filesList.innerHTML = `
            <div class="empty-placeholder">
                <div class="placeholder-img">📂</div>
                <p>Библиотека пуста</p>
                <span>Используйте поиск слева для загрузки статей</span>
            </div>`;
        return;
    }

    filesList.innerHTML = '';
    
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'file-card';
        
        // Логика кнопок: Если есть TXT -> "Читать", иначе -> "Спарсить"
        let actionBtn = '';
        if (item.has_txt) {
            // Передаем данные в кнопку через data-attr
            // (храним превью прямо в атрибуте для простоты, или можно в глобальном объекте)
            actionBtn = `<button class="btn-card primary btn-read">📖 Читать анализ</button>`;
        } else {
            actionBtn = `<button class="btn-card success btn-parse" data-folder="${item.folder_id}">⚙️ Извлечь текст</button>`;
        }

        card.innerHTML = `
            <div class="card-top">
                <div class="card-icon">📄</div>
                <div class="card-info">
                    <div class="card-folder">FOLDER #${item.folder_id}</div>
                    <div class="card-name" title="${item.filename}">${item.filename}</div>
                </div>
            </div>
            <div class="card-actions">
                ${actionBtn}
            </div>
        `;

        // Привязка событий
        if(item.has_txt) {
            card.querySelector('.btn-read').addEventListener('click', () => openModal(item));
        } else {
            card.querySelector('.btn-parse').addEventListener('click', (e) => handleParse(item.folder_id, e.target));
        }

        filesList.appendChild(card);
    });
}

// === SEARCH & DOWNLOAD ===
async function handleSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    const btn = searchBtn;
    const originalText = btn.querySelector('.btn-text').innerText;
    
    btn.disabled = true;
    btn.querySelector('.btn-text').innerText = "Загрузка...";
    btn.querySelector('.btn-loader').style.display = "inline-block";

    try {
        const res = await fetch('/parse/articles', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                search_query: query,
                start_from: parseInt(document.getElementById('startFrom').value) || 0,
                items_per_page: parseInt(document.getElementById('itemsPerPage').value) || 5
            })
        });
        
        if(res.ok) {
            showMessage("Статьи загружены!", "success");
            loadFiles(); // Обновляем список
        } else {
            showMessage("Ошибка при поиске", "error");
        }
    } catch(e) {
        showMessage("Ошибка сети: " + e.message, "error");
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').innerText = originalText;
        btn.querySelector('.btn-loader').style.display = "none";
    }
}

// === LOCAL PARSING ===
async function handleParse(folderId, btnElement) {
    const originalText = btnElement.innerText;
    btnElement.innerText = "⏳...";
    btnElement.disabled = true;

    try {
        const res = await fetch(`/api/v1/parse_local/${folderId}`, { method: 'POST' });
        if(!res.ok) throw new Error("Ошибка");
        
        // Успех -> обновляем список, чтобы кнопка стала "Читать"
        loadFiles();
        showMessage(`Папка ${folderId} обработана`, "success");
    } catch (e) {
        alert("Ошибка парсинга: " + e.message);
        btnElement.innerText = originalText;
        btnElement.disabled = false;
    }
}

// === MODAL VIEW ===
function openModal(item) {
    document.getElementById('modalTitle').innerText = item.filename;
    textArticle.innerText = item.previews.article;
    textAnnotation.innerText = item.previews.annotation;
    textSummary.innerText = item.previews.summary;
    
    modal.style.display = 'flex';
}

function showMessage(msg, type) {
    statusMessage.innerText = msg;
    statusMessage.className = `status-pill ${type}`;
    statusMessage.style.display = 'block';
    setTimeout(() => statusMessage.style.display = 'none', 4000);
}