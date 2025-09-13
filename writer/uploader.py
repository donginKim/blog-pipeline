from __future__ import annotations
from pathlib import Path
from typing import List
from playwright.sync_api import Page, TimeoutError as PWTimeoutError
import os
from datetime import datetime

from dsl import extract_title, extract_images, to_html

IMAGES_DIR = Path("images")

DEBUG_DIR = Path(os.getenv("DEBUG_DIR", "/app/debug"))

def _shot(page: Page, label: str):
    try:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = DEBUG_DIR / f"writer-{label}-{ts}.png"
        page.screenshot(path=str(path), full_page=True)
        print(f"[SHOT] {path}")
        return str(path)
    except Exception as e:
        print(f"[SHOT-ERROR] {e}")
        return None

def _set_title(frame: Frame, title: str):
    title_target = frame.locator('div.se-section.se-section-documentTitle div.se-module-text p')
    title_target.click()
    frame.page.keyboard.type(title)
    frame.page.wait_for_timeout(1000)

def _set_body_html(frame: Frame, body: str):
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

def _insert_images(page: Page, group: List[int]):
    try:
        paths = [str(IMAGES_DIR / f"{i}.jpg") for i in group]
        page.click("button[aria-label='사진'], button[title='사진']")
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(paths)
        page.wait_for_selector("img[src*='blogfiles'], img[src*='postfiles']", timeout=30000)
    except PWTimeoutError:
        _shot(page, f"image-timeout-{'_'.join(map(str, group))}")
        raise
    except Exception:
        _shot(page, f"image-error-{'_'.join(map(str, group))}")
        raise

def _publish_post(frame: Frame):

    publish_button = frame.locator('button.publish_btn__m9KHH')
    publish_button.wait_for(state="visible", timeout=15000)
    publish_button.click(force=True)

    confirm_button = frame.locator('button[data-testid="seOnePublishBtn"]')
    confirm_button.wait_for(state="visible", timeout=10000)
    confirm_button.click()

def write_blog_from_dsl(page: Page, dsl_text: str):
    title, body = extract_title(dsl_text)
    images, body2 = extract_images(body)

    if title:
        _set_title(page.main_frame, title)
    _set_body_html(page.main_frame, body2)

    for block in images:
        _insert_images(page, block.indexes)
        # TODO: block.layout == 'collage'면 에디터 UI에서 레이아웃 클릭 추가

    try:
        _publish_post(page.main_frame)
    except Exception:
        _shot(page, "publish-error")
        raise
    page.wait_for_timeout(1500)