import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("file:///Users/liuenyang/Documents/GitHub/Many%20Tools/ai-test-recorder/test_page.html")
    page.get_by_role("textbox", name="Enter username").click()
    page.get_by_role("textbox", name="Enter username").fill("liu")
    page.get_by_role("textbox", name="Enter username").press("Enter")
    page.get_by_role("textbox", name="Enter username").fill("liu")
    page.get_by_role("textbox", name="Enter username").press("Tab")
    page.locator("#password").fill("12")
    page.locator("#password").press("Tab")
    page.locator("#message").fill("34")
    page.locator("#message").press("Tab")
    page.locator("#country").select_option("cn")
    page.get_by_role("radio").first.check()
    page.get_by_role("button", name="Submit").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
