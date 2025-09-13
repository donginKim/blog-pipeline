from playwright.sync_api import Frame

def set_text_alignment(frame: Frame, alignment: str):
    """
    스마트에디터에서 정렬 드롭다운을 클릭한 후,
    지정된 정렬 방식 (left, center, right, justify)을 선택한다.

    :param frame: mainFrame (에디터의 iframe)
    :param alignment: 정렬 방식 ("left", "center", "right", "justify")
    """
    # 1. 정렬 드롭다운 버튼 클릭
    dropdown_button = frame.locator('button[data-name="align-drop-down-with-justify"]')
    dropdown_button.click()
    frame.page.wait_for_timeout(500)

    # 2. 정렬 옵션 클릭
    if alignment not in {"left", "center", "right", "justify"}:
        raise ValueError('정렬 값은 "left", "center", "right", "justify" 중 하나여야 합니다.')

    option_button = frame.locator(f'button[data-value="{alignment}"]')
    option_button.click()
    frame.page.wait_for_timeout(500)