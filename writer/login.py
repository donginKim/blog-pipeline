# login.py

from playwright.sync_api import Page
from config import NAVER_ID, NAVER_PW

def naver_login(page: Page):
    page.goto("https://nid.naver.com/nidlogin.login")
    page.click('a#loinid')
    page.fill('input#id', NAVER_ID)
    page.fill('input#pw', NAVER_PW)
    page.click('button[type=submit]')
    page.wait_for_timeout(2000)
