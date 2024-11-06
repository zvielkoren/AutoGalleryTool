import json
from pathlib import Path
from tkinter import filedialog

from models.config import GalleryConfig

class Settings:
    def __init__(self, config_path: Path = Path("config.json")):
        self.config_path = config_path
        self.config = GalleryConfig()

    def save_settings(self) -> None:
        settings_dict = {
            "source_dirs": [str(path) for path in self.config.source_dirs],
            "destination_dir": str(self.config.destination_dir),
            "organize_by_date": self.config.organize_by_date,
            "organize_by_type": self.config.organize_by_type,
            "create_thumbnails": self.config.create_thumbnails,
            "thumbnail_size": self.config.thumbnail_size,
            "backup_enabled": self.config.backup_enabled,
            "backup_location": str(self.config.backup_location) if self.config.backup_location else None,
            "organization_prompt": self.config.organization_prompt,
            "custom_prompt": self.config.custom_prompt
        }

        with open(self.config_path, 'w') as f:
            json.dump(settings_dict, f, indent=4)

    def load_settings(self) -> GalleryConfig:
        if not self.config_path.exists():
            return self.config

        with open(self.config_path, 'r') as f:
            settings_dict = json.load(f)

        self.config.source_dirs = [Path(path) for path in settings_dict.get("source_dirs", [])]
        self.config.destination_dir = Path(settings_dict.get("destination_dir", ""))
        self.config.organize_by_date = settings_dict.get("organize_by_date", True)
        self.config.organize_by_type = settings_dict.get("organize_by_type", True)
        self.config.create_thumbnails = settings_dict.get("create_thumbnails", True)
        self.config.thumbnail_size = tuple(settings_dict.get("thumbnail_size", (200, 200)))
        self.config.backup_enabled = settings_dict.get("backup_enabled", False)
        backup_location = settings_dict.get("backup_location")
        self.config.backup_location = Path(backup_location) if backup_location else None
        self.config.organization_prompt = settings_dict.get("organization_prompt", "{main}, {date:YYYY/MM}, {type}")
        self.config.custom_prompt = settings_dict.get("custom_prompt")

        return self.config

    def add_source_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dirs.add(directory)
            self.update_source_listbox()
            self.save_current_settings()

    def choose_destination(self):
        directory = filedialog.askdirectory()
        if directory:
            self.destination_dir.set(directory)
            self.save_current_settings()

    def save(self):
        self.save_settings()


