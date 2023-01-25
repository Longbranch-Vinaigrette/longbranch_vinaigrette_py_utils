from django.http import HttpRequest
from ..Debug import Debug


class DjangoUtils:
    def validate_json_content_type(self, request: HttpRequest) -> dict:
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
