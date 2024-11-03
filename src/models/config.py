from pathlib import Path
from typing import List, Optional, Set, Tuple

class GalleryConfig:
    def __init__(self):
        self.source_dirs: List[Path] = []
        self.destination_dir: Path = Path()
        self.organize_by_date: bool = True
        self.organize_by_type: bool = True
        self.create_thumbnails: bool = True
        self.thumbnail_size: Tuple[int, int] = (200, 200)
        self.file_extensions: Set[str] = {'.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef'}
        self.backup_enabled: bool = False
        self.backup_location: Optional[Path] = None
        self.organization_prompt: str = "{main}, {date:YYYY/MM}, {type}"
        self.custom_prompt: Optional[str] = None

    def add_source_directory(self, path: str | Path) -> None:
        source_path = Path(path)
        if source_path.exists():
            self.source_dirs.append(source_path)
        else:
            raise ValueError(f"Source directory does not exist: {path}")
