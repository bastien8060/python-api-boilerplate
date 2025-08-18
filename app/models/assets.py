from datetime import datetime, timedelta
import json
from firebase_admin import storage
from app import client

class Assets:
    """
    
    """
    
    def createAsset(asset_type: str, name: str) -> str:
        """
        Function to create an asset
        """

        return client.query_single_json("""
            INSERT File {
                name := <str>$name,
                mime_type := <str>$mime_type,
            }""", name=name, mime_type=asset_type)
    
    def uploadAsset(file, asset_type, name):
        """
        Function to upload a file to Firebase Storage
        """

        _id = json.loads(Assets.createAsset(asset_type, name))['id']
        
        # file argument is a Flask request.files object
        # _id is the ID of the asset
        # email is the email of the author
        # check if file is valid
        if not file:
            return '{"error": "No file provided"}', 400
        
        # check if file is too big
        if file.content_length > 10485760:
            return '{"error": "File too big"}', 400
        
        # upload file to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(_id)
        blob.upload_from_file(file)

        return json.dumps({"id": _id}), 200
        
    def getDownloadUrl(_id):
        """
        Function to get a download URL for an asset
        """

        bucket = storage.bucket()
        blob = bucket.blob(_id)
        return blob.generate_signed_url(datetime.now() + timedelta(days=60), method='GET')