# start_gui.py
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# 默认路径
AI_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_URL = "http://localhost:8000/demo/testpage.html"

def start_demo():
    """启动本地 demo 页面"""
    demo_file = os.path.join(AI_TEST_DIR, "testpage.html")
    if not os.path.exists(demo_file):
        messagebox.showerror("错误", f"{demo_file} 不存在")
        return
    subprocess.Popen(["python", os.path.join(AI_TEST_DIR, "start_demo.py")])
    messagebox.showinfo("提示", f"已启动 demo 页面: {DEMO_URL}")

def record_action():
    """录制操作，用户输入 URL"""
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("错误", "请输入 URL")
        return
    recorder_script = os.path.join(AI_TEST_DIR, "recorder", "recorder.py")
    if not os.path.exists(recorder_script):
        messagebox.showerror("错误", f"{recorder_script} 不存在")
        return
    subprocess.Popen(["python", recorder_script, url])
    messagebox.showinfo("提示", f"正在录制操作: {url}")

def run_tests():
    """执行 YAML 测试"""
    runner_script = os.path.join(AI_TEST_DIR, "runner", "runner.py")
    if not os.path.exists(runner_script):
        messagebox.showerror("错误", f"{runner_script} 不存在")
        return
    subprocess.Popen(["python", runner_script])
    messagebox.showinfo("提示", "测试执行中，请查看 reports 目录")

def generate_checklist():
    """生成 Checklist"""
    converter_script = os.path.join(AI_TEST_DIR, "converter", "converter.py")
    if not os.path.exists(converter_script):
        messagebox.showerror("错误", f"{converter_script} 不存在")
        return
    subprocess.run(["python", converter_script])
    messagebox.showinfo("提示", "Checklist 生成完成")

def generate_report():
    """生成 HTML 报告"""
    report_script = os.path.join(AI_TEST_DIR, "report", "report.py")
    if not os.path.exists(report_script):
        messagebox.showerror("错误", f"{report_script} 不存在")
        return
    subprocess.Popen(["python", report_script])
    messagebox.showinfo("提示", "报告生成中，请查看 reports/report.html")

# GUI 主窗口
root = tk.Tk()
root.title("AI Test Recorder GUI")
root.geometry("400x250")

# URL 输入
tk.Label(root, text="录制 URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack()
url_entry.insert(0, DEMO_URL)

# 按钮
tk.Button(root, text="启动 Demo 页面", width=30, command=start_demo).pack(pady=5)
tk.Button(root, text="录制操作", width=30, command=record_action).pack(pady=5)
tk.Button(root, text="生成 Checklist", width=30, command=generate_checklist).pack(pady=5)
tk.Button(root, text="执行 YAML 测试", width=30, command=run_tests).pack(pady=5)
tk.Button(root, text="生成报告", width=30, command=generate_report).pack(pady=5)

root.mainloop()