from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import auth
from iso3166 import countries
import re

from app import client

def strip_username(username: str) -> str:
    """
    Function to strip username of illegal characters, whitespace, capitalization...
    """
    return re.sub(r'[^a-zA-Z0-9\-\_\.]', '', username).lower()

def normalize_email(email: str) -> str:
    """
    Function to normalize email address: space, capitalization, etc...
    """
    return email.strip().lower()

def verify_token(token: str):
    """
    Function to verify a token's validity, and if valid, return the user email
    """
    
    try:
        if not token:
            raise Exception("No token provided")
        
        decoded_token = auth.verify_id_token(token)
        if decoded_token:
            return True, decoded_token['email']
    except Exception as e:
        pass
    
    return False, None

class Account:
    def checkEmailCardinality(email: str):
        return len(client.query("""
            SELECT User
            FILTER .email = <str>$email
            """, email=normalize_email(email)))
    
    def checkUsernameCardinality(username: str):
        return len(client.query("""
            SELECT User
            FILTER .username = <str>$username
            """, username=strip_username(username)))
    
    def setStarredPost(email, postID, starred):
        return client.query_single("""
            UPDATE Post
            FILTER .author.email = <str>$email AND .id = <int32>$postID
            SET {
                starred := <bool>$starred
            }
            """, email=email, postID=postID, starred=starred)
    
    def deletePost(email, postID):
        return client.query_single("""
            DELETE Post
            FILTER .author.email = <str>$email AND .id = <int32>$postID
            """, email=email, postID=postID)
    
    def createPost(title, content, fileID, email):        
        return client.query_single("""
            INSERT Post {
                title := <str>$title,
                content := <int32>$content,
                
                author := (select User FILTER .email = <str>$email),
                file := (select File FILTER .id = <int32>$fileID),
                                   
            }
        """, title=title, content=content, fileID=fileID, email=email)
    
    def create_account(params: dict) -> dict:
        """
        Creates a new User entity in EdgeDB, handling potential errors.

        Args:
            client: The EdgeDB client object.
            params: A dictionary containing the required user details.
            - email: The email address of the user.
            - username: The username of the user.
            - fullname: The full name of the user.
            - invite_key: The shared password of the user.
            - description: A brief description of the user (optional).
            - qualifications: A list of qualifications of the user (optional).
            - avatar_id: The ID of the user's avatar (optional).
            - banner_id: The ID of the user's banner (optional

        Returns:
            A dictionary containing the newly created 'user' object, or an error message if user creation fails.
        """

        # Extract parameters, providing defaults for optional ones
        email = normalize_email(params['email'])
        username = strip_username(params['username'])
        fullname = params['fullname']
        description = params.get('description', "")  # Default to empty string if not provided
        qualifications = params.get('qualifications', [])
        shared_password = params.get('invite_key', "")
        avatar_id = params.get('avatar_id', None)
        banner_id = params.get('banner_id', None)

        if '@' not in email:
            return {'error': f"Invalid email address '{email}'"}

        if not fullname:
            return {'error': f"Full name is required"}
        
        if not username:
            return {'error': f"Username is required"}

        try:
            # Check if user already exists (assuming email is the unique identifier)
            existing_user = client.query_single(
                """
                SELECT User
                FILTER .email = <str>$email
                LIMIT 1;
                """,
                email=email
            )

            if existing_user:
                return {'error': f"User with email '{email}' already exists"}
            
            shared_password_check = client.query_single(
                """
                Select SharedPassword
                FILTER .key = <str>$shared_password
                LIMIT 1;
                """,
                shared_password=shared_password
            )

            if not shared_password_check:
                return {'error': f"Shared password is incorrect"}

            # Create the new User entity
            new_user = client.query_single(
                """
                SELECT (
                    INSERT User {
                        email := <str>$email,
                        username := <str>$username,
                        fullname := <str>$fullname,
                        bio := <str>$description,
                        qualifications := <array<str>>$qualifications,
                    }
                );
                """,
                email=email,
                username=username,
                fullname=fullname,
                description=description,
                qualifications=qualifications
            )

            if banner_id:
                client.query_single(
                    """
                    UPDATE User
                    FILTER .email = <str>$email
                    SET {
                        banner := (SELECT File FILTER .id = <uuid>$banner_id)
                    }
                    """, email=email, banner_id=banner_id
                )

            if avatar_id:
                client.query_single(
                    """
                    UPDATE User
                    FILTER .email = <str>$email
                    SET {
                        avatar := (SELECT File FILTER .id = <uuid>$avatar_id)
                    }
                    """, email=email, avatar_id=avatar_id
                )

            return {'user': new_user}

        except Exception as e:
            return {'error': f"An error occurred while creating the user: {e}"}

    def populateAccount(email: str) -> str:
        """
        Function to populate user from email
        """

        return client.query_single_json("""
            SELECT User {
                *,
                posts: { *, file: { * } },
                avatar: { * },
                banner: { * },
            }
            FILTER .email = <str>$email
            LIMIT 1
            """, email=email)
        