
import json
import os


class SettingsManager:
    """
 This module provides a SettingsManager class for managing application settings.
 Classes:
     SettingsManager: A class for managing application settings.
 Methods:
     load_settings(self): Loads settings from the JSON file.
     get_setting(self, key, default=None): Gets a setting by key, with an optional default.
     save_setting(self, key, value): Saves a setting by key.
     save_settings(self): Saves all settings to the JSON file.
     Usage:
         settings_manager = SettingsManager()
         settings_manager.get_setting("source_dir")
         settings_manager.save_setting("source_dir", "new_source_dir")
         settings_manager.save_settings()
     Example:
         settings_manager = SettingsManager()
         settings_manager.get_setting("source_dir")
         settings_manager.save_setting("source_dir", "new_source_dir")
         settings_manager.save_settings()
         Note:
             This module requires the 'json' module for loading and saving settings.
             The settings file is located at 'C:\\Users\\zvicr\Documents\\Proj\\Python-Projects\\AutoGalleryTool\\config\\settings.json'.
             The settings file is loaded and saved using the 'json' module.
             The settings file is saved to the same location as the script.

 """
    def __init__(self, settings_file="C:\\Users\\zvicr\Documents\\Proj\\Python-Projects\\AutoGalleryTool\\config\\settings.json"):
        """Initializes the SettingsManager with a settings file."""
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        """
        Loads settings from the JSON file.

        :param settings_file: The path to the settings file.

        :return: A dictionary of settings.
        """
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"Settings file '{self.settings_file}' not found.")

    def get_setting(self, key, default=None):

        """
        Gets a setting by key, with an optional default.
        :param key: The key of the setting to get.
        :param default: The default value to return if the setting is not found.

        :return: The value of the setting, or the default value if the setting is not found.
        """
        return self.settings.get(key, default)

    def save_settings(self):
        """
        Saves current settings to the JSON file.

        """
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file, indent=4)

    def update_setting(self, key, value):
        """
        Updates a setting and saves to the JSON file.
        :param key: The key of the setting to update.
        :param value: The new value for the setting.

        """
        self.settings[key] = value
        self.save_settings()
