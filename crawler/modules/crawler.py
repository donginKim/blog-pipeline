from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
from .parser import parse_naver_search_page

def crawl_keyword(keyword: str) -> List[Dict[str, Any]]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://search.naver.com/search.naver?query={keyword}", timeout=60000)
        page.wait_for_timeout(3000)

        results = parse_naver_search_page(page)
        browser.close()
        return results
