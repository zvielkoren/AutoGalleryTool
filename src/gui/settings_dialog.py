import tkinter as tk
from tkinter import ttk
from typing import Tuple
from ..utils.settings import Settings

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.settings = settings
        self.title("Settings")
        self.geometry("400x500")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Variables
        self.thumbnail_width = tk.StringVar(value=str(settings.config.thumbnail_size[0]))
        self.thumbnail_height = tk.StringVar(value=str(settings.config.thumbnail_size[1]))
        self.file_extensions = tk.StringVar(value=", ".join(settings.config.file_extensions))

        self.create_widgets()

    def create_widgets(self):
        # Thumbnail Settings
        thumb_frame = ttk.LabelFrame(self, text="Thumbnail Settings", padding=10)
        thumb_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(thumb_frame, text="Width:").pack(side=tk.LEFT)
        ttk.Entry(thumb_frame, textvariable=self.thumbnail_width, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Label(thumb_frame, text="Height:").pack(side=tk.LEFT)
        ttk.Entry(thumb_frame, textvariable=self.thumbnail_height, width=5).pack(side=tk.LEFT, padx=5)

        # File Extensions
        ext_frame = ttk.LabelFrame(self, text="Supported File Extensions", padding=10)
        ext_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(ext_frame, text="Extensions (comma separated):").pack(anchor=tk.W)
        ttk.Entry(ext_frame, textvariable=self.file_extensions).pack(fill=tk.X, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT)

    def save_settings(self):
        try:
            # Update thumbnail size
            width = int(self.thumbnail_width.get())
            height = int(self.thumbnail_height.get())
            self.settings.config.thumbnail_size = (width, height)

            # Update file extensions
            extensions = {ext.strip() for ext in self.file_extensions.get().split(",")}
            self.settings.config.file_extensions = extensions

            self.settings.save_settings()
            self.destroy()

        except ValueError as e:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numbers for thumbnail dimensions")
