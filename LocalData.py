import os
import json

local_data_path = f"{os.getcwd()}{os.path.sep}local_data.json"


def save_data(new_data, key: str):
    """Save data"""
    data = {}
    with open(local_data_path, "r") as f:
        try:
            data = json.load(f)
        except Exception as ex:
            print("Couldn't load previous data, exception: ", ex)

    # Save the filename so it can be loaded somewhere else
    with open(local_data_path, "w") as f:
        data[key] = new_data
        json.dump(data, f)


def load_data(key: str):
    """Load data"""
    data = None
    with open(local_data_path, "r") as f:
        try:
            data = json.load(f)
            data = data[key]
        except Exception as ex:
            print("Couldn't load previous data, exception: ", ex)
    return data

def load_settings_data(key: str):
    """Load settings data"""
    with open(f"{os.getcwd()}{os.path.sep}settings.json", "r") as f:
        try:
            return json.load(f)[key]
        except:
            pass
    return None