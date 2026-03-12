import os
import requests
import yaml
import subprocess
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

CHECKLIST_PATH = "checklist/tests.yaml"
REPORT_PATH = "reports/report.html"

# -----------------------------
# 1 获取 HTML
# -----------------------------

def fetch_html(url):

    print("Fetching page:", url)

    r = requests.get(url)
    r.raise_for_status()

    return r.text


# -----------------------------
# 2 DOM 智能压缩
# -----------------------------

def extract_dom(html):

    soup = BeautifulSoup(html, "html.parser")

    elements = []

    for tag in soup.find_all(["input", "button", "select", "a", "textarea"]):

        el = {
            "tag": tag.name,
            "id": tag.get("id"),
            "name": tag.get("name"),
            "type": tag.get("type"),
            "placeholder": tag.get("placeholder"),
            "text": tag.text.strip()
        }

        elements.append(el)

    return elements


# -----------------------------
# 3 selector AI 优化
# -----------------------------

def build_selector(el):

    if el.get("id"):
        return f"#{el['id']}"

    if el.get("name"):
        return f"[name='{el['name']}']"

    if el.get("text"):
        txt = el["text"].replace("\n", " ").strip()
        if len(txt) < 30:
            return f"text={txt}"

    return el.get("tag")


# -----------------------------
# 4 AI生成多场景测试
# -----------------------------

def ai_generate_tests(url, html, elements):

    print("AI generating tests...")

    prompt = f"""
You are a senior Playwright automation engineer.

Generate MULTIPLE realistic UI test scenarios.

URL:
{url}

DOM elements:
{elements}

Requirements:

Return VALID YAML.

Structure:

tests:
- name: case_name
  steps:

Allowed actions:

goto
fill
click
expect_text

Schema:

goto:
  action: goto
  url: PAGE_URL

fill:
  action: fill
  target: CSS_SELECTOR
  value: TEXT

click:
  action: click
  target: CSS_SELECTOR

expect_text:
  action: expect_text
  target: CSS_SELECTOR
  value: EXPECTED_TEXT

Rules:

use field names:
action
target
value

Generate scenarios like:

login_success
empty_input_validation
navigation_flow

Prefer selectors:
#id
[name='x']
button text

Return ONLY YAML.
"""

    resp = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": "You generate Playwright YAML tests."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return resp.choices[0].message.content


# -----------------------------
# YAML 自动修复
# -----------------------------

def normalize_yaml(data):

    if not data or "tests" not in data:
        return data

    for test in data["tests"]:

        for step in test.get("steps", []):

            if "selector" in step and "target" not in step:
                step["target"] = step.pop("selector")

            if "text" in step and "value" not in step:
                step["value"] = step.pop("text")

            if "target" in step:

                t = step["target"]

                if isinstance(t, str) and t.startswith("input#"):
                    step["target"] = "#" + t.split("#")[1]

                if isinstance(t, str) and t.startswith("button#"):
                    step["target"] = "#" + t.split("#")[1]

            # fix goto action using target instead of url
            if step.get("action") == "goto":

                # AI sometimes outputs target instead of url
                if "target" in step and "url" not in step:
                    step["url"] = step.pop("target")

                # if value accidentally used
                if "value" in step and "url" not in step:
                    step["url"] = step.pop("value")

                # ensure url exists
                if "url" not in step:
                    step["url"] = "http://localhost"

    return data


# -----------------------------
# 保存 YAML
# -----------------------------

def save_yaml(text):

    print("Saving tests.yaml")

    try:
        data = yaml.safe_load(text)
        data = normalize_yaml(data)

    except Exception:

        print("AI YAML invalid, fallback template")

        data = {
            "tests": [
                {
                    "name": "ai_test",
                    "steps": [
                        {
                            "action": "goto",
                            "url": "http://localhost"
                        }
                    ]
                }
            ]
        }

    os.makedirs("checklist", exist_ok=True)

    with open(CHECKLIST_PATH, "w") as f:
        yaml.dump(data, f)


# -----------------------------
# 执行测试
# -----------------------------

def run_tests():

    print("Running tests...")

    subprocess.run(["python", "runner/runner.py"])

    subprocess.run(["python", "report/report.py"])


# -----------------------------
# 解析错误信息
# -----------------------------

def parse_error():

    if not os.path.exists(REPORT_PATH):
        return "report missing"

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    if "selector" in html:
        return "selector not found"

    if "Timeout" in html:
        return "timeout"

    if "expect" in html:
        return "assertion failed"

    if "FAIL" in html:
        return "test failed"

    return "unknown"


# -----------------------------
# AI 修复 YAML
# -----------------------------

def ai_fix_tests(url, elements, previous_yaml, error_summary):

    print("AI fixing failed tests...")

    prompt = f"""
The following YAML Playwright tests failed.

Error:
{error_summary}

DOM:
{elements}

Previous YAML:
{previous_yaml}

Fix the YAML so tests pass.

Rules:
- Keep YAML structure
- Use actions: goto fill click expect_text
- Use fields: action target value

Return ONLY YAML.
"""

    resp = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": "You fix Playwright YAML tests."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return resp.choices[0].message.content


# -----------------------------
# 检查 FAIL
# -----------------------------

def report_has_fail():

    if not os.path.exists(REPORT_PATH):
        return True

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    return "FAIL" in html


# -----------------------------
# 主 Agent
# -----------------------------

def run_ai_test(url):

    html = fetch_html(url)

    elements = extract_dom(html)

    yaml_text = ai_generate_tests(url, html, elements)

    save_yaml(yaml_text)

    max_retry = 1

    for i in range(max_retry):

        print(f"\n=== Test Attempt {i+1} ===")

        run_tests()

        if not report_has_fail():
            print("All tests PASS")
            break

        error = parse_error()

        print("Detected error:", error)

        with open(CHECKLIST_PATH, "r") as f:
            current_yaml = f.read()

        yaml_text = ai_fix_tests(
            url,
            elements,
            current_yaml,
            error
        )

        save_yaml(yaml_text)

    print("Done. Open reports/report.html")


# -----------------------------
# CI 支持
# -----------------------------

def run_ci():

    url = os.getenv("TEST_URL")

    if not url:
        print("CI mode requires TEST_URL env")
        return

    run_ai_test(url)


# -----------------------------
# main
# -----------------------------

if __name__ == "__main__":

    import sys

    if os.getenv("CI"):
        run_ci()
        exit()

    if len(sys.argv) < 2:
        print("Usage:")
        print("python agent/ai_test_agent.py <url>")
        exit(1)

    run_ai_test(sys.argv[1])