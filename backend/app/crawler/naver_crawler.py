# Async Naver crawler
from playwright.async_api import async_playwright, Page
from typing import List, Dict, Any
import random
import time

from ..core.config import settings


async def parse_naver_search_page(page: Page) -> List[Dict[str, Any]]:
    """Parse Naver search page and extract blog links"""
    results: List[Dict[str, Any]] = []

    # 일반 섹션
    container_divs = await page.query_selector_all(
        "div.sds-comps-base-layout.sds-comps-inline-layout.fds-collection-root"
    )

    for div in container_divs:
        span = await div.query_selector("span")
        if not span:
            continue

        span_text = (await span.inner_text() or "").strip()
        if not span_text or "인기주제" in span_text:
            continue

        boxes = await div.query_selector_all(
            "div.sds-comps-base-layout.sds-comps-inline-layout._keep_wrap.fds-article-simple-box.fds-article-box-mobilefalse"
        )

        article_boxes = []
        for idx, box in enumerate(boxes, start=1):
            seen_links = set()
            links = []

            link_elements = await box.query_selector_all("a")
            for a in link_elements:
                href = (await a.get_attribute("href") or "").strip()
                text = (await a.inner_text() or "").strip()
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
    subject_divs = await page.query_selector_all("div.api_subject_bx")

    for div in subject_divs:
        title_elem = await div.query_selector("div.mod_title_area .title_wrap h2.title")
        if not title_elem:
            continue

        title_text = (await title_elem.inner_text() or "").strip()
        if "인기글" not in title_text:
            continue

        user_boxes = await div.query_selector_all("ul.lst_view div.user_box_inner")
        article_boxes = []

        for idx, user_box in enumerate(user_boxes, start=1):
            a = await user_box.query_selector("div.user_info a")
            if not a:
                continue

            href = (await a.get_attribute("href") or "").strip()
            text = (await a.inner_text() or "").strip()

            if href.startswith("https://blog.naver.com") and text:
                article_boxes.append({
                    "box_index": idx,
                    "links": [{"href": href, "text": text}],
                })

        if article_boxes:
            results.append({"span": title_text, "article_boxes": article_boxes})

    return results


async def crawl_keyword_async(keyword: str, timeout_ms: int = 60000) -> List[Dict[str, Any]]:
    """Crawl Naver search results for a keyword asynchronously"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set user agent
        await page.set_extra_http_headers({"User-Agent": settings.user_agent})
        
        # Navigate to search page
        url = f"https://search.naver.com/search.naver?query={keyword}"
        await page.goto(url, timeout=timeout_ms)
        
        # Wait for page to load
        await page.wait_for_timeout(3000 + random.randint(0, 1000))
        
        # Parse results
        results = await parse_naver_search_page(page)
        
        await browser.close()
        return results

