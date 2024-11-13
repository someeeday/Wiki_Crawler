"""
Wikipedia Crawler

Утилита обходит страницы Википедии
Начинает с указанной статьи и так далее до глубины 6(значение по дефолту)
Каждая уникальная ссылка записывается в бд

Пример использования:
- python3 Crawler.py https://ru.wikipedia.org/wiki/Доксинг --depth 52

Параметры:
- start_url: URL начальной статьи
- --depth: глубина (по умолчанию 6)
"""

import sqlite3
import re
import urllib.request
from urllib.parse import quote, urlparse, urlunparse
from typing import Set
import argparse

class WikipediaCrawler:
    BASE_URL = "https://ru.wikipedia.org"

    def __init__(self, db_name: str = "wikipedia_links.db") -> None:
        """Создание экземпляра и настройка базы данных"""
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Создаёт базу данных SQLite"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY,
                    url TEXT UNIQUE
                )
            """)
            conn.commit()

    def fetch_page(self, url: str) -> str:
        """Загружает HTML содержимое страницы по URL"""
        try:
            parsed_url = urlparse(url)
            encoded_path = quote(parsed_url.path)
            encoded_url = urlunparse(parsed_url._replace(path=encoded_path))
            
            with urllib.request.urlopen(encoded_url) as response:
                if response.status == 404:
                    return ""
                return response.read().decode('utf-8')
        except Exception:
            return ""

    def extract_links(self, html: str) -> Set[str]:
        """Находит и извлекает ссылки на статьи"""
        links = set()
        for match in re.findall(r'href="/wiki/([^":#]+)"', html):
            full_url = f"{self.BASE_URL}/wiki/{match}"
            links.add(full_url)
        return links

    def save_links(self, links: Set[str]) -> None:
        """Сохраняет уникальные ссылки в базе данных"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT OR IGNORE INTO links (url) VALUES (?)", 
                [(link,) for link in links]
            )
            conn.commit()

    def crawl(self, start_url: str, max_depth: int = 6) -> None:
        """Запускает процесс обхода ссылок"""
        to_visit = {start_url}
        visited = set()
        current_depth = 0

        while to_visit and current_depth < max_depth:
            next_to_visit = set()
            for url in to_visit:
                if url in visited:
                    continue

                print(f"Crawling: {url} (Depth {current_depth})")
                html = self.fetch_page(url)
                if html:
                    links = self.extract_links(html)
                    self.save_links(links)
                    visited.add(url)
                    next_to_visit.update(links - visited)

            to_visit = next_to_visit
            current_depth += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Wikipedia articles and save links.")
    parser.add_argument("start_url", type=str, help="The starting Wikipedia article URL")
    parser.add_argument("--depth", type=int, default=6, help="Depth of crawling (default: 6)")

    args = parser.parse_args()
    crawler = WikipediaCrawler()
    crawler.crawl(start_url=args.start_url, max_depth=args.depth)
