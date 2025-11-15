import requests
from modules.config import parser_config
from typing import Optional


def call_openrouter(prompt: str, system_prompt: str = "") -> Optional[str]:
    """
    Вызывает OpenRouter API для генерации текста.
    
    Args:
        prompt: Пользовательский запрос
        system_prompt: Системный промпт (опционально)
    
    Returns:
        Сгенерированный текст или None в случае ошибки
    """
    if not parser_config.OPENROUTER_API_KEY:
        print("Предупреждение: OPENROUTER_API_KEY не установлен")
        return None
    
    url = f"{parser_config.OPENROUTER_BASE_URL}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {parser_config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",  # Опционально
        "X-Title": "CyberLeninka Parser"  # Опционально
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": parser_config.OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Неожиданный формат ответа от OpenRouter: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к OpenRouter: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при работе с OpenRouter: {e}")
        return None


def analyze_article(text: str, title: str) -> Optional[str]:
    """
    Анализирует статью и создает подробный анализ.
    
    Args:
        text: Текст статьи
        title: Название статьи
    
    Returns:
        Анализ статьи или None в случае ошибки
    """
    system_prompt = "Ты - эксперт по анализу научных статей. Твоя задача - провести детальный анализ статьи."
    
    # Ограничиваем размер для экономии токенов
    text_limited = text[:8000] if len(text) > 8000 else text
    
    prompt = f"""Проведи детальный анализ следующей научной статьи:

Название: {title}

Текст статьи:
{text_limited}

Создай подробный анализ статьи, включающий:
1. Основные тезисы и идеи
2. Методологию исследования
3. Ключевые выводы
4. Научную ценность работы
5. Возможные области применения

Анализ должен быть структурированным и информативным."""
    
    return call_openrouter(prompt, system_prompt)


def create_annotation(text: str, title: str) -> Optional[str]:
    """
    Создает аннотацию статьи.
    
    Args:
        text: Текст статьи
        title: Название статьи
    
    Returns:
        Аннотация статьи или None в случае ошибки
    """
    system_prompt = "Ты - эксперт по созданию аннотаций научных статей. Создавай краткие, но информативные аннотации."
    
    # Ограничиваем размер для экономии токенов
    text_limited = text[:8000] if len(text) > 8000 else text
    
    prompt = f"""Создай аннотацию для следующей научной статьи:

Название: {title}

Текст статьи:
{text_limited}

Аннотация должна включать:
- Краткое описание темы и цели исследования
- Основные методы
- Ключевые результаты
- Выводы

Объем: 150-250 слов."""
    
    return call_openrouter(prompt, system_prompt)


def create_summary(text: str, title: str) -> Optional[str]:
    """
    Создает краткий пересказ статьи.
    
    Args:
        text: Текст статьи
        title: Название статьи
    
    Returns:
        Краткий пересказ или None в случае ошибки
    """
    system_prompt = "Ты - эксперт по созданию кратких пересказов научных статей. Создавай понятные и структурированные пересказы."
    
    # Ограничиваем размер для экономии токенов
    text_limited = text[:8000] if len(text) > 8000 else text
    
    prompt = f"""Создай краткий пересказ следующей научной статьи:

Название: {title}

Текст статьи:
{text_limited}

Создай краткий пересказ, который включает:
- Основную идею статьи
- Ключевые моменты и аргументы
- Главные выводы

Пересказ должен быть понятным даже для неспециалистов. Объем: 200-300 слов."""
    
    return call_openrouter(prompt, system_prompt)

