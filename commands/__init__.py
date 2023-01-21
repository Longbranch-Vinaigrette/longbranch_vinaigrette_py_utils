import pprint

from src.submodules.sub_repository_mirror import RepositoryMirror

from src import utils
from src.utils.dbs import RepositorySettings


def list_github_organizations(arg, sql_settings_table):
    """List GitHub organizations"""
    github_token = utils.try_get(sql_settings_table, "github_token")
    github_username = utils.try_get(sql_settings_table, "github_username")

    repository_mirror = RepositoryMirror(
        token=github_token,
        username=github_username)
    try:
        # Check credentials and fetch data
        credentials = repository_mirror.check_credentials()
        print(f"Credentials: {credentials}")
        user_organizations = repository_mirror.list_user_organizations()

        # Check what options the user chose
        if arg == "all":
            print("User organizations: ")
            pprint.pprint(user_organizations)
        else:
            key_list = arg.split(",")
            error_msg = "Options are: 'all', or comma separated keys."

            msg = ""
            for org in user_organizations:
                print(f" --- Org: {org['login']} ---")
                for key in key_list:
                    if key in org:
                        msg += f"{key}: {org[key]}\n"
                print(msg)
                msg = ""
    except Exception as ex:
        print("Error: ")
        print(ex)


def print_github_token(sql_settings_table):
    """Print GitHub token"""
    token = utils.try_get(sql_settings_table, "github_token")
    print("GitHub token: ", token)


def print_github_username(sql_settings_table):
    """Print GitHub username"""
    username = utils.try_get(sql_settings_table, "github_username")
    print("GitHub username: ", username)


def print_repository_settings(username_and_repo_name: str):
    """Print repository settings"""
    repo_settings = RepositorySettings()

    # Get username and repository name
    username, repo_name = username_and_repo_name.split(",")

    # Get data from sqlite
    data = repo_settings.get_repository(username, repo_name)
    print(f"Repository settings for {username}/{repo_name}:")
    pprint.pprint(data)


def repository_settings_set_default_path(username_and_repo_name: str):
    """Change path to default path on a given repository"""
    try:
        repo_settings = RepositorySettings()

        # Get username and repository name
        username, repo_name = username_and_repo_name.split(",")

        # Set default path
        repo_settings.set_default_path(username, repo_name)

        print(f"Repository settings set default path for {username}/{repo_name} [Ok]")
    except Exception as ex:
        print("Exception: ", ex)
        print("Repository settings set default path [Failed]")


def repository_settings_set_default_path_for_every_repository():
    """Restore default path for every repository"""
    try:
        repo_settings = RepositorySettings()

        repo_settings.set_default_path_for_every_repository()

        print("Repository settings set default path for every repository [Ok]")
    except Exception as ex:
        print("Exception: ", ex)
        print("Repository settings set default path for every repository [Failed]")
