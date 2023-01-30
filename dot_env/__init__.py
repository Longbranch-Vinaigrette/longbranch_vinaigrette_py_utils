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

    def __init__(self, path: str = os.getcwd(), debug: bool = False):
        self.path = path
        self.debug = debug

    def get_dot_env_raw(self) -> str:
        """Get raw data on .env in the project root"""
        if self.debug:
            print("\nDotEnvParser -> get_dot_env_raw():")
        try:
            with open(f"{self.path}{os.path.sep}.env") as f:
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

    def get_dot_env_data(self) -> dict:
        """Get dot env data as a dictionary"""
        if self.debug:
            print("\nDotEnvParser -> get_dot_env_data():")
        raw_data: str = self.get_dot_env_raw()
        return self.parse_dot_env(raw_data)


class DotEnvEncoder:
    def __init__(self, data: dict, path: str = os.getcwd(), debug: bool = False):
        self.data = data
        self.path = path
        self.debug = debug

        if self.debug:
            print("\nDotEnvEncoder -> __init__():")
            print("Given path: ", self.path)

    def dot_env_encode_data(self, data: dict):
        """Get encoded data"""
        if self.debug:
            print(f"\nDotEnvEncoder -> get_encoded_data():")

        encoded_environment_variables = ""
        for key, value in data.items():
            encoded_environment_variables += f"{key}={value}\n"
        return encoded_environment_variables

    def upsert_dot_env(self):
        """Upsert environment variables"""
        if self.debug:
            print(f"\nDotEnvEncoder -> upsert_dot_env():")

        # Merge given data + data in the .env file
        dot_env_parser = DotEnvParser(path=self.path)
        dot_env_data: dict = dot_env_parser.get_dot_env_data()
        dot_env_data: dict = {
            **dot_env_data,
            **self.data,
        }

        # Encode data
        encoded_data = self.dot_env_encode_data(dot_env_data)

        if self.debug:
            print("Encoded data: ", encoded_data)

        # Save the data
        dot_env_path = f"{self.path}{os.path.sep}.env"
        with open(dot_env_path, "w") as f:
            f.write(encoded_data)
            if self.debug:
                print(f"Data written to: {dot_env_path}")
