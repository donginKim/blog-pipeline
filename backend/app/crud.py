from __future__ import annotations
from typing import List, Tuple
from datetime import datetime, date
import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Base, Keyword, Blog, KeywordTarget, Run, Result, BlogCredential

# Optional reversible encryption for blog credentials
try:
    from cryptography.fernet import Fernet  # type: ignore
except Exception:  # pragma: no cover
    Fernet = None  # type: ignore


def _get_fernet():
    key = os.getenv("BLOG_CRED_KEY")
    if not key or not Fernet:
        return None
    try:
        return Fernet(key)
    except Exception:
        return None


def _enc(v: str) -> str:
    f = _get_fernet()
    if f:
        return f.encrypt(v.encode("utf-8")).decode("utf-8")
    return v


def _dec(v: str) -> str:
    f = _get_fernet()
    if f:
        try:
            return f.decrypt(v.encode("utf-8")).decode("utf-8")
        except Exception:
            return v
    return v

def init_db(engine) -> None:
    Base.metadata.create_all(bind=engine)

# Keywords
def list_keywords(db: Session):
    return db.execute(select(Keyword).order_by(Keyword.id.desc())).scalars().all()

def get_keyword(db: Session, kid: int):
    return db.get(Keyword, kid)

def add_keyword(db: Session, keyword: str):
    keyword = keyword.strip()
    if not keyword:
        raise ValueError("keyword is empty")
    existing = db.execute(select(Keyword).where(Keyword.keyword == keyword)).scalar_one_or_none()
    if existing:
        return existing
    obj = Keyword(keyword=keyword)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update_keyword(db: Session, kid: int, *, keyword: str | None, is_active: bool | None):
    obj = db.get(Keyword, kid)
    if not obj:
        return None
    if keyword is not None:
        obj.keyword = keyword.strip()
    if is_active is not None:
        obj.is_active = bool(is_active)
    db.commit(); db.refresh(obj)
    return obj

def delete_keyword(db: Session, kid: int) -> bool:
    obj = db.get(Keyword, kid)
    if not obj:
        return False
    db.delete(obj); db.commit()
    return True

# Blogs
def list_blogs(db: Session):
    return db.execute(select(Blog).order_by(Blog.id.desc())).scalars().all()

def get_blog(db: Session, bid: int):
    return db.get(Blog, bid)

def add_blog(db: Session, name: str, url_pattern: str):
    obj = Blog(name=name.strip(), url_pattern=url_pattern.strip())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update_blog(db: Session, bid: int, *, name: str | None, url_pattern: str | None, is_active: bool | None):
    obj = db.get(Blog, bid)
    if not obj:
        return None
    if name is not None:
        obj.name = name.strip()
    if url_pattern is not None:
        obj.url_pattern = url_pattern.strip()
    if is_active is not None:
        obj.is_active = bool(is_active)
    db.commit(); db.refresh(obj)
    return obj

def delete_blog(db: Session, bid: int) -> bool:
    obj = db.get(Blog, bid)
    if not obj:
        return False
    db.delete(obj); db.commit()
    return True

# Targets
def list_targets(db: Session):
    return db.execute(select(KeywordTarget).order_by(KeywordTarget.id.desc())).scalars().all()

def add_target(db: Session, keyword_id: int, blog_id: int):
    exists = db.execute(select(KeywordTarget).where(
        KeywordTarget.keyword_id == keyword_id,
        KeywordTarget.blog_id == blog_id
    )).scalar_one_or_none()
    if exists:
        return exists
    obj = KeywordTarget(keyword_id=keyword_id, blog_id=blog_id)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def delete_target(db: Session, tid: int) -> bool:
    obj = db.get(KeywordTarget, tid)
    if not obj:
        return False
    db.delete(obj); db.commit()
    return True

def mappings(db: Session) -> List[Tuple[Keyword, List[Blog]]]:
    kws = db.execute(select(Keyword).where(Keyword.is_active==True)).scalars().all()
    out: List[Tuple[Keyword, List[Blog]]] = []
    for kw in kws:
        blog_ids = db.execute(select(KeywordTarget.blog_id).where(KeywordTarget.keyword_id==kw.id)).scalars().all()
        blogs: List[Blog] = []
        if blog_ids:
            blogs = db.execute(select(Blog).where(Blog.id.in_(blog_ids), Blog.is_active==True)).scalars().all()
        out.append((kw, blogs))
    return out

# Runs & Results
def start_run(db: Session) -> Run:
    run = Run(started_at=datetime.utcnow())
    db.add(run); db.commit(); db.refresh(run)
    return run

def finish_run(db: Session, run: Run, total: int, ok: int, fail: int) -> None:
    run.finished_at = datetime.utcnow()
    run.total_keywords = total
    run.success_cnt = ok
    run.fail_cnt = fail
    db.commit()

def save_result(db: Session, run_id: int | None, keyword_id: int, blog_id: int, *,
                found: bool, occurrences: int, section: str | None,
                matched_url: str | None, matched_title: str | None,
                snapshot_json: str | None, run_date: date) -> Result:
    r = Result(
        run_id=run_id, keyword_id=keyword_id, blog_id=blog_id, found=found,
        occurrences=occurrences, section=section, matched_url=matched_url,
        matched_title=matched_title, snapshot_json=snapshot_json, run_date=run_date
    )
    db.add(r); db.commit(); db.refresh(r)
    return r

def last_results(db: Session, limit: int = 100):
    return db.execute(select(Result).order_by(Result.id.desc()).limit(limit)).scalars().all()

# --- Blog Credentials ---

def list_blog_credentials(db: Session):
    return db.execute(select(BlogCredential).order_by(BlogCredential.id.desc())).scalars().all()


def get_blog_credential(db: Session, cid: int):
    return db.get(BlogCredential, cid)


def add_blog_credential(db: Session, *, login_id: str, password: str, blog_url: str, phone: str | None = None, is_active: bool = True) -> BlogCredential:
    obj = BlogCredential(
        login_id=login_id.strip(),
        password_enc=_enc(password.strip()),
        blog_url=blog_url.strip(),
        phone=(phone.strip() if phone else None),
        is_active=bool(is_active),
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


def update_blog_credential(db: Session, cid: int, *, login_id: str | None = None,
                           password: str | None = None, blog_url: str | None = None,
                           is_active: bool | None = None):
    obj = db.get(BlogCredential, cid)
    if not obj:
        return None
    if login_id is not None:
        obj.login_id = login_id.strip()
    if password is not None:
        obj.password_enc = _enc(password.strip())
    if blog_url is not None:
        obj.blog_url = blog_url.strip()
    if is_active is not None:
        obj.is_active = bool(is_active)
    db.commit(); db.refresh(obj)
    return obj


def delete_blog_credential(db: Session, cid: int) -> bool:
    obj = db.get(BlogCredential, cid)
    if not obj:
        return False
    db.delete(obj); db.commit()
    return True


def get_blog_credential_with_password(db: Session, cid: int):
    obj = db.get(BlogCredential, cid)
    if not obj:
        return None, None
    return obj, _dec(obj.password_enc)