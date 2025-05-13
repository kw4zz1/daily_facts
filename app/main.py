from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Импортируем правильные зависимости из database
from .database import engine, metadata, get_db
from .routers import users, facts
from . import models, auth

# Создаем таблицы (используем metadata напрямую, как в оригинальном коде)
metadata.create_all(bind=engine)
app = FastAPI()

# Подключаем статику
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="app/templates")

# Регистрируем роутеры
app.include_router(users.router)
app.include_router(facts.router)

# Функция get_db теперь импортируется из database.py,
# поэтому нам не нужно её здесь определять повторно

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Рендерим приветственную страницу напрямую
    return templates.TemplateResponse("index.html", {"request": request})

# Добавление тестовых данных, если они отсутствуют
@app.on_event("startup")
def create_test_data():
    # Используем SessionLocal из database.py через функцию get_db
    db = next(get_db())
    try:
        # Проверка наличия фактов
        fact_count = db.query(models.Fact).count()
        if fact_count == 0:
            # Добавим несколько фактов для тестирования
            test_facts = [
                models.Fact(category="История", text="В Древнем Риме плебеи устраивали забастовки, покидая город."),
                models.Fact(category="Наука", text="Вода расширяется при замерзании, в отличие от большинства веществ."),
                models.Fact(category="Технологии", text="Первый компьютерный баг был настоящим жуком, застрявшим в реле."),
                models.Fact(category="Астрономия", text="На Венере день длиннее, чем год."),
                models.Fact(category="Биология", text="ДНК всех людей на 99.9% идентична."),
            ]
            db.add_all(test_facts)
            db.commit()
    finally:
        db.close()