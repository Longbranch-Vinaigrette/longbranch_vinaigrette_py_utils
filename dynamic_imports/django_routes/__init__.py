"""

Following my own standard that the files must have a class named 'Main'
and inside that class there are functions with the http methods name in lowercase."""
from django.http import HttpRequest
from django.urls import path

from ..Routes import Routes


def execute_method(req: HttpRequest, obj):
    """Execute a function depending on the request method"""
    print("Request method: ", req.method)
    print("Request route: ", req.path_info)
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
            debug: bool = False):
        super().__init__(routes_path, use_full_routes=True, debug=debug)

        # Add or remove starting and trailing slash
        # the default values, comply with django philosophy
        self.start_slash = start_slash
        self.trailing_slash = trailing_slash

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
        for route_path in list(self.routes.keys()):
            route_instance = self.routes[route_path]
            route_name_parsed = self.parse_route_name(route_path)
            urlpatterns.append(
                path(
                    route_name_parsed,
                    lambda request: execute_method(request, route_instance),
                    name=route_name_parsed
                ))

        return urlpatterns
