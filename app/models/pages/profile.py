import json
from app.models.response import response_ok, response_error_auth, response_error_generic
from app import client


def update_profile(payload, email, authed) -> str:
    """
    Function to update a user's profile.
    Called from the frontend via /page/profile/update_profile
    """
    if not authed:
        return response_error_auth("Unauthorized")

    # Validate and sanitize input
    username = payload.get("username")
    fullname = payload.get("fullname")
    bio = payload.get("bio", "")
    qualifications = payload.get("qualifications", [])
    avatar_id = payload.get("avatar_id")
    banner_id = payload.get("banner_id")

    if not username or not fullname:
        return response_error_generic("Username and full name are required.")

    # Clean up qualifications list
    qualifications = [q.strip() for q in qualifications if q.strip()]

    if avatar_id:
        query = json.loads(client.query_single_json("""
            UPDATE User
            FILTER .email = <str>$email
            SET {
                avatar := (SELECT File FILTER .id = <uuid>$avatar_id),
            }
        """, email=email, avatar_id=avatar_id))
        
    if banner_id:
        query = json.loads(client.query_single_json("""
            UPDATE User
            FILTER .email = <str>$email
            SET {
                banner := (SELECT File FILTER .id = <uuid>$banner_id),
            }
        """, email=email, banner_id=banner_id))

    # Perform the update
    query = json.loads(client.query_single_json("""
        UPDATE User
        FILTER .email = <str>$email
        SET {
            username := <str>$username,
            fullname := <str>$fullname,
            bio := <str>$bio,
            qualifications := <array<str>>$qualifications,
        }
    """, email=email, username=username, fullname=fullname, bio=bio,
         qualifications=qualifications))

    return response_ok(query)


def get_private_member(payload, email, authed) -> str:
    """
    Function to get a private member."
    Displayed on the member's page."
    """

    if not authed:
        return response_error_auth("Unauthorized")

    username = payload.get("username")
    query = json.loads(client.query_single_json("""
        SELECT User {
            id,
            *,
            posts: { * , file: { * } },
            avatar: { * },
            banner: { * }
        } FILTER .username = $username AND .email = $email;
    """, username=username, email=email))

    return response_ok(query)

class Model:
    name = "profile"
    content = {
        "update_profile": update_profile,
        "get_profile": get_private_member,

    }