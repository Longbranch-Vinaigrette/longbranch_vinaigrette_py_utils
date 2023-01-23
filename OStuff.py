import json
import platform
import os
import subprocess


def get_platform_system(debug:bool=False):
    """ Some examples of platform module
    # platform.platform()
    # 'Linux-3.3.0-8.fc16.x86_64-x86_64-with-fedora-16-Verne'

    platform.system()
    # 'Linux', 'Darwin', 'Java', 'Windows'
    platform.release()
    # 'XP'
    platform.version()
    # '5.1.2600'
    """
    arch = platform.architecture()
    system_name = platform.system()
    # Possible values:
    # ["Windows", "Linux", "Darwin", "Java"]

    if debug:
        print('\n- system_info.get_platform_system()')
        print('Architecture: %s' % (str(arch)))
        print(f"Os: {system_name}")

    # Check for both x86 and x64
    if system_name == "Windows" and '32bit' not in arch:
        return f"{system_name}64bit"
    elif system_name == "Windows" and '64bit' not in arch:
        return f"{system_name}32bit"
    else:
        return system_name


def get_username(debug=False):
    """Get current user username"""
    if debug:
        print("\n- get_username():")

    os_name = get_platform_system(debug=debug)

    if "Windows32bit" == os_name or "Windows64bit" == os_name:
        import getpass
        return getpass.getuser()
    else:
        import pwd
        import os
        # Get username
        return pwd.getpwuid(os.getuid())[0]


def run_commands(raw_cmds: str, debug:bool=False):
    """Run commands"""
    if debug:
        print("\n- get_username():")

    os_name = get_platform_system(debug=debug)

    if os_name in ["Windows32bit", "Windows64bit"]:
        parsed_cmds = bytes(raw_cmds, 'utf8')
        powershell_path = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"

        # For subprocess.Popen()
        # It's recommended to use fully qualified paths, or
        # some things might be overriden
        process: subprocess.Popen = subprocess.Popen([powershell_path],
                                                     stdin=subprocess.PIPE,
                                                     stdout=subprocess.PIPE,
                                                     shell=True)
        out, err = process.communicate(parsed_cmds)
        print(out.decode("utf-8"))
        process.kill()
        return out, err
    else:
        parsed_cmds = bytes(raw_cmds, 'utf8')

        # For subprocess.Popen()
        # It's recommended to use fully qualified paths, or
        # some things might be overriden
        process: subprocess.Popen = subprocess.Popen(["/bin/bash"],
                                                     stdin=subprocess.PIPE,
                                                     stdout=subprocess.PIPE,
                                                     shell=True)
        out, err = process.communicate(parsed_cmds)
        print(out.decode("utf-8"))
        process.kill()
        return out, err


def create_folders_recursively(path: str):
    """Create folders recursively

    Warning: Don't use relative paths!!"""
    if path.startswith("./"):
        # NO.
        raise Exception("When using create_folders_recursively, "
                        "you have to use the full path.")
    
    folder_listA: list = path.split(os.path.sep)
    folder_list: list = []

    # The first string is empty
    for folder in folder_listA:
        if folder:
            folder_list.append(folder)

    check_path = "/"
    for folder in folder_list:
        check_path += folder

        if not os.path.exists(f"{check_path}"):
            os.mkdir(f"{check_path}")

        # Add a slash
        check_path += "/"


class Shortcut:
    debug = False

    # Get app name
    try:
        with open(f".{os.path.sep}settings.json") as f:
            app_name = json.load(f)["name"]
    except:
        pass

    """Shortcut management and auto start applications"""
    def __init__(self):
        self.user_system = get_platform_system()
        if self.user_system == "Linux":
            self.home_path = f"{os.path.expanduser('~')}"
            self.config_path = f"{self.home_path}/.config"
            self.autostart_path = f"{self.config_path}/autostart"
            self.app_path = f"{self.autostart_path}/DevGui.desktop"

            # Check if it's a distribution build or is just the repository
            with open(f"{os.getcwd()}{os.path.sep}settings.json") as f:
                data = json.load(f)

                try:
                    self.release = data["release"]
                except:
                    # IT's a repository
                    if os.path.exists(f"{os.getcwd()}{os.path.sep}.git"):
                        self.release = False
                    else:
                        self.release = True

    def make_auto_start(self):
        """Make the application autostart when the user boots the device"""
        if self.user_system == "Linux":

            # Props to this random
            # https://askubuntu.com/questions/814/how-to-run-scripts-on-start-up
            if not os.path.exists(self.config_path):
                os.mkdir(self.config_path)
            if not os.path.exists(self.autostart_path):
                os.mkdir(self.autostart_path)

            # Replace older version with this new version
            # Create the .desktop thingy
            info = self.get_dot_desktop_file_data()
            with open(f"{self.app_path}", "w") as f:
                f.write(info)

    def remove_auto_start(self):
        """Remove application autostart when the user boots the device"""
        if self.user_system == "Linux":
            if os.path.exists(self.app_path):
                os.remove(self.app_path)

    def get_dot_desktop_file_data(self, name=None):
        """Get .desktop file data"""
        if not name:
            name = self.app_name

        # Get the execution method
        if self.release:
            execution_method = f"{os.getcwd()}{os.path.sep}{name}"
        else:
            # This app was made on python3.10
            run_app_cmd = f"python3.10 {os.getcwd()}{os.path.sep}main.py"
            cd_to_app_cmd = f"cd {os.getcwd()}"
            execution_method = f'/bin/bash -c "{cd_to_app_cmd}; {run_app_cmd};"'

        if self.debug:
            print("Execution method: ", execution_method)

        # References
        # https://askubuntu.com/questions/281293/creating-a-desktop-file-for-a-new-application
        # https://specifications.freedesktop.org/desktop-entry-spec/latest/
        dot_desktop = \
            "[Desktop Entry]\n" \
            "Version=1.5\n" \
            f"Name={name}\n" \
            f"Comment=DevGui is a program.\n" \
            f"Exec={execution_method}\n" \
            f"Path={os.getcwd()}\n" \
            f"Icon={os.getcwd()}{os.path.sep}icon.svg\n" \
            f"Terminal=false\n" \
            f"Type=Application\n" \
            f"Categories=Utility;Development;\n"
        return dot_desktop


##################
### Path stuff ###
##################
"""Everything that was here was moved to /data_configuration"""
