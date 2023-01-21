import argparse

from . import commands as cmd
from . import LocalData


# Reference/s
# https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments
def parse_arguments():
    """Parse given arguments"""
    # Instantiate the parser
    parser = argparse.ArgumentParser(description="DevGui description")

    # $./main.py --github-token some_github_token
    # Optional arguments
    # Those that change the database
    parser.add_argument("--github-token", type=str,
                        help="The github token to be used")
    parser.add_argument("--github-username", type=str,
                        help="The github username")

    # Those that don't change the database
    parser.add_argument("--debug", type=str,
                        help="Debug and what to debug, comma separated")
    # Options: RepositoryMirror, AppManager

    # No gui
    parser.add_argument("--cmd-only", action='store_true',
                        help="Run commands without interface")
    parser.add_argument("--no-gui", action='store_true',
                        help="Run commands without interface")

    # Print stuff into the console
    parser.add_argument("--list-github-organizations", type=str,
                        help="List the logged in user github organizations.\n"
                             "Options are: 'all', or comma separated keys.")
    parser.add_argument("--print-github-token", action='store_true',
                        help="Prints the github token in the console")
    parser.add_argument("--print-github-username", action='store_true',
                        help="Prints the github username in the console")

    # Local repository settings
    parser.add_argument("--print-repository-settings", type=str,
                        help="print repository settings, the arguments are comma separated\n"
                             "[USERNAME],[REPOSITORY NAME]")
    parser.add_argument("--repository-settings-set-default-path", type=str,
                        help="Restores repository path to default path, the arguments are comma separated\n"
                             "[USERNAME],[REPOSITORY NAME]")
    parser.add_argument("--repository-settings-set-default-path-for-every-repository", action='store_true',
                        help="Restores the default path of every repository, the arguments are \n"
                             "comma separated: [USERNAME],[REPOSITORY NAME]")

    # Start server in the background
    parser.add_argument("--start-server", action="store_true",
                        help="Start server in the background.")
    parser.add_argument("--start-basic-http-server", action="store_true",
                        help="Start basic http server in the background(completely useless).")
    parser.add_argument("--start-optimal-server", action="store_true",
                        help="Start optimal server in the background.")
    parser.add_argument("--port",
                        type=str,
                        help="Set the port to start the server.")

    # Parse
    args = parser.parse_args()

    # Here the keys must match those in the database
    return {
            "github_token": args.github_token,
            "github_username": args.github_username,
            "debug": args.debug,
            "cmd_only": args.cmd_only,
            "no_gui": args.no_gui,
            "list_github_organizations": args.list_github_organizations,
            "print_github_username": args.print_github_username,
            "print_github_token": args.print_github_token,
            "print_repository_settings": args.print_repository_settings,
            "repository_settings_set_default_path": args.repository_settings_set_default_path,
            "repository_settings_set_default_path_for_every_repository": \
                args.repository_settings_set_default_path_for_every_repository,
            "start_server": args.start_server,
            "start_basic_http_server": args.start_basic_http_server,
            "start_optimal_server": args.start_optimal_server,
            "port": args.port,
        }


class ArgumentsHandler:
    db_keys = ["github_token", "github_username"]

    def __init__(
            self,
            sql_settings_table):
        self.sql_settings_table = sql_settings_table

        # Get arugments
        self.arguments = parse_arguments()

        # Store them locally so they can be retrieved somewhere else
        LocalData.save_data(self.arguments, "arguments")

        # Run commands
        self.run_commands()

    def run_commands(self):
        """Run commands"""
        args = self.arguments

        # Run cmds
        if args["list_github_organizations"]:
            cmd.list_github_organizations(
                args["list_github_organizations"],
                self.sql_settings_table
            )
        if args["print_github_token"]:
            cmd.print_github_token(self.sql_settings_table)
        if args["print_github_username"]:
            cmd.print_github_username(self.sql_settings_table)
        if args["print_repository_settings"]:
            cmd.print_repository_settings(args["print_repository_settings"])
        if args["repository_settings_set_default_path"]:
            cmd.repository_settings_set_default_path(args["repository_settings_set_default_path"])
        if args["repository_settings_set_default_path_for_every_repository"]:
            cmd.repository_settings_set_default_path_for_every_repository()

    def get_arguments(self):
        """Get arguments"""
        return self.arguments

    def save_arguments(self):
        """Save data"""
        for key in list(self.arguments.keys()):
            # Only save if the key exists in the database
            if key in self.db_keys:
                value = self.arguments[key]

                if value is None:
                    continue

                data = {
                    "key": key,
                    "value": value,
                }

                # This is to check if it already exists
                #                    Data  Key(Col) Value(Row)
                # sql.insert_replace(data, "key", "asdf")
                self.sql_settings_table.insert_replace(data, "key", key)
