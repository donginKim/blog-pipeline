# app/crud.py
from __future__ import annotations
from typing import Iterable
from datetime import datetime, date
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session
from .models import Base, Blog, Keyword, KeywordTarget, Run, Result

# Create tables if not exist
def init_db(engine):
    Base.metadata.create_all(bind=engine)

# Keywords
def list_keywords(db: Session):
    return db.execute(select(Keyword).order_by(Keyword.id.desc())).scalars().all()

def add_keyword(db: Session, kw: str):
    kw = kw.strip()
    if not kw:
        return None
    existing = db.execute(select(Keyword).where(Keyword.keyword == kw)).scalar_one_or_none()
    if existing:
        return existing
    obj = Keyword(keyword=kw)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# Blogs
def list_blogs(db: Session):
    return db.execute(select(Blog).order_by(Blog.id.desc())).scalars().all()

def add_blog(db: Session, name: str, url_pattern: str):
    obj = Blog(name=name.strip(), url_pattern=url_pattern.strip())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# Mapping
def add_target(db: Session, keyword_id: int, blog_id: int):
    existing = db.execute(
        select(KeywordTarget).where(KeywordTarget.keyword_id==keyword_id, KeywordTarget.blog_id==blog_id)
    ).scalar_one_or_none()
    if existing:
        return existing
    obj = KeywordTarget(keyword_id=keyword_id, blog_id=blog_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# Run + Results
def start_run(db: Session) -> Run:
    run = Run(started_at=datetime.utcnow())
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

def finish_run(db: Session, run: Run, total: int, ok: int, fail: int):
    run.finished_at = datetime.utcnow()
    run.total_keywords = total
    run.success_cnt = ok
    run.fail_cnt = fail
    db.commit()

def save_result(db: Session, run_id: int, keyword_id: int, blog_id: int, *,
                found: bool, occurrences: int, section: str | None, matched_url: str | None,
                matched_title: str | None, snapshot_json: str | None, run_date: date):
    r = Result(
        run_id=run_id,
        keyword_id=keyword_id,
        blog_id=blog_id,
        found=found,
        occurrences=occurrences,
        section=section,
        matched_url=matched_url,
        matched_title=matched_title,
        snapshot_json=snapshot_json,
        run_date=run_date,
    )
    db.add(r)
    db.commit()
    return r

def last_results(db: Session, limit: int = 100):
    return db.execute(select(Result).order_by(Result.id.desc()).limit(limit)).scalars().all()

def mappings(db: Session):
    # returns (Keyword, [Blog,...]) pairs
    kws = db.execute(select(Keyword).where(Keyword.is_active==True)).scalars().all()
    out = []
    for kw in kws:
        blog_ids = db.execute(select(KeywordTarget.blog_id).where(KeywordTarget.keyword_id==kw.id)).scalars().all()
        blogs = []
        if blog_ids:
            blogs = db.execute(select(Blog).where(Blog.id.in_(blog_ids), Blog.is_active==True)).scalars().all()
        out.append((kw, blogs))
    return out