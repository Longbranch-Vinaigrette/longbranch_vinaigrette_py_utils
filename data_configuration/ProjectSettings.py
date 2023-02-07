"""Get important project information stored on the given app/project path"""
import json
import os


class ProjectSettings:
    settings = None

    def __init__(self, path: str, debug=False):
        """Get app/project information/settings data"""
        self.path = path
        self.debug = debug

        try:
            with open(f"{path}{os.path.sep}settings.json") as f:
                self.settings = json.load(f)
        except Exception as ex:
            raise Exception(f"The app at {self.path} is not DevTools compatible.")

    def get_settings(self):
        """Get settings"""
        return self.settings
