"""

Following my own standard that the files must have a class named 'Main'
and inside that class there are functions with the http methods name in lowercase.

If handle_request is 'False' the classes must have a 'handle_request' function to handle
the request, it must receive an argument which is the django HttpRequest."""
import pprint

from django.http import HttpRequest
from django.urls import path

from ..Routes import Routes


def execute_method(req: HttpRequest, obj, debug: bool = False):
    """Execute a function depending on the request method"""
    if debug:
        print("Request method: ", req.method)
        print("Request route: ", req.path_info)
        print("Given object route: ", obj.route)

    if req.method == "GET":
        return obj.get(req)
    elif req.method == "POST":
        return obj.post(req)
    else:
        raise Exception("Method not found")


class DjangoRoutes(Routes):
    def __init__(
            self,
            routes_path: str,
            start_slash: bool = False,
            trailing_slash: bool = True,
            handle_request: bool = True,
            debug: bool = False):
        super().__init__(routes_path, use_full_routes=True, debug=debug)

        # Add or remove starting and trailing slash
        # the default values, comply with django philosophy
        self.start_slash = start_slash
        self.trailing_slash = trailing_slash
        self.handle_request = handle_request

    def parse_route_name(self, route_name: str):
        """Parse route name

        To add/remove the starting slash and add/remove the trailing slash"""
        result: str = route_name

        # Add or remove starting slash
        if self.start_slash:
            if not result.startswith("/"):
                result = f"/{route_name}"
        else:
            if result.startswith("/"):
                result = route_name[1:]

        # Add or remove trailing slash
        if self.trailing_slash:
            if not result.endswith("/"):
                result += "/"
        else:
            if result.endswith("/"):
                result = result[:-1]

        return result

    def get_routes_as_urlpatterns(self):
        """Get routes Django compatible"""
        urlpatterns = []
        if self.debug:
            print("Routes:")
            pprint.pprint(self.routes)
        lambdas = []

        i = 0
        for route_path in list(self.routes.keys()):
            route_instance = self.routes[route_path]
            route_name_parsed = self.parse_route_name(route_path)
            if self.debug:
                print("\n")
                print("Its route: ", route_instance.route)
                print("Parsed route: ", route_name_parsed)
                print(f"path({route_name_parsed}, {route_instance})")

            # TODO: I don't know why it calls the wrong object, it would be cool to fix it later.
            # Some ideas:
            # * Define the function here, inside the iterator, instead of being outside which
            #   may interfere somehow with the references.
            # * Define a class in which you bind the object from the constructor
            #   and in the __call__ function you would receive the request to handle
            #   appropriately.
            if self.handle_request:
                lambdas.append(
                        lambda request: execute_method(
                            request,
                            route_instance,
                            debug=self.debug
                        ))
                urlpatterns.append(
                    path(
                        route_name_parsed,
                        lambdas[i],
                        name=route_name_parsed
                    ))
            else:
                urlpatterns.append(
                    path(
                        route_name_parsed,
                        route_instance.handle_request,
                        name=route_name_parsed
                    )
                )

            i += 1

        return urlpatterns
