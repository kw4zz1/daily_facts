from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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
    try:
        current_user = await auth.get_current_user(request=request, db=db)
    except HTTPException:
        return RedirectResponse("/users/login")

    slugs = list(CATEGORY_SLUGS.keys())
    fact = None

    if category:
        slug = category.lower()
        if slug in slugs:
            remote = parse_and_return_facts(slug)
            if remote:
                data = random.choice(remote)
                try:
                    db_fact = crud.create_fact(
                        db,
                        schemas.FactCreate(
                            title=data["title"],
                            text=data["text"],
                            category=data["category"],
                        ),
                    )
                    fact = schemas.FactOut.from_orm(db_fact)
                except Exception:
                    db_fact = crud.get_fact_by_content(db, data["text"])
                    if db_fact:
                        fact = schemas.FactOut.from_orm(db_fact)
                    else:
                        fact = schemas.FactOut(id=0, **data)
            else:
                dbf = crud.get_random_fact(db, CATEGORY_SLUGS[slug])
                if dbf:
                    fact = schemas.FactOut.from_orm(dbf)
    else:
        slug = random.choice(slugs)
        remote = parse_and_return_facts(slug)
        if remote:
            data = random.choice(remote)
            try:
                db_fact = crud.create_fact(
                    db,
                    schemas.FactCreate(
                        title=data["title"],
                        text=data["text"],
                        category=data["category"],
                    ),
                )
                fact = schemas.FactOut.from_orm(db_fact)
            except Exception:
                db_fact = crud.get_fact_by_content(db, data["text"])
                if db_fact:
                    fact = schemas.FactOut.from_orm(db_fact)
                else:
                    fact = schemas.FactOut(id=0, **data)

    history = crud.get_user_history(db, current_user.id)

    return templates.TemplateResponse(
        "facts.html",
        {
            "request": request,
            "fact": fact,
            "categories": slugs,
            "current_category": category,
            "history": history,
            "CATEGORY_SLUGS": CATEGORY_SLUGS,
            "CATEGORY_NAMES": CATEGORY_NAMES,
        },
    )


@router.post("/save")
async def save_fact(
    request: Request,
    fact_id: int = Form(...),
    db: Session = Depends(database.get_db),
):
    try:
        current_user = await auth.get_current_user(request=request, db=db)
    except HTTPException:
        return RedirectResponse("/users/login")

    crud.save_user_fact(db, current_user.id, fact_id)

    referer = request.headers.get("referer") or "/facts/"
    return RedirectResponse(url=referer, status_code=303)


@router.get("/api/fact")
async def api_get_fact(
    category: Optional[str] = None,
    db: Session = Depends(database.get_db),
    request: Request = None,
):
    try:
        await auth.get_current_user(request=request, db=db)
    except HTTPException:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    slugs = list(CATEGORY_SLUGS.keys())
    fact = None

    if category and category.lower() in slugs:
        slug = category.lower()
        remote = parse_and_return_facts(slug)
        if remote:
            data = random.choice(remote)
            # Попытка получить факт из БД или создать новый, возвращая с id
            db_fact = crud.get_fact_by_content(db, data["text"])
            if not db_fact:
                try:
                    db_fact = crud.create_fact(
                        db,
                        schemas.FactCreate(
                            title=data["title"],
                            text=data["text"],
                            category=data["category"],
                        ),
                    )
                except Exception:
                    pass
            fact = {
                "id": db_fact.id if db_fact else 0,
                "title": data["title"],
                "text": data["text"],
                "category": data["category"],
            }
    else:
        slug = random.choice(slugs)
        remote = parse_and_return_facts(slug)
        if remote:
            data = random.choice(remote)
            db_fact = crud.get_fact_by_content(db, data["text"])
            if not db_fact:
                try:
                    db_fact = crud.create_fact(
                        db,
                        schemas.FactCreate(
                            title=data["title"],
                            text=data["text"],
                            category=data["category"],
                        ),
                    )
                except Exception:
                    pass
            fact = {
                "id": db_fact.id if db_fact else 0,
                "title": data["title"],
                "text": data["text"],
                "category": data["category"],
            }

    if fact is None:
        return JSONResponse({"error": "No facts found"}, status_code=404)

    return fact
