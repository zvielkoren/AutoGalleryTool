from pathlib import Path
from watchdog.events import FileSystemEventHandler
from .image_processor import ImageProcessor

class FileWatcher(FileSystemEventHandler):
    def __init__(self, processor: ImageProcessor):
        self.processor = processor

    def on_created(self, event):
        if not event.is_directory:
            self.processor.organize_image(Path(event.src_path))
