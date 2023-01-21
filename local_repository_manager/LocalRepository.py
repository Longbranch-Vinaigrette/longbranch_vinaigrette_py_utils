import os

from src.utils.app_manager import AppManager

from src.utils.app_manager.RestartApp import RestartApp
from src.utils.local_repository_manager.AppInfo import AppInfo


class LocalRepository(AppInfo):
    """Handles/Manages a single repository given by path"""
    filename = "settings.json"

    def __init__(self, path: str, debug=False):
        super().__init__(path, "settings.json", debug)

        if not os.path.exists(f"{path}{os.path.sep}.git"):
            raise Exception(f"Couldn't find .git folder at {path}.")

        self.path = path
        self.username = path.split("/")[-2]
        self.repository_name = path.split("/")[-1]

    def restart_app(self):
        """Restart the app at the given path"""
        return RestartApp(self.repository_name, self.path)

    def start_app(self):
        """Start the app"""
        return AppManager(self.path).start_app()

    def setup_and_restart(self):
        """Setup and start"""
        return AppManager(self.path).setup_and_restart()

    def stop_app(self):
        """Stop app"""
        return AppManager(self.path).stop_app()

