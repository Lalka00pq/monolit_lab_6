// Элементы DOM
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const startFromInput = document.getElementById('startFrom');
const itemsPerPageInput = document.getElementById('itemsPerPage');
const statusMessage = document.getElementById('statusMessage');
const filesList = document.getElementById('filesList');
const refreshBtn = document.getElementById('refreshBtn');
const clearBtn = document.getElementById('clearBtn');

// Загрузка списка файлов при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
});

// Обработчик поиска
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

// Обработчик обновления списка файлов
refreshBtn.addEventListener('click', loadFiles);
// Обработчик очистки содержимого папок
if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
        const ok = confirm('Вы уверены? Это удалит все файлы внутри подпапок в `files/`, но сами папки останутся.');
        if (!ok) return;
        showMessage('Выполняется очистка папок...', 'info');
        try {
            const resp = await fetch('/api/v1/files/clear', { method: 'DELETE' });
            if (!resp.ok) throw new Error('HTTP status ' + resp.status);
            const data = await resp.json();
            showMessage(`Очистка завершена: ${data.cleared} элементов удалено.`, 'success');
            setTimeout(() => loadFiles(), 800);
        } catch (err) {
            console.error('Ошибка очистки папок:', err);
            showMessage('Ошибка при очистке: ' + err.message, 'error');
        }
    });
}

// Функция обработки поиска
async function handleSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        showMessage('Пожалуйста, введите запрос для поиска', 'error');
        return;
    }
    
    // Блокируем кнопку и показываем загрузку
    setLoading(true);
    showMessage('Поиск и загрузка статей...', 'info');
    
    try {
        const response = await fetch('/parse/articles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search_query: query,
                start_from: parseInt(startFromInput.value) || 0,
                items_per_page: parseInt(itemsPerPageInput.value) || 12
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.text();
        
        showMessage('Статьи успешно загружены!', 'success');
        
        // Обновляем список файлов после загрузки
        setTimeout(() => {
            loadFiles();
        }, 1000);
        
    } catch (error) {
        console.error('Ошибка при поиске:', error);
        showMessage('Произошла ошибка при загрузке статей: ' + error.message, 'error');
    } finally {
        setLoading(false);
    }
}

// Функция загрузки списка файлов
async function loadFiles() {
    filesList.innerHTML = '<div class="loading-placeholder">Загрузка списка файлов...</div>';
    
    try {
        const response = await fetch('/api/v1/files');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.files && data.files.length > 0) {
            displayFiles(data.files);
        } else {
            filesList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📄</div>
                    <p>Нет загруженных файлов</p>
                    <p style="margin-top: 8px; font-size: 0.9rem;">Выполните поиск, чтобы загрузить статьи</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Ошибка при загрузке файлов:', error);
        filesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <p>Ошибка при загрузке списка файлов</p>
                <p style="margin-top: 8px; font-size: 0.9rem;">${error.message}</p>
            </div>
        `;
    }
}

// Функция отображения файлов
function displayFiles(files) {
    filesList.innerHTML = files.map(file => `
        <div class="file-card">
            <div class="file-card-header">
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <div class="file-name" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</div>
                    <div class="file-folder">Папка: ${file.folder}</div>
                </div>
            </div>
            <div class="file-meta">
                <span class="file-size">${file.size_mb} MB</span>
                <span class="file-path">${file.path}</span>
            </div>
        </div>
    `).join('');
}

// Функция показа сообщения
function showMessage(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
    
    // Автоматически скрываем сообщение через 5 секунд (кроме ошибок)
    if (type !== 'error') {
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 5000);
    }
}

// Функция установки состояния загрузки
function setLoading(loading) {
    searchBtn.disabled = loading;
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoader = searchBtn.querySelector('.btn-loader');
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Функция экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

