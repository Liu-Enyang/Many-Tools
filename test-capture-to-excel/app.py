import io
import os
import time
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from PIL import ImageGrab, Image
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from pynput import keyboard


# =========================
# 数据模型
# =========================
@dataclass
class CaptureItem:
    index: int
    timestamp: datetime
    image_path: str
    hash_value: str


@dataclass
class CaptureSession:
    session_id: str
    session_dir: str
    excel_path: str
    captures: List[CaptureItem] = field(default_factory=list)
    is_recording: bool = False


# =========================
# 核心服务
# =========================
class TestCaptureApp:
    def __init__(self, ui_callback=None) -> None:
        self.base_output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(self.base_output_dir, exist_ok=True)

        self.session: Optional[CaptureSession] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        self.last_saved_hash: Optional[str] = None
        self.last_clipboard_hash: Optional[str] = None

        self.ui_callback = ui_callback

        # Excel 输出配置
        self.excel_title = "【カスタマイズ】　XXXの対応"
        self.sheet_name = "0001"
        self.output_dir = self.base_output_dir

    # -------------------------
    # UI 通知
    # -------------------------
    def _notify_ui(self) -> None:
        if self.ui_callback:
            self.ui_callback()

    # -------------------------
    # 会话管理
    # -------------------------
    def start_recording(self) -> bool:
        if self.session and self.session.is_recording:
            print("已经在录制中。")
            return False

        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(self.output_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)

        excel_path = os.path.join(session_dir, f"{session_id}_screenshots.xlsx")

        self.session = CaptureSession(
            session_id=session_id,
            session_dir=session_dir,
            excel_path=excel_path,
            captures=[],
            is_recording=True
        )

        self.last_saved_hash = None
        self.last_clipboard_hash = None
        self.stop_event.clear()

        # 开始录制时记录当前剪贴板，避免把旧图保存进去
        try:
            clipboard_obj = ImageGrab.grabclipboard()
            if isinstance(clipboard_obj, Image.Image):
                self.last_clipboard_hash = self._calculate_image_hash(clipboard_obj)
        except Exception:
            pass

        self.monitor_thread = threading.Thread(
            target=self._monitor_clipboard,
            daemon=True
        )
        self.monitor_thread.start()

        print("=" * 60)
        print(f"开始录制: {session_id}")
        print("请使用 Alt + PrintScreen 截取当前活动窗口。")
        print("结束快捷键: Ctrl + Alt + F10")
        print(f"输出目录: {session_dir}")
        print("=" * 60)

        self._notify_ui()
        return True

    def stop_recording(self) -> bool:
        if not self.session or not self.session.is_recording:
            print("当前没有录制中的会话。")
            return False

        self.session.is_recording = False
        self.stop_event.set()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)

        print("=" * 60)
        print("录制结束，开始导出 Excel...")
        self._export_to_excel()
        print(f"Excel 已生成: {self.session.excel_path}")
        print(f"共保存截图: {len(self.session.captures)} 张")
        print("=" * 60)

        self._notify_ui()
        return True

    def reset_session(self) -> None:
        if self.session and self.session.is_recording:
            return

        self.session = None
        self.last_saved_hash = None
        self.last_clipboard_hash = None
        self._notify_ui()

    # -------------------------
    # 剪贴板监听
    # -------------------------
    def _monitor_clipboard(self) -> None:
        while not self.stop_event.is_set():
            try:
                clipboard_obj = ImageGrab.grabclipboard()

                if clipboard_obj is None:
                    time.sleep(0.3)
                    continue

                if isinstance(clipboard_obj, Image.Image):
                    current_hash = self._calculate_image_hash(clipboard_obj)

                    # 剪贴板没变化，不处理
                    if current_hash == self.last_clipboard_hash:
                        time.sleep(0.3)
                        continue

                    self.last_clipboard_hash = current_hash
                    self._handle_clipboard_image(clipboard_obj, current_hash)

            except Exception as e:
                print(f"[剪贴板监听异常] {e}")

            time.sleep(0.3)

    def _handle_clipboard_image(self, image: Image.Image, img_hash: str) -> None:
        if not self.session or not self.session.is_recording:
            return

        if img_hash == self.last_saved_hash:
            return

        self.last_saved_hash = img_hash

        index = len(self.session.captures) + 1
        timestamp = datetime.now()
        filename = f"{index:03d}_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
        image_path = os.path.join(self.session.session_dir, filename)

        image.save(image_path, "PNG")

        item = CaptureItem(
            index=index,
            timestamp=timestamp,
            image_path=image_path,
            hash_value=img_hash
        )
        self.session.captures.append(item)

        print(f"[已保存] 第 {index} 张 -> {image_path}")
        self._notify_ui()

    @staticmethod
    def _calculate_image_hash(image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return hashlib.md5(buffer.getvalue()).hexdigest()

    # -------------------------
    # Excel 导出
    # -------------------------
    def _export_to_excel(self) -> None:
        if not self.session:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = self._safe_sheet_name(self.sheet_name)

        # 缩放
        ws.sheet_view.zoomScale = 80

        # 标题
        ws["A1"] = self.excel_title

        # 图片从第3行开始
        current_row = 3

        for item in self.session.captures:
            img_for_excel = self._create_resized_excel_image(item.image_path, max_width=800)
            anchor_cell = f"A{current_row}"
            ws.add_image(img_for_excel, anchor_cell)

            pil_img = Image.open(item.image_path)
            _, display_height = self._get_resized_size(
                pil_img.width,
                pil_img.height,
                max_width=800
            )

            estimated_rows = max(18, int(display_height / 20))

            for r in range(current_row, current_row + estimated_rows):
                ws.row_dimensions[r].height = 20

            # 下一张图从“结束行 + 3”开始
            current_row += estimated_rows + 2

        wb.save(self.session.excel_path)

    def _create_resized_excel_image(self, image_path: str, max_width: int = 800) -> XLImage:
        pil_img = Image.open(image_path)
        new_width, new_height = self._get_resized_size(
            pil_img.width,
            pil_img.height,
            max_width=max_width
        )

        xl_img = XLImage(image_path)
        xl_img.width = new_width
        xl_img.height = new_height
        return xl_img

    @staticmethod
    def _get_resized_size(width: int, height: int, max_width: int) -> tuple[int, int]:
        if width <= max_width:
            return width, height

        ratio = max_width / width
        return int(width * ratio), int(height * ratio)

    @staticmethod
    def _safe_sheet_name(name: str) -> str:
        invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
        safe_name = name
        for ch in invalid_chars:
            safe_name = safe_name.replace(ch, "_")
        safe_name = safe_name.strip() or "Sheet1"
        return safe_name[:31]


# =========================
# GUI
# =========================
class TestCaptureGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("辅助测试截图工具")
        self.root.geometry("800x770")
        self.root.minsize(760, 500)

        self.app = TestCaptureApp(ui_callback=self._refresh_ui_safe)
        self.hotkey_listener = None

        self.status_var = tk.StringVar(value="未开始")
        self.capture_count_var = tk.StringVar(value="0")
        self.session_dir_var = tk.StringVar(value="")
        self.excel_path_var = tk.StringVar(value="")
        self.output_dir_var = tk.StringVar(value=self.app.output_dir)
        self.title_var = tk.StringVar(value=self.app.excel_title)
        self.sheet_name_var = tk.StringVar(value=self.app.sheet_name)

        self.start_button: Optional[ttk.Button] = None
        self.stop_button: Optional[ttk.Button] = None
        self.reset_button: Optional[ttk.Button] = None

        self._build_ui()
        self._create_menu()
        self.refresh_ui()
        self.start_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_menu(self) -> None:
        menubar = tk.Menu(self.root)

        # Help 菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)

        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def show_about(self) -> None:
        messagebox.showinfo(
            "About",
            "Test Capture Tool v1.0\n\nAuthor: Mysoft Liu\n© 2026"
        )
    # -------------------------
    # 热键
    # -------------------------
    def start_hotkeys(self) -> None:
        self.hotkey_listener = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+<f9>": lambda: self.root.after(0, self.start_recording),
            "<ctrl>+<alt>+<f10>": lambda: self.root.after(0, self.stop_recording),
        })
        self.hotkey_listener.start()

    def stop_hotkeys(self) -> None:
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None

    # -------------------------
    # UI 构建
    # -------------------------
    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main,
            text="辅助测试截图工具",
            font=("Yu Gothic UI", 15, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 12))

        # 输出配置
        config_frame = ttk.LabelFrame(main, text="输出配置", padding=12)
        config_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(config_frame, text="Excel 标题").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Entry(config_frame, textvariable=self.title_var, width=72).grid(row=0, column=1, columnspan=2, sticky="ew", pady=6)

        ttk.Label(config_frame, text="Sheet 名称").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Entry(config_frame, textvariable=self.sheet_name_var, width=30).grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(config_frame, text="输出目录").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Entry(config_frame, textvariable=self.output_dir_var, width=56).grid(row=2, column=1, sticky="ew", pady=6)
        ttk.Button(config_frame, text="选择目录", command=self.choose_output_dir).grid(row=2, column=2, padx=(8, 0), pady=6)

        config_frame.columnconfigure(1, weight=1)

        # 状态区域
        status_frame = ttk.LabelFrame(main, text="当前状态", padding=12)
        status_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(status_frame, text="状态").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(status_frame, text="截图数量").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Label(status_frame, textvariable=self.capture_count_var).grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(status_frame, text="会话目录").grid(row=2, column=0, sticky="nw", padx=(0, 12), pady=6)
        ttk.Label(status_frame, textvariable=self.session_dir_var, wraplength=560).grid(row=2, column=1, sticky="w", pady=6)

        ttk.Label(status_frame, text="Excel 文件").grid(row=3, column=0, sticky="nw", padx=(0, 12), pady=6)
        ttk.Label(status_frame, textvariable=self.excel_path_var, wraplength=560).grid(row=3, column=1, sticky="w", pady=6)

        # 按钮区域
        button_frame = ttk.Frame(main)
        button_frame.pack(fill="x", pady=(0, 12))

        self.start_button = ttk.Button(button_frame, text="开始录制", command=self.start_recording)
        self.start_button.pack(side="left", padx=(0, 8))

        self.stop_button = ttk.Button(button_frame, text="结束并导出 Excel", command=self.stop_recording)
        self.stop_button.pack(side="left", padx=(0, 8))

        ttk.Button(button_frame, text="打开输出目录", command=self.open_output_dir).pack(side="left", padx=(0, 8))

        self.reset_button = ttk.Button(button_frame, text="清空状态", command=self.reset_session)
        self.reset_button.pack(side="left")

        # 说明区域
        help_frame = ttk.LabelFrame(main, text="使用说明", padding=12)
        help_frame.pack(fill="both", expand=True)

        help_text = (
            "开始方式：\n"
            "  1. 点击“开始录制”按钮\n"
            "  2. 或按快捷键 Ctrl + Alt + F9\n\n"
            "结束方式：\n"
            "  1. 点击“结束并导出 Excel”按钮\n"
            "  2. 或按快捷键 Ctrl + Alt + F10\n\n"
            "截图方式：\n"
            "  使用 Alt + PrintScreen 截取当前活动窗口。\n\n"
            "说明：\n"
            "  录制开始后，每次用 Alt + PrintScreen 截图，程序会自动保存图片。\n"
            "  结束后会自动生成 Excel，并直接打开保存好的 Excel 文件。"
        )
        ttk.Label(help_frame, text=help_text, justify="left").pack(anchor="w")

    # -------------------------
    # 设置
    # -------------------------
    def apply_settings(self) -> None:
        self.app.excel_title = self.title_var.get().strip() or "截图结果"
        self.app.sheet_name = self.sheet_name_var.get().strip() or "ScreenShots"
        self.app.output_dir = self.output_dir_var.get().strip() or self.app.base_output_dir
        os.makedirs(self.app.output_dir, exist_ok=True)

    def choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get() or os.getcwd())
        if selected:
            self.output_dir_var.set(selected)

    # -------------------------
    # 操作
    # -------------------------
    def start_recording(self) -> None:
        try:
            self.apply_settings()
            started = self.app.start_recording()
            self.refresh_ui()
            if not started:
                messagebox.showinfo("提示", "当前已经在录制中。")
        except Exception as e:
            messagebox.showerror("错误", f"开始录制失败：\n{e}")

    def stop_recording(self) -> None:
        try:
            stopped = self.app.stop_recording()
            self.refresh_ui()

            if not stopped:
                messagebox.showinfo("提示", "当前没有录制中的会话。")
                return

            if self.app.session and os.path.exists(self.app.session.excel_path):
                try:
                    os.startfile(self.app.session.excel_path)
                except Exception as open_err:
                    messagebox.showwarning(
                        "提示",
                        f"Excel 已生成，但自动打开失败：\n{open_err}\n\n文件位置：\n{self.app.session.excel_path}"
                    )
        except Exception as e:
            messagebox.showerror("错误", f"结束录制失败：\n{e}")

    def open_output_dir(self) -> None:
        path = ""
        if self.app.session and self.app.session.session_dir:
            path = self.app.session.session_dir
        else:
            path = self.output_dir_var.get().strip() or self.app.base_output_dir

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("错误", f"打开目录失败：\n{e}")

    def reset_session(self) -> None:
        if self.app.session and self.app.session.is_recording:
            messagebox.showwarning("提示", "录制中不能清空，请先结束录制。")
            return

        self.app.reset_session()
        self.refresh_ui()

    # -------------------------
    # 刷新UI
    # -------------------------
    def _refresh_ui_safe(self) -> None:
        self.root.after(0, self.refresh_ui)

    def refresh_ui(self) -> None:
        session = self.app.session

        if session and session.is_recording:
            self.status_var.set("录制中")
        elif session:
            self.status_var.set("已结束")
        else:
            self.status_var.set("未开始")

        if session:
            self.capture_count_var.set(str(len(session.captures)))
            self.session_dir_var.set(session.session_dir)
            self.excel_path_var.set(session.excel_path)
        else:
            self.capture_count_var.set("0")
            self.session_dir_var.set("")
            self.excel_path_var.set("")

        if self.start_button and self.stop_button and self.reset_button:
            if session and session.is_recording:
                self.start_button.state(["disabled"])
                self.stop_button.state(["!disabled"])
                self.reset_button.state(["disabled"])
            else:
                self.start_button.state(["!disabled"])
                self.stop_button.state(["!disabled"])
                self.reset_button.state(["!disabled"])

    # -------------------------
    # 关闭
    # -------------------------
    def on_close(self) -> None:
        try:
            self.app.stop_event.set()
            self.stop_hotkeys()
        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("vista")
    except tk.TclError:
        pass

    gui = TestCaptureGUI(root)
    root.mainloop()