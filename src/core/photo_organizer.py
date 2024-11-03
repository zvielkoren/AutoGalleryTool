from pathlib import Path
from typing import Optional
from datetime import datetime
from ..models.tokens import TokenType, OrganizationToken
from ..models.metadata import ImageMetadata

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

    def parse(self, prompt: str):
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

    @staticmethod
    def _apply_custom_format(metadata: ImageMetadata, format_str: str) -> str:
        formatted = format_str
        if metadata.name:
            formatted = formatted.replace("%name", metadata.name)
        if metadata.tags:
            formatted = formatted.replace("%tags", '_'.join(metadata.tags))
        if metadata.camera_model:
            formatted = formatted.replace("%camera", metadata.camera_model)
        return formatted
