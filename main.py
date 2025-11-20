# project
from modules.parser import download_data, search_cyberleninka
from schemas.schemas import SearchRequest
# 3rd party
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil

app = FastAPI(
    title="CyberLeninka Parser API",
    description="API для парсинга и скачивания статей с CyberLeninka.ru",
    version="1.0.0"
)

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")


@app.get("/", response_class=HTMLResponse, summary="Главная страница с UI")
async def read_root(request: Request):
    """Главная страница с интерфейсом для поиска статей."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/v1/files", summary="Получить список загруженных файлов")
async def get_files():
    """Возвращает информацию о всех загруженных файлах."""
    files_dir = Path("./files")
    files_info = []

    if files_dir.exists():
        for folder in sorted(files_dir.iterdir(), key=lambda x: int(x.name) if x.name.isdigit() else 0):
            if folder.is_dir():
                for file in folder.iterdir():
                    if file.is_file():
                        # Включаем PDF и текстовые файлы
                        if file.suffix in ['.pdf', '.txt']:
                            files_info.append({
                                "folder": folder.name,
                                "name": file.name,
                                "path": str(file.relative_to(files_dir)),
                                "size": file.stat().st_size,
                                "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                                "type": file.suffix
                            })

    return {"files": files_info, "total": len(files_info)}


@app.delete("/api/v1/files/clear", summary="Очистить содержимое подпапок в ./files (не удалять сами папки)")
async def clear_files():
    """Удаляет все файлы и вложенные директории внутри каждой подпапки в `./files`, но не удаляет сами подпапки."""
    files_dir = Path("./files")
    removed_items = 0

    if not files_dir.exists():
        return {"cleared": 0, "message": "Папка ./files не найдена"}

    for folder in files_dir.iterdir():
        if folder.is_dir():
            # Удаляем все содержимое внутри папки, но не саму папку
            for item in folder.iterdir():
                try:
                    if item.is_file() or item.is_symlink():
                        item.unlink()
                        removed_items += 1
                    elif item.is_dir():
                        # Удаляем рекурсивно вложенную директорию
                        shutil.rmtree(item)
                        removed_items += 1
                except Exception:
                    # Игнорируем отдельные ошибки удаления, продолжаем
                    continue

    return {"cleared": removed_items, "message": "Содержимое подпапок очищено (папки сохранены)."}


@app.get("/api/v1/health", summary="Проверка работоспособности")
def health_check():
    """Простой эндпоинт для проверки статуса сервера."""
    return {"status": "ok", "message": "Парсер API готов к работе. Используйте /parse/articles."}


@app.post("/parse/articles")
async def parse_articles(info: SearchRequest):
    data = search_cyberleninka(
        info.search_query, info.start_from, info.items_per_page)
    result = download_data(data)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
