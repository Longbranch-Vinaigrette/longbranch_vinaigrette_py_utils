"""Get important project information stored on the given app/project path"""
import json
import os


class ProjectInfo:
    info = None

    def __init__(self, path: str, debug=False):
        """Get app/project information/settings data"""
        self.path = path
        self.debug = debug

        try:
            with open(f"{path}{os.path.sep}settings.json", "r") as f:
                self.info = json.load(f)["devtools"]
        except Exception as ex:
            raise Exception(f"The app at {self.path} is not DevTools compatible.")

    def load_settings_data(self, key: str):
        """Load settings data"""
        with open(f"{self.path}{os.path.sep}settings.json", "r") as f:
            try:
                return json.load(f)[key]
            except:
                pass
        return None

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
