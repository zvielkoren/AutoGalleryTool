# main.py
import time

from modules.device_detector import DeviceDetector
from modules.sorting_files import FileSorter
from config.settings import SettingsManager



def main():
    settings_manager = SettingsManager()
    src_dir = settings_manager.get_setting("source_dir")
    dest_dir = settings_manager.get_setting("destination_dir")

    fileSorter = FileSorter(src_dir, dest_dir)
    fileSorter.sort_files()
if __name__ == "__main__":
    main()
