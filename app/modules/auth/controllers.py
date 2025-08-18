from firebase_admin import auth
from flask import Blueprint, request
from app.models.auth import Account
from app import limiter, resp_handler

mod_auth = Blueprint('auth', __name__, url_prefix='/api/auth')

def clean_token(token: str) -> str:
    """
    Function to clean a token of the 'Bearer' prefix
    """
    return token.split(" ")[-1]

def verify_token(token: str):
    """
    Function to verify a token's validity, and if valid, return the user email
    """
    
    try:
        token = clean_token(token)
        decoded_token = auth.verify_id_token(token, clock_skew_seconds=10)
        if decoded_token:
            return True, decoded_token['email']
    except Exception as e:
        pass
    
    return False, None


@mod_auth.route('/verify', methods=['GET'])
@limiter.limit("120/minute;5/second", deduct_when=lambda response: response.status_code != 503)
def verify():
    ''' 
    Function to verify a user's token/secret key against their username
    Returns the user object if successful
    '''

    try:
        token = request.headers.get('Authorization')
        verified, email = verify_token(token)
        if not verified:
            return resp_handler.get_handler("token_auth")
        else:            
            return Account.populateAccount(email)

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))


@mod_auth.route('/email/validate/<email>', methods=['GET'])
@limiter.limit("120/minute;5/second", deduct_when=lambda response: response.status_code != 503)
def emailCardinality(email):
    '''
    Function to check if an email is already signed up
    '''

    try:
        count = Account.checkEmailCardinality(email)
        return resp_handler.get_handler("response_ok", {"data": {"count": count}})
    
    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))
    
@mod_auth.route('/username/validate/<username>', methods=['GET'])
@limiter.limit("120/minute;5/second", deduct_when=lambda response: response.status_code != 503)
def usernameCardinality(username):
    '''
    Function to check if a username is already signed up
    '''

    try:
        count = Account.checkUsernameCardinality(username)
        return resp_handler.get_handler("response_ok", {"data": {"count": count}})
    
    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))     

@mod_auth.route('/signup', methods=['POST'])
@limiter.limit("120/minute;5/second", deduct_when=lambda response: response.status_code != 503)
def signup():
    '''
    Function to sign up a user
    '''

    try:
        data = request.get_json(force=True)
        account = Account.create_account(data)

        if not account.get("user"):
            return resp_handler.get_handler("unhandled_error", "Account creation failed")

        return resp_handler.get_handler("response_ok", {"data": account})
        
    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))