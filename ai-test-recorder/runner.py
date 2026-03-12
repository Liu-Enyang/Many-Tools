import yaml
import os
from playwright.sync_api import sync_playwright

# Helper function to highlight elements
def highlight(page, selector):
    try:
        # Remove previous highlights
        page.evaluate(
            """() => {
                document.querySelectorAll('[data-ai-test-highlight]').forEach(el => {
                    el.style.outline = '';
                    el.style.outlineOffset = '';
                    el.removeAttribute('data-ai-test-highlight');
                });
            }"""
        )

        locator = page.locator(selector)
        handle = locator.element_handle(timeout=5000)

        if handle:
            page.evaluate(
                """(el) => {
                    el.style.outline = '3px solid red';
                    el.style.outlineOffset = '2px';
                    el.setAttribute('data-ai-test-highlight', 'true');
                }""",
                handle
            )
    except:
        pass

SCREENSHOT_DIR = "reports/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_tests():

    with open("checklist/tests.yaml") as f:
        data = yaml.safe_load(f)

    results = []

    with sync_playwright() as p:

        # browser = p.chromium.launch(headless=False)
        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        for test in data["tests"]:

            page = browser.new_page()

            print("Running:", test["name"])

            for i, step in enumerate(test["steps"]):

                try:

                    action = step["action"]

                    if action == "goto":

                        page.goto(step["url"])


                    elif action == "click":
                        highlight(page, step["target"])
                        page.locator(step["target"]).click(timeout=10000)

                    elif action == "fill":
                        highlight(page, step["target"])
                        page.locator(step["target"]).fill(step["value"], timeout=10000)

                    elif action == "expect_text":
                        highlight(page, step["target"])
                        text = page.locator(step["target"]).inner_text()
                        assert step["value"] in text


                    screenshot = f"{SCREENSHOT_DIR}/{test['name']}_{i}_pass.png"
                    page.screenshot(path=screenshot)

                    results.append({
                        "test": test["name"],
                        "step": action,
                        "result": "PASS",
                        "screenshot": screenshot
                    })

                except Exception as e:

                    screenshot = f"{SCREENSHOT_DIR}/{test['name']}_{i}_fail.png"

                    page.screenshot(path=screenshot)

                    results.append({
                        "test": test["name"],
                        "step": action,
                        "result": "FAIL",
                        "error": str(e),
                        "screenshot": screenshot
                    })

                    break

            page.close()

        browser.close()

    return results


if __name__ == "__main__":

    r = run_tests()

    for x in r:
        print(x)