#Wikipedia Crawler

Утилита обходит страницы Википедии
Начинает с указанной статьи и так далее до глубины 6(значение по дефолту)
Каждая уникальная ссылка записывается в бд

Пример использования:
- python3 Crawler.py https://ru.wikipedia.org/wiki/Доксинг --depth 52

Параметры:
- start_url: URL начальной статьи
- --depth: глубина (по умолчанию 6)
