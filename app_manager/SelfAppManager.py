import os
import subprocess

from ..data_configuration import LocalData
from ..app_manager import AppManager
from .. import os_stuff


class SelfAppManager:
    def __init__(self, start_cmd: str = "", debug: bool = False):
        """Self app manager

        This is script is intended to manage this very app, not apps somewhere else, for that
        use app_manager.AppManager"""
        self.start_cmd = start_cmd
        self.debug = debug

        # Reference/s
        # https://www.geeksforgeeks.org/python-os-getpid-method/
        pid = os.getpid()
        if self.debug:
            print("Process pid: ", pid)
            print("Pid type: ", type(pid))
        os_stuff.capture_pid()

    def start_app(self):
        if self.debug:
            print("\nstart_app()")

        if not self.start_cmd:
            raise Exception("Start cmd command not defined.")

        parsed_cmds = bytes(self.start_cmd, 'utf8')
        if self.debug:
            print("Parsed cmds: ", parsed_cmds)

        # For subprocess.Popen()
        # It's recommended to use fully qualified paths, or
        # some things might be overriden
        process: subprocess.Popen = subprocess.Popen(["/bin/sh"],
                                                     stdin=subprocess.PIPE,
                                                     stdout=subprocess.PIPE,
                                                     shell=True)
        LocalData.save_data(
            {
                "subprocesses": {
                    "pids": [process.pid]
                }
            },
            True)

        out, err = process.communicate(parsed_cmds)
        if self.debug:
            print("Communicated with subprocess")
        print(out.decode("utf-8"))

    def stop_app(self):
        if self.debug:
            print("\nstop_app():")

        previous_data = LocalData.load_data()
        original_process_pid = previous_data["pid"]

        # Remove pid
        os_stuff.remove_pid()

        AppManager(os.getcwd()).send_term_signal(original_process_pid)
