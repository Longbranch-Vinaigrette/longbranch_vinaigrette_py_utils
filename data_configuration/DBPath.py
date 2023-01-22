import os

from . import DataLocation


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
