from requests import Session
import random
import time
from bs4 import BeautifulSoup

CATEGORY_MAP = {
    "facts": "obshhie",
    "science": "nauka",
    "history": "istoriya",
    "animals": "zhivotnye",
    "psychology": "psihologiya"
}

BASE_URL = "https://www.factroom.ru/category/"


async def fetch_facts_from_category(slug: str) -> list[str]:
    """
    Получает список фактов из указанной категории с помощью обычного HTTP-запроса
    без рендеринга JavaScript
    """
    url = f"{BASE_URL}{slug}"
    session = Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    })

    print(f"[parse] Fetching: {url}")
    facts = []

    try:
        # Добавляем задержку, чтобы не нагружать сервер
        time.sleep(1)

        response = session.get(url, timeout=10)
        response.raise_for_status()  # Проверка на успешный статус

        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем статьи/факты разными способами
        articles = soup.select("div.post-card") or soup.select("article") or soup.select("div.post")
        print(f"[parse] Found {len(articles)} articles in category '{slug}'")

        # Если стандартный поиск не дал результатов, ищем блоки с контентом
        if not articles:
            articles = soup.select("div.content-area article") or soup.select("div.content article")
            print(f"[parse] Found {len(articles)} articles using fallback selectors")

        for article in articles:
            # Ищем заголовок
            title = None
            for heading in ['h2', 'h3', 'h1']:
                title_elem = article.select_one(heading)
                if title_elem:
                    title = title_elem
                    break

            # Если заголовка нет, ищем первый параграф
            if not title:
                content_div = article.select_one("div.post-content, div.content")
                if content_div:
                    title = content_div.select_one("p")

            # Если нашли текст, добавляем его в список фактов
            if title and title.text.strip():
                fact_text = title.text.strip()
                if len(fact_text) > 10:  # Минимальная длина для факта
                    facts.append(fact_text)

        # Если по-прежнему нет фактов, ищем параграфы
        if not facts:
            paragraphs = soup.select("div.post-content p, div.content p")
            for p in paragraphs:
                if p.text.strip() and len(p.text.strip()) > 20:
                    facts.append(p.text.strip())

        return facts
    except Exception as e:
        print(f"[ERROR] Cannot fetch category page: {e}")
        return []
    finally:
        session.close()


async def parse_and_return_facts(category: str) -> list[str]:
    """
    Получает факты для указанной категории и пробует загрузить
    с нескольких страниц, если это необходимо
    """
    slug = CATEGORY_MAP.get(category, "obshhie")
    print(f"[parse] Slug: {category}, Human: {slug}")

    # Получаем факты с первой страницы
    facts = await fetch_facts_from_category(slug)
    print(f"[parse] Parsed {len(facts)} facts")

    # Если фактов мало или их нет, пробуем вторую страницу
    if len(facts) < 3:
        second_page_facts = await fetch_facts_from_page(slug, 2)
        facts.extend(second_page_facts)
        print(f"[parse] Added {len(second_page_facts)} facts from second page")

    return facts


async def fetch_facts_from_page(slug: str, page: int) -> list[str]:
    """Получает факты с конкретной страницы категории"""
    url = f"{BASE_URL}{slug}/page/{page}"
    session = Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    })

    print(f"[parse] Fetching page {page}: {url}")
    facts = []

    try:
        # Добавляем задержку
        time.sleep(1)

        response = session.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.select("div.post-card") or soup.select("article") or soup.select("div.post")

        if not articles:
            articles = soup.select("div.content-area article") or soup.select("div.content article")

        for article in articles:
            title = None
            for heading in ['h2', 'h3', 'h1']:
                title_elem = article.select_one(heading)
                if title_elem:
                    title = title_elem
                    break

            if not title:
                content_div = article.select_one("div.post-content, div.content")
                if content_div:
                    title = content_div.select_one("p")

            if title and title.text.strip():
                fact_text = title.text.strip()
                if len(fact_text) > 10:
                    facts.append(fact_text)

        return facts
    except Exception as e:
        print(f"[ERROR] Cannot fetch page {page}: {e}")
        return []
    finally:
        session.close()


def get_random_fact(facts: list[str]) -> str:
    """Возвращает случайный факт из списка или сообщение об отсутствии фактов"""
    if not facts:
        return "Фактов нет"
    return random.choice(facts)