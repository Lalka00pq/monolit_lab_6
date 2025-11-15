import requests
from time import sleep
from config import parser_config


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


search_term = "хор"
items_per_page = 10
max_pages = 2
all_articles = []

for page in range(max_pages):
    start_index = page * items_per_page  # 0, 10, 20 и т.д.

    # 1. Получение данных
    data = search_cyberleninka(search_term, start_index, items_per_page)

    if data and 'articles' in data:
        articles = data['articles']
        total_found = data.get('found', 0)

        if not articles:
            print("Больше нет результатов.")
            break

        all_articles.extend(articles)
        print(
            f"✅ Страница {page + 1}: Найдено {len(articles)} статей. Всего найдено: {total_found}")

        # 2. Обработка и очистка данных
        for article in articles:
            title = article.get('name', 'N/A')
            annotation = article.get('annotation', 'N/A')
            link = article.get('link', 'N/A')

            title_clean = title.replace('<b>', '').replace('</b>', '')
            annotation_clean = annotation.replace(
                '<b>', '').replace('</b>', '')

        sleep(2)
    else:
        print("Ошибка при получении данных или пустой ответ, прекращение парсинга.")
        break

print(f"\n--- Парсинг завершен ---")
print(f"Всего собрано статей по запросу '{search_term}': {len(all_articles)}")
for article in all_articles:
    print(f"    Название: {article['name'][:80]}...")
