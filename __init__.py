import json
import copy

from . import OStuff
from .data_configuration import DBPath


def load_repository_settings_data(
        column_name: str,
        username: str,
        db_filename: str = "devtools.db",
        sql_repository_settings=None,
        debug: bool = False,
    ):
    """Load repository settings data

    There are multiple things that must be done to load this correctly.
    If no instance of a database is given, it creates a new one."""
    try:
        from ..sqlite3_utils import Sqlite3Utils
    except:
        print("Warning: dev_tools_utils -> load_repository_settings_data():")
        print("sqlite3_utils submodule not found.")
        return

    if debug:
        print("load_repository_settings_data():")
        print(f"Column name: {column_name}")
        print(f"username: {username}")

    # If no instance of a database was given, create a new one just this once
    if not sql_repository_settings:
        db_path = DBPath.get_sql_db_path(db_filename)
        sql_repository_settings = Sqlite3Utils(db_path, "repository_settings")

    # This might throw an error
    try:
        #                                   Column
        #                                     |          Value
        data = sql_repository_settings.get(column_name, username)
    except Exception:
        return

    # If there's no data return
    if not data:
        return

    # If there's a single item in data, it will not be a list
    # but a dictionary
    if isinstance(data, dict):
        return [data]

    # Enabled is like this: 'enabled': '{"type": "bool", "value": false}'
    for i in range(len(data)):
        item = data[i]
        try:
            # Load enabled
            enabled = json.loads(item["enabled"])["value"]

            setup_finalized = json.loads(item["setup_finalized"])["value"]
            if isinstance(setup_finalized, dict):
                setup_finalized = setup_finalized["value"]

            # Replace previous value in the dictionary
            item["enabled"] = enabled
            item["setup_finalized"] = setup_finalized
        except Exception as err:
            pass

    return data


def merge_data(normal_data: list, replace_for: list, key: str, debug=False) -> list:
    """Merge data

    Both args have to be dictionary lists"""
    temp_list: list = []
    result = copy.deepcopy(normal_data)

    if not normal_data or not replace_for:
        if debug:
            print("No data given")
            print("First argument: ", normal_data)
            print("Second argument: ", replace_for)
            print("Key: ", key)
        raise Exception("utils -> merge_data(): No data given:")

    if debug:
        print("Finding new items...")

    # Find new items
    for i in range(len(replace_for)):
        itemB = replace_for[i]

        for j in range(len(result)):
            itemA = result[j]
            if itemA[key] == itemB[key]:
                break
        else:
            # Only executed if the inner loop did NOT break
            # If the inner loop didn't break, it means that the data is new,
            # in this case, we want to insert it, but it's dangerous
            # inserting data to a list that we are looping through,
            # we can insert it to a different list, and then we can
            # join them
            if debug:
                print(f"This item is new: {itemB[key]}\n", itemB)
            temp_list.append(itemB)

    if debug:
        print("Replacing previous values...")

    # Replace previous data
    for i in range(len(result)):
        # If item is modified, it will also be modified inside result
        itemA:dict = result[i]
        if debug:
            print("--------------------------------")
            print(f"Dictionary number {i}: ", itemA)

        for j in range(len(replace_for)):
            itemB = replace_for[j]
            if debug:
                print(f"Do both have the same key("
                      f"{itemA[key]} == {itemB[key]})?: {itemA[key] == itemB[key]}")

            # Both items are the same
            if itemA[key] == itemB[key]:
                if debug:
                    print(f"Replace for: ", itemB)

                b_keys = list(itemB.keys())
                for b_key in b_keys:
                    if debug:
                        print(f"    Replacing ({b_key}) value "
                              f"{itemA.get(b_key, None)} "
                              f"for value {itemB[b_key]}")
                    itemA[b_key] = itemB[b_key]

                # Break inner loop
                break
    # We insert it at the end, so we don't loop
    # through items that we know are completely new
    # Join lists
    result += temp_list
    return result


def try_get(sql_settings_table, key_name, debug=False):
    """Try get

    Only for sql settings table
    Try to get something from the local database"""
    if debug:
        print("/src/utils -> try_get():")

    value = ""
    try:
        # Get username
        raw_data = sql_settings_table.get("key", key_name)
        if debug:
            print("Raw data: ", raw_data)
            print("Raw data: ", type(raw_data))
        value = raw_data["value"] \
            if (type(raw_data) == type({}) and raw_data) \
            else raw_data if raw_data else ""

        # Double level deep:
        # {'key': 'fetch_repositories', 'value': '{"type": "bool", "value": true}'}
        try:
            data = json.loads(value)
            if debug:
                print(f"Second level: ", data)
            value = data["value"] \
                if (type(data) == type({}) and data) \
                else data
        except Exception as ex:
            pass
    except Exception as ex:
        data = {
            "key": key_name,
            "value": "",
        }
        # Create table
        sql_settings_table.insert_replace(data, "key", key_name)
        # End exception
    return value
