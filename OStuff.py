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


def run_commands(raw_cmds: str, debug: bool = False):
    """Run commands"""
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
    else:
        parsed_cmds = bytes(raw_cmds, 'utf8')

        # For subprocess.Popen()
        # It's recommended to use fully qualified paths, or
        # some things might be overriden
        process: subprocess.Popen = subprocess.Popen(["/bin/bash", "-c"],
                                                     stdin=subprocess.PIPE,
                                                     stdout=subprocess.PIPE,
                                                     shell=True)
        out, err = process.communicate(parsed_cmds)

    if out:
        print(out.decode("utf-8"))
    elif err:
        print(err.decode("utf-8"))
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

