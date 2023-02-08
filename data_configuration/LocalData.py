"""Get local data configuration

This data is temporary, and must not be submitted to a version hosting service like GitHub"""
import os
import json

filename = "local_data.json"


def get_local_settings_path() -> str:
    """Get local settings path

    A file inside the application folder, where local app data is stored.
    If it doesn't exist, this function will create the file, that's why it's recommended over
    just simply getting the path."""
    return LocalData(create_if_not_existent=True).get_local_settings_path()


def save_data(new_data: dict, debug: bool = False):
    """Save data without removing old data

    Instead, it replaces the old data with the new data if it was given"""
    return LocalData(create_if_not_existent=True).save_data(new_data)


def load_data():
    """Load data"""
    return LocalData(create_if_not_existent=True).load_data()


class LocalData:
    """Local data

    It's used for handling the file at ./.local/local_data.json
    Previously at ./local_data.json"""
    def __init__(self,
                 folder: str = os.getcwd(),
                 create_if_not_existent: bool = False,
                 debug: bool = False):
        self.debug = debug

        local_folder = f"{folder}{os.path.sep}.local"

        if not os.path.exists(local_folder):
            if create_if_not_existent:
                os.mkdir(local_folder)
            else:
                raise Exception(f"dev_tools_utils/data_configuration/LocalData.py -> "
                                f"LocalData.__init__(): "
                                f"The folder: {local_folder} doesn't exist.")

        # If the folder does exist, it's highly likely that it was my intervention
        # therefore we don't need to check create_if_not_existent any further.

        self.file_path = f"{local_folder}{os.path.sep}{filename}"
        if not os.path.exists(self.file_path):
            # App settings path
            app_settings = f"{folder}{os.path.sep}settings.json"
            if os.path.exists(app_settings):
                # Load data
                with open(app_settings) as f:
                    data = json.load(f)

                # Insert the data onto the local file
                with open(self.file_path, "w") as f:
                    json.dump(data, f)
            else:
                # settings.json doesn't exist
                # Then we will create an empty file
                with open(self.file_path, "w") as f:
                    json.dump({}, f)

    def get_local_settings_path(self):
        """Get local settings file path"""
        return self.file_path

    def save_data(self, new_data: dict):
        """Save data without removing old data

        Instead, it replaces the old data with the new data if it was given"""
        data = {}
        # If there's already data there, load it
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                data = json.load(f)

        # It's a string somehow
        if isinstance(data, str):
            data = json.loads(data)

        # Save the filename so it can be loaded somewhere else
        with open(self.file_path, "w") as f:
            data = {
                **data,
                **new_data,
            }
            json.dump(data, f)

    def load_data(self):
        """Load local data"""
        data = None
        with open(self.file_path, "r") as f:
            try:
                data = json.load(f)
            except Exception as ex:
                print("Couldn't load previous data, exception: ", ex)
        return data
