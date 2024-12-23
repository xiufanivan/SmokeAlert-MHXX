import os
import sys
import time
import simpleaudio as sa
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from PIL import ImageTk, Image


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class SmokeAlertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("烟雾弹提醒")
        self.root.geometry("400x300")

        self.style = ttkb.Style(theme="lumen")
        self.root.style = self.style
        self.icon_path = get_resource_path("icon.ico")

        if os.path.exists(self.icon_path):
            try:
                icon = Image.open(self.icon_path)
                photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(True, photo)
                print("成功使用 iconphoto 设置图标")
            except Exception as e:
                print(f"使用 iconphoto 设置图标出错：{e}")
        else:
            print("icon.ico 文件不存在，跳过设置图标")

        self.interval = tk.IntVar(value=55)
        self.is_running = False
        self.remaining_time = 0
        self.is_topmost = False
        self.sound_path = get_resource_path("alarm.wav")

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="烟雾弹提醒", font=("微软雅黑", 18, "bold")).pack(pady=10)

        frame = ttk.Frame(self.root)
        frame.pack(pady=10)
        ttk.Label(frame, text="时间间隔 (秒):", font=("微软雅黑", 12)).grid(row=0, column=0, padx=5)
        ttk.Entry(frame, textvariable=self.interval, width=4, font=("微软雅黑", 12)).grid(row=0, column=1, padx=5)

        self.timer_label = ttk.Label(self.root, text="剩余时间: --", font=("微软雅黑", 12), foreground="blue")
        self.timer_label.pack(pady=10)

        self.start_button = ttk.Button(self.root, text="启动", command=self.start_timer, width=10, takefocus=False)
        self.start_button.pack(pady=5)
        self.stop_button = ttk.Button(self.root, text="停止", command=self.stop_timer, width=10, state=tk.DISABLED,
                                      takefocus=False)
        self.stop_button.pack(pady=5)

        self.topmost_button = ttk.Button(self.root, text="置顶窗口", command=self.toggle_topmost, width=10,
                                         takefocus=False)
        self.topmost_button.pack(pady=5)

    def start_timer(self):
        if self.is_running:
            messagebox.showinfo("提示", "定时器已经在运行中！")
            return

        interval = self.interval.get()
        if interval <= 0:
            messagebox.showerror("错误", "时间间隔必须大于0！")
            return

        self.is_running = True
        self.remaining_time = interval
        self.update_timer_label()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.after_id = self.root.after(1000, self.timer_tick)

    def stop_timer(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)
        self.update_timer_label()  # 停止时更新标签显示"--"

    def timer_tick(self):
        if self.is_running:
            self.remaining_time -= 1
            self.update_timer_label()
            if self.remaining_time <= 0:
                Thread(target=self.play_sound, daemon=True).start()
                self.remaining_time = self.interval.get()
            self.after_id = self.root.after(1000, self.timer_tick)

    def play_sound(self):
        try:
            wave_obj = sa.WaveObject.from_wave_file(get_resource_path(self.sound_path))
            play_obj = wave_obj.play()
            while play_obj.is_playing() and self.is_running:
                time.sleep(0.1)
            if not self.is_running:
                play_obj.stop()
        except FileNotFoundError:
            messagebox.showerror("错误", "提示音文件未找到！")
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误：{e}")

    def update_timer_label(self):
        if self.is_running:
            self.timer_label.config(text=f"剩余时间: {self.remaining_time} 秒")
        else:
            self.timer_label.config(text=f"剩余时间: --")

    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        self.root.attributes('-topmost', self.is_topmost)
        if self.is_topmost:
            self.topmost_button.config(text="取消置顶")
        else:
            self.topmost_button.config(text="置顶窗口")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmokeAlertApp(root)
    root.mainloop()
