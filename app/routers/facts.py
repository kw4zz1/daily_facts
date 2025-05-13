from fastapi import APIRouter, Request, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from .. import crud, auth, database, schemas

router = APIRouter(prefix="/facts", tags=["facts"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def facts_page(
    request: Request,
    category: Optional[str] = None,
    db: Session = Depends(database.SessionLocal),
):
    # Попытка получить текущего пользователя по cookie
    try:
        current_user = await auth.get_current_user(request=request, db=db)
    except HTTPException:
        return RedirectResponse(url="/users/login")

    # Берём случайный факт (по категории, если указана)
    fact = crud.get_random_fact(db, category)
    # Все доступные категории
    categories = crud.list_categories(db)
    # История сохранённых фактов пользователя
    history = crud.get_user_history(db, current_user.id)

    return templates.TemplateResponse("facts.html", {
        "request": request,
        "fact": fact,
        "categories": categories,
        "history": history
    })


@router.post("/save")
async def save_fact(
    request: Request,
    fact_id: int = Form(...),
    db: Session = Depends(database.SessionLocal),
):
    # Проверяем авторизацию
    try:
        current_user = await auth.get_current_user(request=request, db=db)
    except HTTPException:
        return RedirectResponse(url="/users/login")

    # Сохраняем факт в историю
    crud.save_user_fact(db, current_user.id, fact_id)
    return RedirectResponse(url="/facts/", status_code=303)
