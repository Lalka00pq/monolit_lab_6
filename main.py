# main.py

from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from typing import List, Dict, Any
# Импортируем нашу логику парсинга
from modules.parser import download_data, search_cyberleninka

app = FastAPI(
    title="CyberLeninka Parser API",
    description="API для парсинга и скачивания статей с CyberLeninka.ru",
    version="1.0.0"
)


class SearchRequest(BaseModel):
    query: str
    limit: int = 12  # По умолчанию 12 статей


class ArticleResult(BaseModel):
    title: str
    pdf_link: str
    download_status: str
    download_path: Optional[str] = None


class SearchResponse(BaseModel):
    message: str
    results: List[ArticleResult]


@app.get("/", summary="Проверка работоспособности")
def read_root():
    """Простой эндпоинт для проверки статуса сервера."""
    return {"status": "ok", "message": "Парсер API готов к работе. Используйте /parse/articles."}


@app.post(
    "/parse/articles",
    response_model=SearchResponse,
    summary="Запустить парсинг и скачивание статей"
)
async def parse_and_download_articles(request: SearchRequest):
    """
    Парсит первые LIMIT статей по заданному запросу с CyberLeninka, 
    скачивает их PDF-версии в папку 'files/' и возвращает список результатов.
    """

    if request.limit > 20:
        raise HTTPException(
            status_code=400, detail="Лимит статей не может превышать 20 за один запрос.")

    # Вызываем синхронную функцию парсинга
    download_results = fetch_articles_and_download(
        request.query, request.limit)

    if isinstance(download_results, dict) and download_results.get("error"):
        raise HTTPException(status_code=500, detail=download_results["error"])

    # Форматируем ответ в соответствии со схемой Pydantic
    return SearchResponse(
        message=f"Парсинг и скачивание по запросу '{request.query}' завершены.",
        results=download_results
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
