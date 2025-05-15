# app/routers/facts.py

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import random

from .. import crud, auth, database, schemas
from ..factroom_parser import parse_and_return_facts, CATEGORY_SLUGS, CATEGORY_NAMES

router = APIRouter(prefix="/facts", tags=["facts"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def facts_page(
    request: Request,
    category: Optional[str] = None,
    db: Session = Depends(database.get_db),
):
    # 1) Аутентификация
    try:
        current_user = await auth.get_current_user(request=request, db=db)
    except HTTPException:
        return RedirectResponse("/users/login")

    # 2) Список доступных slug’ов
    slugs = list(CATEGORY_SLUGS.keys())

    # 3) Попытка получить факт
    fact: Optional[schemas.FactOut] = None
    if category:
        slug = category.lower()
        if slug in slugs:
            # 3.1) Сначала онлайн-парсинг через WP-API
            remote = parse_and_return_facts(slug)
            if remote:
                data = random.choice(remote)
                fact = schemas.FactOut(
                    id=0,
                    title = data["title"],
                    text = data["text"],
                    category = data["category"],
                )
                # Сохраняем в локальную БД (игнорируем дубли)
                try:
                    crud.create_fact(
                        db,
                        schemas.FactCreate(
                            title=data["title"],
                            text=data["text"],
                            category=data["category"],
                        ),
                    )
                except Exception:
                    pass
            else:
                # 3.2) Если онлайн не вернул — берём из БД по category
                dbf = crud.get_random_fact(db, CATEGORY_SLUGS[slug])
                if dbf:
                    fact = schemas.FactOut.from_orm(dbf)
    else:
        # 4) Без category — случайный факт из всей БД
        dbf = crud.get_random_fact(db, None)
        if dbf:
            fact = schemas.FactOut.from_orm(dbf)

    # 5) История сохранённых фактов текущего пользователя
    history = crud.get_user_history(db, current_user.id)

    # 6) Рендерим шаблон
    return templates.TemplateResponse(
        "facts.html",
        {
            "request": request,
            "fact": fact,
            "categories": slugs,
            "current_category": category,
            "history": history,
            "CATEGORY_SLUGS": CATEGORY_SLUGS,  # ← добавь
            "CATEGORY_NAMES": CATEGORY_NAMES  # ← добавь
        },
    )

