from __future__ import annotations
import json, os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app import crud
from datetime import datetime, timezone, timedelta, date
from app.crawler.naver import crawl_keyword

load_dotenv()

TIMEOUT_MS = int(os.getenv("CRAWL_TIMEOUT_MS", "60000"))


KST = timezone(timedelta(hours=9))
def kst_today() -> date:
    return datetime.now(tz=KST).date()

def _count_occurrences(parsed, url_pattern: str):
    cnt = 0
    first = None
    first_title = None
    first_section = None
    for block in parsed:
        span = block.get("span")
        for box in block.get("article_boxes", []):
            for link in box.get("links", []):
                href = link.get("href") or ""
                text = link.get("text") or ""
                if href.startswith(url_pattern):
                    cnt += 1
                    if not first:
                        first = href
                        first_title = text
                        first_section = span
    return cnt, first, first_title, first_section


def run_once():
    db: Session = SessionLocal()
    run = crud.start_run(db)
    run_date = kst_today()

    total = ok = fail = 0

    try:
        mappings = crud.mappings(db)  # [(Keyword, [Blog,...]), ...]
        for kw, blogs in mappings:
            if not blogs:
                continue
            total += 1
            try:
                parsed = crawl_keyword(kw.keyword, timeout_ms=TIMEOUT_MS)
                snapshot = json.dumps(parsed, ensure_ascii=False)
                for blog in blogs:
                    cnt, first_url, first_title, section = _count_occurrences(parsed, blog.url_pattern)
                    crud.save_result(
                        db,
                        run_id=run.id,
                        keyword_id=kw.id,
                        blog_id=blog.id,
                        found=(cnt > 0),
                        occurrences=cnt,
                        section=section,
                        matched_url=first_url,
                        matched_title=first_title,
                        snapshot_json=snapshot if cnt > 0 else None,
                        run_date=run_date,
                    )
                ok += 1
            except Exception as e:
                fail += 1
                # optional: log the exception in a separate table or stdout
                print(f"[ERROR] keyword={kw.keyword} err={e}")
    finally:
        crud.finish_run(db, run, total, ok, fail)
        db.close()

if __name__ == "__main__":
    run_once()

# app/utils/time.py
from __future__ import annotations
from datetime import datetime, timezone, timedelta, date

KST = timezone(timedelta(hours=9))

def kst_today() -> date:
    return datetime.now(tz=KST).date()