import json

from app.models.response import response_ok, response_error_auth
from app import client

def get_members(payload, email, authed) -> str:
    """
    Function to list all of public members.
    Displayed on the members page.
    """
    
    query = json.loads(client.query_single_json("""
        SELECT {
            results := (
                SELECT User {
                    id,
                    username,
                    fullname,
                    posts: { * , file: { * } },
                    avatar: { * },
                    banner: { * },
                    bio,
                    qualifications,
                } ORDER BY .created_at ASC
            )
        };
    """))

    return response_ok(query)

def get_public_member(payload, email, authed) -> str:
    """
    Function to get a public member."
    Displayed on the member's page."
    """

    username = payload.get("username")
    query = json.loads(client.query_single_json("""
        SELECT User {
            id,
            username,
            fullname,
            posts: { * , file: { * } },
            avatar: { * },
            banner: { * },
            bio,
            qualifications,
        } FILTER .username = $username;
    """, username=username))

    return response_ok(query)

def get_projects(payload, email, authed) -> str:
    """
    Function to list all of public projects.
    Displayed on the projects page.
    """

    query = json.loads(client.query_single_json("""
        SELECT {
            results := (
                SELECT Project {
                    *, banner: { * }, logo: { * }, 
                    members: { *, user: { 
                        id, username, fullname, avatar: { * } 
                    } }
                } ORDER BY .created_at DESC
            )
        };
    """))

    return response_ok(query)

class Model:
    name = "generic"
    content = {
        "get_members": get_members,
        "get_public_member": get_public_member,
        "get_projects": get_projects,
    }