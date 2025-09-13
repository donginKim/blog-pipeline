from __future__ import annotations
import os
from playwright.sync_api import Page, Frame, TimeoutError as PWTimeoutError

NAVER_ID = os.getenv("NAVER_ID", "")
NAVER_PW = os.getenv("NAVER_PW", "")

TARGET_AFTER_LOGIN = os.getenv(
    "NAVER_AFTER_LOGIN_URL",
    "https://blog.naver.com/GoBlogWrite.naver",
)

# 여러 DOM 변형을 고려한 다중 선택자
ID_SEL = "input#id, input[name='id']"
PW_SEL = "input#pw, input[name='pw']"
BTN_SEL = "button[type='submit'], button:has-text('로그인'), input[type='submit']"


def _find_login_context(page: Page) -> Page | Frame:
    """로그인 입력 필드가 위치한 컨텍스트(Page/Frame)를 찾는다."""
    try:
        if page.locator(ID_SEL).count() > 0:
            return page
    except Exception:
        pass
    for fr in page.frames:
        try:
            if fr.locator(ID_SEL).count() > 0:
                return fr
        except Exception:
            continue
    return page

def naver_login(page: Page):
    # 로그인 페이지 이동 (DOMContentLoaded 까지만 기다리면 DOM 탐색이 더 빠름)
    page.goto("https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fsection.blog.naver.com%2FBlogHome.naver", wait_until="domcontentloaded")

    try:
        page.wait_for_selector("a#loinid, #loinid", timeout=3000)
        page.click("a#loinid, #loinid")
    except Exception:
        pass

    page.wait_for_timeout(500)

    ctx = _find_login_context(page)

    # 입력 필드 대기 + 디버깅 스크린샷
    try:
        ctx.wait_for_selector(ID_SEL, timeout=15000)
    except PWTimeoutError:
        try:
            page.screenshot(path="~/Workshop/monitors/login-timeout.png", full_page=True)
        except Exception:
            pass
        raise

    # 자주 바뀌는 DOM을 대비해 다중 셀렉터로 입력
    ctx.fill(ID_SEL, NAVER_ID)
    ctx.fill(PW_SEL, NAVER_PW)

    # 로그인 시도: 버튼 클릭 → 실패 시 Enter 제출
    try:
        ctx.click(BTN_SEL, timeout=5000)
    except Exception:
        try:
            ctx.press(PW_SEL, "Enter")
        except Exception:
            pass

    # 네트워크 안정화 대기
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(15000)

    # (중요) 로그인 후 원하는 페이지로 보장 이동
    try:
        page.wait_for_load_state("networkidle", timeout=3000)  # 남은 자동 리다이렉트 여지
    except Exception:
        pass

    if not page.url.startswith("https://blog.naver.com/GoBlogWrite.naver"):
        page.goto(TARGET_AFTER_LOGIN, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass