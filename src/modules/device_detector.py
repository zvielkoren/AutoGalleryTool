"""
Detects connected external removable devices by checking available drive letters.


Returns:
    list: A list of connected removable devices.
"""
import os
import string
import subprocess
import logging
from src.config.settings import SettingsManager
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeviceDetector:
    def __init__(self):
        logger.info("Initializing DeviceDetector")
        self.settings_manager = SettingsManager()  # Create an instance
        settings = self.settings_manager.get_setting("device_detection")
        self.ignore_drives = settings["ignore_drives"]
        self.removable_drive_type = settings["removable_drive_type"]

    def detect_devices(self):
        """Detects connected external removable devices by checking available drive letters.

        Returns:
            list: A list of connected removable devices.
        """
        logger.info("Starting device detection")
        try:
            devices = [drive for drive in self.get_available_drives() if self.is_removable(drive)]
            logger.info(f"Detected {len(devices)} removable devices: {devices}")
            return devices
        except Exception as e:
            logger.error(f"Error during device detection: {str(e)}")
            return []

    def get_available_drives(self):
        """Returns a list of available drives on Windows."""
        logger.debug("Scanning for available drives")
        try:
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            logger.debug(f"Found drives: {drives}")
            return drives
        except Exception as e:
            logger.error(f"Error scanning drives: {str(e)}")
            return []

    def is_removable(self, drive):
        """Checks if a drive is removable by querying the drive type using `wmic`.

        Args:
            drive (str): The drive letter.

        Returns:
            bool: True if the drive is considered removable, otherwise False.
        """
        logger.debug(f"Checking if drive {drive} is removable")
        try:
            if not os.path.exists(drive):
                logger.warning(f"Drive {drive} does not exist")
                return False

            command = f"wmic logicaldisk where DeviceID='{drive[0]}:' get DriveType /value"
            logger.debug(f"Executing command: {command}")
            result = subprocess.run(command, capture_output=True, text=True, shell=False)

            if result.returncode != 0:
                logger.error(f"Command failed with return code {result.returncode}")
                return False

            drive_type_output = result.stdout.strip()
            drive_type = drive_type_output.split("=")[-1] if "=" in drive_type_output else None

            if not drive_type:
                logger.warning(f"Could not determine drive type for {drive}")
                return False

            is_removable = drive_type == self.removable_drive_type  # '2' indicates a removable drive
            logger.debug(f"Drive {drive} type: {drive_type}, is removable: {is_removable}")
            return is_removable
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking drive {drive}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking drive {drive}: {str(e)}")
            return False

