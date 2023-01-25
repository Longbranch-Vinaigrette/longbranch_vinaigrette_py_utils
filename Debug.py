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


class Debug:
    def __init__(
            self,
            msg: str,
            error: bool = False,
            field: str = "",
            state: str = "success"):
        """Api handler for my debugging format"""
        # Message
        self.msg = msg
        # Whether it's an error or not
        self.error = error
        # The field which caused the error
        self.field = field
        # The state of the error(used for css styles)
        self.state = state

    def get_message(self):
        """Get the message"""
        return {
            "message": self.msg,
            "error": self.error,
            "field": self.field,
            "state": self.state
            # "uuid": get_uuid(),
            # "date": get_iso_date(),
        }

    def get_full_message(self):
        return {
            "debug": self.get_message(),
        }
