"""
References
https://askubuntu.com/questions/281293/creating-a-desktop-file-for-a-new-application
https://specifications.freedesktop.org/desktop-entry-spec/latest/
https://askubuntu.com/questions/814/how-to-run-scripts-on-start-up
https://askubuntu.com/questions/5172/running-a-desktop-file-in-the-terminal
"""
import os


class DesktopEntry:
    debug = False

    def __init__(
            self,
            app_path: str,
            app_name: str,
            commands: str,
            version: str = "v1.0.0",
            debug: bool = False):
        """This an API for the "desktop entries" standard

        More info at:
        https://specifications.freedesktop.org/desktop-entry-spec/latest/
        """
        self.app_path = app_path
        self.app_name = app_name
        self.commands = commands
        self.version = version
        self.debug = debug

        if self.debug:
            print("Shortcut -> __init__():")

        self.home_path = f"{os.path.expanduser('~')}"
        self.config_path = f"{self.home_path}/.config"
        self.autostart_path = f"{self.config_path}/autostart"
        self.desktop_entry_path = f"{self.autostart_path}/{app_name}.desktop"

        # Create directories if they don't exist
        if not os.path.exists(self.config_path):
            os.mkdir(self.config_path)
        if not os.path.exists(self.autostart_path):
            os.mkdir(self.autostart_path)

    def get_start_on_boot(self):
        """Get start on boot

        :returns True if start on boot is enabled, false otherwise"""
        return os.path.exists(self.desktop_entry_path)

    def enable_start_on_boot(self):
        """Make the application start when the user boots the device"""
        info = self.get_dot_desktop_file_data()
        with open(f"{self.desktop_entry_path}", "w") as f:
            f.write(info)

    def disable_start_on_boot(self):
        """Remove application's 'start on boot' feature"""
        if os.path.exists(self.desktop_entry_path):
            os.remove(self.desktop_entry_path)

    def toggle_start_on_boot(self):
        """Toggles between 'enable_start_on_boot' and 'disable_start_on_boot'
        If the app doesn't start on boot, this will make it so the application does start on boot,
        otherwise if the application starts on boot, this will remove that feature."""
        if os.path.exists(self.desktop_entry_path):
            self.disable_start_on_boot()
        else:
            self.enable_start_on_boot()

    def get_dot_desktop_file_data(self):
        """Get .desktop file data"""
        dot_desktop = \
            "[Desktop Entry]\n" \
            f"Version={self.version}\n" \
            f"Name={self.app_name}\n" \
            f"Comment={self.app_name} is an app\n" \
            f"Exec={self.commands}\n" \
            f"Path={self.app_path}\n" \
            f"Icon={self.app_path}{os.path.sep}icon.svg\n" \
            f"Terminal=false\n" \
            f"Type=Application\n" \
            f"Categories=Utility;Development;\n"
        return dot_desktop
