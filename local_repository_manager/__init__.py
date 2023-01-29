import os

from ..data_configuration import DataLocation
from .LocalRepository import LocalRepository


class LocalRepositoryManager:
    path: str = DataLocation.get_repositories_path()

    users = []
    debug = False

    def __init__(self, repositories_path: str = "", debug=False):
        if repositories_path:
            self.path = repositories_path
        self.debug = debug

        if self.debug:
            print("LocalRepositoryManager -> __init__():")
            print("Given path: ", self.path)
        users_path = self.get_subdirectories_path(self.path)
        self.users = self.path_list_to_name_list(users_path)

        if self.debug:
            print("Users: ", self.users)

    def get_users(self) -> list:
        """Get users"""
        return self.users

    def path_list_to_name_list(self, path_list:list):
        """Takes a path list and returns just the last
        folder/file name of every path in the list"""
        return [subd.split("/")[-1] for subd in path_list]

    def get_subdirectories_path(self, scan_path: str):
        """Get subdirectories of a specific path"""
        return [f.path for f in os.scandir(scan_path) if f.is_dir()]

    def get_user_repository_list_path(self, username: str):
        """Get local repository list of a given user"""
        if self.debug:
            print("LocalRepositoryManager -> get_user_repository_list():")

        user_repositories_path = f"{self.path}{os.path.sep}{username}"
        return self.get_subdirectories_path(user_repositories_path)

    def get_user_repository_list(self, username: str):
        """Get local repository list of a given user"""
        user_repositories_path = self.get_user_repository_list_path(username)
        user_repositories_list = self.path_list_to_name_list(user_repositories_path)
        return user_repositories_list

    def get_user_repos_info(self, username: str) -> list:
        """Get user repository info"""
        user_repositories: list = []
        for name in self.get_user_repository_list(username):
            # Repository path
            repository_path = f"{self.path}{os.path.sep}{username}{os.path.sep}{name}"

            # Is devtools compatible?
            devtools = LocalRepository(repository_path).is_devtools_compatible()

            # Append repository
            user_repositories.append({
                "user": username,
                "name": name,
                "path": repository_path,
                "start_on_boot": False,
                "dev_tools": devtools,
            })

        return user_repositories

    def get_all_repos_info(self) -> list:
        """Get repositories information"""
        if self.debug:
            print("LocalRepositoryManager -> get_all_repos_info():")

        temp_list = []
        for user in self.users:
            temp_list += self.get_user_repos_info(user)

        return temp_list
