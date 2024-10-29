"""
This module provides a class for sorting files in a directory based on their file extension.

Classes:
    FileSorter: A class for sorting files in a directory based on their file extension.
    Methods:
        sort_files(self): Sorts files in the source directory into the destination directory based on file extension.
        move_file(self, filename): Moves a file from the source directory to the destination directory.
        check_file_extension(self, filename): Checks if a file has a valid file extension.


    Usage:
        sorter = FileSorter("source_dir", "destination_dir")
        sorter.sort_files()

Example:
        sorter = FileSorter("source_dir", "destination_dir")
        sorter.sort_files()

    Note:
        This module requires the 'os' module for file operations.
        It also requires the 'shutil' module for file operations.
It also requires the 'json' module for loading and saving settings.
"""

import os
import shutil

from config.settings import SettingsManager


class FileSorter:
    """
    A class for sorting files in a directory based on their file extension.
    Attributes:
        source_dir (str): The source directory where files are located.
        destination_dir (str): The destination directory where files will be sorted.
        files_extensions (dict): A dictionary of file extensions and their corresponding destination directories.
        settings_manager (SettingsManager): An instance of the SettingsManager class for managing settings.
    Methods:
        sort_files(self): Sorts files in the source directory into the destination directory based on file extension.
        move_file(self, filename): Moves a file from the source directory to the destination directory.
        check_file_extension(self, filename): Checks if a file has a valid file extension.

    """
    def __init__(self, source_dir, destination_dir):
        self.settings_manager = SettingsManager

        self.source_dir = self.settings_manager.get_setting("source_dir")
        self.destination_dir = self.settings_manager.get_setting("destination_dir")
        self.files_extensions = self.settings_manager.get_setting("files_extensions")

    def sort_files(self):
        """
        Sorts files in the source directory into the destination directory based on file extension.
        If the destination directory doesn't exist, it creates it.

        :return: None
        """
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)
        for filename in os.listdir(self.source_dir):
            if os.path.isfile(os.path.join(self.source_dir, filename)):
                self.move_file(filename)


    def move_file(self, filename):
        """
        Moves a file from the source directory to the destination directory.

        :param filename:
        :return:
        """
        source_path = os.path.join(self.source_dir, filename)
        destination_path = os.path.join(self.destination_dir, filename)
        shutil.move(source_path, destination_path)


    def check_extension(self, filename):
        """
        Checks if the file extension is in the list of allowed extensions.
        :param filename:
        :return: Boolean
        """
        file_extension = os.path.splitext(filename)[1]
        if file_extension in self.files_extensions:
            return True
        else:
            return False

