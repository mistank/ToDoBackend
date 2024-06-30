import binascii

from fastapi import Request, Response, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from itsdangerous import URLSafeTimedSerializer, BadSignature
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
CSRF_TOKEN_EXPIRATION = 3600  # 1 hour

serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_csrf_token() -> str:
    random_bytes = os.urandom(16)
    random_string = binascii.hexlify(random_bytes).decode()  # convert bytes to string
    return serializer.dumps(random_string)


def verify_csrf_token(token):
    try:
        serializer.loads(token, max_age=CSRF_TOKEN_EXPIRATION)
        return True
    except BadSignature:
        return False


async def csrf_protect(request: Request, call_next, exclude=None):
    if exclude is None:
        exclude = []
    if request.url.path not in exclude:
        if request.method in ("POST", "PUT", "DELETE"):
            print(request.headers)
            csrf_token = request.headers.get("cookie").split("X-CSRF-Token=")[1]
            print("CSRF: " + csrf_token)
            if not csrf_token or not verify_csrf_token(csrf_token):
                raise HTTPException(status_code=403, detail="Invalid CSRF token")

    response = await call_next(request)
    response.set_cookie(key="X-CSRF-Token", value=generate_csrf_token(), httponly=True, secure=True)
    return response