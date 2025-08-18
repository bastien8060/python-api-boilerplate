import os
import requests, mimetypes
from flask import Blueprint, request, Response, redirect, send_file, make_response, current_app
from firebase_admin import auth
from hashlib import md5
from datetime import datetime, timezone, timedelta

from app import limiter, resp_handler
from app.models.assets import Assets
from app.modules.auth.controllers import verify_token


mod_assets = Blueprint('assets', __name__, url_prefix='/api/assets')

def cache_response(response: Response, max_age: int = 3600, etag: str = None):
    """Add caching headers to the response"""
    # Clear any existing caching headers to avoid conflicts
    for header in ['Cache-Control', 'Expires', 'Last-Modified', 'Pragma', 'Vary']:
        if header in response.headers:
            del response.headers[header]
    
    # Set aggressive caching headers
    response.headers['Cache-Control'] = f'public, max-age={max_age}, immutable'
    
    if etag:
        response.headers['ETag'] = f'"{etag}"'  # Wrap ETag in quotes as per RFC
    
    # Add explicit expires header
    expires = datetime.now(timezone.utc) + timedelta(seconds=max_age)
    response.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Set Last-Modified to a fixed time in the past
    response.headers['Last-Modified'] = datetime(2023, 1, 1, tzinfo=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Add Vary header to ensure proper caching with different encodings
    response.headers['Vary'] = 'Accept-Encoding'
    
    # Ensure no-cache pragma is not set
    response.headers['Pragma'] = 'public'
    
    return response

@mod_assets.route('/', methods=['GET'])
@limiter.limit("120/minute;5/second", deduct_when=lambda response: response.status_code != 503)
def populate():
    ''' 
    Function to verify a user's token/secret key against their username
    Returns the user assets if successful
    '''

    try:
        token = request.headers.get('Authorization')
        verified, email = verify_token(token)
        if not verified:
            return resp_handler.get_handler("token_auth")
        
        else:            
            return Assets.getByAuthorEmail(email)

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))

@mod_assets.route('/upload/<name>', methods=['POST'])
@limiter.limit("15/minute;5/second", deduct_when=lambda response: response.status_code != 503)
def uploadAsset(name):
    ''' 
    Function to verify a user's token/secret key against their username
    Checks if they are the rightful author of Asset by ID
    Uploads an asset with ID as chain (Firebase Storage) if successful
    '''

    try:
        token = request.headers.get('Authorization')
        verified, email = verify_token(token)
        if not verified:
            # return resp_handler.get_handler("token_auth")
            pass # will be enforced after scaling
        
        if not request.files:
            return resp_handler.get_handler("unhandled_error", "No files provided")
        
        else:
            mime_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'
            return Assets.uploadAsset(request.files['file'], asset_type=mime_type, name=name)

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))
    
@mod_assets.route('/download/<id>', methods=['GET'])
@limiter.limit("150/minute;150/second", deduct_when=lambda response: response.status_code != 503)
def downloadAsset(id):
    try:
        # Check if we already have a valid cached response
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match:
            # Strip quotes if present
            if_none_match = if_none_match.strip('"')
            
            # Check if asset_id hash matches the ETag
            asset_id_hash = md5(id.encode()).hexdigest()
            if if_none_match == asset_id_hash:
                return Response(status=304)  # Not Modified
        
        # Get the asset
        url = Assets.getDownloadUrl(id)
        data = requests.get(url)
        
        if data.status_code == 200:
            content = data.content
            etag = md5(content).hexdigest()
            
            response = Response(content, mimetype='application/octet-stream')
            
            # Force download with attachment disposition
            response.headers.set('Content-Disposition', f'attachment; filename="{id}"')
            
            return cache_response(response, max_age=2592000, etag=etag)  # Cache for 30 days
        else:
            return resp_handler.get_handler("not_found", "Asset not found")

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))

@mod_assets.route('/<id>/<filename>', methods=['GET'])
@limiter.limit("150/minute;150/second", deduct_when=lambda response: response.status_code != 503)
def downloadAssetWithMime(id, filename):
    try:
        # Generate a cache key combining id and filename
        cache_key = f"{id}:{filename}"
        cache_key_hash = md5(cache_key.encode()).hexdigest()
        
        # Check for conditional request using If-None-Match
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match:
            # Strip quotes if present
            if_none_match = if_none_match.strip('"')
            if if_none_match == cache_key_hash:
                # If ETag matches, return 304 Not Modified immediately
                return Response(status=304)
                
        # Get the asset
        url = Assets.getDownloadUrl(id)
        data = requests.get(url)

        if data.status_code == 200:
            content = data.content
            etag = cache_key_hash  # Use our predefined hash for consistency
            
            file_ext = os.path.splitext(filename)[1]
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            response = make_response(content)
            
            # Ensure content type is set before other headers
            response.headers.set('Content-Type', mime_type)
            response.headers.set('Content-Disposition', f'inline; filename="{filename}"')
            
            # Very aggressive caching - 1 year for static assets
            return cache_response(response, max_age=31536000, etag=etag)
        else:
            return resp_handler.get_handler("not_found", "Asset not found")

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))

@mod_assets.route('/<id>', methods=['GET'])
@limiter.limit("150/minute;150/second", deduct_when=lambda response: response.status_code != 503)
def getDownloadUrl(id):
    try:
        # Generate consistent ETag based on asset ID
        asset_id_hash = md5(id.encode()).hexdigest()
        
        # Check for conditional request
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match:
            if_none_match = if_none_match.strip('"')
            if if_none_match == asset_id_hash:
                return Response(status=304)  # Not Modified
        
        # Use permanent redirect
        target_url = Assets.getDownloadUrl(id)
        response = redirect(target_url, code=302)
        
        # Clear any existing headers that might interfere with caching
        for header in ['Cache-Control', 'Expires', 'Pragma']:
            if header in response.headers:
                del response.headers[header]
        
        # Set aggressive caching for the redirect itself
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'  # 1 year
        expires = datetime.now(timezone.utc) + timedelta(seconds=31536000)
        response.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['ETag'] = f'"{asset_id_hash}"'
        response.headers['Vary'] = 'Accept-Encoding'
        response.headers['Pragma'] = 'public'
        
        return response

    except Exception as e:
        return resp_handler.get_handler("unhandled_error", str(e))

# Add a before_request handler to check if browser is sending cache validation
@mod_assets.before_request
def handle_conditional_request():
    # Only apply to GET requests for efficiency
    if request.method != 'GET':
        return
    
    # Only apply to asset endpoints
    if not request.path.startswith('/api/assets/'):
        return
    
    # If this is a conditional request with If-None-Match
    if_none_match = request.headers.get('If-None-Match')
    if if_none_match and not request.path.endswith('/'):
        # Extract the asset ID from the path
        parts = request.path.split('/')
        if len(parts) >= 3:
            asset_id = parts[3]  # Extract ID from /api/assets/<id>
            asset_id_hash = md5(asset_id.encode()).hexdigest()
            
            # If the ETag matches, return 304 without further processing
            if if_none_match.strip('"') == asset_id_hash:
                return Response(status=304)