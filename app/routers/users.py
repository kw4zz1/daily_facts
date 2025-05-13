from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .. import crud, auth, schemas
from ..database import get_db
import traceback

router = APIRouter(
    prefix="/users",
    tags=["users"]
)
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Проверяем, что логин ещё не занят
    if crud.get_user_by_username(db, username=username):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Этот логин уже занят"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Пытаемся создать пользователя и ловим возможные ошибки
    try:
        crud.create_user(db, schemas.UserCreate(username=username, password=password))
    except IntegrityError as e:
        db.rollback()
        print("IntegrityError при создании пользователя:", e)
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Пользователь с таким именем уже существует"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        db.rollback()
        traceback.print_exc()  # печатает полный стектрейс в консоль
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Внутренняя ошибка сервера"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Успешно создан — редирект на страницу логина
    return RedirectResponse(url="/users/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/facts/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=60 * auth.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
