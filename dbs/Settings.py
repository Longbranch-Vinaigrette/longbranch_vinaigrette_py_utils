from ...sqlite3_utils import Sqlite3Utils
from ..data_configuration import DBPath


class Settings:
    def __init__(self, debug: bool = False):
        # Get the filename of the DB
        db_path = DBPath.get_full_db_path()
        self.sql_settings_table = Sqlite3Utils(
            db_path,
            "settings",
            parse_json=True,
            debug=debug)

    def upsert(self, data: dict, filterA: dict):
        """Alias for insert replace"""
        return self.sql_settings_table.insert_replace_v2(data, filterA)

    def get(self, key: str):
        """Get data from the settings table"""
        return self.sql_settings_table.get("key", key, True)["value"]
