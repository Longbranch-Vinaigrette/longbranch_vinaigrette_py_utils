import os
import subprocess

from ..data_configuration import LocalData
from .. import app_manager


class SelfAppManager:
    def __init__(self, start_cmd: str, capture_pid: bool = False, debug: bool = False):
        """Self app manager

        This is script is intended to manage this very app, not apps somewhere else, for that
        use app_manager.AppManager"""
        self.start_cmd = start_cmd
        self.capture_pid = capture_pid
        self.debug = debug

        # Reference/s
        # https://www.geeksforgeeks.org/python-os-getpid-method/
        if capture_pid:
            pid = os.getpid()
            if self.debug:
                print("Process pid: ", pid)
                print("Pid type: ", type(pid))
            LocalData.save_data(
                {
                    "pid": pid,
                    # If this app kills spawned subprocesses on exit, which is true by default
                    "killsSubprocessesOnExit": True,
                },
                True)

    def start_app(self):
        if self.debug:
            print("\nstart_app()")

        parsed_cmds = bytes(self.start_cmd, 'utf8')
        print("Parsed cmds: ", parsed_cmds)

        # For subprocess.Popen()
        # It's recommended to use fully qualified paths, or
        # some things might be overriden
        process: subprocess.Popen = subprocess.Popen(["/bin/sh"],
                                                     stdin=subprocess.PIPE,
                                                     stdout=subprocess.PIPE,
                                                     shell=True)
        print("Database server started")
        LocalData.save_data(
            {
                "subprocesses": {
                    "pids": [process.pid]
                }
            },
            True)

        out, err = process.communicate(parsed_cmds)
        print("Communicated with subprocess")
        print(out.decode("utf-8"))

    def stop_app(self):
        if self.debug:
            print("\nstop_app():")

        previous_data = LocalData.load_data()
        original_process_pid = previous_data["pid"]
        # Remove pid, just in case
        LocalData.save_data({
            "pid": "",
        })

        app_manager.send_term_signal(original_process_pid, debug=self.debug)
