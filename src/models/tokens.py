from enum import Enum
from dataclasses import dataclass
from typing import Optional

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
