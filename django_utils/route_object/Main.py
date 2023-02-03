import json

from django.http import HttpRequest

from ...django_utils import DjangoUtils
from ...Debug import Debug


def validate_plain_text_content_type(request: HttpRequest):
    """Validate if the Content-Type of the request is plain/text"""
    try:
        if request.headers["Content-Type"] == "text/plain":
            return True
        else:
            msg = f"Expected Content-Type of text/plain, given " \
                  f"Content-Type: {request.headers['Content-Type']}"
            return Debug(msg, error=True, state="error") \
                .get_full_message()
    except Exception as ex:
        print("Exception: ")
        print(ex)
        return Debug(f"Unknown error when trying to validate that the Content-Type "
                     f"is plain/text, error: {str(ex)}.", error=True,
                     state="error") \
            .get_full_message()


class Main:
    data_dependencies: list = []
    post_fn = None

    def __init__(self,
                 route: str,
                 get_fn=None,
                 post_fn=None,
                 mime_type: str = "application/json"):
        self.route = route
        self.get_fn = get_fn
        if post_fn:
            print(f"Settings post fn, for route {route}.")
            self.post_fn = post_fn
        self.mime_type = mime_type

        self.debug = False

    def set_get_fn(self, get_fn):
        self.get_fn = get_fn

    def set_post_fn(self, post_fn):
        self.post_fn = post_fn

    def set_data_dependencies(self, data_dependencies: list):
        """Set data dependencies

        The list should be a list of keyword names to search inside the dictionary
        of a request with application/json headers"""
        self.data_dependencies = data_dependencies

    def post(self, request: HttpRequest):
        """Make a post request"""
        dj_utils = DjangoUtils(request)

        # Check if the request has Content-Type
        if not ("Content-Type" in request.headers):
            return Debug("Content-Type not given.", error=True, state="error") \
                .get_full_message()

        # Now, some routes require a specific Content-Type
        if self.mime_type == "application/json":
            print("Using default mime_type application/json")
            data = dj_utils.validate_json_content_type(request)

            # If there is "debug" in data it means that there was an error
            if not "debug" in data:
                body: dict = json.loads(request.body.decode("utf-8"))

                # Check if the required data was given
                try:
                    # Inform the user in case the data is in a bad format.
                    if not isinstance(self.data_dependencies, list):
                        msg = "Data dependencies is not a list."
                        raise Exception(msg)
                    if len(self.data_dependencies) <= 0:
                        msg = "No data dependencies in a POST request with Content-Type set" \
                              "to application/json"
                        raise Exception(msg)

                    # Set error message to give to the user
                    for key in self.data_dependencies:
                        # Detect if the key was given or not
                        try:
                            element = body[key]
                        except:
                            msg = f"Key error, {key} was not given."
                            raise Exception(msg)
                except Exception as ex:
                    print("Exception: ", ex)
                    data = {
                        "debug": Debug(msg, error=True,
                                       state="danger").get_message(),
                    }
                    return dj_utils.get_json_response(data)

                try:
                    print("Executing fn: ", self.post_fn)
                    if self.post_fn:
                        return self.post_fn(request)
                    else:
                        raise Exception("This route doesn't handle the given method.")
                except Exception as ex:
                    print(f"\nroute_object({self.route}) -> Main -> post -> Exception: ", ex)
                    data = {
                        "debug": Debug(f"Unknown error: {str(ex)}", error=True,
                                       state="error").get_message(),
                    }

            return dj_utils.get_json_response(data)
        elif self.mime_type == "text/plain":
            # This is the mime we're gonna use for arbitrary code execution
            # Check that the content type is in fact plain/text
            result = validate_plain_text_content_type(request)

            # If it's a bool and is True, then it's the correct Content-Type
            if isinstance(result, bool) and result:
                return self.post_fn(request)
            else:
                # Return the error message
                return dj_utils.get_json_response(result)
        else:
            msg = "There are no routes that support the given Content-Type."
            print(msg)
            data = {
                "debug": Debug(msg, error=True,
                               state="danger").get_message(),
            }
            return dj_utils.get_json_response(data)

    def get(self, request: HttpRequest):
        """Make a get request"""
        dj_utils = DjangoUtils(request)
        data = dj_utils.validate_accept_json()

        # If there is "debug" in data it means that there was an error
        if not "debug" in data:
            try:
                if self.get_fn:
                    return self.get_fn(request)
                else:
                    raise Exception("This route doesn't handle the given method.")
            except Exception as ex:
                print("Exception: ", ex)
                data = {
                    "debug": Debug("Unknown error.", error=True,
                                   state="error").get_message(),
                }

        return dj_utils.get_json_response(data)

    def handle_request(self, req: HttpRequest):
        """Handle request"""
        if req.method == "POST":
            return self.post(req)
        elif req.method == "GET":
            return self.get(req)
        else:
            raise Exception("This route doesn't handle the given method.")
