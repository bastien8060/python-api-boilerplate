# app/models/post.py

import json
from uuid import UUID

from app.models.response import response_ok, response_error_auth, response_error_generic
from app import client

def insert_post(payload, email, authed) -> str:
    """
    Create a new post for the authenticated user.
    Called from: /page/generic/insert_post
    """
    if not authed:
        return response_error_auth("Unauthorized")

    title = payload.get("title")
    content = payload.get("content", "")
    starred = payload.get("starred", False)
    file_id = payload.get("file_id")

    if not title:
        return response_error_generic("Post title is required.")

    query = json.loads(client.query_single_json("""
        INSERT Post {
            title := <str>$title,
            content := <str>$content,
            starred := <bool>$starred,
            author := (SELECT User FILTER .email = <str>$email)
        }
    """, title=title, content=content, starred=starred, email=email))

    media_query = None
    if file_id:
        media_query = json.loads(client.query_single_json("""
            UPDATE Post
            FILTER .id = <uuid>$post_id
            SET {
                file := (SELECT File FILTER .id = <uuid>$file_id)
            }
        """, file_id=file_id, post_id=query["id"]))

    return response_ok({ "status": "created", "id": query["id"], "queries": [query, media_query] })


def edit_post(payload, email, authed) -> str:
    """
    Update an existing post owned by the user.
    Called from: /page/generic/edit_post
    """
    if not authed:
        return response_error_auth("Unauthorized")

    post_id = payload.get("id")
    title = payload.get("title")
    content = payload.get("content", "")
    starred = payload.get("starred", False)
    file_id = payload.get("file_id")

    if not post_id or not title:
        return response_error_generic("Post ID and title are required.")

    # Validate UUID
    try:
        UUID(post_id)
    except ValueError:
        return response_error_generic("Invalid post ID format.")

    if file_id:
        media_query = json.loads(client.query_single_json("""
            UPDATE Post
            FILTER .id = <uuid>$post_id
            SET {
                file := (SELECT File FILTER .id = <uuid>$file_id)
            }
        """, file_id=file_id, post_id=post_id))
    else:
        media_query = json.loads(client.query_single_json("""
            UPDATE Post
            FILTER .id = <uuid>$post_id
            SET {
                file := { }
            }
        """, post_id=post_id))

    query = json.loads(client.query_single_json("""
        UPDATE Post
        FILTER .id = <uuid>$post_id AND .author.email = <str>$email
        SET {
            title := <str>$title,
            content := <str>$content,
            starred := <bool>$starred,
        }
    """, post_id=post_id, title=title, content=content, starred=starred, email=email))

    return response_ok({ "status": "updated", "queries": [query, media_query] })


def delete_post(payload, email, authed) -> str:
    """
    Delete an existing post owned by the user.
    Called from: /page/generic/delete_post
    """
    if not authed:
        return response_error_auth("Unauthorized")

    post_id = payload.get("id")
    if not post_id:
        return response_error_generic("Post ID is required.")

    # Validate UUID
    try:
        UUID(post_id)
    except ValueError:
        return response_error_generic("Invalid post ID format.")

    client.query_single_json("""
        DELETE Post
        FILTER .id = <uuid>$post_id AND .author.email = <str>$email
    """, post_id=post_id, email=email)

    return response_ok({ "status": "deleted" })

def get_posts_member(payload, email, authed) -> str:
    """
    Function to get a public member's posts.
    Displayed on the member's page.
    """

    username = payload.get("username")
    query = json.loads(client.query_single_json("""
        SELECT User {
            posts: { * , file: { * } },
        } FILTER .username = <str>$username;
    """, username=username))

    return response_ok(query)

# Finally, register everything in a Post model router:
class Model:
    name = "posts"
    content = {
        "get_by_user": get_posts_member,
        "insert": insert_post,
        "edit": edit_post,
        "delete": delete_post,
    }
