from playwright.sync_api import Frame

def insert_separator(frame: Frame, line_type: str = "default"):
    """
    스마트에디터에서 구분선을 삽입한다.

    :param frame: mainFrame (에디터의 iframe)
    :param line_type: "default", "line1" ~ "line7" 중 하나
    """
    # 유효성 검사
    valid_types = {"default"} | {f"line{i}" for i in range(1, 8)}
    if line_type not in valid_types:
        raise ValueError(f"line_type 값은 {valid_types} 중 하나여야 합니다.")

    # 1. 구분선 드롭다운 버튼 클릭
    dropdown_trigger = frame.locator('button.se-document-toolbar-select-option-button[data-name="horizontal-line"]')
    dropdown_trigger.click()
    frame.page.wait_for_timeout(300)

    # 2. 원하는 구분선 옵션 클릭
    dropdown_container = frame.locator('div.se-toolbar-option-insert-horizontal-line[role="listbox"]')
    option_button = dropdown_container.locator(f'button[data-value="{line_type}"]')
    option_button.click()
    frame.page.wait_for_timeout(500)