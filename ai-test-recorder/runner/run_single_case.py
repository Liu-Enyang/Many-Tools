import sys
import os
import json
import yaml
import traceback
import time
from playwright.sync_api import sync_playwright

STATE_FILE = "state/cases_state.json"

def run_case(case_file):
    # Ensure stdout is line-buffered for immediate print
    sys.stdout.reconfigure(line_buffering=True)

    case_name = os.path.splitext(os.path.basename(case_file))[0]

    # Load existing state
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    else:
        state = {}

    with open(case_file) as f:
        case = yaml.safe_load(f)

    steps = case.get("steps", [])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            case_start_time = None
            case_end_time = None
            for i, step in enumerate(steps):
                start_time = time.time()
                if case_start_time is None:
                    case_start_time = start_time

                action = step["action"]

                if action == "goto":
                    page.goto(step["url"])

                elif action == "fill":
                    page.fill(step["target"], step["value"])

                elif action == "click":
                    page.click(step["target"])

                elif action == "expect_text":
                    txt = page.locator(step["target"]).inner_text(timeout=10000)
                    assert step["value"] in txt

                end_time = time.time()
                step_duration = end_time - start_time

                # Record timing info and screenshot path in step
                step["start_time"] = start_time
                step["end_time"] = end_time
                step["duration"] = step_duration

                screenshot_dir = "reports/screenshots"
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshot_dir, f"{case_name}_{i}.png")
                page.screenshot(path=screenshot_path)
                step["screenshot"] = screenshot_path

                case_end_time = end_time

            case["case_duration"] = case_end_time - case_start_time if case_start_time and case_end_time else None

            # Write back updated case file with timing and screenshot info
            with open(case_file, "w") as f:
                yaml.safe_dump(case, f)

            browser.close()
            state[case_name] = "PASS"
            os.makedirs("state", exist_ok=True)
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
            sys.exit(0)

        except Exception as e:
            print(f"{case_name} FAIL:", e, flush=True)
            # traceback.print_exc()
            browser.close()
            state[case_name] = "FAIL"
            os.makedirs("state", exist_ok=True)
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
            sys.exit(1)
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python run_single_case.py <case_file>", flush=True)
        sys.exit(1)
    run_case(sys.argv[1])