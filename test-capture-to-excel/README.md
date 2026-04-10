# Test Capture to Excel

一个用于 Windows 测试辅助的桌面工具。

---

## 作者

Mysoft Liu

---

## 功能

- GUI 操作
- 快捷键开始/结束（Ctrl + Alt + F9 / F10）
- Alt + PrintScreen 自动截图，自动去重
- 自动导出 Excel（截图按顺序排列，80% 比例缩放）
- 自动打开 Excel
- 支持自定义 Excel 标题、Sheet 名称、输出目录
- **整合功能**：将输出目录下所有会话的 Excel 合并为一个文件（按 Sheet 名升序排列）
- 最小化后自动缩到系统托盘，截图时弹出气泡提示

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

- 录制开始后，每次使用 `Alt + PrintScreen` 截图，程序会自动保存图片并弹出气泡通知
- 点击”结束并导出 Excel”后，会生成 Excel 并自动打开
- 支持通过 GUI 自定义 Excel 标题、Sheet 名称和输出目录
- 点击”整合文件”可将当前输出目录下所有会话的截图合并到一个 Excel（每个会话对应一个 Sheet）
- 最小化窗口后程序缩到系统托盘，双击图标可恢复窗口

## 快捷键

| 快捷键 | 功能 |
|---|---|
| `Ctrl + Alt + F9` | 开始录制 |
| `Ctrl + Alt + F10` | 结束录制并导出 Excel |
| `Alt + PrintScreen` | 截取当前活动窗口 |
