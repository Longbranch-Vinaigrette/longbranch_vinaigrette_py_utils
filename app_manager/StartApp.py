"""Starts an app by the given path

The app will remain running in the background even after the
program is finished"""
import subprocess


class StartApp:
    def __init__(self, path: str, project_info, debug: bool = False):
        self.path: str = path
        self.project_info = project_info
        self.debug: bool = debug

        self.start_commands = self.get_start_commands()
        if self.debug:
            print("Start commands: ", self.start_commands)

        result = self.start_app()
        if self.debug:
            print("Exit code: ", result)

    def get_start_commands(self):
        """Get only the commands to start the app

        Which should be with these keys:
        start, start_alt_1, start_alt_2, ..., start_alt_n
        """
        start_commands: list = []
        commands = self.project_info.get_commands()
        for cmd_name in list(commands.keys()):
            if cmd_name.startswith("start"):
                start_commands.append(commands[cmd_name])
        return start_commands

    def start_app(self):
        """Starts an app at the given path"""
        for start_com in self.start_commands:
            if self.debug:
                print(f" --- Command: {start_com} --- ")

            cmd = f"""pwd &&
                cd {self.path} &&
                pwd &&
                {start_com} &&
                pwd;"""

            # Reference:
            # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
            process = subprocess.Popen(["/bin/bash", "-c", cmd],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
            try:
                # This is to separate the process, it will only work
                # if the process keeps running after the timeout.
                stdout, stderr = process.communicate(timeout=1)
            except subprocess.TimeoutExpired:
                # Successfully started and now it's a standalone process
                return 0
            except Exception as ex:
                if self.debug:
                    print("Exception: ", ex)
                continue
        return 1
