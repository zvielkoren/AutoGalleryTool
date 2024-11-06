import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from pathlib import Path

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGallery Tool Launcher")
        self.root.geometry("400x300")

        # Set icon using PhotoImage instead of iconbitmap
        icon_path = Path(__file__).parent / "assets" / "icons" / "AutoGalleryTool_Icon.png"
        if icon_path.exists():
            icon = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, icon)

        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(expand=True)

        title_label = ttk.Label(
            main_frame,
            text="AutoGallery Tool",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)

        # Add buttons with modern styling
        style = ttk.Style()
        style.configure("Launch.TButton", padding=10)

        ttk.Button(
            main_frame,
            text="Launch Desktop Version",
            command=self.launch_desktop,
            style="Launch.TButton",
            width=25
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Launch Web Version",
            command=self.launch_web,
            style="Launch.TButton",
            width=25
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Exit",
            command=root.quit,
            width=25
        ).pack(pady=20)

    def launch_desktop(self):
        desktop_path = Path(__file__).parent / "main.py"
        subprocess.Popen([sys.executable, str(desktop_path)])

    def launch_web(self):
        web_path = Path(__file__).parent / "web" / "app.py"
        subprocess.Popen([sys.executable, str(web_path)])

