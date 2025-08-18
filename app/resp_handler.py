import logging
from flask import jsonify, make_response

logger = logging.getLogger(__name__)

class RespHandler(object):
    def __init__(self, debug=False):
        self.debug = debug
    
    def get_handler(self, respType, args=None):
        if hasattr(self, respType):
            if args is None:
                return getattr(self, respType)()
            return getattr(self, respType)(args)

        else:
            logger.error(f"Unhandled Error: {respType}")
            return self.unhandled_error(str(args))
        
    def invalid_request(self, error):
        logger.warning(f"[!] invalid request: {error}")
        return make_response(jsonify({"status": "Invalid Request", "msg": error}), 400)

    def server_error(self, error):
        logger.error(f"[!] server error: {error}")
        return make_response(jsonify({"status": error}), 503)

    def unhandled_error(self, error):
        logger.error(f"[!] unhandled error: {error}")
        return make_response(jsonify({"status": "server error", "msg": error}), 503)

    def unauthorized(self, error):
        logger.warning(f"[!] unauthorized: {error}")
        return make_response(jsonify({"status": "Unauthorized", "msg": error}), 403)

    def forbidden(self, error):
        logger.warning(f"[!] forbidden: {error}")
        return make_response(jsonify({"status": "Forbidden", "msg": error}), 403)

    def token_auth(self):
        logger.warning("[!] token auth failed")
        return make_response(jsonify({"status": "Unauthorized", "msg": "Incorrect Authorization (username or token)"}), 401)

    def rate_limit_exceeded(self):
        logger.warning("[!] rate limit exceeded")
        return make_response(jsonify({"status": "Rate Limit Exceeded"}), 429)
    
    def not_found(self, path):
        logger.warning("[!] not found")
        return make_response(jsonify({"status": "Not Found", "msg": f"Resource not found: {path}"}), 404)
    
    def response_ok(self, args={}):
        if "data" in args:
            data = args["data"]
            logger.info(f"[+] response OK: {data}")
            return jsonify(data)
        elif "msg" in args:
            msg = args["msg"]
            logger.info(f"response OK: {msg}")
            return make_response(jsonify({"status": "OK", "msg": msg}), 200)
        else:
            logger.info("response OK")
            return make_response(jsonify({"status": "OK"}), 200)