import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        # Source Directories Frame
        source_frame = ttk.LabelFrame(self, text="Source Directories", padding=10)
        source_frame.pack(fill=tk.X, padx=10, pady=5)

        self.source_listbox = tk.Listbox(source_frame, height=5)
        self.source_listbox.pack(fill=tk.X, expand=True)
        for dir_path in self.settings.config.source_dirs:
            self.source_listbox.insert(tk.END, str(dir_path))

        source_buttons = ttk.Frame(source_frame)
        source_buttons.pack(fill=tk.X, pady=5)
        ttk.Button(source_buttons, text="Add Directory",
               command=self.add_source_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(source_buttons, text="Remove Selected",
               command=self.remove_source_dir).pack(side=tk.LEFT)

        # Destination Directory Frame
        dest_frame = ttk.LabelFrame(self, text="Destination Directory", padding=10)
        dest_frame.pack(fill=tk.X, padx=10, pady=5)

        self.dest_dir = tk.StringVar(value=str(self.settings.config.destination_dir))
        ttk.Entry(dest_frame, textvariable=self.dest_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dest_frame, text="Browse",
               command=self.choose_destination).pack(side=tk.LEFT, padx=5)

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

    def add_source_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_listbox.insert(tk.END, directory)

    def remove_source_dir(self):
        selection = self.source_listbox.curselection()
        if selection:
            self.source_listbox.delete(selection[0])

    def choose_destination(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dest_dir.set(directory)
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
