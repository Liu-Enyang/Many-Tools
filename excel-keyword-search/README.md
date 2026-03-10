# Excel Keyword Search Tool

一个简单易用的 **Excel 关键字搜索工具**。  
通过图形界面选择文件夹并输入关键字，程序会扫描该目录下的所有 Excel 文件，并将包含关键字的单元格位置汇总到一个新的 Excel 文件中。

适用于：

- 批量查找 Excel 数据
- 审计 / 财务数据检查
- 合同编号检索
- 公司内部数据搜索

---

# 功能特点

- 📂 选择文件夹扫描
- 🔎 搜索 Excel 单元格关键字
- 📊 实时搜索进度条
- 📄 显示当前扫描文件
- 📈 统计搜索结果数量
- 📁 支持 Excel 格式  
  - .xlsx  
  - .xlsm  
  - .xls  

搜索完成后自动生成：

search_results.xlsx

结果示例：

| File | Sheet | Cell | Value | Path |
|-----|------|------|------|------|
| test.xlsx | Sheet1 | B5 | contract123 | /data/test.xlsx |

---

# 项目结构

excel-keyword-search

├── excel_keyword_search.py  
├── requirements.txt  
├── README.md  
└── .gitignore

---

# 安装依赖

建议使用 **Python 3.9+**

---

# Mac / Linux 安装步骤

创建虚拟环境

python3 -m venv venv

激活虚拟环境

source venv/bin/activate

安装依赖

pip install -r requirements.txt

运行程序

python excel_keyword_search.py

---

# Windows 安装步骤

创建虚拟环境

python -m venv venv

激活虚拟环境

venv\\Scripts\\activate

安装依赖

pip install -r requirements.txt

运行程序

python excel_keyword_search.py

---

# 打包为可执行文件

使用 PyInstaller 打包。

Windows：

pyinstaller --onefile --noconsole excel_keyword_search.py

生成：

dist/excel_keyword_search.exe

Mac：

pyinstaller --onefile --noconsole excel_keyword_search.py

生成：

dist/excel_keyword_search

---

# requirements.txt

openpyxl  
xlrd  
pyinstaller  

安装：

pip install -r requirements.txt

---

# 使用方法

1. 打开程序  
2. 点击 Browse 选择 Excel 文件夹  
3. 输入需要搜索的关键字  
4. 点击 Start Search  
5. 程序自动生成 search_results.xlsx  

---

# License

MIT License

---

# 贡献

欢迎提交 Issue 或 Pull Request 来改进这个工具。
