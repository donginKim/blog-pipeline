from __future__ import annotations
from typing import List, Dict, Any
from playwright.sync_api import Page, sync_playwright
import os
import platform
from pathlib import Path

# --- Local/cron cross-env guard ---------------------------------------------
# Docker에서는 PLAYWRIGHT_BROWSERS_PATH=/ms-playwright 를 쓰지만,
# 로컬(macOS/Windows 등)에서는 이 경로가 없어서 실행에 실패한다.
# 로컬에서 이 경로가 존재하지 않으면 환경변수를 제거해 기본 캐시 경로를 쓰게 한다.
def _neutralize_playwright_path_for_local():
    p = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if not p:
        return
    try:
        if platform.system() != "Linux":
            if not Path(p).exists():
                os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
                os.environ.pop("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", None)
                print("[PW] neutralized PLAYWRIGHT_BROWSERS_PATH for local run")
    except Exception:
        os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
        os.environ.pop("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", None)
        print("[PW] neutralized PLAYWRIGHT_BROWSERS_PATH (fallback)")

CRAWL_TIMEOUT_MS = int(os.getenv("CRAWL_TIMEOUT_MS", "60000"))

def crawl_keyword(keyword: str) -> List[Dict[str, Any]]:
    _neutralize_playwright_path_for_local()
    launch_args = ["--no-sandbox", "--disable-dev-shm-usage"] if platform.system() == "Linux" else []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=launch_args)
        try:
            page = browser.new_page()
            page.goto(f"https://search.naver.com/search.naver?query={keyword}", timeout=CRAWL_TIMEOUT_MS)
            # 고정 대기 대신 첫 컨테이너 등장까지 대기 (더 안정적)
            page.wait_for_selector("div.sds-comps-base-layout.sds-comps-inline-layout.fds-collection-root", timeout=10000)
            return parse_naver_search_page(page)
        finally:
            browser.close()

def parse_naver_search_page(page: Page) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    # ---------------------------
    # 일반 섹션
    # ---------------------------
    container_divs = page.query_selector_all(
        "div.sds-comps-base-layout.sds-comps-inline-layout.fds-collection-root"
    )

    for div in container_divs:
        span = div.query_selector("span")
        if not span:
            continue

        span_text = span.inner_text().strip()
        if not span_text or "인기주제" in span_text:
            continue

        boxes = div.query_selector_all(
            "div.sds-comps-base-layout.sds-comps-inline-layout._keep_wrap.fds-article-simple-box.fds-article-box-mobilefalse"
        )

        article_boxes = []
        for idx, box in enumerate(boxes, start=1):
            seen_links = set()
            links = []

            for a in box.query_selector_all("a"):
                href = a.get_attribute("href") or ""
                text = a.inner_text().strip()
                key = (href.strip(), text.strip())

                if (
                        href.startswith("https://blog.naver.com")
                        and text
                        and key not in seen_links
                ):
                    seen_links.add(key)
                    links.append({"href": href, "text": text})

            if links:
                article_boxes.append({
                    "box_index": idx,
                    "links": links
                })

        if article_boxes:
            results.append({
                "span": span_text,
                "article_boxes": article_boxes
            })

    # ---------------------------
    # 인기글 섹션
    # ---------------------------
    subject_divs = page.query_selector_all("div.api_subject_bx")

    for div in subject_divs:
        title_elem = div.query_selector("div.mod_title_area .title_wrap h2.title")
        if not title_elem:
            continue

        title_text = title_elem.inner_text().strip()
        if "인기글" not in title_text:
            continue

        user_boxes = div.query_selector_all("ul.lst_view div.user_box_inner")
        article_boxes = []

        for idx, user_box in enumerate(user_boxes, start=1):
            a = user_box.query_selector("div.user_info a")
            if not a:
                continue

            href = a.get_attribute("href") or ""
            text = a.inner_text().strip()

            if href.startswith("https://blog.naver.com") and text:
                article_boxes.append({
                    "box_index": idx,
                    "links": [{
                        "href": href,
                        "text": text
                    }]
                })

        if article_boxes:
            results.append({
                "span": title_text,
                "article_boxes": article_boxes
            })

    return results