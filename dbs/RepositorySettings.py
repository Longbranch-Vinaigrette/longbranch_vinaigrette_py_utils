import os

from ...sqlite3_utils import Sqlite3Utils
from ..data_configuration import DataLocation, DBPath


class RepositorySettings:
    repositories_path = f"{DataLocation.get_data_path()}/repositories"

    def __init__(self, debug: bool = False):
        self.debug = debug

        if self.debug:
            print("\nRepositorySettings -> __init__():")

        self.table = "repository_settings"

        # Get the filename of the DB
        db_path = DBPath.get_full_db_path()
        self.sql_repository_settings = Sqlite3Utils(
            db_path,
            self.table,
            parse_json=True,
            debug=self.debug)

    def get_all(self):
        """Get every repository settings data"""
        data = self.sql_repository_settings.run_query(
            f"""SELECT * FROM {self.table}""",
            # Decode json data automatically
            True)
        return data

    def get_user_repositories(self, username: str):
        """Get user repositories"""
        data = self.sql_repository_settings.run_query(f"""
            SELECT * FROM {self.table}
                WHERE user='{username}'
            """)
        return data

    def get_repository(self, username: str, repository_name: str):
        """Get repository settings data"""
        data = self.sql_repository_settings.run_query(f"""
            SELECT * FROM {self.table}
                WHERE user='{username}'
            INTERSECT
                SELECT * FROM {self.table}
                    WHERE name='{repository_name}'
            """,
            True)
        return data

    def delete_row(self, username: str, repository_name: str):
        """Delete a row"""
        self.sql_repository_settings.run_query(f"""
            DELETE FROM {self.table}
                WHERE (user='{username}' AND name='{repository_name}');
            """)

    def upsert(self, data: dict, filterA: dict):
        """Insert or replace data"""
        if self.debug:
            print("RepositorySettings -> upsert():")
        return self.sql_repository_settings.insert_replace_v2(data, filterA)

    def set_default_path(self, username: str, repository_name: str):
        """Set path to default path"""
        self.sql_repository_settings.insert_replace({
                "path": f"{self.repositories_path}/{username}/{repository_name}"
            },
            "user",
            username,
            {
                "name": repository_name,
            })

    def set_default_path_for_every_repository(self):
        """Set default path for every repository"""
        data = self.sql_repository_settings.get_all()
        for item in data:
            username = item["user"]
            repository_name = item["name"]
            sep = os.path.sep

            # Update path
            path = f"{self.repositories_path}{sep}{item['user']}{sep}{item['name']}"
            self.sql_repository_settings.insert_replace_v2(
                {
                    "path": path
                },
                {
                    "user": username,
                    "name": repository_name
                }
            )
