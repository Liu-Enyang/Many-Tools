import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from openpyxl import load_workbook, Workbook

class ExcelSearchApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Excel关键字搜索工具")
        self.root.geometry("520x260")

        self.folder_path = tk.StringVar()
        self.keyword = tk.StringVar()

        self.create_ui()

    def create_ui(self):

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="选择文件夹:").grid(row=0, column=0, sticky="w")

        tk.Entry(frame, textvariable=self.folder_path, width=40).grid(row=0, column=1)

        tk.Button(frame, text="浏览", command=self.select_folder).grid(row=0, column=2, padx=5)

        tk.Label(frame, text="输入关键字:").grid(row=1, column=0, pady=10, sticky="w")

        tk.Entry(frame, textvariable=self.keyword, width=40).grid(row=1, column=1)

        tk.Button(self.root, text="开始搜索", command=self.start_search, height=2, width=15).pack(pady=10)

        self.progress = ttk.Progressbar(self.root, length=400)
        self.progress.pack(pady=10)

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def start_search(self):

        if not self.folder_path.get():
            messagebox.showwarning("提示", "请选择文件夹")
            return

        if not self.keyword.get():
            messagebox.showwarning("提示", "请输入关键字")
            return

        thread = threading.Thread(target=self.search)
        thread.start()

    def search(self):

        folder = self.folder_path.get()
        keyword = self.keyword.get()

        excel_files = []

        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".xlsx") or file.endswith(".xlsm"):
                    excel_files.append(os.path.join(root, file))

        if not excel_files:
            messagebox.showinfo("提示", "未找到Excel文件")
            return

        self.progress["maximum"] = len(excel_files)

        results = []

        for i, file_path in enumerate(excel_files):

            try:
                wb = load_workbook(file_path, data_only=True)

                for sheet in wb.sheetnames:

                    ws = wb[sheet]

                    for row in ws.iter_rows():
                        for cell in row:

                            if cell.value:

                                value = str(cell.value)

                                if keyword in value:
                                    results.append([
                                        os.path.basename(file_path),
                                        sheet,
                                        cell.coordinate,
                                        value,
                                        file_path
                                    ])

            except:
                pass

            self.progress["value"] = i + 1
            self.status_label.config(text=f"正在扫描: {i+1}/{len(excel_files)}")

        self.save_results(results)

    def save_results(self, results):

        if not results:
            messagebox.showinfo("完成", "未找到包含关键字的内容")
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "搜索结果"

        ws.append(["文件名", "Sheet", "单元格", "内容", "完整路径"])

        for r in results:
            ws.append(r)

        save_path = os.path.join(self.folder_path.get(), "搜索结果.xlsx")

        wb.save(save_path)

        messagebox.showinfo("完成", f"搜索完成！结果已保存:\n{save_path}")


if __name__ == "__main__":

    root = tk.Tk()
    app = ExcelSearchApp(root)
    root.mainloop()