from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple

@dataclass
class ImageMetadata:
    date_taken: Optional[datetime]
    camera_model: Optional[str]
    file_type: str
    size: int
    dimensions: Tuple[int, int]
    name: str = ""
    tags: List[str] = None
