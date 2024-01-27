from django.http import JsonResponse


class CustomException(Exception):
    """
    Params:
        msg* (string): Message for output
        code (string): Additional id exception for some purposes
    """

    def __init__(self, msg: str, code: str = None) -> None:
        super().__init__()
        self.msg = msg
        self.code = code

    def __str__(self) -> str:
        return self.msg

    def to_json(self) -> dict:
        return {
            "message": self.msg,
            "code": self.code,
        }

    def to_json_response(self):
        return JsonResponse(self.to_json(), status=500)


class ClientError(CustomException):
    def to_json_response(self):
        return JsonResponse(self.to_json(), status=400)


class ObjectNotFound(CustomException):
    def to_json_response(self):
        return JsonResponse(self.to_json(), status=404)


class ConflictError(CustomException):
    def to_json_response(self):
        return JsonResponse(self.to_json(), status=409)
