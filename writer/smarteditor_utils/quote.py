# smarteditor_utils/quote.py

from playwright.sync_api import Frame

def insert_quote(frame: Frame, text: str):
    """
    스마트에디터에서 인용구 버튼을 눌러 인용 영역을 생성하고,
    해당 영역에 지정한 텍스트를 입력한다.

    :param frame: mainFrame (에디터의 iframe)
    :param text: 인용구에 입력할 텍스트
    """
    # 1. 인용구 버튼 클릭
    quote_button = frame.locator('button[data-name="quotation-layout"]')
    quote_button.click()
    frame.page.wait_for_timeout(1000)

    # 2. 생성된 인용구 영역의 span 또는 p 요소 선택
    quote_target = frame.locator(
        'div.se-section-quotation span.__se-node, div.se-section-quotation p'
    )
    quote_target.first.click()

    # 3. 텍스트 입력
    frame.page.keyboard.type(text)
    frame.page.wait_for_timeout(500)