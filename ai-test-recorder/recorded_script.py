import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:8000/demo/testpage.html")
    page.locator("#username").click()
    page.locator("#username").fill("wang")
    page.locator("#password").click()
    page.locator("#password").fill("234")
    page.get_by_role("button", name="Login").click()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
