# uploader.py

import time
import pyautogui
from playwright.sync_api import Page, Frame
from parser import parse_post_file
from config import CATEGORY_NO, UPLOAD_IMAGE_FILES

def go_to_editor_page(page: Page) -> Frame:
    """에디터 페이지로 이동하고 mainFrame을 반환"""
    page.goto(f"https://blog.naver.com/steve1145?Redirect=Write&categoryNo={CATEGORY_NO}")
    page.wait_for_timeout(5000)
    return page.frame(name="mainFrame")

def write_post_title(frame: Frame, title: str):
    """제목 작성"""
    # 제목 입력
    title_target = frame.locator('div.se-section.se-section-documentTitle div.se-module-text p')
    title_target.click()
    frame.page.keyboard.type(title)
    frame.page.wait_for_timeout(1000)

def write_post_content(frame: Frame, body: str):
    """본문 작성 (DSL 파서 적용)"""
    from smarteditor_utils.dsl_parser import parse_and_execute_dsl

    # 본문 입력 포커싱
    body_target = frame.locator('div.se-section.se-section-text div.se-module-text p')
    body_target.click()
    frame.page.wait_for_timeout(500)

    # DSL 파서 실행
    parse_and_execute_dsl(frame, body)

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
    title, body = parse_post_file("post.txt")
    frame = go_to_editor_page(page)
    write_post_title(frame, title)
    write_post_content(frame, body)
    publish_post(frame)
