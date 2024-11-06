import ctypes
import sys
import os
from pathlib import Path

from src.launcher import LauncherGUI
from src.utils.logs_utils import setup_logging
myappid = 'com.zvielkoren.AutoGalleryTool.1.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk

def main():
    setup_logging()

    root = tk.Tk()

    icon_path = Path(__file__).parent / "assets" / "icons" / "AutoGalleryTool_Icon.png"
    if icon_path.exists():
        icon = tk.PhotoImage(file=str(icon_path))
        root.iconphoto(True, icon)

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(expand=True)

    app = LauncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
