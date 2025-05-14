from requests_html import AsyncHTMLSession
import random

CATEGORY_MAP = {
    "facts": "obshhie",
    "science": "nauka",
    "history": "istoriya",
    "animals": "zhivotnye",
    "psychology": "psihologiya"
}

BASE_URL = "https://www.factroom.ru/category/"


async def fetch_facts_from_category(slug: str) -> list[str]:
    url = f"{BASE_URL}{slug}"
    session = AsyncHTMLSession()
    print(f"[parse] Fetching: {url}")
    try:
        response = await session.get(url)
        # Убираем рендеринг JS, потому что он не нужен
        articles = response.html.find("article")
        print(f"[parse] Found {len(articles)} articles in category '{slug}'")
        facts = []
        for article in articles:
            title = article.find("h1", first=True)
            if title and title.text.strip():
                facts.append(title.text.strip())
        return facts
    except Exception as e:
        print(f"[ERROR] Cannot fetch category page: {e}")
        return []
    finally:
        await session.close()


async def parse_and_return_facts(category: str) -> list[str]:
    slug = CATEGORY_MAP.get(category, "obshhie")
    print(f"[parse] Slug: {category}, Human: {slug}")
    facts = await fetch_facts_from_category(slug)
    print(f"[parse] Parsed {len(facts)} facts")
    return facts


def get_random_fact(facts: list[str]) -> str:
    if not facts:
        return "Фактов нет"
    return random.choice(facts)
