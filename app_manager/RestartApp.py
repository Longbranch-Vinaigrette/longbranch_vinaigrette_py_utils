import os
import pprint
from threading import Thread

from ..dbs.RepositorySettings import RepositorySettings
from .. import Debug
from ..app_manager import AppManager


class RestartApp:
    """Keeping for backwards compatibility reasons"""
    def __init__(
            self,
            repository_name: str,
            repository_path: str,
            unique_key: str = "",
            full_name: str = "",
            only_restart_if_start_on_boot_is_enabled: bool = False,
            debug: bool = False
    ):
        # Get names and stuff
        self.path = repository_path
        self.full_name = full_name
        self.username = self.path.split(os.path.sep)[-2]
        self.repository_name = repository_name
        self.unique_key = unique_key
        self.only_restart_if_start_on_boot_is_enabled = only_restart_if_start_on_boot_is_enabled
        self.debug = debug

        if self.debug:
            print("RestartApp -> __init__():")
            print(f"Repository pulled: {self.repository_name}")
            print(f"Repository path: {self.path}")
            print(f"Username: {self.username}")

        # Get app settings
        repository_settings = RepositorySettings()
        self.app_settings = repository_settings.get_repository(
            self.username,
            self.repository_name)

        self.restart_app()

    def restart_app(self):
        """Restart app

        Restarts an app if it's enabled"""
        # Should debug app manager?
        if self.debug:
            print("RestartApp -> restart_app():")

        # The app is not enabled, don't restart
        if self.only_restart_if_start_on_boot_is_enabled:
            if not self.app_settings["start_on_boot"]:
                if self.debug:
                    print("The app is not enabled, therefore it's not necessary to restart "
                          "the app.")
                return

        if self.debug:
            print("App settings: ")
            pprint.pprint(self.app_settings)
            print(f"Is enabled?: {self.app_settings['enabled']}")
            print(f"Setup finalized?: {self.app_settings['setup_finalized']}")

        # Check if the user added a parameter to debug the app manager
        should_debug_app_manager = Debug.should_debug_app_manager()

        # Restart the app after a git pull
        def app_management():
            # Stop the process
            app = AppManager(
                f"{self.path}",
                threaded=False,
                # Check if the user gave an argument to debug this particular part
                # of the program
                debug=should_debug_app_manager
                )
            app.stop_app()

            # Setup and start the app
            app.setup_and_start(self.app_settings)

        # Start the app in a new thread
        thread = Thread(target=app_management)
        thread.start()
