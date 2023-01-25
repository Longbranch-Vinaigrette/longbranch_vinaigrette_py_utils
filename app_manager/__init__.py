"""App manager

Manages app instantiation and termination,
only for linux"""
import json
import os
import subprocess
from threading import Thread

from ..data_configuration.ProjectInfo import ProjectInfo
from .. import Debug
from ..dbs.RepositorySettings import RepositorySettings

from .StartApp import StartApp
from .ProcessInfo import ProcessInfo


def send_term_signal(pid: int, debug: bool = False):
    """Send term signal by pid"""
    if debug:
        print("\nsend_term_signal():")
    # Start a new process to shut down the previous process
    # For this we will send a sigterm, which was captured before
    raw_cmds = f"""
    kill -s 15 {pid}
    """
    parsed_cmds = bytes(raw_cmds, 'utf8')

    # For subprocess.Popen()
    # It's recommended to use fully qualified paths, or
    # some things might be overriden
    process: subprocess.Popen = subprocess.Popen(["/bin/sh"],
                                                 stdin=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 shell=True)
    out, err = process.communicate(parsed_cmds)


class AppManager:
    """App manager

    If stop and start are close in time of execution
    then the app might first be started and then stopped
    so this might not be the wanted behaviour, for that
    set threaded to false
    """
    def __init__(
            self,
            path: str,
            threaded: bool = True,
            debug: bool = False):
        self.path: str = path
        self.threaded = threaded
        self.debug: bool = debug

        self.app_name: str = path.split(os.path.sep)[-1]
        self.username: str = path.split(os.path.sep)[-2]
        self.start_commands: list = []

        # Check if the user added a parameter to debug the app manager
        if not self.debug:
            should_debug_app_manager = Debug.should_debug_app_manager()
            self.debug = should_debug_app_manager

        # Get app settings
        repository_settings = RepositorySettings()
        self.app_settings = repository_settings.get_repository(self.username, self.app_name)

        self.project_info = ProjectInfo(self.path, debug=debug)

    def setup_and_start(self, item):
        """Start the app"""
        if self.debug:
            print("AppManager -> setup_and_start():")

        def setup_and_start():
            project_info = ProjectInfo(item["path"])

            if self.debug:
                print("Path: ", item["path"])
                print("Project info: ", project_info.info)
            if project_info.info is not None:
                setup_command = project_info.get_setup_command()

                if self.debug:
                    print("Setup command: ", setup_command)
                    print("Start command: ", project_info.get_start_command())

                # Setup app
                if setup_command:
                    cmd = f"""cd {item['path']} &&
                                pwd &&
                                {setup_command}"""

                    # Run command
                    ProcessInfo("setup").run_subprocess(cmd)

                    item["setup_finalized"] = True

                # Start app
                if self.debug:
                    print("Starting app")
                StartApp(self.path, self.project_info, debug=self.debug)

        # Threaded or not
        if self.threaded:
            # Start the app in a new thread
            def run_fn():
                setup_and_start()

            thread = Thread(target=run_fn)
            thread.start()
        else:
            # Run normally
            setup_and_start()

    def start_app(self):
        """Starts the application in the background"""
        if self.debug:
            print("AppManager -> start_app():")

        def start_app():
            # The app will be executed on creation
            StartApp(self.path, self.project_info, debug=self.debug)

        if self.threaded:
            # Start the app in a new thread
            def run_fn():
                start_app()

            thread = Thread(target=run_fn)
            thread.start()
        else:
            start_app()

    def stop_app(self):
        """Stops the application in the background"""
        if self.debug:
            print("AppManager -> stop_app():")

        def stop_app():
            """Stop app in the given path"""
            app_data = self.project_info.info
            if app_data and app_data["commands"]:
                commands = app_data["commands"]

                # Check if the app has a stop command
                if commands["stop"]:
                    # Run stop command
                    parsed_cmds = bytes(commands["stop"], 'utf8')
                    if self.debug:
                        print("Stop command: ", parsed_cmds)

                    stop_process: subprocess.Popen = subprocess.Popen(["/bin/sh"],
                                                                 stdin=subprocess.PIPE,
                                                                 stdout=subprocess.PIPE,
                                                                 shell=True)
                    out, err = stop_process.communicate(parsed_cmds)

                    if self.debug:
                        print(out)

                    # App terminated go back
                    return

            # To kill get the pid and use 'kill <PID>'

            # If the command is for example 'python3.10 main.py'
            # we can separate the command name from the parameters by
            # splitting by spaces
            # Retrieve data from the path
            commands = self.project_info.get_commands()

            # Some DevTools apps might store the pid inside the project path

            if not commands:
                print("AppManger -> stop_app():")
                msg = "The app has no commands, AppManager can't figure out a way to find the app pid."
                raise Exception(msg)

            # Split by spaces and get the first which is the command name
            command_name = commands["start"].split(" ")[0]
            if self.debug:
                print(f"Command name: {command_name}")

            # Get the cwd of multiple processes and check if
            # there's a settings.json file in their path.
            pinfo = ProcessInfo(
                command_name,  # This is the problem
                ["euser", "pid", "ppid", "cmd"],
                add_cwd=True,
                debug=self.debug)
            pdata = pinfo.get_processes_info_by_name()

            # Some process have more than one subprocess that must also
            # be killed, so don't break the loop after killing one subprocess
            for process in pdata:
                if self.debug:
                    print(f"--- {process['pid']} ---")
                    print(f"User: {process['euser']}")
                    print(f"Given directory: {self.path}")
                    print(f"Current Working Directory(cwd): {process['cwd']}")
                    print(f"Command: {process['cmd']}")

                project_info = ProjectInfo(process["cwd"])
                if project_info.info is not None:
                    # This is the app
                    if self.debug:
                        print("Status: This is the app, sending kill signal.")
                    subprocess.run(["kill", f"{process['pid']}"])
                elif project_info.info is None:
                    # This is not the app
                    if self.debug:
                        print("Status: This is not the app.")

        if self.threaded:
            # I don't think this is necessary, but just in case
            def run_fn():
                stop_app()

            thread = Thread(target=run_fn)
            thread.start()
        else:
            stop_app()

    def setup_and_restart(self):
        """Restart app

        Restarts an app if it's enabled"""
        if self.debug:
            print("AppManager -> setup_and_restart():")
            print(f"Repository path: {self.path}")

        # Restart the app after a git pull
        def app_management():
            # Stop the process
            app = AppManager(
                f"{self.path}",
                threaded=False,
                # Check if the user gave an argument to debug this particular part
                # of the program
                debug=self.debug
                )
            app.stop_app()

            # Setup and start the app
            app.setup_and_start(self.app_settings)

        if self.threaded:
            # Start the app in a new thread
            thread = Thread(target=app_management)
            thread.start()
        else:
            app_management()
