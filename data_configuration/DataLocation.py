import os
import json

from . import LocalData


filename = ".devtools"
local_settings_path = LocalData.get_local_settings_path()


def get_global_data_path():
    """Get global data path"""
    path = f"{os.path.expanduser('~')}{os.path.sep}{filename}"
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def get_default_data_location():
    """Get default data location

    Which should be the global data path"""
    return get_global_data_path()


def get_local_data_location():
    """Get local data location"""
    path = f"{os.getcwd()}{os.path.sep}{filename}"
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def get_data_path() -> str:
    """Get data path

    Get the path where the data will be stored"""
    with open(local_settings_path) as f:
        try:
            data = json.load(f)
            data_path = data["data_path"]
        except:
            data_path = get_default_data_location()
    return data_path


def get_repositories_path(debug=False):
    """Get repositories path, if it doesn't exist, returns default repository path"""
    if debug:
        print("\nDataLocation -> get_default_path():")

    # This is cross-platform
    with open(local_settings_path) as f:
        try:
            data = json.load(f)
            data_path = data["data_path"]
        except:
            data_path = get_default_data_location()
    my_repositories = f"{data_path}{os.path.sep}repositories"

    if not os.path.exists(data_path):
        os.mkdir(data_path)

    if not os.path.exists(my_repositories):
        os.mkdir(my_repositories)

    return my_repositories
