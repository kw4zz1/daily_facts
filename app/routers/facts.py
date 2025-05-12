from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import crud, auth, database, schemas

router = APIRouter(prefix="/facts", tags=["facts"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def facts_page(
    request: Request,
    category: str = None,
    db: Session = Depends(database.SessionLocal)
):
    # Проверяем авторизацию
    try:
        current_user = await auth.get_current_user(request=request, db=db)
    except HTTPException:
        # Если пользователь не авторизован, перенаправляем на страницу входа
        return RedirectResponse(url="/users/login")

    fact = crud.get_random_fact(db, category)
    categories = crud.list_categories(db)
    history = crud.get_user_history(db, current_user.id)
    return templates.TemplateResponse(
        "facts.html",
        {
            "request": request,
            "fact": fact,
            "categories": categories,
            "history": history,
            "user": current_user  # Передаем информацию о пользователе в шаблон
        }
    )

@router.post("/save")
async def save_fact(
    request: Request,
    fact_id: int = Form(...),
    db: Session = Depends(database.SessionLocal)
):
    try:
        current_user = await auth.get_current_user(request=request, db=db)
        crud.save_user_fact(db, current_user.id, fact_id)
        return RedirectResponse(url="/facts/", status_code=303)
    except HTTPException:
        return RedirectResponse(url="/users/login")