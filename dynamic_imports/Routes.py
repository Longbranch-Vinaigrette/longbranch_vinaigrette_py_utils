"""Routes
Get server routes for python servers

1. Introduction
    This class is used to search the given path recursively and return
    a list of routes from the path to be stored on and only on memory.
1.1. Purpose
    When creating a new route, you would normally have to add it manually,
    and manually call it's many functions, that would be a lot of work sometimes.

    With this class you will relieve a lot of that hassle, and you will only need
    to implement an interpreter of the routes' dictionary.
1.2. Terminology
    SAME LEVEL:
        Same level refers to files that are on the same folder:
            /home/user/apps
            /home/user/hello.txt

2. Schema of given the given routes path
    The routes may have folders and [NAME].py files, in which the .py files will
    be instantiated and the folders will be added to the dictionary and MAY
    contain more instanced python files.

    Names inside the routes folder that are at the SAME LEVEL SHALL NOT
    have same names, for example:
    ###### Legal:
        /routes
        | - /app.py
        | - /test.py
        | - /apps       < - Folder
        | - | - /db_manager.py
    ###### Illegal:
        /routes
        | - /app.py     < - File with name 'app'(.py is removed from the name)
        | - /app        < - Folder with name 'app'
        | - | - /some_file.py
        | - /test.py
        | - /apps
        | - | - /db_manager.py
    Failing to comply will raise an exception.
2.1. Ignored folders and files
    The folder '__pycache__' will be ignored.
2.2. Python files schema
    The python files should have a class inside called 'Main', this class
    MUST have the request methods in lower case, like this:
    ```python
    class Main:
        def __init__(self, route: str = ""):
            self.route = route

        def get(self, req: dict, res: dict):
            print(f"\n{self.route}")

            # Set it's body
            res["body"] = {
                "message": "Success",
                "queryTo": self.route
            }
            return res

        def post(self, req: dict, res: dict):
            print(f"\n{self.route}")

            # Set it's body
            res["body"] = {
                "message": f"Query received at: {self.route}",
            }
            return res
    ```
    Also note that the class constructor MUST receive an argument which is the relative
    route.

3. Routes(This very class)
    To get the routes after instantiating the class, use [OBJECT].get_routes(),
    this will return a dictionary with every route instantiated.
3.1. Building an interpreter
    To use routes you would have to create a small interpreter for the dictionary object
    which has every instantiated class.
    You would normally call the get function of the instantiated class
    when receiving a request to the file route, for example:
        ```HTTP/1.1
        GET /test HTTP/1.1
        ```

        For that request you MUST call:
        ```python
        routes_dictionary["test"].get()
        ```
"""
import importlib.util
import os


class Routes:
    def __init__(self, starting_path: str, use_full_routes: bool = False, debug: bool = False):
        """Routes object

        IF use_full_routes is True, the dictionary indexes will be, the full route instead
        of being nested.
        """
        self.starting_path = starting_path
        self.use_full_routes = use_full_routes
        self.debug = debug

        self.routes = self.get_routes()

    def get_routes(self):
        """Dynamic routes importing

        Note: That files must have a 'Main' class"""
        return self._get_routes(self.starting_path, self.debug)

    def raise_error_on_repeated_names(self, path: str):
        """If there's a repeated name raise an error
        We need indices to confirm that is not the same file"""
        i = 0
        for f in os.listdir(path):
            f_renamed = f.replace(".py", "")

            j = 0
            for f2 in os.listdir(path):
                # Same indices, next item
                if i == j:
                    continue

                # These two have the same name
                f2_renamed = f2.replace(".py", "")
                if f_renamed == f2_renamed:
                    raise Exception(f"There are two files with the same name at: "
                                    f"{path}")
                j += 1
            i += 1

    def discover_routes(self, path: str) -> dict:
        """Discover routes"""
        files = [f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f))]

        functions: dict = {}

        for file in files:
            file_path = f"{path}{os.path.sep}{file}"

            spec = importlib.util.spec_from_file_location("main", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            route_name = file.replace(".py", "")

            route_location = path.replace(self.starting_path, "").replace("\\", "/")
            full_route_name = f"{route_location}/{route_name}"

            # If using routes as indexes
            if self.use_full_routes:
                functions[full_route_name] = module.Main(full_route_name)
            else:
                functions[route_name] = module.Main(full_route_name)

        return functions

    def _get_routes(self, path: str, debug: bool = False) -> dict:
        """Dynamic routes importing

        Note: That files must have a 'Main' class"""
        if debug:
            print(f"Now searching at: {path}")

        # Validate that there are not repeated route names
        self.raise_error_on_repeated_names(path)

        # Discover and instantiate routes
        functions: dict = self.discover_routes(path)

        # Recursive search
        folders = [f for f in os.listdir(path)
                   if not os.path.isfile(os.path.join(path, f))]
        if debug:
            print("Folders: ", folders)
        for folder in folders:
            if not folder == "__pycache__":
                if debug:
                    print(f"{folder}")

                # If using routes as indexes
                if self.use_full_routes:
                    subfunctions = self._get_routes(f"{path}{os.path.sep}{folder}",
                                              debug=debug)
                    functions = {
                        **functions,
                        **subfunctions,
                    }
                else:
                    subfunctions = self._get_routes(f"{path}{os.path.sep}{folder}",
                                              debug=debug)
                    functions[folder] = subfunctions

        return functions

    def get_route_object(self, route: str):
        """Get the class of the requested route

        This is a built-in interpreter of the routes dictionary,
        just give it a route and it will return the class needed, then call
        the method you want, e.g:
        ```python
        route = "/database/get"

        # Get the route object in the routes dictionary
        route_object = get_route_object(route)

        # Now call the methods
        if method == "GET":
            route_object.get()
        if method == "POST":
            route_object.post()
        ```
        """
        # Get the route by parts
        paths = [_ for _ in route.split("/") if _]
        msg = f"Unknown error or route '{route}' not found."

        # Search path
        temp_routes = dict(self.routes)
        for path in paths:
            try:
                temp_routes = temp_routes[path]

                if self.is_folder(temp_routes):
                    # It's not a class
                    continue

                # It's a class
                return temp_routes
            except Exception as ex:
                print(msg)
                print("Exception: ", ex)
                raise Exception(msg)
        msg += "(2)"
        print(msg)
        raise Exception(msg)

    def is_folder(self, route):
        """Check whether the route is a folder or not"""
        if isinstance(route, dict):
            return True
        else:
            return False
