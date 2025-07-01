# main.py

from playwright.sync_api import sync_playwright
from login import naver_login
from uploader import write_blog
from utils import delay

def run():
    delay(2)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        naver_login(page)
        write_blog(page)

        browser.close()

if __name__ == "__main__":
    run()
