from __future__ import annotations
# app/main.py

from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from .db import engine, SessionLocal, wait_for_db
from . import crud

app = FastAPI(title="Naver Monitor")

templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def on_startup():
    # DB가 실제로 리슨할 때까지 대기 후 테이블 생성
    wait_for_db()
    crud.init_db(engine)

@app.get("/")
def index(request: Request):
    db = SessionLocal()
    try:
        kws = crud.list_keywords(db)
        blogs = crud.list_blogs(db)
        results = crud.last_results(db, limit=100)
        maps = crud.mappings(db)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "keywords": kws,
            "blogs": blogs,
            "results": results,
            "mappings": maps,
        })
    finally:
        db.close()

@app.post("/keywords")
def add_keyword(keyword: str = Form(...)):
    db = SessionLocal()
    try:
        crud.add_keyword(db, keyword)
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()

@app.post("/blogs")
def add_blog(name: str = Form(...), url_pattern: str = Form(...)):
    db = SessionLocal()
    try:
        crud.add_blog(db, name, url_pattern)
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()

@app.post("/targets")
def add_target(
        keyword_id: int = Form(...),
        blog_id: int = Form(...),
        background_tasks: BackgroundTasks = None,
):
    db = SessionLocal()
    try:
        crud.add_target(db, keyword_id, blog_id)
        # 연결 직후 해당 매핑만 1회 크롤 (백그라운드)
        if background_tasks is not None:
            from batch.run_crawl import run_for_mapping
            background_tasks.add_task(run_for_mapping, keyword_id, blog_id)
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()