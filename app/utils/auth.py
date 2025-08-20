import json
import time
from functools import wraps

import httpx
from flask import request
from jose import jwt

from app.config import settings

# simple in-memory cache for JWKS
_JWKS_CACHE = {"expires": 0, "data": None}


def _get_jwks():
    now = time.time()
    if _JWKS_CACHE["data"] and now < _JWKS_CACHE["expires"]:
        return _JWKS_CACHE["data"]
    

    url = f"{settings.KEYCLOAK_BASE_URL}/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    resp = httpx.get(url)
    resp.raise_for_status()
    _JWKS_CACHE["data"] = resp.json()
    _JWKS_CACHE["expires"] = now + 3600  # cache for 1 hour
    return _JWKS_CACHE["data"]


def verify_token(token: str):
    try:
        token = token.split(" ")[-1]
        jwks = _get_jwks()
        header = jwt.get_unverified_header(token)
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                claims = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    audience=settings.KEYCLOAK_CLIENT_ID,
                )
                return True, claims
    except Exception:
        pass
    return False, None


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from app import resp_handler

        token = request.headers.get("Authorization", "")
        valid, claims = verify_token(token)
        if not valid:
            return resp_handler.token_auth_failed()
        return fn(claims, *args, **kwargs)

    return wrapper
