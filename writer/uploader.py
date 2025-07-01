# uploader.py

import time
import pyautogui
from playwright.sync_api import Page, Frame
from config import CATEGORY_NO, UPLOAD_IMAGE_FILES, POST_TITLE, POST_BODY


def go_to_editor_page(page: Page) -> Frame:
    """에디터 페이지로 이동하고 mainFrame을 반환"""
    page.goto(f"https://blog.naver.com/steve1145?Redirect=Write&categoryNo={CATEGORY_NO}")
    page.wait_for_timeout(5000)
    return page.frame(name="mainFrame")


def upload_images(frame: Frame):
    """이미지 업로드 처리 (Esc, set_input_files 등 포함)"""
    frame.click('button.se-image-toolbar-button:has-text("사진")')
    time.sleep(3)
    pyautogui.press("esc")  # 파일 업로드 창 닫기
    frame.page.wait_for_timeout(1000)

    frame.locator('input#hidden-file').set_input_files(UPLOAD_IMAGE_FILES)
    frame.page.wait_for_timeout(3000)

    frame.locator('label[for="image-type-collage"]').click()
    frame.page.wait_for_timeout(3000)


def write_post_content(frame: Frame):
    """제목과 본문 작성"""
    # 본문 입력
    body_target = frame.locator('div.se-section.se-section-text div.se-module-text p')
    body_target.click()
    frame.page.keyboard.type(POST_BODY)
    frame.page.wait_for_timeout(1000)

    # 제목 입력
    title_target = frame.locator('div.se-section.se-section-documentTitle div.se-module-text p')
    title_target.click()
    frame.page.keyboard.type(POST_TITLE)
    frame.page.wait_for_timeout(1000)

    # 도움말 닫기
    help_close_button = frame.locator('button.se-help-panel-close-button')
    if help_close_button.count() > 0:
        help_close_button.click()
        frame.page.wait_for_timeout(500)


def publish_post(frame: Frame):
    """발행 버튼 클릭 및 확인"""
    publish_button = frame.locator('button.publish_btn__m9KHH')
    publish_button.wait_for(state="visible", timeout=15000)
    publish_button.click(force=True)

    confirm_button = frame.locator('button[data-testid="seOnePublishBtn"]')
    confirm_button.wait_for(state="visible", timeout=10000)
    confirm_button.click()


def write_blog(page: Page):
    """전체 글쓰기 실행 함수"""
    frame = go_to_editor_page(page)
    upload_images(frame)
    write_post_content(frame)
    publish_post(frame)
