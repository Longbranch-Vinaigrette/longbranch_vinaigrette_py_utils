from .Routes import Routes


class DjangoRoutes:
    def __init__(self, path: str, debug: bool = False):
        self.routes = Routes(path, debug=debug)

    def get_routes_list(self):
        """Get routes Django compatible"""

