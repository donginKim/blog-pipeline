from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from login import naver_login
from uploader import write_blog_from_dsl

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/ms-playwright")

app = FastAPI(title="Naver Writer")

class WriteIn(BaseModel):
    file: str  # /app/generated/xxxx.txt

# --- Helpers to ensure editor is fully loaded before writing ---
NAVER_BLOG_ID = os.getenv("NAVER_BLOG_ID") or os.getenv("BLOG_ID")

TITLE_SEL = (
    "input.se_publish_title, input#title, input[name='title'], "
    "textarea#title, textarea[name='title'], [placeholder*='제목'], "
    "[role='textbox'][aria-label*='제목']"
)

CONTENT_EDITABLE_SEL = "div[contenteditable='true']"


def _find_ctx_with_selector(page, selector):
    """Return page or first frame that contains the selector."""
    try:
        if page.locator(selector).count() > 0:
            return page
    except Exception:
        pass
    for fr in page.frames:
        try:
            if fr.locator(selector).count() > 0:
                return fr
        except Exception:
            continue
    return page


def ensure_editor_ready(page):
    """
    After login, make sure we are on the Naver blog write editor and
    the title/body controls are present before proceeding.
    """
    for attempt in (1, 2):  # try once, then reload once if needed
        # If blog id is available, jump directly to write form on first attempt
        if attempt == 1 and NAVER_BLOG_ID:
            page.goto(
                f"https://blog.naver.com/PostWriteForm.naver?blogId={NAVER_BLOG_ID}",
                wait_until="domcontentloaded",
            )
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        # 1) Title present on page or any frame?
        try:
            ctx = _find_ctx_with_selector(page, TITLE_SEL)
            if ctx.locator(TITLE_SEL).count() > 0:
                ctx.wait_for_selector(TITLE_SEL, timeout=10000)
                return
        except Exception:
            pass

        # 2) Body editable div present on any frame?
        try:
            for fr in page.frames:
                try:
                    if fr.locator(CONTENT_EDITABLE_SEL).count() > 0:
                        fr.wait_for_selector(CONTENT_EDITABLE_SEL, timeout=10000)
                        return
                except Exception:
                    continue
            # fallback to known editor iframe selector
            page.wait_for_selector("iframe[title*='본문']", timeout=10000)
            fr = page.frame_locator("iframe[title*='본문']").frame()
            fr.wait_for_selector(CONTENT_EDITABLE_SEL, timeout=10000)
            return
        except Exception:
            pass

        # Not ready yet — soft reload and retry once
        try:
            page.wait_for_timeout(1000)
            page.reload(wait_until="domcontentloaded")
        except Exception:
            pass

    # If we get here, editor didn't appear in time
    raise HTTPException(503, "Naver editor not ready (title/body controls not found)")

@app.post("/write")
def write(inp: WriteIn):
    f = Path(inp.file)
    if not f.exists():
        raise HTTPException(404, f"not found: {f}")
    if os.getenv("DOWNLOAD_IMAGES_FIRST", "1") == "1":
        print("[WARN] image download")

    headless = os.getenv("HEADLESS", "1") == "1"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(locale="ko-KR", timezone_id="Asia/Seoul")
        page = context.new_page()
        try:
            naver_login(page)
            ensure_editor_ready(page)
            dsl = f.read_text(encoding="utf-8")
            write_blog_from_dsl(page, dsl)
            return {"ok": True}
        finally:
            context.close()
            browser.close()