import requests
from config import parser_config
import os


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
    return 'ok'


data = search_cyberleninka('python')
print(data)
result = download_data(data)
print(result)
