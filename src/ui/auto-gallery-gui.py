import tkinter as tk
from enum import Enum
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from queue import Queue
import logging
from typing import Optional, List
import os
import shutil
from datetime import datetime
from dataclasses import dataclass
from PIL import Image
import pillow_heif
import piexif
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



@dataclass
class ImageMetadata:
    date_taken: Optional[datetime]
    camera_model: Optional[str]
    file_type: str
    size: int
    dimensions: tuple[int, int]
    name: str = ""  # Added name field
    tags: List[str] = None  # Added tags field

class GalleryConfig:
    def __init__(self):
        self.source_dirs: List[Path] = []
        self.destination_dir: Path = Path()
        self.organize_by_date: bool = True
        self.organize_by_type: bool = True
        self.create_thumbnails: bool = True
        self.thumbnail_size: tuple[int, int] = (200, 200)
        self.file_extensions: set[str] = {'.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef'}
        self.backup_enabled: bool = False
        self.backup_location: Optional[Path] = None
        self.organization_prompt: str = "{main}, {date:YYYY/MM}, {type}"  # Added default organization prompt
        self.custom_prompt: Optional[str] = None  # Added custom prompt


    def add_source_directory(self, path: str | Path) -> None:
        source_path = Path(path)
        if source_path.exists():
            self.source_dirs.append(source_path)
        else:
            raise ValueError(f"Source directory does not exist: {path}")

class ImageProcessor:
    def __init__(self, config: GalleryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.photo_organizer = PhotoOrganizer()
        pillow_heif.register_heif_opener()
        self.observer = None

    def extract_metadata(self, image_path: Path) -> ImageMetadata:
        try:
            with Image.open(image_path) as img:
                dimensions = img.size
                file_type = img.format or image_path.suffix[1:].upper()
                date_taken = None
                camera_model = None

                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    if exif_data:
                        if 36867 in exif_data:  # DateTimeOriginal
                            try:
                                date_str = exif_data[36867]
                                date_taken = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                            except ValueError:
                                self.logger.warning(f"Could not parse date from EXIF: {date_str}")

                        if 272 in exif_data:  # Model
                            camera_model = exif_data[272]

                return ImageMetadata(
                    date_taken=date_taken,
                    camera_model=camera_model,
                    file_type=file_type,
                    size=image_path.stat().st_size,
                    dimensions=dimensions,
                    name=image_path.stem,
                    tags=[]  # Initialize empty tags list
                )

        except Exception as e:
            self.logger.error(f"Error processing {image_path}: {str(e)}")
            return None

    def organize_image(self, source_path: Path) -> None:
        if not source_path.suffix.lower() in self.config.file_extensions:
            return

        try:
            metadata = self.extract_metadata(source_path)
            if not metadata:
                return

            # Get the destination directory path from PhotoOrganizer
            dest_dir = self.photo_organizer.organize_by_prompt(
                self.config.organization_prompt,
                metadata,
                self.config.destination_dir,
                self.config.custom_prompt
            )

            # Create destination directory if it doesn't exist
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Create final destination path including filename
            final_dest = dest_dir / source_path.name

            # Copy file to destination
            shutil.copy2(source_path, final_dest)

            # Create thumbnail if enabled
            if self.config.create_thumbnails:
                self._create_thumbnail(source_path, final_dest)

            # Backup if enabled
            if self.config.backup_enabled and self.config.backup_location:
                backup_path = self.config.backup_location / final_dest.relative_to(self.config.destination_dir)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, backup_path)

        except Exception as e:
            self.logger.error(f"Error organizing {source_path}: {str(e)}")

    def _create_thumbnail(self, source_path: Path, dest_path: Path) -> None:
        try:
            with Image.open(source_path) as img:
                img.thumbnail(self.config.thumbnail_size)
                thumb_path = dest_path.parent / 'thumbnails' / dest_path.name
                thumb_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(thumb_path, quality=85, optimize=True)
        except Exception as e:
            self.logger.error(f"Error creating thumbnail for {source_path}: {str(e)}")

class FileWatcher(FileSystemEventHandler):
    def __init__(self, processor: ImageProcessor):
        self.processor = processor

    def on_created(self, event):
        if not event.is_directory:
            self.processor.organize_image(Path(event.src_path))

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
        self.status_queue = Queue()
        self.processor: Optional[ImageProcessor] = None
        self.custom_prompt = tk.StringVar()
        self.organization_prompt = tk.StringVar(value="{main}, {date:YYYY/MM}, {type}")
        # Create GUI elements
        self.create_widgets()

        # Set up logging to GUI
        self.setup_logging()

        # Start status update loop
        self.update_status()


    def create_widgets(self):
        # Source Directories Frame
        source_frame = ttk.LabelFrame(self.root, text="Source Directories", padding=10)
        source_frame.pack(fill=tk.X, padx=10, pady=5)

        self.source_listbox = tk.Listbox(source_frame, height=5)
        self.source_listbox.pack(fill=tk.X, expand=True)

        source_buttons = ttk.Frame(source_frame)
        source_buttons.pack(fill=tk.X, pady=5)

        ttk.Button(source_buttons, text="Add Directory",
                   command=self.add_source_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(source_buttons, text="Remove Selected",
                   command=self.remove_source_dir).pack(side=tk.LEFT)

        # Destination Directory Frame
        dest_frame = ttk.LabelFrame(self.root, text="Destination Directory", padding=10)
        dest_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Entry(dest_frame, textvariable=self.destination_dir).pack(side=tk.LEFT,
                                                                      fill=tk.X, expand=True)
        ttk.Button(dest_frame, text="Browse",
                   command=self.choose_destination).pack(side=tk.LEFT, padx=5)

        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Checkbutton(options_frame, text="Create Thumbnails",
                        variable=self.create_thumbnails).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Organize by Date",
                        variable=self.organize_by_date).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Organize by File Type",
                        variable=self.organize_by_type).pack(anchor=tk.W)

        # Backup Frame
        backup_frame = ttk.LabelFrame(self.root, text="Backup", padding=10)
        backup_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Checkbutton(backup_frame, text="Enable Backup",
                        variable=self.backup_enabled).pack(anchor=tk.W)

        backup_location_frame = ttk.Frame(backup_frame)
        backup_location_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(backup_location_frame,
                  textvariable=self.backup_location).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(backup_location_frame, text="Browse",
                   command=self.choose_backup).pack(side=tk.LEFT, padx=5)

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

        # Control Buttons with Enhanced Style
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

    def start_processing(self):
        """Start processing images in a separate thread"""
        self.start_btn["state"] = "disabled"
        self.stop_btn["state"] = "normal"

        try:
            config = self.create_config()
            self.processor = ImageProcessor(config)

            def process_thread():
                try:
                    # Process existing files
                    for source_dir in config.source_dirs:
                        for file_path in Path(source_dir).glob('*'):
                            if file_path.is_file():
                                self.processor.organize_image(file_path)

                    # Start watching for new files
                    observer = Observer()
                    event_handler = FileWatcher(self.processor)

                    for source_dir in config.source_dirs:
                        observer.schedule(event_handler, str(source_dir), recursive=False)

                    self.processor.observer = observer
                    observer.start()

                except Exception as e:
                    logging.error(f"Error during processing: {str(e)}")
                    messagebox.showerror("Error", f"Processing error: {str(e)}")

            # Start processing thread
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
        """Stop processing images"""
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

    def remove_source_dir(self):
        selection = self.source_listbox.curselection()
        if selection:
            directory = self.source_listbox.get(selection[0])
            self.source_dirs.remove(directory)
            self.update_source_listbox()

    def update_source_listbox(self):
        self.source_listbox.delete(0, tk.END)
        for directory in sorted(self.source_dirs):
            self.source_listbox.insert(tk.END, directory)

    def choose_destination(self):
        directory = filedialog.askdirectory()
        if directory:
            self.destination_dir.set(directory)

    def choose_backup(self):
        directory = filedialog.askdirectory()
        if directory:
            self.backup_location.set(directory)

    def setup_logging(self):
        class QueueHandler(logging.Handler):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue

            def emit(self, record):
                self.queue.put(self.format(record))

        # Configure logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Add queue handler
        queue_handler = QueueHandler(self.status_queue)
        queue_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(queue_handler)

    def update_status(self):
        """Update status text from queue"""
        while not self.status_queue.empty():
            message = self.status_queue.get()
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.see(tk.END)
        self.root.after(100, self.update_status)
    def create_config(self) -> GalleryConfig:
        """Create GalleryConfig from GUI settings"""
        config = GalleryConfig()

        # Validate required fields
        if not self.source_dirs:
            raise ValueError("No source directories selected")
        if not self.destination_dir.get():
            raise ValueError("No destination directory selected")

        # Set configuration
        for source_dir in self.source_dirs:
            config.add_source_directory(source_dir)

        config.destination_dir = Path(self.destination_dir.get())
        config.create_thumbnails = self.create_thumbnails.get()
        config.organize_by_date = self.organize_by_date.get()
        config.organize_by_type = self.organize_by_type.get()
        config.backup_enabled = self.backup_enabled.get()
        config.thumbnail_size = (200, 200)  # Add thumbnail size configuration
        config.file_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef'}  # Add supported file extensions

        if config.backup_enabled:
            if not self.backup_location.get():
                raise ValueError("Backup is enabled but no backup location selected")
            config.backup_location = Path(self.backup_location.get())
        return config

    



class TokenType(Enum):
    MAIN_FOLDER = "main"
    DATE = "date"
    TYPE = "type"
    TAGS = "tags"
    CAMERA = "camera"
    CUSTOM = "custom"

@dataclass
class OrganizationToken:
    type: TokenType
    format: Optional[str] = None

class PromptParser:
    def __init__(self):
        self.token_patterns = {
            "{main}": TokenType.MAIN_FOLDER,
            "{date:*}": TokenType.DATE,
            "{type}": TokenType.TYPE,
            "{tags}": TokenType.TAGS,
            "{camera}": TokenType.CAMERA,
            "{custom:*}": TokenType.CUSTOM
        }

    def parse(self, prompt: str) -> List[OrganizationToken]:
        tokens = []
        parts = prompt.split(',')

        for part in parts:
            part = part.strip()
            token = self._identify_token(part)
            if token:
                tokens.append(token)

        return tokens

    def _identify_token(self, part: str) -> Optional[OrganizationToken]:
        for pattern, token_type in self.token_patterns.items():
            if pattern.endswith('*}'):
                base_pattern = pattern[:-2]
                if part.startswith(base_pattern[:-1]):
                    format_str = part[len(base_pattern)-1:-1]
                    return OrganizationToken(token_type, format_str)
            elif part == pattern:
                return OrganizationToken(token_type)
        return None

class PhotoOrganizer:
    def __init__(self):
        self.parser = PromptParser()

    def organize_by_prompt(self, prompt: str, metadata: ImageMetadata, base_dest: Path, custom_prompt: Optional[str] = None) -> Path:
        tokens = self.parser.parse(prompt)
        path_parts = []

        for token in tokens:
            if token.type == TokenType.MAIN_FOLDER:
                path_parts.append(base_dest)
            elif token.type == TokenType.DATE:
                date_str = self._format_date(metadata.date_taken, token.format)
                path_parts.append(date_str)
            elif token.type == TokenType.TYPE:
                path_parts.append(metadata.file_type.lower())
            elif token.type == TokenType.TAGS:
                if metadata.tags:
                    path_parts.append('/'.join(metadata.tags))
            elif token.type == TokenType.CAMERA:
                if metadata.camera_model:
                    path_parts.append(metadata.camera_model)
            elif token.type == TokenType.CUSTOM:
                if custom_prompt:
                    formatted = self._apply_custom_format(metadata, custom_prompt)
                    path_parts.append(formatted)
                elif token.format:
                    formatted = self._apply_custom_format(metadata, token.format)
                    path_parts.append(formatted)

        return Path(*path_parts)
    @staticmethod
    def _format_date(date: datetime, format_str: Optional[str]) -> str:
        if not date:
            return "unknown_date"
        if format_str:
            return date.strftime(format_str)
        return date.strftime("%Y/%m/%d")

def stop_processing(self):
    """Stop processing images"""
    if self.processor and self.processor.observer:
        self.processor.observer.stop()
        self.processor.observer.join()
        logging.info("Stopped image processing.")
        messagebox.showinfo("Info", "Processing stopped")

def main():
    root = tk.Tk()
    app = AutoGalleryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()