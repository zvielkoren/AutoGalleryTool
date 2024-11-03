import logging
import shutil
from pathlib import Path
from PIL import Image
import pillow_heif
from ..models.config import GalleryConfig
from ..models.metadata import ImageMetadata
from .photo_organizer import PhotoOrganizer
from datetime import datetime

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
                    tags=[]
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

            # Move file to destination (instead of copy)
            shutil.move(source_path, final_dest)
            self.logger.info(f"Moved {source_path} to {final_dest}")

            # Create thumbnail if enabled
            if self.config.create_thumbnails:
                self._create_thumbnail(final_dest, final_dest)

            # Backup if enabled
            if self.config.backup_enabled and self.config.backup_location:
                backup_path = self.config.backup_location / final_dest.relative_to(self.config.destination_dir)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(final_dest, backup_path)
                self.logger.info(f"Backed up to {backup_path}")

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
