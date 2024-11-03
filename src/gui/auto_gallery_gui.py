import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from queue import Queue
import logging
from typing import Optional
from watchdog.observers import Observer

from ..models.config import GalleryConfig
from ..core.image_processor import ImageProcessor
from ..core.file_watcher import FileWatcher

class AutoGalleryGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AutoGallery Tool")
        self.root.geometry("600x700")

        # Variables
        self.source_dirs = set()
        self.destination_dir = tk.StringVar()
        self.create_thumbnails = tk.BooleanVar(value=True)
        self.organize_by_date = tk.BooleanVar(value=True)
        self.organize_by_type = tk.BooleanVar(value=True)
        self.backup_enabled = tk.BooleanVar(value=False)
        self.backup_location = tk.StringVar()
        self.organization_prompt = tk.StringVar(value="{main}, {date:YYYY/MM}, {type}")
        self.custom_prompt = tk.StringVar()
        self.status_queue = Queue()
        self.processor: Optional[ImageProcessor] = None

        self.create_widgets()
        self.setup_logging()
        self.update_status()

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
        self.start_btn["state"] = "disabled"
        self.stop_btn["state"] = "normal"

        try:
            config = self.create_config()
            self.processor = ImageProcessor(config)

            def process_thread():
                try:
                    for source_dir in config.source_dirs:
                        for file_path in Path(source_dir).glob('*'):
                            if file_path.is_file():
                                self.processor.organize_image(file_path)

                    observer = Observer()
                    event_handler = FileWatcher(self.processor)

                    for source_dir in config.source_dirs:
                        observer.schedule(event_handler, str(source_dir), recursive=False)

                    self.processor.observer = observer
                    observer.start()

                except Exception as e:
                    logging.error(f"Error during processing: {str(e)}")
                    messagebox.showerror("Error", f"Processing error: {str(e)}")

            threading.Thread(target=process_thread, daemon=True).start()
            logging.info("Started processing images...")

        except ValueError as e:
            messagebox.showerror("Configuration Error", str(e))
            self.start_btn["state"] = "normal"
            self.stop_btn["state"] = "disabled"
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            self.start_btn["state"] = "normal"
            self.stop_btn["state"] = "disabled"

    def stop_processing(self):
        if self.processor and self.processor.observer:
            self.processor.observer.stop()
            self.processor.observer.join()
            logging.info("Stopped image processing.")
            messagebox.showinfo("Info", "Processing stopped")

        self.start_btn["state"] = "normal"
        self.stop_btn["state"] = "disabled"
