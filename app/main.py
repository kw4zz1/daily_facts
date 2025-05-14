from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import engine, metadata, get_db
from .routers import users, facts
from . import models, auth

metadata.create_all(bind=engine)
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(users.router)
app.include_router(facts.router)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
def create_test_data():
    db = next(get_db())
    try:
        if db.query(models.Fact).count() == 0:
            sample = [
                {"category":"История","title":"Плебеи в Риме","text":"В Древнем Риме плебеи устраивали забастовки, покидая город."},
                {"category":"Наука","title":"Вода и лед","text":"Вода расширяется при замерзании, в отличие от большинства веществ."},
                {"category":"Технологии","title":"Первый баг","text":"Первый компьютерный «баг» был настоящим жуком, застрявшим в реле."},
                {"category":"Астрономия","title":"День на Венере","text":"На Венере день длиннее, чем год."},
                {"category":"Биология","title":"Человеческая ДНК","text":"ДНК всех людей на 99.9% идентична."},
            ]
            for f in sample:
                db.add(models.Fact(category=f["category"], title=f["title"], text=f["text"]))
            db.commit()
    finally:
        db.close()
