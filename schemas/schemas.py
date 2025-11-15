from pydantic import BaseModel
from typing import List, Optional


class SearchRequest(BaseModel):
    search_query: str
    start_from: int = 0
    items_per_page: int = 12


class ArticleResult(BaseModel):
    title: str
    pdf_link: str
    download_status: str
    download_path: Optional[str] = None


class SearchResponse(BaseModel):
    message: str
    results: List[ArticleResult]
