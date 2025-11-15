from PyPDF2 import PdfReader
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Извлекает текст из PDF файла.
    
    Args:
        pdf_path: Путь к PDF файлу
    
    Returns:
        Извлеченный текст или None в случае ошибки
    """
    try:
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            print(f"Файл не найден: {pdf_path}")
            return None
        
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)
            except Exception as e:
                print(f"Ошибка при извлечении текста со страницы {page_num}: {e}")
                continue
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            print(f"Не удалось извлечь текст из PDF: {pdf_path}")
            return None
        
        return full_text
        
    except Exception as e:
        print(f"Ошибка при обработке PDF файла {pdf_path}: {e}")
        return None

