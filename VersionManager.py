import os
import json
import shutil


class VersionManager:
    versions_path = f"{os.getcwd()}{os.path.sep}.."

    def __init__(self):
        self.highest_version: str = ""

        # Get this application version and
        # get a list of integers of this application version
        with open(f"{os.getcwd()}{os.path.sep}settings.json") as f:
            self.app_info = json.load(f)

            # Convert a version to an integer list
            self.current_version_list = self.version_to_int_list(self.app_info["version"])

    def get_highest_version(self) -> str:
        """Get the highest version

        It's required to check higher versions with
        the function check_higher_versions"""
        return self.highest_version

    def get_highest_version_path(self) -> str:
        """Get the highest version path

        It's required to check higher versions with
        the function check_higher_versions"""
        return f"{os.getcwd()}{os.path.sep}..{os.path.sep}{self.highest_version}"

    def is_this_app(self, path: str):
        """Check if the app at the path is this application"""
        # Verify that it's this app
        try:
            with open(path) as f:
                temp_data = json.load(f)

                # It's not the same program/application
                if not temp_data["name"] == self.app_info["name"]:
                    return False
        except Exception as ex:
            # It doesn't have settings.json, therefore is not this app
            return False
        return True

    def version_to_int_list(self, version: str):
        """Convert a version to an int list"""
        # It could be like this v1.1.1-beta
        # It firsts replaces the "v" for nothing so it's removed
        # then splits the '-'(hyphen)(result: [1.1.1, beta])
        # then it takes the first item, which in
        # this case would be 1.1.1, then it is split again
        # and the result will be [1, 1, 1]
        version_list = version.replace("v", "").split("-")[0].split(".")

        # Parse integers
        version_list = [int(version) for version in version_list]
        return version_list

    def check_higher_versions(self) -> bool:
        """Check if there is a higher version on the device

        Returns True if there is a higher version"""
        folders = [f.path for f in os.scandir(self.versions_path) if f.is_dir()]

        higher_version = self.app_info["version"]
        for folder in folders:
            # Grab the last one, which is the folder name,
            # and at the same time, it's its version
            app_version = folder.split("/")[-1]

            # Check if it is this app
            app_settings_path = f"{self.versions_path}{os.path.sep}" \
                                f"{app_version}{os.path.sep}settings.json"
            if not self.is_this_app(app_settings_path):
                continue

            # Separate version
            try:
                versions = self.version_to_int_list(app_version)
            except:
                # It's not this application
                continue
            for i in range(len(self.current_version_list)):
                if versions[i] > self.current_version_list[i]:
                    # There is a version greater than this one, in this device,
                    # but, this one may not be the only one, so break the
                    # inner loop and keep searching
                    higher_version = app_version
                    break

        # If they are different
        # it means that the user is using a lower version, whilst
        # there is a higher version in his device
        if not higher_version == self.app_info["version"]:
            self.highest_version = higher_version
            return True
        return False

    def get_older_versions_list(self, debug=False) -> list:
        """Get older versions list"""
        if debug:
            print("/src/utils -> VersionManager -> get_older_versions_list():\n")
        folders = [f.path for f in os.scandir(self.versions_path) if f.is_dir()]

        if debug:
            print("Versions path: ", self.versions_path)
            print("Folders: ", folders)

        with open(f"{os.getcwd()}{os.path.sep}settings.json") as f:
            app_info = json.load(f)
            current_version = []
            # It could be like this 1.1.1-beta
            # Basically it first splits the -(result: [1.1.1, beta])
            # then it takes the first item, which in
            # this case would be 1.1.1, then it is split again
            # and the result will be [1, 1, 1]
            for version in app_info["version"].replace("v", "") \
                    .split("-")[0].split("."):
                try:
                    current_version.append(int(version))
                except Exception as ex:
                    pass

        if debug:
            print("\nCurrent version: ", current_version)

        older_versions = []
        for folder in folders:
            # Grab the last one, which is the folder name,
            # and at the same time, it's its version
            app_version = folder.split("/")[-1]
            print(f"\n--- App: {app_version} ---")

            # Verify that it's this app
            try:
                with open(f"{self.versions_path}{os.path.sep}"
                          f"{app_version}{os.path.sep}settings.json") as f:
                    temp_data = json.load(f)

                    # It's not the same program/application
                    if not temp_data["name"] == app_info["name"]:
                        if debug:
                            print("It's not this application, skipping...")
                        continue
            except Exception as ex:
                # It doesn't have settings.json
                if debug:
                    print("It's not this application, skipping...")
                    print("Exception: ", ex)
                continue

            # Separate version
            versions = app_version.replace("v", "").split("-")[0].split(".")
            if debug:
                print("Versions: ", versions)
            for i in range(len(current_version)):
                version = versions[i]
                try:
                    version = int(versions[i])
                except:
                    # Can't be converted, next
                    if debug:
                        print("This ", version, " cannot be converted to int.")
                    break
                this_version = current_version[i]
                if version < this_version:
                    # There is a version greater than this one, in this device,
                    # but, this one may not be the only one, so break the
                    # inner loop and keep searching
                    if debug:
                        print("\n", version, " is less than the current one,"
                            "therefore it should be deleted.")
                    older_versions.append(app_version)
                    break
        return older_versions

    def delete_previous_versions(self, debug=False):
        """Delete previous versions"""
        if debug:
            print("\n/src/utils -> VersionManager -> delete_previous_versions():")

        older_versions = self.get_older_versions_list(debug=debug)
        if debug:
            print("\nPrevious versions: ", older_versions)

        if len(older_versions) > 0:
            for version in older_versions:
                directory = f"{self.versions_path}{os.path.sep}{version}"
                if debug:
                    print(f"Deleting directory {directory}")
                shutil.rmtree(directory)
