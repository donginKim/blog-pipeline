from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional
from sqlalchemy import select
from .models import Result

from app.jobs.run_crawl import run_once, run_for_mapping
from .db import engine, SessionLocal, wait_for_db
from . import crud
from .schemas import (
    KeywordOut, BlogOut, TargetOut,
    AddKeywordIn, UpdateKeywordIn,
    AddBlogIn, UpdateBlogIn,
    AddTargetIn,
    BlogCredentialOut, AddBlogCredentialIn, UpdateBlogCredentialIn,
)

app = FastAPI(title="Naver Monitor API")

# CORS (개발 편의용: 운영에서는 도메인으로 제한 권장)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    wait_for_db()
    crud.init_db(engine)

# --- Health ---
@app.get("/api/health")
def health():
    return {"ok": True}

# --- Keywords ---
@app.get("/api/keywords", response_model=list[KeywordOut])
def list_keywords():
    db = SessionLocal()
    try:
        return crud.list_keywords(db)
    finally:
        db.close()

@app.post("/api/keywords", response_model=KeywordOut, status_code=201)
def add_keyword(payload: AddKeywordIn):
    db = SessionLocal()
    try:
        return crud.add_keyword(db, payload.keyword)
    finally:
        db.close()

@app.get("/api/keywords/{kid}", response_model=KeywordOut)
def get_keyword(kid: int):
    db = SessionLocal()
    try:
        obj = crud.get_keyword(db, kid)
        if not obj:
            raise HTTPException(404, "keyword not found")
        return obj
    finally:
        db.close()

@app.patch("/api/keywords/{kid}", response_model=KeywordOut)
def update_keyword(kid: int, payload: UpdateKeywordIn):
    db = SessionLocal()
    try:
        obj = crud.update_keyword(db, kid, keyword=payload.keyword, is_active=payload.is_active)
        if not obj:
            raise HTTPException(404, "keyword not found")
        return obj
    finally:
        db.close()

@app.delete("/api/keywords/{kid}", status_code=204)
def delete_keyword(kid: int):
    db = SessionLocal()
    try:
        if not crud.delete_keyword(db, kid):
            raise HTTPException(404, "keyword not found")
        return None
    finally:
        db.close()

# --- Blogs ---
@app.get("/api/blogs", response_model=list[BlogOut])
def list_blogs():
    db = SessionLocal()
    try:
        return crud.list_blogs(db)
    finally:
        db.close()

@app.post("/api/blogs", response_model=BlogOut, status_code=201)
def add_blog(payload: AddBlogIn):
    db = SessionLocal()
    try:
        return crud.add_blog(db, payload.name, payload.url_pattern)
    finally:
        db.close()

@app.get("/api/blogs/{bid}", response_model=BlogOut)
def get_blog(bid: int):
    db = SessionLocal()
    try:
        obj = crud.get_blog(db, bid)
        if not obj:
            raise HTTPException(404, "blog not found")
        return obj
    finally:
        db.close()

@app.patch("/api/blogs/{bid}", response_model=BlogOut)
def update_blog(bid: int, payload: UpdateBlogIn):
    db = SessionLocal()
    try:
        obj = crud.update_blog(db, bid, name=payload.name, url_pattern=payload.url_pattern, is_active=payload.is_active)
        if not obj:
            raise HTTPException(404, "blog not found")
        return obj
    finally:
        db.close()

@app.delete("/api/blogs/{bid}", status_code=204)
def delete_blog(bid: int):
    db = SessionLocal()
    try:
        if not crud.delete_blog(db, bid):
            raise HTTPException(404, "blog not found")
        return None
    finally:
        db.close()

# --- Targets (Keyword ↔ Blog) ---
@app.get("/api/targets", response_model=list[TargetOut])
def list_targets():
    db = SessionLocal()
    try:
        return crud.list_targets(db)
    finally:
        db.close()

@app.post("/api/targets", response_model=TargetOut, status_code=201)
def add_target(payload: AddTargetIn):
    db = SessionLocal()
    try:
        return crud.add_target(db, payload.keyword_id, payload.blog_id)
    finally:
        db.close()

@app.delete("/api/targets/{tid}", status_code=204)
def delete_target(tid: int):
    db = SessionLocal()
    try:
        if not crud.delete_target(db, tid):
            raise HTTPException(404, "target not found")
        return None
    finally:
        db.close()

# --- Blog Credentials ---
@app.get("/api/creds", response_model=list[BlogCredentialOut])
def list_creds():
    db = SessionLocal()
    try:
        return crud.list_blog_credentials(db)
    finally:
        db.close()


@app.post("/api/creds", response_model=BlogCredentialOut, status_code=201)
def add_cred(payload: AddBlogCredentialIn):
    db = SessionLocal()
    try:
        return crud.add_blog_credential(
            db,
            login_id=payload.login_id,
            password=payload.password,
            blog_url=payload.blog_url,
            phone=payload.phone,
            is_active=payload.is_active,
        )
    finally:
        db.close()


@app.get("/api/creds/{cid}", response_model=BlogCredentialOut)
def get_cred(cid: int):
    db = SessionLocal()
    try:
        obj = crud.get_blog_credential(db, cid)
        if not obj:
            raise HTTPException(404, "credential not found")
        return obj
    finally:
        db.close()


@app.patch("/api/creds/{cid}", response_model=BlogCredentialOut)
def update_cred(cid: int, payload: UpdateBlogCredentialIn):
    db = SessionLocal()
    try:
        obj = crud.update_blog_credential(
            db,
            cid,
            login_id=payload.login_id,
            password=payload.password,
            blog_url=payload.blog_url,
            phone=payload.phone,
            is_active=payload.is_active,
        )
        if not obj:
            raise HTTPException(404, "credential not found")
        return obj
    finally:
        db.close()


@app.delete("/api/creds/{cid}", status_code=204)
def delete_cred(cid: int):
    db = SessionLocal()
    try:
        if not crud.delete_blog_credential(db, cid):
            raise HTTPException(404, "credential not found")
        return None
    finally:
        db.close()

@app.get("/api/results")
def api_results(limit: int = Query(200, le=1000), date: Optional[str] = None):
    db = SessionLocal()
    try:
        q = select(Result).order_by(Result.id.desc())
        if date:
            q = select(Result).where(Result.run_date == date).order_by(Result.id.desc())
        q = q.limit(limit)
        rows = db.execute(q).scalars().all()
        # 필요한 필드만 직렬화
        out = []
        for r in rows:
            out.append({
                "keyword_id": r.keyword_id,
                "blog_id": r.blog_id,
                "found": r.found,
                "occurrences": r.occurrences,
                "section": r.section,
                "matched_url": r.matched_url,
                "matched_title": r.matched_title,
                "run_date": r.run_date.isoformat(),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })
        return out
    finally:
        db.close()

@app.post("/api/run", status_code=202)
def api_run(background_tasks: BackgroundTasks, keyword_id: Optional[int] = None, blog_id: Optional[int] = None):
    """수동 배치 실행: 전체 매핑 또는 단일 매핑(쿼리스트링으로 keyword_id, blog_id 전달 시)"""
    if keyword_id is not None and blog_id is not None:
        background_tasks.add_task(run_for_mapping, keyword_id, blog_id)
        return {"ok": True, "mode": "single", "keyword_id": keyword_id, "blog_id": blog_id}
    background_tasks.add_task(run_once)
    return {"ok": True, "mode": "all"}