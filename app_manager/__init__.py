"""App manager

Manages app instantiation and termination,
only for linux"""
import os
import subprocess
from threading import Thread

from ..data_configuration.ProjectInfo import ProjectInfo
from .. import Debug
from ..dbs.RepositorySettings import RepositorySettings

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

        # Check if the user added a parameter to debug the app manager
        if not self.debug:
            should_debug_app_manager = Debug.should_debug_app_manager()
            self.debug = should_debug_app_manager

        # Get app settings
        repository_settings = RepositorySettings()
        self.app_settings = repository_settings.get_repository(self.username, self.app_name)

        self.project_info = ProjectInfo(self.path, debug=debug)

    def send_term_signal(self, pid: int):
        """Send term signal by pid"""
        if self.debug:
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

    def get_process_info_by_command_name(self, command_name: str):
        """Get process infor by command name"""
        if self.debug:
            print("\nAppManager -> get_process_info_by_command_name():")
        # Get the cwd of multiple processes
        pinfo = ProcessInfo(
            command_name,
            ["euser", "pid", "ppid", "cmd"],
            add_cwd=True,
            debug=self.debug)
        pdata = pinfo.get_processes_info_by_name()
        return pdata

    def get_processes_info(self):
        """Get processes info/data"""
        if self.debug:
            print("\nAppManager -> get_processes_info():")
        commands = ProjectInfo(self.path).get_commands()

        # Check if the app has commands first, if not, it's impossible to identify it.
        if not commands:
            print("AppManger -> get_processes_info():")
            msg = "The app has no commands, AppManager can't figure out a way to find the app pid."
            # TODO: It's still possible to get the pid if you have the cwd.
            #       But this might be too slow.
            raise Exception(msg)

        # Split by spaces and get the first which is the command name
        command_name = commands["start"].split(" ")[0]
        if self.debug:
            print(f"Command name: {command_name}")

        processes_data = self.get_process_info_by_command_name(command_name)
        return processes_data

    def terminate_app(self):
        """Terminate an app by the command name"""
        if self.debug:
            print("\nAppManager -> terminate_app():")
        processes_data = self.get_processes_info()

        # Some process have more than one subprocess that must also
        # be killed, so don't break the loop after killing one subprocess
        for process in processes_data:
            if self.debug:
                print(f"--- {process['pid']} ---")
                print(f"User: {process['euser']}")
                print(f"Current Working Directory(cwd): {process['cwd']}")
                print(f"Command: {process['cmd']}")

            try:
                # This throws an error if it's not DevTools compatible(Doesn't have a settings.json
                # with the field 'devtools')
                ProjectInfo(process["cwd"])

                # This app is DevTools compatible
                # Check if it's the same app we are looking for
                if self.path == process["cwd"]:
                    # This is the app
                    if self.debug:
                        print("Status: This is the app, sending kill signal.")
                    subprocess.run(["kill", "-s", "15", f"{process['pid']}"])
                    # The app might have more processes therefore we need to keep looping
            except:
                # This app is not DevTools compatible
                if self.debug:
                    print("Status: This is not the app.")

    def is_app_running(self):
        """Check if the app is running"""
        if self.debug:
            print("AppManager -> terminate_app():")


    ##################
    ### Operations ###
    ##################
    def start_app(self):
        """Starts the application in the background"""
        if self.debug:
            print("AppManager -> start_app():")

        def start_app():
            # The app will be executed on creation
            StartApp(self.path, self.project_info, debug=self.debug)

        if self.threaded:
            thread = Thread(target=start_app)
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
                # subprocess.run(["kill", "-s", "15", f"{pid}"])
                self.send_term_signal(pid)
                return

            # If the app has no stop command, no pid file, we need to do it the hard way.
            # Search for the app and terminate it
            self.terminate_app()
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
