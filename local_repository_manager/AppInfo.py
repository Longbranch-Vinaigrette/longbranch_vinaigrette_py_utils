import json
import os


class AppInfo:
    def __init__(
            self,
            path: str,
            filename: str = "settings.json",
            debug: bool = False,
            *args,
            **kwargs,
    ):
        self.path = path
        self.filename = filename
        self.debug = debug

        self.config = self.get_config()

    def get_config(self) -> dict:
        """Get settings.json dev-gui data"""
        data = None
        try:
            with open(f"{self.path}{os.path.sep}{self.filename}", "r") as f:
                data = json.load(f)["dev-gui"]
        except Exception as ex:
            pass
        return data

    # Get commands
    def get_commands(self):
        """Get commands"""
        try:
            return self.config["commands"]
        except Exception as ex:
            print(ex)
            return None

    def get_start_command(self):
        """Get start command"""
        try:
            return self.config["commands"]["start"]
        except Exception as ex:
            print(ex)
            return None

    def get_setup_command(self):
        """Get setup command"""
        try:
            commands = self.config["commands"]
            if "setup" in commands:
                return self.config["commands"]["setup"]
            else:
                return None
        except Exception as ex:
            print(ex)
            return None

    def get_info(self):
        """Get info"""
        return self.config

    def get_data(self):
        """Get data"""
        return self.config