import json
import os


class SettingsManager:
    def __init__(self, settings_file="../config/settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"Settings file '{self.settings_file}' not found.")

    def get_setting(self, key, default=None):
        """Gets a setting by key, with an optional default."""
        return self.settings.get(key, default)

    def save_settings(self):
        """Saves current settings to the JSON file."""
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file, indent=4)

    def update_setting(self, key, value):
        """Updates a setting and saves to the JSON file."""
        self.settings[key] = value
        self.save_settings()
