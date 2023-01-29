import json
import os

from ..app_manager import AppManager


class LocalRepository:
    """Handles/Manages a single repository given by path"""
    filename = "settings.json"

    def __init__(self, path: str, debug=False):
        self.debug = debug
        if self.debug:
            print("LocalRepository -> __init__():")

        if not os.path.exists(f"{path}{os.path.sep}.git"):
            raise Exception(f"Couldn't find .git folder at {path}.")

        self.path = path
        self.username = path.split("/")[-2]
        self.repository_name = path.split("/")[-1]

    def is_devtools_compatible(self):
        """Check if the app is devtools compatible"""
        try:
            with open(self.path) as f:
                data = json.load(f)
                if data["devtools"]:
                    return True
        except:
            pass
        return False

    def restart_app(self):
        """Restart the app at the given path"""
        return AppManager(self.path).restart_app()

    def start_app(self):
        """Start the app"""
        return AppManager(self.path).start_app()

    def stop_app(self):
        """Stop app"""
        return AppManager(self.path).stop_app()

