from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import random

from .. import crud, auth, database, schemas
from ..factroom_parser import parse_and_return_facts, CATEGORY_MAP

router = APIRouter(prefix="/facts", tags=["facts"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def facts_page(
    request: Request,
    category: Optional[str] = None,
    db: Session = Depends(database.get_db),
):
    # Аутентификация
    try:
        current_user = await auth.get_current_user(request=request, db=db)
    except HTTPException:
        return RedirectResponse(url="/users/login")

    fact = None

    if category:
        category = category.lower()

        # Проверка — действительно ли это валидная категория
        if category not in CATEGORY_MAP:
            return templates.TemplateResponse("facts.html", {
                "request": request,
                "fact": None,
                "categories": crud.list_categories(db),
                "history": crud.get_user_history(db, current_user.id)
            })

        # 🟢 Асинхронный вызов парсера
        remote_facts = await parse_and_return_facts(category)

        if remote_facts:
            chosen_text = random.choice(remote_facts)
            chosen = {
                "title": chosen_text.split(".")[0],
                "text": chosen_text,
                "category": category
            }

            # сохраняем факт в базу
            try:
                crud.create_fact(db, schemas.FactCreate(
                    title=chosen["title"],
                    text=chosen["text"],
                    category=chosen["category"]
                ))
            except Exception:
                pass

            # подготавливаем для шаблона
            fact = schemas.FactOut(
                id=0,  # временный id, потому что он не из БД
                title=chosen["title"],
                text=chosen["text"],
                category=chosen["category"]
            )
    else:
        # Без категории — выбираем случайный из БД
        db_fact = crud.get_random_fact(db)
        fact = schemas.FactOut.from_orm(db_fact) if db_fact else None

    return templates.TemplateResponse("facts.html", {
        "request": request,
        "fact": fact,
        "categories": crud.list_categories(db),
        "history": crud.get_user_history(db, current_user.id)
    })
