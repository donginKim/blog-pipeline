# smarteditor_utils/image.py

import time
import pyautogui
from typing import List
from playwright.sync_api import Frame

def insert_images(frame: Frame, image_paths: List[str], layout: str = "photo"):
    """
    스마트에디터에서 이미지 삽입 버튼을 클릭하고,
    지정된 이미지 파일들을 업로드한 뒤 이미지 배치 형식을 설정한다.

    :param frame: mainFrame (에디터의 iframe)
    :param image_paths: 업로드할 이미지 파일 경로 리스트
    :param layout: 이미지 배치 형식 ("개별사진", "콜라주", "슬라이드") 중 하나 (기본값: "photo")
    """
    # 1. "사진" 버튼 클릭
    frame.click('button.se-image-toolbar-button:has-text("사진")')
    time.sleep(3)

    # 2. OS 파일 선택 창 닫기 (pyautogui로 esc)
    pyautogui.press("esc")
    frame.page.wait_for_timeout(1000)

    # 3. 파일 업로드
    frame.locator('input#hidden-file').set_input_files(image_paths)
    frame.page.wait_for_timeout(3000)

    # 4. 이미지 배치 형식 적용
    if layout == "개별사진" or layout == "photo":
        frame.locator('label[for="image-type-list"]').click()
        frame.page.wait_for_timeout(3000)
    elif layout == "콜라주" or layout == "collage":
        frame.locator('label[for="image-type-collage"]').click()
        frame.page.wait_for_timeout(3000)
    elif layout == "슬라이드" or layout == "slide":
        frame.locator('label[for="image-type-slide"]').click()
        frame.page.wait_for_timeout(3000)
    else:
        raise ValueError('layout must be one of "개별사진", "콜라주", or "슬라이드"')