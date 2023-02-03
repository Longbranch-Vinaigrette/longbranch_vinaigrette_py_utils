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
                msg = f"The expected Content-Type was application/json, but " \
                      f"{request.headers['Content-Type']} was given"
                return Debug(msg, error=True, state="error") \
                    .get_full_message()
        else:
            return Debug("Content-Type not given.", error=True, state="error") \
                .get_full_message()
    except Exception as ex:
        print("Exception: ")
        print(ex)
        return Debug(f"Unknown error: {str(ex)}.", error=True,
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

    def validate_accept_json(self):
        """Validate if the Accept header of the request is json"""
        try:
            if "Accept" in self.request.headers:
                json_supported_headers = ["application/json", "application/*", "*/*"]
                if self.request.headers["Accept"] in json_supported_headers:
                    return {}
                else:
                    msg = f"Accept header not supported, given: {self.request.headers['Accept']}"
                    return Debug(msg, error=True, state="error") \
                        .get_full_message()
            else:
                return Debug("'Accept' header not given.", error=True, state="error") \
                    .get_full_message()
        except Exception as ex:
            print("Exception: ")
            print(ex)
            return Debug(f"Unknown error: {str(ex)}.", error=True,
                         state="error") \
                .get_full_message()
