import json
import os


class ProjectInfo:
    info = None

    def __init__(self, path: str, debug=False):
        self.path = path
        self.debug = debug

        try:
            with open(f"{path}{os.path.sep}settings.json", "r") as f:
                self.info = json.load(f)["dev-gui"]
        except Exception as ex:
            if self.debug:
                print("Error: Couldn't retrieve data, ", ex)

    def get_commands(self):
        """Get commands"""
        try:
            return self.info["commands"]
        except Exception as ex:
            print(ex)
            return None

    def get_start_command(self):
        """Get start command"""
        try:
            return self.info["commands"]["start"]
        except Exception as ex:
            print(ex)
            return None

    def get_setup_command(self):
        """Get setup command"""
        try:
            commands = self.info["commands"]
            if "setup" in commands:
                return self.info["commands"]["setup"]
            else:
                return None
        except Exception as ex:
            print(ex)
            return None

    def get_info(self):
        """Get info"""
        return self.info

    def get_data(self):
        """Get data"""
        return self.info

    def get_version(self):
        """Get the version"""
        return self.info["version"]
