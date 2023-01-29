import os


class DotEnvLine:
    def __init__(self, line: str):
        self.line = line

    def get_var_name(self) -> str:
        """Get the var name"""
        return self.line.split("=")[0]

    def get_value(self) -> str:
        """Get the value"""
        return self.line.split("=", 1)[1]


class DotEnvParser:
    raw_env_data: str = ""
    parsed_data: dict = {}

    def __init__(self, debug: bool = False):
        self.debug = debug

    def get_dot_env_raw(self) -> str:
        """Get raw data on .env in the project root"""
        if self.debug:
            print("\nDotEnvParser -> get_dot_env_raw():")
        try:
            with open(f"{os.getcwd()}{os.path.sep}.env") as f:
                self.raw_env_data = f.read()
                return self.raw_env_data
        except:
            return ""

    def parse_dot_env(self, raw_data: str) -> dict:
        """Convert dot env raw data into dictionary data"""
        if self.debug:
            print("\nDotEnvParser -> parse_dot_env():")
        env_vars: dict = {}

        # Use cached data if possible
        if len(list(env_vars.keys())) > 0:
            if self.debug:
                print("Cached data found, returning it.")
            return self.parsed_data

        if self.debug:
            print("Cached data not found, parsing data.")

        # Raw data might be an empty string
        if raw_data:
            lines_list: list = raw_data.splitlines()
            for line in lines_list:
                env_var = DotEnvLine(line)
                env_vars[env_var.get_var_name()] = env_var.get_value()

        self.parsed_data = env_vars
        return env_vars

    def get_dot_env_data(self):
        """Get dot env data as a dictionary"""
        if self.debug:
            print("\nDotEnvParser -> get_dot_env_data():")
        raw_data: str = self.get_dot_env_raw()
        return self.parse_dot_env(raw_data)
