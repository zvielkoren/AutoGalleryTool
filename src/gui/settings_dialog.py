import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from typing import Tuple
from ..utils.settings import Settings


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.settings = settings
        self.title("Settings")
        self.geometry("500x600")

        # Initialize source directories list
        self.source_dirs = set(str(path) for path in settings.config.source_dirs)


        # Variables
        self.thumbnail_width = tk.StringVar(value=str(settings.config.thumbnail_size[0]))
        self.thumbnail_height = tk.StringVar(value=str(settings.config.thumbnail_size[1]))
        self.file_extensions = tk.StringVar(value=", ".join(settings.config.file_extensions))
        self.destination_dir = tk.StringVar(value=str(settings.config.destination_dir))
        self.organize_by_date = tk.BooleanVar(value=settings.config.organize_by_date)
        self.organize_by_type = tk.BooleanVar(value=settings.config.organize_by_type)
        self.create_thumbnails = tk.BooleanVar(value=settings.config.create_thumbnails)
        self.organization_prompt = tk.StringVar(value=settings.config.organization_prompt)
        self.backup_enabled = tk.BooleanVar(value=settings.config.backup_enabled)

        self.backup_location = tk.StringVar(value=str(settings.config.backup_location) if settings.config.backup_location else "")


        # Create widgets
        self.create_widgets()

        # Update listbox with current directories
        self.update_source_listbox()

    def update_source_listbox(self):
        self.source_listbox.delete(0, tk.END)
        for directory in sorted(self.source_dirs):
            self.source_listbox.insert(tk.END, directory)
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

        # Backup Settings
        backup_frame = ttk.LabelFrame(self, text="Backup Settings", padding=10)
        backup_frame.pack(fill=tk.X, padx=10, pady=5)

        self.backup_enabled = tk.BooleanVar(value=self.settings.config.backup_enabled)
        ttk.Checkbutton(backup_frame, text="Enable Backup",
                        variable=self.backup_enabled,
                        command=self.sync_config).pack(anchor=tk.W)

        backup_path_frame = ttk.Frame(backup_frame)
        backup_path_frame.pack(fill=tk.X, pady=5)
        self.backup_path = tk.StringVar(value=str(self.settings.config.backup_location or ""))
        ttk.Entry(backup_path_frame, textvariable=self.backup_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(backup_path_frame, text="Browse", command=self.choose_backup).pack(side=tk.LEFT, padx=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT)

    def sync_config(self, *args):
        """Sync current settings to config file"""
        self.settings.config.backup_enabled = self.backup_enabled.get()
        self.settings.config.backup_location = Path(self.backup_path.get()) if self.backup_path.get() else None
        # ... sync other settings ...
        self.settings.save_settings()

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
            self.settings.config.destination_dir = Path(directory)
            self.settings.save_settings()


    def save_settings(self):
        try:
            # Get current source directories from listbox
            source_dirs = []
            for i in range(self.source_listbox.size()):
                source_dirs.append(self.source_listbox.get(i))

            # Update config with current values
            self.settings.config.source_dirs = [Path(d) for d in source_dirs]
            self.settings.config.destination_dir = Path(self.destination_dir.get()) if self.destination_dir.get() else Path()
            self.settings.config.create_thumbnails = self.create_thumbnails.get()
            self.settings.config.organize_by_date = self.organize_by_date.get()
            self.settings.config.organize_by_type = self.organize_by_type.get()
            self.settings.config.backup_enabled = self.backup_enabled.get()

            if self.backup_enabled.get() and self.backup_location.get():
                self.settings.config.backup_location = Path(self.backup_location.get())

            # Save settings to file
            self.settings.save()

            # Show success message
            tk.messagebox.showinfo("Success", "Settings saved successfully")

            # Close settings dialog
            self.destroy()

        except Exception as e:
            tk.messagebox.showerror("Save Error", f"Could not save settings: {str(e)}")




    def choose_backup(self):
        directory = filedialog.askdirectory()
        if directory:
            self.backup_path.set(directory)
            self.sync_config()