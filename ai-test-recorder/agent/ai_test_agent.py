import os
import requests
import yaml
import subprocess
from bs4 import BeautifulSoup
from openai import OpenAI

# client = OpenAI()
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
CHECKLIST_PATH = "checklist/tests.yaml"


# -----------------------------
# 1 获取 HTML
# -----------------------------
def fetch_html(url):

    print("Fetching page:", url)

    r = requests.get(url)
    r.raise_for_status()

    return r.text


# -----------------------------
# 2 简化 DOM
# -----------------------------
def extract_dom(html):

    soup = BeautifulSoup(html, "html.parser")

    elements = []

    for tag in soup.find_all(["input", "button", "select", "a"]):

        el = {
            "tag": tag.name,
            "id": tag.get("id"),
            "name": tag.get("name"),
            "text": tag.text.strip()
        }

        elements.append(el)

    return elements


# -----------------------------
# 3 AI生成测试
# -----------------------------
def ai_generate_tests(url, html, elements):

    print("AI generating tests...")

    prompt = f"""
You are a senior Playwright automation testing engineer.

Your task is to generate **valid YAML test cases** for a web page.

Target URL:
{url}

Detected interactive HTML elements:
{elements}

IMPORTANT RULES:

1. Output MUST be valid YAML.
2. Root structure MUST be:

tests:
- name: test_name
  steps:

3. Only use the following actions:

goto
fill
click
expect_text

4. Field names MUST follow this schema:

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

5. ALWAYS use the field name **target** (NOT selector).

6. ALWAYS use **value** for expected text (NOT text).

7. Prefer stable selectors in this priority order:
   id → name → button text → tag

Examples:

target: "#username"
target: "input[name='email']"
target: "button"

8. Generate 1–2 realistic user flow test cases.

Example output:

tests:
- name: basic_page_test
  steps:
  - action: goto
    url: {url}
"""

    resp = client.chat.completions.create(
        # model="gpt-4o-mini",
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen3-max",
        messages=[
            {"role": "system", "content": "You generate web test cases."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    text = resp.choices[0].message.content

    return text


# -----------------------------
# 4 保存 YAML
# -----------------------------
def save_yaml(text):

    print("Saving tests.yaml")

    try:
        data = yaml.safe_load(text)
    except Exception:
        print("AI output invalid YAML, fallback template")

        data = {
            "tests":[
                {
                    "name":"ai_test",
                    "steps":[
                        {
                            "action":"goto",
                            "url":"http://localhost"
                        }
                    ]
                }
            ]
        }

    with open(CHECKLIST_PATH, "w") as f:
        yaml.dump(data, f)


# -----------------------------
# 5 运行测试
# -----------------------------
def run_tests():

    print("Running tests...")

    subprocess.run(["python", "runner/runner.py"])

    subprocess.run(["python", "report/report.py"])


# -----------------------------
# 主流程
# -----------------------------
def run_ai_test(url):

    html = fetch_html(url)

    elements = extract_dom(html)

    yaml_text = ai_generate_tests(url, html, elements)

    save_yaml(yaml_text)

    run_tests()

    print("Done. Open reports/report.html")


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("python agent/ai_test_agent.py <url>")
        sys.exit(1)

    run_ai_test(sys.argv[1])