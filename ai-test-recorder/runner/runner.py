import yaml
import os
import time
from playwright.sync_api import sync_playwright


def highlight(page, selector):

    try:

        page.evaluate("""
        () => {
            document.querySelectorAll('[data-ai-test-highlight]').forEach(el=>{
                el.style.outline=''
                el.removeAttribute('data-ai-test-highlight')
            })
        }
        """)

        handle = page.query_selector(selector)

        if handle:

            page.evaluate(
                """(el)=>{
                el.style.outline='3px solid red'
                el.setAttribute('data-ai-test-highlight','true')
                }""",
                handle
            )

    except:
        pass


def run_tests():

    results = []

    with open("checklist/tests.yaml") as f:

        tests = yaml.safe_load(f)["tests"]

    os.makedirs("reports/screenshots", exist_ok=True)

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        for test in tests:

            case_start = time.time()

            name = test["name"]

            for i, step in enumerate(test["steps"]):

                step_start = time.time()

                try:

                    action = step["action"]

                    if action == "goto":

                        page.goto(step["url"])

                    elif action == "click":

                        highlight(page, step["target"])
                        page.click(step["target"])

                    elif action == "fill":

                        highlight(page, step["target"])
                        page.fill(step["target"], step["value"])

                    elif action == "expect_text":

                        highlight(page, step["target"])
                        text = page.inner_text(step["target"])
                        assert step["value"] in text

                    screenshot = f"reports/screenshots/{name}_{i}.png"

                    page.screenshot(path=screenshot, full_page=True)

                    step_duration = round(time.time() - step_start, 3)

                    results.append({
                        "case": name,
                        "step": step,
                        "result": "PASS",
                        "duration": step_duration,
                        "screenshot": screenshot
                    })

                except Exception as e:

                    screenshot = f"reports/screenshots/{name}_{i}_fail.png"

                    page.screenshot(path=screenshot, full_page=True)

                    step_duration = round(time.time() - step_start, 3)

                    results.append({
                        "case": name,
                        "step": step,
                        "result": "FAIL",
                        "duration": step_duration,
                        "error": str(e),
                        "screenshot": screenshot
                    })

                    # stop executing remaining steps in this test case
                    break

            case_duration = round(time.time() - case_start, 3)

            results.append({
                "case": name,
                "type": "case_summary",
                "duration": case_duration
            })

        browser.close()

    return results