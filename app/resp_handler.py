import logging
from flask import jsonify, make_response

logger = logging.getLogger(__name__)


class RespHandler:
    def __init__(self, debug: bool = False):
        self.debug = debug

    def ok(self, data=None, msg: str | None = None):
        if data is None:
            payload = {"status": "OK", "msg": msg}
            return make_response(jsonify(payload), 200)
        return jsonify(data)

    def error(self, msg: str, status: int):
        logger.error(f"[!] {status}: {msg}")
        return make_response(jsonify({"status": "error", "msg": msg}), status)

    def invalid_request(self, error: str):
        logger.warning(f"[!] invalid request: {error}")
        return self.error(f"Invalid Request: {error}", 400)

    def server_error(self, error: str):
        return self.error(error, 503)

    def unauthorized(self, error: str):
        logger.warning(f"[!] unauthorized: {error}")
        return self.error(f"Unauthorized: {error}", 403)

    def token_auth_failed(self):
        logger.warning("[!] token auth failed")
        return make_response(
            jsonify({"status": "Unauthorized", "msg": "Incorrect Authorization (username or token)"}),
            401,
        )

    def rate_limit_exceeded(self):
        logger.warning("[!] rate limit exceeded")
        return make_response(jsonify({"status": "Rate Limit Exceeded"}), 429)

    def not_found(self, path: str):
        logger.warning("[!] not found")
        return make_response(
            jsonify({"status": "Not Found", "msg": f"Resource not found: {path}"}),
            404,
        )
