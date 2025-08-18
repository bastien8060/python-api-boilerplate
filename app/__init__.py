import gel
import firebase_admin
from flask import Flask, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import logging

from app.resp_handler import RespHandler

# Define the WSGI application object
app = Flask(__name__)
# Load configurations
app.config.from_object('app.config')

# Enable CORS
CORS(app)

# Configure Flask Limiter
limiter = Limiter(
  get_remote_address,
  app=app
)

# Add logging
logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s %(levelname)s : %(message)s',
  filename='./be-main.log',
  filemode='a'
)

# use that logger
logger = logging.getLogger(__name__)

logger.info('Starting BE...')

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
  cred = firebase_admin.credentials.Certificate(app.config['FIREBASE_CREDENTIALS'])
  firebase_admin.initialize_app(cred, {'storageBucket': app.config['FIREBASE_BUCKET']})

conn_config = {}

# Initialize Gel client
client = gel.create_client(
  port=conn_config.get('port', None),
  host=conn_config.get('host', None),
  password=conn_config.get('password', None),
  tls_security='insecure',
)

# Initialize response handler
resp_handler = RespHandler(app.config['DEBUG'])

# Sample HTTP 404 error handling
@app.errorhandler(404)
def not_found(error):
  path = request.path
  logger.error("status=404, error={}, path={}".format(error, path))
  return resp_handler.get_handler("not_found", args=path)

# Handle 429/API rate limit errors
@app.errorhandler(429)
def ratelimit_handler(error):
  logger.error("status=429, error={}".format(error))
  return resp_handler.get_handler("rate_limit_exceeded")

# Add CORS headers to response
@app.after_request 
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'POST,GET,PUT,DELETE,OPTIONS,UPDATE')
  return response

# Add static serve directory
@app.route('/static/<path:path>')
def send_static(path):
  return send_from_directory('static', path)

@app.route('/')
def index():
  return send_from_directory('static', 'index.html')

# Import blueprints
from app.modules.auth.controllers import mod_auth as auth_module
from app.modules.assets.controllers import mod_assets as assets_module
from app.modules.page.controllers import mod_page as page_module

# Register blueprints
app.register_blueprint(auth_module)
app.register_blueprint(assets_module)
app.register_blueprint(page_module)