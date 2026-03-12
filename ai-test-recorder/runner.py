import yaml
import os
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "reports/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_tests():

    with open("checklist/tests.yaml") as f:
        data = yaml.safe_load(f)

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        for test in data["tests"]:

            page = browser.new_page()

            print("Running:", test["name"])

            for i, step in enumerate(test["steps"]):

                try:

                    action = step["action"]

                    if action == "goto":

                        page.goto(step["url"])


                    elif action == "click":

                        page.locator(step["target"]).click(timeout=10000)


                    elif action == "fill":

                        page.locator(step["target"]).fill(step["value"], timeout=10000)


                    elif action == "expect_text":

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