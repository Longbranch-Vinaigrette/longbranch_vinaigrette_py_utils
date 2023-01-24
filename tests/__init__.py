import pprint

from ..data_configuration import DataLocation, DBPath
from ..local_repository_manager import LocalRepositoryManager
from ..dynamic_imports.Routes import Routes


def test_db_paths(show_output: bool = False, debug: bool = False):
    if debug:
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


def test_local_repository_manager(show_output: bool = False, debug: bool = False):
    if debug:
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


def test_dynamic_imports_routes(routes_path: str, show_output: bool = False, debug: bool = False):
    if debug:
        print("\ntests -> test_dynamic_imports_routes():")

    try:
        routes = Routes(routes_path, debug=debug)
        print("[OK] Routes()")
        if show_output:
            print(routes)
    except Exception as ex:
        print("[Failed] Routes()")
        print("Exception: ", ex)
        print("Cannot proceed with Routes object")
        return

    try:
        out = routes.get_routes()
        print("[OK] Routes.get_routes()")
        if show_output:
            pprint.pprint(out)
    except Exception as ex:
        print("[Failed] Routes.get_routes()")
        print("Exception: ", ex)

    try:
        routes.use_full_routes = True
        out = routes.get_routes()
        print("[OK] Routes.get_routes() (Using full routes as indexes)")
        if show_output:
            pprint.pprint(out)
    except Exception as ex:
        print("[Failed] Routes.get_routes() (Using full routes as indexes)")
        print("Exception: ", ex)


class Tests:
    def __init__(self, debug: bool = False):
        pass
