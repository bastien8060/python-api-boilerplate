import httpx
from flask import Blueprint, request

from app import limiter, resp_handler
from app.config import settings
from app.utils.auth import require_auth

mod_auth = Blueprint('auth', __name__, url_prefix='/api/auth')


@mod_auth.route('/callback', methods=['POST'])
@limiter.limit("60/minute")
def callback():
    data = request.get_json() or {}
    code = data.get("code")
    code_verifier = data.get("code_verifier")
    redirect_uri = data.get("redirect_uri")
    if not redirect_uri or redirect_uri not in settings.KEYCLOAK_ALLOWED_REDIRECTS:
        return resp_handler.invalid_request("invalid redirect")
    
    url = settings.KEYCLOAK_BASE_URL + '/' + settings.KEYCLOAK_REALM
    token_endpoint = f"{url}/protocol/openid-connect/token"
    r = httpx.post(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
        },
    )
    if r.status_code != 200:
        return resp_handler.unauthorized("token exchange failed")
    tokens = r.json()
    response = resp_handler.ok(data={"token": tokens["access_token"]})
    response.set_cookie(
        "refresh_token",
        tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Strict",
        domain=settings.AUTH_BASE_DOMAIN,
    )
    return response


@mod_auth.route('/refresh', methods=['POST'])
@limiter.limit("60/minute")
def refresh():
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return resp_handler.unauthorized("missing refresh token")
    
    url = settings.KEYCLOAK_BASE_URL + '/' + settings.KEYCLOAK_REALM
    token_endpoint = f"{url}/protocol/openid-connect/token"
    r = httpx.post(
        token_endpoint,
        data={
            "grant_type": "refresh_token",
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "refresh_token": refresh_token,
        },
    )
    if r.status_code != 200:
        return resp_handler.unauthorized("refresh failed")
    tokens = r.json()
    response = resp_handler.ok(data={"token": tokens["access_token"]})
    response.set_cookie(
        "refresh_token",
        tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Strict",
        domain=settings.AUTH_BASE_DOMAIN,
    )
    return response


@mod_auth.route('/logout', methods=['POST'])
def logout():
    response = resp_handler.ok(msg="logged out")
    response.delete_cookie("refresh_token", domain=settings.AUTH_BASE_DOMAIN)
    return response


@mod_auth.route('/me', methods=['GET'])
@limiter.limit("120/minute")
@require_auth
def me(claims):
    return resp_handler.ok(data=claims)
