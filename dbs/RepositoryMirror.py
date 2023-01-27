from ...sqlite3_utils import Sqlite3Utils
from ..data_configuration import DataLocation, DBPath


class RepositoryMirror:
    repositories_path = f"{DataLocation.get_data_path()}/repositories"

    def __init__(self, db_name: str = "repository_mirror", debug: bool = False):
        self.db_name = db_name
        self.debug = debug

        if self.debug:
            print("\nRepositoryMirror -> __init__():")

        # Get the filename of the DB
        db_path = DBPath.get_full_db_path()
        self.sql_repository_settings = Sqlite3Utils(
            db_path,
            self.db_name,
            parse_json=True,
            debug=self.debug)

    def get_all(self):
        """Get all data"""
        if self.debug:
            print("\nRepositoryMirror -> get_all():")

        data = self.sql_repository_settings.run_query(
            f"""SELECT * FROM {self.db_name}""",
            # Decode json data automatically
            True)
        return data

    def get_data(self, key: str):
        """Get data"""
        if self.debug:
            print("\nRepositoryMirror -> get_data():")

        data = self.sql_repository_settings.run_query(f"""
            SELECT * FROM {self.db_name}
                WHERE key='{key}'""",
            True)
        return data

    def upsert(self, data: dict, key: str):
        """Insert or replace data"""
        if self.debug:
            print("\nRepositoryMirror -> upsert():")

        return self.sql_repository_settings.insert_replace_v2(data, {
            "key": key,
        })
