import os
import shutil
import subprocess

# 项目根目录
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_DIR, 'dist')
BUILD_DIR = os.path.join(PROJECT_DIR, 'build')
EXE_NAME = 'start_gui.exe'

# 1. 清理上次打包
if os.path.exists(DIST_DIR):
    shutil.rmtree(DIST_DIR)
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)

# 2. 确保 Playwright 浏览器已经下载
print("正在安装 Playwright 浏览器...")
# subprocess.run(['python', '-m', 'playwright', 'install'], check=True)

# 3. PyInstaller 打包命令
pyinstaller_cmd = [
    'pyinstaller',
    '--onefile',
    '--windowed',
    os.path.join(PROJECT_DIR, 'start_gui.py')
]

print("开始打包 exe 文件...")
subprocess.run(pyinstaller_cmd, check=True)

# 4. 打包完成提示
exe_path = os.path.join(DIST_DIR, EXE_NAME)
if os.path.exists(exe_path):
    print(f"打包完成！生成文件: {exe_path}")
else:
    print("打包完成，但未找到 exe 文件，请检查 PyInstaller 日志")