import pprint

from ..data_configuration import DataLocation, DBPath, LocalData
from ..data_configuration.ProjectInfo import ProjectInfo
from ..local_repository_manager import LocalRepositoryManager


def test_db_paths(show_output: bool = False):
    print("\ntests -> test_db_paths():")

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


def test_local_repository_manager(show_output: bool = False):
    print("\ntests -> test_local_repository_manager():")

    try:
        rep_manager = LocalRepositoryManager(DataLocation.get_repositories_path(), debug=True)
        print("[OK] LocalRepositoryManager()")
        if show_output:
            print(rep_manager)
    except:
        print("[Failed] LocalRepositoryManager()")
        print("Cannot proceed with LocalRepositoryManager")
        return

    try:
        out = rep_manager.get_all_repos_info()
        print("[OK] LocalRepositoryManager.get_all_repos_info()")
        if show_output:
            pprint.pprint(out)
    except:
        print("[Failed] LocalRepositoryManager.get_all_repos_info()")


class Tests:
    def __init__(self, debug: bool = False):
        pass
