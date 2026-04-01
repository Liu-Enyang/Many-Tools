# Test Capture to Excel

一个用于 Windows 测试辅助的桌面工具。

---

## 作者

Mysoft Liu

---

## 功能

- GUI 操作
- 快捷键开始/结束
- Alt + PrintScreen 自动截图
- 自动导出 Excel
- 自动打开 Excel

---

## 环境

- Windows 10 / 11
- Python 3.10+

---

## 使用步骤

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

#### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

#### CMD

```cmd
venv\Scripts\activate.bat
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行程序

```bash
python app.py
```

---

## 打包 EXE

### 安装打包工具

```bash
pip install pyinstaller
```

### 执行打包

```bash
pyinstaller --clean test_capture_gui.spec
```

---

## 输出结果

打包完成后，生成的 EXE 在：

```text
dist\TestCaptureToExcel\TestCaptureToExcel.exe
```

---

## 说明

- 录制开始后，每次使用 `Alt + PrintScreen` 截图，程序会自动保存图片
- 点击“结束并导出 Excel”后，会生成 Excel 并自动打开
- 支持通过 GUI 自定义 Excel 标题和 Sheet 名称
