# AI Test Recorder

一个简单的 Web 自动化测试 Demo。

功能：

- 浏览器操作录制
- 自动生成 Checklist
- 自动执行测试
- HTML 报告

技术：

- Python
- Playwright
- YAML
- Jinja2

---

# 安装

pip install -r requirements.txt

安装浏览器

playwright install

---

# 使用流程

1 录制浏览器操作

python recorder.py http://localhost:8080

生成

recorded_script.py

---

2 转换为 Checklist

python converter.py

生成

checklist/test.yaml

---

3 执行测试

python runner.py

---

4 生成测试报告

python report.py

报告位置

reports/report.html