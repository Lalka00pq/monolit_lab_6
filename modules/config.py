from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict


class ParserConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    SITE_URL: str = 'https://cyberleninka.ru'
    PARSE_URL: str = 'https://cyberleninka.ru/api/search'
    HEADERS: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://cyberleninka.ru/',
        'Content-Type': 'application/json',
        'Accept': '*/*',
    }
    LOAD_DIR: str = './files'
    OPENROUTER_API_KEY: str = ''
    OPENROUTER_MODEL: str = ''  # 'openai/gpt-4o-mini'
    OPENROUTER_BASE_URL: str = ''  # 'https://openrouter.ai/api/v1'


parser_config = ParserConfig()
