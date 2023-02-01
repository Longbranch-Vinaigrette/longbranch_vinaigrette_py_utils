"""App manager

Manages app instantiation and termination,
only for linux


"""
import os
import subprocess
from threading import Thread

from ... import process_utils

from ..data_configuration.ProjectInfo import ProjectInfo
from ..dbs.RepositorySettings import RepositorySettings
from .. import Debug
from .. import OStuff

from .StartApp import StartApp
from .ProcessInfo import ProcessInfo


class AppManager:
    """App manager

    Manages execution, stop, restarting and setup of a given app
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

        # Get app settings
        repository_settings = RepositorySettings()
        self.app_settings = repository_settings.get_repository(self.username, self.app_name)

        self.project_info = ProjectInfo(self.path, debug=debug)

    def send_term_signal(self, pid: int):
        """Send term signal by pid"""
        if self.debug:
            print("\nAppManager -> send_term_signal():")
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

    def is_app_running(self):
        """Check if the app is running"""
        if self.debug:
            print("\nAppManager -> is_app_running():")
        return process_utils.check_is_app_running_by_cwd(self.path)


    ##################
    ### Operations ###
    ##################
    def start_app(self):
        """Starts the application in the background"""
        if self.debug:
            print("\nAppManager -> start_app():")

        def start_app():
            # The app will be executed on creation
            # StartApp(self.path, self.project_info, debug=self.debug)
            start_command = self.project_info.get_start_command()
            if not start_command:
                raise Exception("The app doesn't have a start command.")
            else:
                out, err = OStuff.run_commands(start_command)

        if self.threaded:
            thread = Thread(target=start_app)
            thread.start()
        else:
            start_app()

    def stop_app(self):
        """Stops the application in the background"""
        if self.debug:
            print("\nAppManager -> stop_app():")

        def stop_app():
            """Stop app in the given path"""
            app_data = self.project_info.info
            if app_data and app_data["commands"]:
                commands = app_data["commands"]

                # Check if the app has a stop command
                if "stop" in commands:
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

            # Some DevTools apps might store the pid
            if "pid" in self.project_info.info:
                pid = self.project_info.info["pid"]
                if self.debug:
                    print("Pid found: ", pid)
                    print("Killing process.")
                os.kill(pid, 15)
                return

            # If the app has no stop command, no pid file, we need to do it the hard way.
            # Search for the app and terminate it(with signal 15)
            process_utils.kill_all_by_cwd_and_subfolders(self.path)
        if self.threaded:
            # I don't think this is necessary, but just in case
            def run_fn():
                stop_app()

            thread = Thread(target=run_fn)
            thread.start()
        else:
            stop_app()

    def restart_app(self):
        """Restarts an app"""
        if self.debug:
            print("\nAppManager -> restart_app():")

        # Check if the user added a parameter to debug the app manager
        should_debug_app_manager = Debug.should_debug_app_manager()

        # Restart the app after a git pull
        def app_management():
            # Stop the process
            app = AppManager(
                f"{self.path}",
                threaded=False,
                # Check if the user gave an argument to debug this particular part
                # of the program
                debug=should_debug_app_manager
                )
            app.stop_app()

            # Start the app
            app.start_app()

        # Check if it's threaded and restart the app
        if self.threaded:
            thread = Thread(target=app_management)
            thread.start()
        else:
            app_management()

    def run_command(self, command_name: str):
        """Run a command on the given app"""
        # Run a command
        def app_management():
            commands = self.project_info.get_commands()
            subprocess.run(["/bin/bash", "-c", f"'cd {self.path}; {commands[command_name]};'"])

        # Check if it's threaded and run command
        if self.threaded:
            thread = Thread(target=app_management)
            thread.start()
        else:
            app_management()
