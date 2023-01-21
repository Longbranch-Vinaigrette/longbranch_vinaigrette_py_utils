import json
import os


def should_debug_app_manager():
    # Check if it should on debug mode or not
    should_debug = False
    with open(f"{os.getcwd()}{os.path.sep}local_data.json") as f:
        try:
            local_data = json.load(f)
            args = local_data["arguments"]
            debug_elements = args["debug"]
            debug_list = [
                "app_manager",
                "app-manager",
                "AppManager",
                "process-info",
                "process_info",
                "ProcessInfo"
            ]

            if debug_elements is not None:
                for debug_item in debug_elements.split(","):
                    if debug_item in debug_list:
                        should_debug = True
                        print("Debug enabled for AppManager and ProcessInfo")
                        break
        except Exception as ex:
            # This error shouldn't happen
            print("Exception: ", ex)
    return should_debug
