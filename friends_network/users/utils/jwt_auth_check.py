import jwt
from rest_framework.request import Request
from django.contrib.auth.models import User

from functools import wraps
from django.http import HttpResponse

from friends_network import settings


def jwt_auth_check(view_function):
    @wraps(view_function)
    def wrap(self, request: Request, *args, **kwargs):
        header_prefix = "Bearer"
        header: str = request.headers.get("Authorization")

        if header is None or not header.startswith(header_prefix):
            return HttpResponse(status=400)

        token = header.removeprefix(header_prefix).strip()

        try:
            decoded = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

            request.user = User.objects.get(id=decoded["id"])

        except jwt.exceptions.InvalidSignatureError:
            return HttpResponse(status=401)
        except jwt.ExpiredSignatureError:
            return HttpResponse(status=401)

        return view_function(self, request, *args, **kwargs)

    return wrap
