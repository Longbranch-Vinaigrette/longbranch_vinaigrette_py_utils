"""Get local data configuration

This data is temporary, and must not be submitted to a version hosting service like GitHub"""
import os
import json


def _get_local_settings_path() -> str:
    """Get local settings path"""
    return f"{os.getcwd()}{os.path.sep}local_settings.json"


def get_local_settings_path() -> str:
    """Get local settings path

    A file inside the application folder, where local app data is stored.
    If it doesn't exist, this function will create the file, that's why it's recommended over
    just simply getting the path."""
    path = _get_local_settings_path()

    if not os.path.exists(path):
        with open(path, "w+") as f:
            json.dump(json.dumps({}), f)
    return path


def save_data(new_data, key: str):
    """Save data"""
    data = {}
    with open(get_local_settings_path(), "r") as f:
        try:
            data = json.load(f)
        except Exception as ex:
            print("Couldn't load previous data, exception: ", ex)

    # Save the filename so it can be loaded somewhere else
    with open(get_local_settings_path(), "w") as f:
        data[key] = new_data
        json.dump(data, f)


def load_data(key: str):
    """Load data"""
    data = None
    with open(get_local_settings_path(), "r") as f:
        try:
            data = json.load(f)
            data = data[key]
        except Exception as ex:
            print("Couldn't load previous data, exception: ", ex)
    return data
