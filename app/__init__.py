import gel
import logging
from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import settings
from app.resp_handler import RespHandler

app = Flask(__name__)
app.config.from_mapping(DEBUG=settings.DEBUG)
CORS(app)

limiter = Limiter(get_remote_address, app=app)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s %(levelname)s : %(message)s'
)

resp_handler = RespHandler(settings.DEBUG)
client = gel.create_client()

from app.modules.auth.controllers import mod_auth
from app.modules.items.controllers import mod_items

app.register_blueprint(mod_auth)
app.register_blueprint(mod_items)

@app.errorhandler(404)
def not_found(error):
    return resp_handler.not_found(request.path)

@app.errorhandler(429)
def ratelimit_handler(error):
    return resp_handler.rate_limit_exceeded()
