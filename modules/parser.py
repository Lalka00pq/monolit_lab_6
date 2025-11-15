import requests
from modules.config import parser_config
import os
from modules.pdf_processor import extract_text_from_pdf
from modules.openrouter_client import analyze_article, create_annotation, create_summary


def search_cyberleninka(search_query: str,
                        start_from: int = 0,
                        items_per_page: int = 10):
    """Отправляет POST-запрос к API и возвращает JSON-данные."""
    payload = {
        "from": start_from,
        "mode": "articles",
        "q": search_query,
        "size": items_per_page
    }

    print(f"Отправка запроса: {payload}")

    try:
        response = requests.post(
            parser_config.PARSE_URL, headers=parser_config.HEADERS, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None


def process_pdf_with_ai(pdf_path: str, title: str, folder_path: str):
    """
    Обрабатывает PDF файл с помощью AI: извлекает текст и создает анализ, аннотацию и пересказ.

    Args:
        pdf_path: Путь к PDF файлу
        title: Название статьи
        folder_path: Путь к папке для сохранения текстовых файлов
    """
    print(f"Начало обработки PDF: {pdf_path}")

    # Извлекаем текст из PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(
            f"Не удалось извлечь текст из {pdf_path}, пропускаем AI обработку")
        return

    print(f"Текст извлечен, длина: {len(text)} символов")

    # Базовое имя файла (без расширения)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Создаем анализ
    print("Создание анализа статьи...")
    analysis = analyze_article(text, title)
    if analysis:
        analysis_path = os.path.join(folder_path, f"{base_name}_анализ.txt")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            f.write(analysis)
        print(f"Анализ сохранен: {analysis_path}")
    else:
        print("Не удалось создать анализ")

    # Создаем аннотацию
    print("Создание аннотации...")
    annotation = create_annotation(text, title)
    if annotation:
        annotation_path = os.path.join(
            folder_path, f"{base_name}_аннотация.txt")
        with open(annotation_path, 'w', encoding='utf-8') as f:
            f.write(annotation)
        print(f"Аннотация сохранена: {annotation_path}")
    else:
        print("Не удалось создать аннотацию")

    # Создаем пересказ
    print("Создание пересказа...")
    summary = create_summary(text, title)
    if summary:
        summary_path = os.path.join(folder_path, f"{base_name}_пересказ.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Пересказ сохранен: {summary_path}")
    else:
        print("Не удалось создать пересказ")

    print(f"Обработка PDF завершена: {pdf_path}")


def download_data(data: dict):
    if data is None:
        return None
    for i, article in enumerate(data.get('articles', [])):
        title = article.get('name', 'N/A')
        annotation = article.get('annotation', 'N/A')
        link = article.get('link', 'N/A')

        title_clean = title.replace('<b>', '').replace('</b>', '')
        annotation_clean = annotation.replace(
            '<b>', '').replace('</b>', '')
        print(title_clean, annotation_clean, link)
        pdf_response = requests.get(
            f'{parser_config.SITE_URL}{link}/pdf', headers=parser_config.HEADERS)
        print('Запрос отправлен')
        if not os.path.exists(f"{parser_config.LOAD_DIR}/{i+1}"):
            os.makedirs(f"{parser_config.LOAD_DIR}/{i+1}")
        file = f"{parser_config.LOAD_DIR}/{i+1}/{title_clean}.pdf"
        pdf_response = requests.get(
            f'{parser_config.SITE_URL}{link}/pdf', headers=parser_config.HEADERS)
        with open(file, 'wb') as f:
            f.write(pdf_response.content)

        # Обрабатываем PDF с помощью AI
        folder_path = f"{parser_config.LOAD_DIR}/{i+1}"
        process_pdf_with_ai(file, title_clean, folder_path)

    return 'парсинг выполнен'
