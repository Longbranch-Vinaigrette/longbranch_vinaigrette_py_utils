import json

from django.http import HttpRequest, HttpResponse

from ..Debug import Debug


def get_json_response(data: dict):
    """Get a Django json response with the given data"""
    res = HttpResponse(json.dumps(data))
    res.headers["Content-Type"] = "application/json"
    return res


def validate_json_content_type(request: HttpRequest):
    """Validate if the Content-Type of the request is json"""
    try:
        if "Content-Type" in request.headers:
            if request.headers["Content-Type"] == "application/json":
                return {}
            else:
                msg = f"Content-Type not supported, given " \
                      f"Content-Type: {request.headers['Content-Type']}"
                return Debug(msg, error=True, state="error") \
                    .get_full_message()
        else:
            return Debug("Content-Type not given.", error=True, state="error") \
                .get_full_message()
    except Exception as ex:
        print("Exception: ")
        print(ex)
        return Debug("Unknown error, it's likely that the table doesn't exist.", error=True,
                     state="error") \
            .get_full_message()


class DjangoUtils:
    def __init__(self, request: HttpRequest = None, debug: bool = False):
        self.request = request
        self.debug = debug

    def get_json_response(self, data: dict):
        """Get a Django json response with the given data"""
        if self.debug:
            print("\nDjangoUtils -> get_json_response():")
        return get_json_response(data)

    def validate_json_content_type(self, request: HttpRequest) -> dict:
        """Validate if the Content-Type of the request is json"""
        if self.debug:
            print("\nDjangoUtils -> validate_json_content_type():")
        return validate_json_content_type(request)
