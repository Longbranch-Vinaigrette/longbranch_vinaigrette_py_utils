from ...sqlite3_utils import Sqlite3Utils
from ..data_configuration import DataLocation, DBPath


class RepositoriesTable:
    repositories_path = f"{DataLocation.get_data_path()}/repositories"

    def __init__(self, db_name: str = "repositories", debug: bool = False):
        self.db_name = db_name
        self.debug = debug

        if self.debug:
            print("\nRepositories -> __init__():")

        # Get the filename of the DB
        db_path = DBPath.get_full_db_path()
        self.sql_repository_settings = Sqlite3Utils(
            db_path,
            self.db_name,
            parse_json=True,
            debug=self.debug,
        )

    def get_all(self):
        """Get all data"""
        if self.debug:
            print("\nRepositories -> get_all():")

        data = self.sql_repository_settings.run_query(
            f"""SELECT * FROM {self.db_name}""",
            # Decode json data automatically
            True)
        return data

    def get_data(self, filterA: dict):
        """Get data"""
        if self.debug:
            print("\nRepositories -> get_data():")

        data = self.sql_repository_settings.get_filtered(filterA)
        return data

    def upsert(self, data: dict, filterA: dict):
        """Insert or replace data"""
        if self.debug:
            print("\nRepositoryMirror -> upsert():")

        return self.sql_repository_settings.insert_replace_v2(data, filterA)
