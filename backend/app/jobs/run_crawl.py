from __future__ import annotations

import requests, os
import json
import traceback
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, parse_qs
from zoneinfo import ZoneInfo

from app.db import engine, SessionLocal, wait_for_db
from app import crud
from app.crawler.naver import crawl_keyword
from app.notify import send_alert  # ALERT_PROVIDER=LOG|TWILIO ... (see app/notify.py)
from app.ai_blog import write_post_md

KST = ZoneInfo("Asia/Seoul")
WRITER_URL = os.getenv("WRITER_URL", "http://writer:8080/write")

def kst_today():
    """Return today's date in KST (Asia/Seoul)."""
    return datetime.now(KST).date()


def extract_blog_id(url_pattern: str) -> Optional[str]:
    """
    Extract Naver blog id from:
      - https://blog.naver.com/<id>
      - ...?blogId=<id>
    """
    u = urlparse(url_pattern)
    path_id = (u.path or "").strip("/").split("/")[0] if u.path else ""
    if path_id and path_id.lower() != "postview.naver":
        return path_id
    qs = parse_qs(u.query or "")
    if "blogId" in qs and qs["blogId"]:
        return qs["blogId"][0]
    return None


def eval_snapshot(snapshot, blog_pattern: str):
    """
    Decide if given snapshot contains posts for target blog.
    Returns: (found: bool, occurrences: int, first_section: str|None, first_url: str|None, first_title: str|None)
    """
    bid = extract_blog_id(blog_pattern)
    cnt = 0
    first_section = None
    first_url = None
    first_title = None

    def is_match(href: str) -> bool:
        if not href.startswith("https://blog.naver.com"):
            return False
        if bid:
            if f"blogId={bid}" in href:
                return True
            if f"/{bid}/" in href or href.rstrip("/").endswith(f"/{bid}"):
                return True
        # fallback: plain containment
        return blog_pattern in href

    for sec in snapshot:
        section_name = sec.get("span")
        for box in sec.get("article_boxes", []):
            for link in box.get("links", []):
                href = (link.get("href") or "").strip()
                title = (link.get("text") or "").strip()
                if is_match(href):
                    cnt += 1
                    if first_url is None:
                        first_url = href
                        first_title = title
                        first_section = section_name

    return (cnt > 0, cnt, first_section, first_url, first_title)


def run_once():
    """
    Crawl all active (keyword ↔ mapped blogs) and store results.
    After the batch, send a single alert listing keywords with zero matches.
    """
    wait_for_db()
    crud.init_db(engine)

    db = SessionLocal()
    run = None
    total = ok = fail = 0
    alert_lines: list[str] = []
    missing_keywords: list[str] = []

    try:
        run = crud.start_run(db)
        today = kst_today()

        mappings = crud.mappings(db)  # [(Keyword, [Blog,...])]
        for kw, blogs in mappings:
            total += 1

            # If no mapped blogs, skip (not an alert target)
            if not blogs:
                print(f"[SKIP] keyword='{kw.keyword}' (no mapped blogs)")
                ok += 1
                continue

            try:
                print(f"[CRAWL] keyword='{kw.keyword}' blogs={len(blogs)}")
                snapshot = crawl_keyword(kw.keyword)
                snapshot_json = json.dumps(snapshot, ensure_ascii=False)

                found_any = False
                saved = 0

                for blog in blogs:
                    found, occ, section, url, title = eval_snapshot(snapshot, blog.url_pattern)
                    if found:
                        found_any = True
                    crud.save_result(
                        db,
                        run.id,
                        kw.id,
                        blog.id,
                        found=found,
                        occurrences=occ,
                        section=section,
                        matched_url=url,
                        matched_title=title,
                        snapshot_json=snapshot_json,
                        run_date=today,
                    )
                    saved += 1

                if not found_any:
                    alert_lines.append(f"- {kw.keyword} (매칭 0건)")
                    missing_keywords.append(kw.keyword)

                ok += 1
                print(f"[SAVED] keyword='{kw.keyword}' rows={saved}")

            except Exception as e:
                fail += 1
                print(f"[ERROR] keyword='{kw.keyword}' err={e}")
                traceback.print_exc()

        if run:
            crud.finish_run(db, run, total, ok, fail)

        # Send a single aggregated alert at the end (if needed)
        if alert_lines:
            body = "네이버 모니터링 알림\n" + "\n".join(alert_lines) + f"\n기준일: {today.isoformat()}"
            send_alert(body)
            for k in missing_keywords:
                try:
                    path = write_post_md(k, today)
                    print(f"[AI] generated blog draft -> {path} (keyword='{k}')")

                    try:
                        r = requests.post(WRITER_URL, json={"file": path}, timeout=30)
                        print("[WRITE] status", r.status_code, r.text[:200])
                    except Exception as e:
                        print(f"[WRITE ERROR] failed to call writer for {path}: {e}")
                except Exception as e:
                    print(f"[AI ERROR] failed to generate post for '{k}': {e}")

        print(f"[CRON] done total={total} ok={ok} fail={fail} at {datetime.utcnow().isoformat()}Z")

    finally:
        db.close()


def run_for_mapping(keyword_id: int, blog_id: int):
    """
    Run a one-off crawl for a single (keyword, blog) mapping.
    Useful right after creating a mapping from the API (background task).
    """
    wait_for_db()
    crud.init_db(engine)

    db = SessionLocal()
    run = None
    try:
        kw = crud.get_keyword(db, keyword_id)
        blog = crud.get_blog(db, blog_id)
        if not kw or not blog:
            print(f"[SKIP] invalid mapping: keyword_id={keyword_id}, blog_id={blog_id}")
            return

        run = crud.start_run(db)
        today = kst_today()

        print(f"[CRAWL-ONE] keyword='{kw.keyword}' blog='{blog.url_pattern}'")
        snapshot = crawl_keyword(kw.keyword)
        snapshot_json = json.dumps(snapshot, ensure_ascii=False)

        found, occ, section, url, title = eval_snapshot(snapshot, blog.url_pattern)
        crud.save_result(
            db,
            run.id,
            kw.id,
            blog.id,
            found=found,
            occurrences=occ,
            section=section,
            matched_url=url,
            matched_title=title,
            snapshot_json=snapshot_json,
            run_date=today,
        )

        # Optional: alert if not found
        if not found:
            send_alert(f"네이버 모니터링 알림\n- {kw.keyword} (매칭 0건)\n기준일: {today.isoformat()}")
            try:
                path = write_post_md(kw.keyword, today)
                print(f"[AI] generated blog draft -> {path}")
            except Exception as e:
                print(f"[AI ERROR] failed to generate post for '{kw.keyword}': {e}")

        crud.finish_run(db, run, total=1, ok=1, fail=0)
        print(f"[DONE-ONE] keyword='{kw.keyword}' saved=1 found={found}")

    except Exception:
        if run:
            crud.finish_run(db, run, total=1, ok=0, fail=1)
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run_once()