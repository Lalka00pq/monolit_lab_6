import shutil
import pdfplumber
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# Импортируем твои модули (убедись, что они существуют)
from schemas.schemas import SearchRequest 
from modules.parser import download_data, search_cyberleninka

app = FastAPI(title="CyberLeninka Parser Pro")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")

FILES_DIR = Path("./files")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# === 1. ПОЛУЧЕНИЕ СПИСКА ПАПОК (БИБЛИОТЕКИ) ===
@app.get("/api/v1/library")
async def get_library():
    """Сканирует папки 1, 2, 3... и проверяет статус (PDF + TXT)"""
    if not FILES_DIR.exists():
        return {"data": []}

    # Сортируем папки как числа
    folders = sorted(
        [d for d in FILES_DIR.iterdir() if d.is_dir() and d.name.isdigit()],
        key=lambda x: int(x.name)
    )

    library_data = []
    for folder in folders:
        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            continue
        
        pdf_file = pdf_files[0]
        base_name = pdf_file.stem
        
        # Проверка наличия TXT файлов
        path_article = folder / f"{base_name}_article.txt"
        path_annotation = folder / f"{base_name}_annotation.txt"
        path_summary = folder / f"{base_name}_summary.txt"
        
        has_txt = path_article.exists() and path_annotation.exists() and path_summary.exists()

        # Читаем превью, если файлы есть
        previews = {}
        if has_txt:
            previews = {
                "article": read_head(path_article, 3000),
                "annotation": read_head(path_annotation, 1000),
                "summary": read_head(path_summary, 1500)
            }

        library_data.append({
            "folder_id": folder.name,
            "filename": pdf_file.name,
            "size_mb": round(pdf_file.stat().st_size / (1024 * 1024), 2),
            "has_txt": has_txt,
            "previews": previews
        })

    return {"data": library_data}

# === 2. ГЕНЕРАЦИЯ TXT (ПАРСИНГ PDF) ===
@app.post("/api/v1/parse_local/{folder_id}")
async def parse_local_pdf(folder_id: str):
    folder_path = FILES_DIR / folder_id
    if not folder_path.exists():
        raise HTTPException(404, "Папка не найдена")

    pdf_files = list(folder_path.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(404, "PDF не найден")
    
    pdf_file = pdf_files[0]
    base_name = pdf_file.stem
    
    # Извлекаем текст
    full_text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text: full_text += text + "\n"
    except Exception as e:
        raise HTTPException(500, f"Ошибка PDF: {e}")

    if not full_text:
        raise HTTPException(400, "Не удалось извлечь текст (возможно скан)")

    # --- Эвристика разделения ---
    import re
    # Ищем аннотацию
    anno_match = re.search(r'(Аннотация|Abstract|Annotation)[:\.]?\s*(.*?)(Ключевые слова|Keywords|Введение|Introduction)', full_text, re.DOTALL | re.IGNORECASE)
    annotation_text = anno_match.group(2).strip() if anno_match else "Аннотация не найдена автоматически."
    
    # Делаем псевдо-пересказ (каждое 15-е предложение)
    sentences = full_text.replace('\n', ' ').split('. ')
    summary_text = ". ".join([s for i, s in enumerate(sentences) if i % 15 == 0])

    # Сохраняем
    try:
        (folder_path / f"{base_name}_article.txt").write_text(full_text, encoding="utf-8")
        (folder_path / f"{base_name}_annotation.txt").write_text(annotation_text, encoding="utf-8")
        (folder_path / f"{base_name}_summary.txt").write_text(summary_text, encoding="utf-8")
    except Exception as e:
        raise HTTPException(500, f"Ошибка записи: {e}")

    return {"status": "ok"}

# === 3. ПОИСК И СКАЧИВАНИЕ (Твой старый функционал) ===
@app.post("/parse/articles")
async def parse_articles(info: SearchRequest):
    data = search_cyberleninka(info.search_query, info.start_from, info.items_per_page)
    result = download_data(data)
    return result

@app.delete("/api/v1/files/clear")
async def clear_files():
    """Удаляет всё из папки files"""
    removed = 0
    if FILES_DIR.exists():
        for item in FILES_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
                removed += 1
            else:
                item.unlink()
                removed += 1
    return {"cleared": removed}

def read_head(path, limit):
    try:
        text = path.read_text(encoding="utf-8")
        return text[:limit] + ("..." if len(text) > limit else "")
    except: return "Ошибка чтения"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)