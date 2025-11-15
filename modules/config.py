from pydantic_settings import BaseSettings
from typing import Dict


class ParserConfig(BaseSettings):
    SITE_URL: str = 'https://cyberleninka.ru'
    PARSE_URL: str = 'https://cyberleninka.ru/api/search'
    HEADERS: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://cyberleninka.ru/',
        'Content-Type': 'application/json',
        'Accept': '*/*',
    }
    LOAD_DIR: str = './files'


parser_config = ParserConfig()
