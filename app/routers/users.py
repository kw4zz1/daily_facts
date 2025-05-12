from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import crud, schemas, auth, database

router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(database.SessionLocal)
):
    # Проверяем, существует ли уже пользователь с таким именем
    existing_user = crud.get_user_by_username(db, username)
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Пользователь с таким именем уже существует"}
        )

    # Создаем нового пользователя
    try:
        user = crud.create_user(db, schemas.UserCreate(username=username, password=password))
        # После успешной регистрации перенаправляем на страницу входа
        return RedirectResponse(url="/users/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")  # Логируем ошибку
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Ошибка при регистрации. Пожалуйста, попробуйте еще раз."}
        )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(database.SessionLocal)
):
    user = crud.get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверные учетные данные"}
        )

    access_token = auth.create_access_token(data={"sub": user.username})

    response = RedirectResponse(url="/facts/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # не доступно JavaScript
        samesite="lax",  # безопаснее при переходах между сайтами
        max_age=1800  # 30 минут
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response