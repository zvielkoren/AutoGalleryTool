import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from queue import Queue
import logging
from typing import Optional
from watchdog.observers import Observer
import sys
import os
from .settings_dialog import SettingsDialog
from ..models.config import GalleryConfig
from ..core.image_processor import ImageProcessor
from ..core.file_watcher import FileWatcher
from ..utils.settings import Settings

import ctypes

myappid = 'com.zvielkoren.AutoGalleryTool.1.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
class AutoGalleryGUI:
    def get_resource_path(self):
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent
        else:
            base_path = Path(__file__).parent.parent.parent
        return base_path / "assets" / "icons"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AutoGallery Tool")
        self.root.geometry("600x700")

        # Initialize settings first
        self.settings = Settings()
        self.config = self.settings.load_settings()

        # Initialize variables with settings values
        self.source_dirs = set(str(path) for path in self.config.source_dirs)
        self.destination_dir = tk.StringVar(value=str(self.config.destination_dir))
        self.create_thumbnails = tk.BooleanVar(value=self.config.create_thumbnails)
        self.organize_by_date = tk.BooleanVar(value=self.config.organize_by_date)
        self.organize_by_type = tk.BooleanVar(value=self.config.organize_by_type)
        self.backup_enabled = tk.BooleanVar(value=self.config.backup_enabled)
        self.backup_location = tk.StringVar(value=str(self.config.backup_location) if self.config.backup_location else "")
        self.organization_prompt = tk.StringVar(value=self.config.organization_prompt)
        self.custom_prompt = tk.StringVar()
        self.status_queue = Queue()
        self.processor = None

        # Create GUI elements
        self.create_widgets()

        # Load icons
        icon_path = self.get_resource_path() / "AutoGalleryTool_Icon.png"
        try:
            window_icon = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, window_icon)
            self.window_icon = window_icon
        except Exception as e:
            print(f"Icon path: {icon_path}")
            print(f"Error loading icon: {e}")

        self.setup_logging()
        self.update_status()
    def sync_config(self):
        """Sync current GUI state with config file"""
        self.settings.config.source_dirs = [Path(d) for d in self.source_dirs]
        self.settings.config.destination_dir = Path(self.destination_dir.get())
        self.settings.config.create_thumbnails = self.create_thumbnails.get()
        self.settings.config.organize_by_date = self.organize_by_date.get()
        self.settings.config.organize_by_type = self.organize_by_type.get()
        self.settings.config.backup_enabled = self.backup_enabled.get()
        self.settings.config.backup_location = Path(self.backup_location.get()) if self.backup_location.get() else None
        self.settings.config.organization_prompt = self.organization_prompt.get()
        self.settings.config.custom_prompt = self.custom_prompt.get() if self.custom_prompt.get() else None

        self.settings.save_settings()
    def create_widgets(self):


        # Organization Pattern Frame
        pattern_frame = ttk.LabelFrame(self.root, text="Organization Pattern", padding=10)
        pattern_frame.pack(fill=tk.X, padx=10, pady=5)

        patterns = [
            ("{main}, {date:YYYY/MM}, {type}", "Basic - By Date and Type"),
            ("{main}, {date:YYYY}, {camera}, {custom:event_%name}", "Advanced - With Camera and Event"),
            ("{main}, {tags}, {date:YYYY-MM-DD}", "With Tags")
        ]

        for pattern, desc in patterns:
            btn = ttk.Button(pattern_frame, text=desc,
                             command=lambda p=pattern: self.organization_prompt.set(p))
            btn.pack(anchor=tk.W, pady=2)

        self.prompt_entry = ttk.Entry(pattern_frame, textvariable=self.organization_prompt, width=50)
        self.prompt_entry.pack(fill=tk.X, pady=5)

        # Custom Format Options
        custom_frame = ttk.LabelFrame(self.root, text="Custom Format Options", padding=10)
        custom_frame.pack(fill=tk.X, padx=10, pady=5)

        # Available tags
        tags_frame = ttk.LabelFrame(custom_frame, text="Available Tags", padding=5)
        tags_frame.pack(fill=tk.X, pady=5)

        available_tags = [
            ("%name", "Original filename"),
            ("%tags", "Image tags"),
            ("%camera", "Camera model"),
            ("%date", "Date taken"),
            ("%type", "File type")
        ]

        for tag, desc in available_tags:
            ttk.Label(tags_frame, text=f"{tag} - {desc}").pack(anchor=tk.W)

        # Custom format input
        format_input = ttk.Frame(custom_frame)
        format_input.pack(fill=tk.X, pady=5)

        ttk.Label(format_input, text="Custom Format:").pack(side=tk.LEFT)
        self.custom_entry = ttk.Entry(format_input, textvariable=self.custom_prompt, width=40)
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Quick format buttons
        quick_formats = [
            ("Event", "event_%name"),
            ("Date-Event", "event_%name_%date"),
            ("Camera-Event", "%camera_event_%name")
        ]

        quick_frame = ttk.Frame(custom_frame)
        quick_frame.pack(fill=tk.X, pady=5)

        for label, fmt in quick_formats:
            btn = ttk.Button(quick_frame, text=label,
                             command=lambda f=fmt: self.custom_prompt.set(f))
            btn.pack(side=tk.LEFT, padx=2)
        # Progress Frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create text widget with scrollbar
        self.log_text = tk.Text(progress_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(progress_frame, orient="vertical",
                                  command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control Buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        style = ttk.Style()
        style.configure("Start.TButton", background="green")
        style.configure("Stop.TButton", background="red")

        self.start_btn = ttk.Button(control_frame, text="▶ Start Processing",
                                    command=self.start_processing,
                                    style="Start.TButton", width=20)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⬛ Stop",
                                   command=self.stop_processing,
                                   style="Stop.TButton", width=20)
        self.stop_btn.pack(side=tk.LEFT)
        self.stop_btn["state"] = "disabled"
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Checkbutton(options_frame, text="Create Thumbnails",
                        variable=self.create_thumbnails).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Organize by Date",
                        variable=self.organize_by_date).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Organize by File Type",
                        variable=self.organize_by_type).pack(anchor=tk.W)

    # Add the settings button here
        ttk.Button(options_frame, text="Advanced Settings",
               command=self.show_settings_dialog).pack(anchor=tk.W, pady=5)

    def show_settings_dialog(self):
        SettingsDialog(self.root, self.settings)

    def setup_logging(self):
        class QueueHandler(logging.Handler):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue

            def emit(self, record):
                self.queue.put(self.format(record))

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        queue_handler = QueueHandler(self.status_queue)
        queue_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(queue_handler)

    def update_status(self):
        while not self.status_queue.empty():
            message = self.status_queue.get()
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.see(tk.END)
        self.root.after(100, self.update_status)

    def create_config(self) -> GalleryConfig:
        config = GalleryConfig()

        if not self.source_dirs:
            raise ValueError("No source directories selected")
        if not self.destination_dir.get():
            raise ValueError("No destination directory selected")

        for source_dir in self.source_dirs:
            config.add_source_directory(source_dir)

        config.destination_dir = Path(self.destination_dir.get())
        config.create_thumbnails = self.create_thumbnails.get()
        config.organize_by_date = self.organize_by_date.get()
        config.organize_by_type = self.organize_by_type.get()
        config.backup_enabled = self.backup_enabled.get()
        config.organization_prompt = self.organization_prompt.get()
        config.custom_prompt = self.custom_prompt.get() if self.custom_prompt.get() else None

        if config.backup_enabled:
            if not self.backup_location.get():
                raise ValueError("Backup is enabled but no backup location selected")
            config.backup_location = Path(self.backup_location.get())

        return config

    def start_processing(self):
        """Start processing images in a separate thread"""
        try:
            # Load current settings
            config = self.settings.load_settings()

            # Check if source directories exist and are set
            if not config.source_dirs or not any(Path(src).exists() for src in config.source_dirs):
                tk.messagebox.showinfo("Configuration Required", "Please configure source directories first")
                self.show_settings_dialog()
                return

            self.processor = ImageProcessor(config)
            self.start_btn["state"] = "disabled"
            self.stop_btn["state"] = "normal"

            def process_thread():
                try:
                    # Process existing files
                    for source_dir in config.source_dirs:
                        source_path = Path(source_dir)
                        if source_path.exists():
                            for file_path in source_path.glob('*'):
                                if file_path.is_file():
                                    self.processor.organize_image(file_path)

                    # Start watching for new files
                    observer = Observer()
                    event_handler = FileWatcher(self.processor)

                    for source_dir in config.source_dirs:
                        if Path(source_dir).exists():
                            observer.schedule(event_handler, str(source_dir), recursive=False)

                    observer.start()

                except Exception as e:
                    logging.error(f"Error during processing: {str(e)}")
                    messagebox.showerror("Error", f"Processing error: {str(e)}")

            # Start processing thread
            threading.Thread(target=process_thread, daemon=True).start()
            logging.info("Started processing images...")

        except ValueError as e:
            messagebox.showerror("Configuration Error", str(e))

    def stop_processing(self):
        if self.processor and self.processor.observer:
            self.processor.observer.stop()
            self.processor.observer.join()
            logging.info("Stopped image processing.")
            messagebox.showinfo("Info", "Processing stopped")

        self.start_btn["state"] = "normal"
        self.stop_btn["state"] = "disabled"



    def add_source_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dirs.add(directory)
            self.update_source_listbox()
            self.sync_config()
            logging.info(f"Added source directory: {directory}")

    def remove_source_dir(self):
        selection = self.source_listbox.curselection()
        if selection:
            directory = self.source_listbox.get(selection[0])
            self.source_dirs.remove(directory)
            self.update_source_listbox()
            self.sync_config()
            logging.info(f"Removed source directory: {directory}")

    def update_source_listbox(self):
        self.source_listbox.delete(0, tk.END)
        for directory in sorted(self.source_dirs):
            self.source_listbox.insert(tk.END, directory)

    def sync_config(self):
        self.settings.config.source_dirs = [Path(d) for d in self.source_dirs]
        self.settings.save_settings()

    def destroy(self):
        if self.processor and self.processor.observer:
            self.processor.observer.stop()
            self.processor.observer.join()
            logging.info("Stopped image processing.")

        # Call the parent class destroy method
        self.root.destroy()
        super().destroy()

