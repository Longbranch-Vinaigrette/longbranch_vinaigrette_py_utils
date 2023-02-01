"""Get process info v2

Added process cwd along with the process info, the command used
to get the path is a bit slow though.

IMPORTANT: Even if I don't use it, don't remove it unless I make a better version of it.

Reference/s:
https://realpython.com/python-subprocess/#processes-and-subprocesses
https://stackoverflow.com/questions/606041/how-do-i-get-the-path-of-a-process-in-unix-linux
https://man7.org/linux/man-pages/man1/ps.1.html
"""
import subprocess


class ProcessInfo:
    def __init__(
            self,
            process_name: str,
            format_specifiers: list = [],
            add_cwd: bool = False,
            debug: bool = False):
        """Note that for the cwd it's required to have the pid"""
        self.process_name = process_name
        self.format_specifiers = format_specifiers
        self.add_cwd = add_cwd
        self.debug = debug

        # If no format specifiers are given
        # this will be the default
        if len(format_specifiers) <= 0:
            # When using default 'ps -ef', these are the formats:
            # "uid", "pid", "c", "stime", "tty", "time", "cmd"
            # but in reality their names are different
            self.format_specifiers = "euser,pid,ppid,c,stime,tty,time,cmd".split(",")

    def run_subprocess(self, cmd: str):
        """Run a subprocess"""
        try:
            process = subprocess.run([
                "bash", "-c", cmd
            ],
                check=True,  # If there's an error raise an exception
                capture_output=True,  # Store output on process.stdout
            )

            # Store data
            process_info = process.stdout.decode("utf-8")
            return process_info
        except FileNotFoundError as exc:
            if self.debug:
                print(f"Process failed because the executable could not be found.\n{exc}")
        except subprocess.CalledProcessError as exc:
            if self.debug:
                print(
                    f"Process failed because did not return a successful return code. "
                    f"Returned {exc.returncode}\n{exc}"
                )
        except subprocess.TimeoutExpired as exc:
            if self.debug:
                print(f"Process timed out.\n{exc}")
        return None

    def get_cwd(self, pid: str):
        """Get cwd by pid"""
        cwd = self.run_subprocess(f"readlink /proc/{pid}/cwd")

        if cwd:
            # The [:-1] is because it comes with a f*ing space at the end, I've wasted 20 minutes
            # of my life trying to figure it out.
            cwd = cwd[:-1]
        return cwd

    def get_cwd_by_pid_lsof(self, pid: str):
        """Get working directory of the process running with the given pid

        @deprecated"""
        # lsof is too slow
        cwd = self.run_subprocess(f"lsof -p {pid} | grep cwd")

        # Some processes don't have cwd
        if not cwd:
            return

        return self.parse_cwd(cwd)

    def parse_info(self, pinfo: str, format_names: list):
        """Parse any kind of info given by the output of the ps command"""
        result = {}

        for i in range(len(format_names)):
            # If it's the last one, just add it directly
            if i == len(format_names) - 1:
                result[format_names[i]] = pinfo
                break

            # The first is username
            try:
                format_value, remaining = pinfo.split(' ', maxsplit=1)
                result[format_names[i]] = format_value
            except Exception as ex:
                # Sometimes the last element is empty, thus
                # this would throw an error
                if self.debug:
                    print("Exception: ", ex)
                break
            remaining = remaining.strip()
            pinfo = remaining

        return result

    def parse_cwd(self, cwd: str):
        """Parse cwd to human-readable"""
        names = ["Command", "Pid", "User", "FD", "Type", "Device", "Size/Off",
                 "Node", "Name"]

        return self.parse_info(cwd, names)["Name"]

    def get_custom_processes_by_name(self, name: str, format_specifiers: list):
        """Get process information by process name"""
        cmd = f"ps -eo {','.join(format_specifiers)} | grep {name}"
        if self.debug:
            print("Cmd: ", cmd)
        return self.run_subprocess(cmd)

    def custom_process_data_to_dictionary_list(
                self,
                process_data: str,
                format_specifiers: list
            ) -> list:
        """Convert process data to dictionary list

        Convert proces data returned by using 'ps' command to a
        dictionary list"""
        plist = process_data.split('\n')
        result = []

        for i in range(len(plist)):
            process: str = plist[i]

            # Get process info as  a dictionary
            parsed_info: dict = self.parse_info(process, format_specifiers)

            # Check if it's empty
            if len(list(parsed_info.keys())) <= 0:
                continue

            if self.add_cwd:
                # Get cwd by pid
                pid = parsed_info["pid"]
                process_cwd = self.get_cwd(pid)
                parsed_info["cwd"] = process_cwd

            result.append(parsed_info)

        return result

    def get_processes_info_by_name(self):
        """Get process info by name"""
        process_str_data = self.get_custom_processes_by_name(
            self.process_name, self.format_specifiers)
        pdata = self.custom_process_data_to_dictionary_list(
            process_str_data,
            self.format_specifiers)
        return pdata

    def get_custom_processes_info_by_name(self, name: str, format_specifiers: list = []):
        """Get process info by name"""
        if len(format_specifiers) <= 0:
            format_specifiers = self.format_specifiers

        process_str_data = self.get_custom_processes_by_name(name, format_specifiers)
        pdata = self.custom_process_data_to_dictionary_list(process_str_data, format_specifiers)
        return pdata
