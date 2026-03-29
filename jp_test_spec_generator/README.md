# JP Test Spec Generator

ASP.NET WebForms 画面资料解析工具。

## Phase 1
输入以下资料，生成 analysis.json：

- Summary.aspx
- Summary.aspx.cs
- spec.xlsx

## 输出
- output/analysis.json

## 环境准备

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## 运行
```bash
cd src
python main.py