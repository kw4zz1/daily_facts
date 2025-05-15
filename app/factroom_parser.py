# app/factroom_parser.py

import requests
import html
from bs4 import BeautifulSoup
import random

BASE = "https://www.factroom.ru"
API = BASE + "/wp-json/wp/v2"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
}

# Сопоставление внутренних slug → человекочитаемое имя
CATEGORY_SLUGS = {
    "facts":       "fakty",
    "science":     "nauka",
    "history":     "istoriya",
    "animals":     "zhivotnye",
    "psychology":  "psihologiya",
}
CATEGORY_NAMES = {
    "fakty":       "Общие",
    "nauka":       "Наука",
    "istoriya":    "История",
    "zhivotnye":   "Животные",
    "psihologiya":"Психология",
}


def _get_category_id(real_slug: str) -> int | None:
    """Запрашивает /categories?slug={real_slug}, возвращает первый id или None."""
    url = f"{API}/categories"
    params = {"slug": real_slug}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=5)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]["id"]
    except Exception as e:
        print(f"[parser] Не смогли получить ID категории '{real_slug}': {e}")
    return None


def parse_and_return_facts(slug: str) -> list[dict[str,str]]:
    """
    Для переданного user-slug (facts/science/…) возвращает список:
      {"title": ..., "text": ..., "category": ...}
    путем запроса к /wp-json/wp/v2/posts?categories={id}.
    """
    real_slug = CATEGORY_SLUGS.get(slug, slug)
    cat_id = _get_category_id(real_slug)
    if not cat_id:
        return []

    url = f"{API}/posts"
    params = {
        "categories": cat_id,
        "per_page":   20,   # сколько фактов выкачать
        "_fields":    "id,title.rendered,excerpt.rendered",
    }

    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=5)
        r.raise_for_status()
    except Exception as e:
        print(f"[parser] Ошибка при запросе постов для '{slug}': {e}")
        return []

    out = []
    for post in r.json():
        # title.rendered — заголовок поста
        raw_title = html.unescape(post["title"]["rendered"])
        # excerpt.rendered — HTML-фрагмент; парсим из него чистый текст
        ex_html = post["excerpt"]["rendered"]
        text = (
            BeautifulSoup(ex_html, "html.parser")
            .get_text(separator=" ", strip=True)
        )
        if len(text) < 20:
            continue

        out.append({
            "title": raw_title,
            "text":  text,
            "category": CATEGORY_NAMES.get(real_slug, real_slug.capitalize())
        })

    print(f"[parser] Получили {len(out)} фактов из категории '{slug}'")
    return out


def get_random_fact(facts: list[dict[str,str]]) -> dict[str,str] | None:
    """Выбирает наугад один факт из списка."""
    if not facts:
        return None
    return random.choice(facts)
