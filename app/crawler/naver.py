from __future__ import annotations
from typing import List, Dict, Any
from playwright.sync_api import Page, sync_playwright
import random, time

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)


def parse_naver_search_page(page: Page) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    # 일반 섹션
    container_divs = page.query_selector_all(
        "div.sds-comps-base-layout.sds-comps-inline-layout.fds-collection-root"
    )

    for div in container_divs:
        span = div.query_selector("span")
        if not span:
            continue

        span_text = (span.inner_text() or "").strip()
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
                href = (a.get_attribute("href") or "").strip()
                text = (a.inner_text() or "").strip()
                key = (href, text)

                if (
                        href.startswith("https://blog.naver.com")
                        and text
                        and key not in seen_links
                ):
                    seen_links.add(key)
                    links.append({"href": href, "text": text})

            if links:
                article_boxes.append({"box_index": idx, "links": links})

        if article_boxes:
            results.append({"span": span_text, "article_boxes": article_boxes})

    # 인기글 섹션
    subject_divs = page.query_selector_all("div.api_subject_bx")

    for div in subject_divs:
        title_elem = div.query_selector("div.mod_title_area .title_wrap h2.title")
        if not title_elem:
            continue

        title_text = (title_elem.inner_text() or "").strip()
        if "인기글" not in title_text:
            continue

        user_boxes = div.query_selector_all("ul.lst_view div.user_box_inner")
        article_boxes = []

        for idx, user_box in enumerate(user_boxes, start=1):
            a = user_box.query_selector("div.user_info a")
            if not a:
                continue

            href = (a.get_attribute("href") or "").strip()
            text = (a.inner_text() or "").strip()

            if href.startswith("https://blog.naver.com") and text:
                article_boxes.append({
                    "box_index": idx,
                    "links": [{"href": href, "text": text}],
                })

        if article_boxes:
            results.append({"span": title_text, "article_boxes": article_boxes})

    return results


def crawl_keyword(keyword: str, timeout_ms: int = 60000) -> List[Dict[str, Any]]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": USER_AGENT})
        url = f"https://search.naver.com/search.naver?query={keyword}"
        page.goto(url, timeout=timeout_ms)
        page.wait_for_timeout(3000 + random.randint(0, 1000))
        results = parse_naver_search_page(page)
        browser.close()
        return results