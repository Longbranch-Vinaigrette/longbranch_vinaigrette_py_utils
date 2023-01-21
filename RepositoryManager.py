from datetime import datetime, timedelta
import dateutil.parser
import json
import os
from queue import Queue
from threading import Event, Lock

from . import OStuff
from src.submodules.sub_sqlite3_utils import Sqlite3Utils


def get_subdirectories(scan_path: str):
    """Get subdirectories of a specific path"""
    return [f.path for f in os.scandir(scan_path) if f.is_dir()]


class RepositoryManager:
    """Repository manager"""
    projects_path: str = OStuff.get_default_path()
    username: str = ""
    token: str = ""
    unique_key: str = "full_name"
    debug: bool = False

    sleep = 3.0
    max_clone_repositories: int = 5000

    # 300 seconds = five minutes
    sleep_between_attempts = 300

    repositories: list = []
    old_repositories: list = []

    # Start the library
    sql_repositories_table = None

    rep_mirror = None

    def __init__(self, projects_path: str,
                 username: str,
                 token: str,
                 lock: Lock,
                 queue: Queue,
                 unique_key: str = "full_name",
                 sleep: int = 3,
                 max_clone_repositories: int = 5000,
                 debug: bool = False,
                 sleep_between_attempts=600,
                 db_name: str = "dev_gui.db",
                 git_pull_callback=None,
                 git_clone_callback=None):
        """Constructor

        sleep: Sleep between pulls and/or clones, in seconds"""
        # Remove '/' at the end of the provided path
        projects_path = projects_path[:-1] if projects_path.endswith("/") else projects_path
        self.projects_path = projects_path

        self.username = username
        self.token = token
        self.lock = lock
        self.queue = queue
        self.unique_key = unique_key
        self.sleep = sleep
        self.max_clone_repositories = max_clone_repositories
        self.debug = debug
        self.sleep_between_attempts = sleep_between_attempts
        self.db_name = db_name
        self.git_pull_callback = git_pull_callback
        self.git_clone_callback = git_clone_callback

        if self.debug:
            print("RepositoryMirror - __init__():")

        # To stop this thread
        self.stop = False

        # This function solves every problem with the path
        db_path = OStuff.get_sql_db_path(db_name)

        # Create repositories table
        # sqlite3_utils.insert_replace() creates new keys for the table if
        # the keys in the data provided are not in the table,
        # so we can create a table with only one key,
        # preferably, the unique key with a value that will exist in future data,
        # so it can be replaced
        self.sql_repositories_table = Sqlite3Utils(
            db_path,
            "repositories")

        # Repository mirror
        from src.submodules.sub_repository_mirror import RepositoryMirror
        self.rep_mirror = RepositoryMirror(
            token=token,
            username=username,
            debug=self.debug)

        if self.debug:
            print("Fetching repositories from github")
        # repository-mirror submodule
        # self.rep_mirror.token = token
        # self.rep_mirror.username = username
        self.repositories = self.fetch_repository_data(sleep=0)
        if not self.repositories:
            if self.debug:
                print("No repositories fetched")

            # This return is wrong
            # Because the user could have an organization
            # return
        if self.debug:
            print("Fetching done")

        # List organizations
        orgs = self.rep_mirror.list_user_organizations()
        if self.debug:
            print("Organizations: ")

        # Create folders
        # org["login"] is the organization name
        folder_names = [username] + [org["login"] for org in orgs]
        for name in folder_names:
            folder_path = f"{projects_path}{os.path.sep}{name}"
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

        # Get the repositories of the organizations
        org_repositories = [self.get_org_repositories(org) for org in orgs]
        for org_repos in org_repositories:
            self.repositories += org_repos

        # Get repositories on the local database
        self.old_repositories = self.sql_repositories_table.get_all()

        # Get the filename of the DB
        with open(f"{os.getcwd()}{os.path.sep}local_data.json", "r") as f:
            local_data = json.load(f)
            db_filename = local_data["DBFilename"]
        db_path = OStuff.get_sql_db_path(db_filename)
        self.sql_repository_settings = Sqlite3Utils(db_path, "repository_settings")

        # It wasn't working, because I didn't update this value on the loop
        # current_time = datetime.now()

        # Update submodules
        update_in = timedelta(days=0,
                              hours=0,
                              minutes=0,
                              seconds=0,
                              microseconds=0)

        check_should_stop = timedelta(days=0,
                              hours=0,
                              minutes=0,
                              seconds=0,
                              microseconds=0)

        ten_seconds_passed = False
        while True:
            current_time = datetime.now()
            now = timedelta(days=current_time.day,
                            hours=current_time.hour,
                            minutes=current_time.minute,
                            seconds=current_time.second,
                            microseconds=current_time.microsecond)

            if self.should_stop():
                break

            # Do something every ten seconds
            if now.seconds % 10 == 0 and not ten_seconds_passed:
                if self.debug:
                    print("Seconds: ", now.seconds)
                    print("The now: ", now)
                    print("The check should stop: ", check_should_stop)
                    print("now > check_should_stop: ", now > check_should_stop)
                ten_seconds_passed = True

            # We have to make a switch here
            if now.seconds % 11 == 0:
                ten_seconds_passed = False

            # Check if it should stop
            if now > check_should_stop:
                if self.debug:
                    print("RepositoryManager -> __init__() -> check_should_stop:")

                if self.stop:
                    break

                # Check on the settings table
                sql_settings_table = Sqlite3Utils(
                    db_path,
                    "settings")
                try:
                    if self.debug:
                        print("Checking should stop")
                    should_stop = \
                        sql_settings_table.get("key", "stop_repository_manager")["value"]

                    # Should stop is a json string
                    should_stop = json.loads(should_stop)["value"]

                    if self.debug:
                        print("Should stop: ", should_stop)

                    # Stop the loop
                    if should_stop:
                        if self.debug:
                            print("RepositoryManager will be stopped.")
                        # Now to not stop it the next time, we have to set it to false
                        sql_settings_table.insert_replace_v2(
                            {
                                "key": "stop_repository_manager",
                                "value": False,
                            },
                            {
                                "key": "stop_repository_manager"
                            }
                        )
                        break
                except Exception as ex:
                    if self.debug:
                        print("Exception: ", ex)

                if self.debug:
                    print("RepositoryManager will not be stopped.")
                check_should_stop = timedelta(days=current_time.day,
                                      hours=current_time.hour,
                                      minutes=current_time.minute,
                                      # Check every minute
                                      seconds=current_time.second + 60,
                                      microseconds=current_time.microsecond)

                if self.debug:
                    print("The now: ", now)
                    print("Check should stop: ", check_should_stop)

            # Update repositories
            if now > update_in:
                self.update_repositories()

                if self.stop:
                    break

                update_in = timedelta(days=current_time.day,
                                      hours=current_time.hour,
                                      minutes=current_time.minute,
                                      seconds=current_time.second + self.sleep_between_attempts,
                                      microseconds=current_time.microsecond)
                if self.debug:
                    print("Sleeping before trying to check updates again.")
                    print("Minutes:Seconds")
                    print(f"The now: {current_time.minute}:{current_time.second}")
                    seconds = self.sleep_between_attempts + current_time.second
                    minutes = int(seconds / 60) + current_time.minute
                    seconds = seconds % 60 if minutes >= 1 else seconds
                    print(f"The update in: {minutes}:{seconds}")
                    print(f"Now > update_in: {now > update_in}")
                    print(f"Now < update_in: {now < update_in}")
                    print(f"It will update in: {self.sleep_between_attempts / 60} minutes.")
                # threading.Event.wait(pause, timeout=self.sleep_between_attempts)

        # After the loop ends

    def get_org_repositories(self, org: dict):
        """Fetch and return the repositories of a given organization

        'org' must be an organization information dictionary that you get
        from querying GitHub api"""
        if self.debug:
            print("RepositoryManager -> get_org_repositories():")

        org_name = org["login"]

        endpoint = f'/orgs/{org_name}/repos'
        organization_repositories = self.rep_mirror.run_query(endpoint)
        if self.debug:
            print(f"{org_name}: {len(organization_repositories)}")
            print(f"Repositories names: ", [org["name"] for org in organization_repositories])
            print(f"Repositories: {len(organization_repositories)}")

        return organization_repositories

    def should_stop(self):
        """Check if it should stop

        Returns true if it should stop"""
        with self.lock:
            value = ""
            if not self.queue.empty():
                value = self.queue.get()

                # It's a dictionary
                if isinstance(value, dict):
                    pass
                # The thread has to stop
                elif value == "stop":
                    if self.debug:
                        print("Received stop signal, stopping RepositoryManager")
                    return True
        return False

    def fetch_repository_data(self, per_page=100,
                              sleep=5, max_repos=100, debug=False):
        """Fetch repository data"""
        if self.debug or debug:
            print("\n- fetch_repository_data():")

        credentials = self.rep_mirror.check_credentials()
        if self.debug or debug:
            if credentials:
                print("Credentials OK")
            else:
                print("Bad credentials")

        if not credentials:
            return None

        # GitHub has a limit of 100 repos per request
        rep_data = self.rep_mirror.get_repository_list(
            per_page,
            sleep,
            max_repos,
            debug=False)

        # Save the data
        for rep in rep_data:
            self.sql_repositories_table.insert_replace(rep, self.unique_key, rep[self.unique_key])

        if debug:
            print("Total fetched: ", len(rep_data))
            print("Done fetching printing the first ten: ")
            for i in range(len(rep_data)):
                if rep_data[i] is None:
                    break
                print(f"{i}: {rep_data[i][self.unique_key]}")

        return rep_data

    def get_old_repository_data(self, name):
        """Get old repository data"""
        for repository in self.old_repositories:
            if repository["name"] == name:
                return repository

    def insert_update(self, rep_data: dict, unique_key: str, unique_key_val):
        """Update repository locally"""
        self.sql_repositories_table.insert_replace(rep_data,
                                                   unique_key_name=unique_key,
                                                   unique_key_val=unique_key_val)

    def update_repositories(self):
        """Update repositories"""
        projects_path: str = self.projects_path
        # subdirectories = get_subdirectories(projects_path)
        pause: Event = Event()

        max_clone_repositories: int = self.max_clone_repositories

        # These repositories are the recently fetched ones
        for i in range(len(self.repositories)):
            repository = self.repositories[i]

            if max_clone_repositories <= 0:
                break
            full_name: str = repository[self.unique_key]
            splitted: list = full_name.split("/")
            username: str = splitted[0]
            repo_name: str = splitted[1]
            user_path: str = f"{projects_path}{os.path.sep}{username}"

            if self.debug:
                print(f"----- {full_name} -----")
                print(f"Repo name: {repo_name}")

            # if username in user_folders:
            clone_url = repository["ssh_url"]

            # Get folders in this directory
            local_repositories = get_subdirectories(user_path)

            # /home/[USERNAME]/.devgui/repositories/[GITHUB_USERNAME]
            # print(f"User path: {user_path}")

            # Repo folders
            repo_folders = [subd.split("/")[-1] for subd in local_repositories]

            if repo_name in repo_folders:
                # Here is where one should check if the repository
                # was updated, or not
                # We can use "pushed_at" to check the last time it was pushed,
                # and then check if it's different from the local database,
                # then pull the repository
                old_repository_data: dict = self.get_old_repository_data(repo_name)
                if not old_repository_data:
                    print(f"Warning: When looking for {repo_name} there was no data found.")
                    continue

                # Parse dates
                old_date = dateutil.parser.isoparse(old_repository_data["pushed_at"])
                new_date = dateutil.parser.isoparse(repository["pushed_at"])

                if self.debug:
                    print("Old date: ", old_date)
                    print("New date: ", new_date)
                if new_date > old_date:
                    if self.debug:
                        print("The remote repository is newer")

                    # This repository must be pulled
                    if self.debug:
                        print(f"Detected changes on the remote repository, pulling: {clone_url}")
                        print("Last push: ", new_date)
                    repo_path = f"{user_path}/{repo_name}"

                    # Commands
                    raw_cmds = f'''
                        cd {repo_path};
                        pwd;
                        git pull {clone_url};
                        '''
                    if self.debug:
                        print("Running: ", raw_cmds)
                    OStuff.run_commands(raw_cmds)

                    # Now after pulling, we have to update the repository data locally
                    self.insert_update(
                        repository,
                        self.unique_key,
                        full_name)

                    # Call event
                    self.on_git_pull(
                        repo_name,
                        repo_path,
                        self.unique_key,
                        full_name)
                else:
                    if self.debug:
                        print("The remote repository is older or the same")
                    # Skip
                    continue
            else:
                if self.debug:
                    print(f"Repository doesn't exist, cloning: {clone_url}")
                # Commands
                raw_cmds = f'''
                    cd {user_path};
                    pwd;
                    git clone {clone_url};
                    '''
                OStuff.run_commands(raw_cmds)

                # Update data locally
                self.insert_update(
                    repository,
                    self.unique_key,
                    full_name)

                # Only when repositories are cloned will this count go down
                max_clone_repositories -= 1

                # Call event
                repo_path = f"{user_path}/{repo_name}"
                self.on_git_clone(repo_name, repo_path)

            # Wait before the next action
            Event.wait(pause, timeout=self.sleep)

            # After cloning or pulling
            # Check if it should stop
            self.stop = self.should_stop()
            if self.stop:
                return

    # Events
    def on_git_pull(
            self,
            repository_name: str,
            repository_path: str,
            unique_key: str,
            full_name: str,
            ):
        """Called after a git pull"""
        if self.debug:
            print("RepositoryManager -> on_git_pull():")
            print(f"Repository pulled: {repository_name}")

        if self.git_pull_callback is not None:
            self.git_pull_callback(
                repository_name,
                f"{repository_path}",
                unique_key,
                full_name,
                # self.sql_repository_settings,
                debug=True
            )

    def on_git_clone(
            self,
            repository_name: str,
            repository_path: str):
        """Called after a git clone"""
        if self.debug:
            print("RepositoryManager -> on_git_clone():")
            print(f"Repository cloned: {repository_name}")

        if self.git_clone_callback is not None:
            self.git_clone_callback(
                repository_name,
                repository_path)
