# Test Capture to Excel

一个用于 Windows 测试辅助的桌面工具。

------------------------------------------------------------------------

## 作者

Mysoft Liu

------------------------------------------------------------------------

## 功能

-   GUI 操作
-   快捷键开始/结束
-   Alt+PrintScreen 自动截图
-   自动导出 Excel
-   自动打开 Excel

------------------------------------------------------------------------

## 环境

-   Windows 10/11
-   Python 3.10+

------------------------------------------------------------------------

## 使用步骤

1.  创建虚拟环境： python -m venv venv

2.  激活： .`\venv`{=tex}`\Scripts`{=tex}`\Activate`{=tex}.ps1

3.  安装依赖： pip install -r requirements.txt

4.  运行： python app.py

------------------------------------------------------------------------

## 打包

pip install pyinstaller pyinstaller --clean test_capture_gui.spec

------------------------------------------------------------------------

## 输出

dist`\TestCaptureToExcel`{=tex}`\TestCaptureToExcel`{=tex}.exe
