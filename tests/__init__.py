import pprint

from ..data_configuration import DataLocation, DBPath, LocalData
from ..data_configuration.ProjectInfo import ProjectInfo


def test_db_paths(show_output: bool = False):
    print("tests -> test_db_paths():")

    try:
        out = DBPath.get_databases_path()
        print("[OK] DBPath.get_databases_path()")
        if show_output:
            print(out)
    except:
        print("[Failed] DBPath.get_databases_path()")

    try:
        out = DBPath.get_sql_db_path()
        print("[OK] DBPath.get_sql_db_path()")
        if show_output:
            print(out)
    except:
        print("[Failed] DBPath.get_sql_db_path()")

    try:
        out = DBPath.get_databases_path_list()
        print("[OK] DBPath.get_databases_path_list()")
        if show_output:
            pprint.pprint(out)
    except:
        print("[Failed] DBPath.get_databases_path_list()")


class Tests:
    def __init__(self, debug: bool = False):
        pass
