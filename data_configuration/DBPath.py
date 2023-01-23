import json
import os

from . import DataLocation
from . import LocalData


def get_databases_path():
    """Get the path where database/s will be stored"""
    return f"{DataLocation.get_data_path()}{os.path.sep}database"


def get_sql_db_path(name="devtools.db"):
    """Get the path where the sql database should be stored"""
    # Path where sql dbs are stored
    db_path = get_databases_path()
    if not os.path.exists(db_path):
        os.mkdir(db_path)

    return f"{db_path}{os.path.sep}{name}"


def get_databases_path_list():
    """Get databases path list

    This will return a list of every '.db' file path stored on the configured get_data_path()"""
    db_list = os.listdir(get_databases_path())
    result = []
    for db_name in db_list:
        if db_name.endswith(".db"):
            result.append(f"{get_databases_path()}{os.path.sep}{db_name}")
    return result


def get_full_db_path():
    # Get the filename of the DB
    db_filename = "devtools.db"
    try:
        with open(LocalData.get_local_settings_path(), "r") as f:
            local_data = json.load(f)
            db_filename = local_data["DBFilename"] if local_data["DBFilename"] else "devtools.db"
    except:
        db_filename = "devtools.db"
    db_path = get_sql_db_path(db_filename)
    return db_path
