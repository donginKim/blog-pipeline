# main.py

from playwright.sync_api import sync_playwright
from google_drive.google_drive_downloader import download_today_images
from login import naver_login
from uploader import write_blog
from utils import delay

def run():
    download_today_images()  # 이미지 다운로드 먼저 실행

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
