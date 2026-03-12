import yaml
from playwright.sync_api import sync_playwright


CHECKLIST_FILE = "checklist/test.yaml"


def execute():

    with open(CHECKLIST_FILE) as f:
        data = yaml.safe_load(f)

    steps = data["steps"]

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for step in steps:

            try:

                action = step["action"]

                if action == "goto":
                    page.goto(step["url"])

                elif action == "fill":
                    page.fill(step["target"], step["value"])

                elif action == "click":
                    page.click(step["target"])

                results.append({
                    "result": "PASS",
                    "step": step
                })

            except Exception as e:

                results.append({
                    "result": "FAIL",
                    "step": step,
                    "error": str(e)
                })

        browser.close()

    return results


if __name__ == "__main__":

    results = execute()

    for r in results:
        print(r)