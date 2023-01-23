"""Get local data configuration

This data is temporary, and must not be submitted to a version hosting service like GitHub"""
import os
import json


def _get_local_settings_path() -> str:
    """Get local settings path"""
    # Django uses local_settings.json, so I can't use it.
    return f"{os.getcwd()}{os.path.sep}local_data.json"


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


def save_data(new_data: dict, debug: bool = False):
    """Save data without removing old data

    Instead, it replaces the old data with the new data if it was given"""
    data = {}
    with open(get_local_settings_path(), "r") as f:
        try:
            data = json.load(f)
        except Exception as ex:
            # Maybe the file doesn't exist
            print("Couldn't load previous data, exception: ", ex)

    if debug:
        print("Previous data: ", data)
        print("Its type: ", type(data))

    # It's a string somehow
    if isinstance(data, str):
        data = json.loads(data)

    # Save the filename so it can be loaded somewhere else
    with open(get_local_settings_path(), "w") as f:
        data = {
            **data,
            **new_data,
        }
        if debug:
            print("Data to store: ", data)
        json.dump(data, f)


def load_data():
    """Load data"""
    data = None
    with open(get_local_settings_path(), "r") as f:
        try:
            data = json.load(f)
        except Exception as ex:
            print("Couldn't load previous data, exception: ", ex)
    return data
