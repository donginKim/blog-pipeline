# smarteditor_utils/formatting.py

from playwright.sync_api import Frame

def toggle_formatting_button(frame: Frame, name: str):
    """
    주어진 이름의 포맷팅 버튼을 찾아 클릭하고 500ms 대기한다.

    :param frame: mainFrame (에디터의 iframe)
    :param name: data-name 속성 값 (예: "italic")
    """
    button = frame.locator(f'button[data-name="{name}"]')
    button.click()
    frame.page.wait_for_timeout(500)

def insert_formatted_text(frame: Frame, format_name: str, text: str):
    """
    지정된 포맷팅을 활성화하고, 주어진 텍스트를 입력한 후 500ms 대기하고, 다시 포맷팅을 비활성화한다.

    :param frame: mainFrame (에디터의 iframe)
    :param format_name: 포맷팅 버튼의 data-name 속성 값 (예: "italic")
    :param text: 포맷팅이 적용된 상태로 입력할 텍스트
    """
    toggle_formatting_button(frame, format_name)
    frame.page.keyboard.type(text)
    frame.page.wait_for_timeout(500)
    toggle_formatting_button(frame, format_name)