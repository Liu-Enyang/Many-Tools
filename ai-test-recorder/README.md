# AI Test Recorder

一个简单的 **Web 自动化测试 Demo**，通过录制浏览器操作自动生成测试脚本，并执行测试生成报告。

适合用于：

- Web 自动化测试
- Checklist 自动执行
- Demo / PoC 项目
- AI 自动化测试平台原型

---

# 功能

当前版本支持：

- 浏览器操作录制（Playwright Codegen）
- Playwright 脚本自动转换为 YAML Checklist
- 自动执行 YAML 测试步骤
- 每一步自动截图
- 当前操作元素红框标记
- HTML 测试报告
- 支持多个 TestCase
- YAML 断言（expect_text）

---

# 技术栈

- Python
- Playwright
- YAML
- Jinja2

---

# 项目结构

```
ai-test-recorder
│
├── recorder/
│   └── recorder.py           # 浏览器操作录制
│
├── converter/
│   └── converter.py          # Playwright 脚本转 YAML
│
├── runner/
│   └── runner.py             # 执行 YAML 测试
│
├── report/
│   └── report.py             # 生成 HTML 报告
│
├── checklist/                # 测试用例
│   └── tests.yaml
│
├── reports/                  # 测试报告
│   ├── report.html
│   └── screenshots/
│
├── recorded_script.py        # 录制生成的 Playwright 脚本
└── test_page.html            # 本地测试页面
```

---

# 安装

安装 Python 依赖

```
pip install -r requirements.txt
```

安装 Playwright 浏览器

```
playwright install
```

---

# 使用流程

## 1 录制浏览器操作

启动录制：

```
python recorder.py http://localhost:8080
```

或录制本地页面：

```
python recorder.py file:///Users/liuenyang/Documents/GitHub/Many%20Tools/ai-test-recorder/test_page.html
```

录制完成后会生成：

```
recorded_script.py
```

---

## 2 生成 Checklist

将录制脚本转换为 YAML 测试用例：

```
python converter.py
```

生成文件：

```
checklist/tests.yaml
```

示例：

```
tests:
- name: login_test
  steps:
  - action: goto
    url: http://localhost:8080

  - action: fill
    target: '#username'
    value: admin

  - action: fill
    target: '#password'
    value: 123456

  - action: click
    target: role=button[name="Login"]

  - action: expect_text
    target: "#result"
    value: "Login success"
```

---

## 3 执行测试

执行 YAML 测试步骤：

```
python runner.py
```

执行过程中：

- 每个步骤都会执行浏览器操作
- 每一步都会自动截图
- 当前操作的控件会用红框高亮

截图位置：

```
reports/screenshots/
```

示例：

```
reports/screenshots/
login_test_0_pass.png
login_test_1_pass.png
login_test_2_fail.png
```

---

## 4 生成测试报告

生成 HTML 报告：

```
python report.py
```

报告位置：

```
reports/report.html
```

报告内容包含：

- TestCase 名称
- 执行步骤
- 执行结果（PASS / FAIL）
- 每一步的截图

---

# 示例报告

报告示例：

| Test | Step | Result | Screenshot |
|-----|-----|-----|-----|
| login_test | goto | PASS | view |
| login_test | fill username | PASS | view |
| login_test | click login | FAIL | view |

点击 **view** 可以查看当时页面截图。

---

# 后续可扩展功能

未来可以扩展：

- AI 自动生成测试步骤
- LLM 自动生成 YAML 测试用例
- 更智能的 selector 解析
- 并行执行测试
- Allure 风格测试报告
- CI/CD 自动执行测试（GitHub Actions）
- Web UI 测试管理界面