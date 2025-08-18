from flask import Blueprint, request
from firebase_admin import auth
from app import limiter, resp_handler
from app.models.page import Page
from app.modules.auth.controllers import verify_token

mod_page = Blueprint('page', __name__, url_prefix='/api/page')

@mod_page.route('/<page>/<component>', methods=['GET'])
@limiter.limit("300/minute;15/second", deduct_when=lambda response: response.status_code != 503)
def getPageHandler(page, component):
    ''' 
    Function to verify a user's token/secret key against their username
    Returns the user object if successful
    '''
    payload = {}

    try:
        payload = request.args.to_dict()
    except Exception as e:
        pass
    
    try:
        token = request.headers.get('Authorization')
        verified, email = verify_token(token)
        authResult = {"email": email, "verified": verified}
        
        resp, code, headers = Page.run(page, component, payload, authResult)
        return resp, code, headers

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))
    
@mod_page.route('/<page>/<component>', methods=['POST', 'PUT', 'UPDATE', 'DELETE'])
@limiter.limit("300/minute;15/second", deduct_when=lambda response: response.status_code != 503)
def postPageHandler(page, component):
    ''' 
    Function to verify a user's token/secret key against their username
    Returns the user object if successful
    '''
    payload = {}

    try:
        payload = request.get_json()
    except Exception as e:
        pass
    
    try:
        token = request.headers.get('Authorization')
        verified, email = verify_token(token)
        authResult = {"email": email, "verified": verified}

        resp, code, headers = Page.run(page, component, payload, authResult)
        return resp, code, headers

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))