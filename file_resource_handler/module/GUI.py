import os
import tkinter as tk
from tkinter import filedialog

from module.File_handler import File_handler


class GUI:
    def __init__(self):
        self.window = tk.Tk(className="file resource handler")

        self.button_select_dir = tk.Button(self.window, text="選擇目錄", command=self.choose_directory)
        self.button_select_dir.pack()

        self.button_image = tk.Button(self.window, text="壓縮圖片", command=self.compress_images)
        self.button_image.pack()

        self.label = tk.Label(self.window, text="目錄路徑：")
        self.label.pack()

        self.text = tk.Text(self.window, height=1)
        self.text.pack()

        self.directory_path = ""

    # 判斷選擇目錄
    def choose_directory(self):
        folder_path = filedialog.askdirectory()
        if os.path.exists(folder_path):
            print("已選擇目錄：", folder_path)
            self.directory_path = folder_path
            self.text.delete(1.0, tk.END)  # 刪除之前的目錄路徑
            self.text.insert(tk.END, folder_path)  # 顯示新的目錄路徑
        else:
            print("目錄不存在。")

    # 防呆機制要先選目錄
    def compress_images(self):
        if self.directory_path:
            File_handler(self.directory_path).handle_reading()
        else:
            print("請先選擇目錄。")

    # 介面驅動
    def show(self):
        self.window.mainloop()
