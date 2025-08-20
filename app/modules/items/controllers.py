from flask import Blueprint

from app import limiter, resp_handler
from app.models.item import Item
from app.utils.auth import require_auth

mod_items = Blueprint('items', __name__, url_prefix='/api/items')


@mod_items.route('/', methods=['GET'])
def list_items():
    data = Item.list()
    return resp_handler.ok(data=data)


@mod_items.route('/secure', methods=['GET'])
@limiter.limit("60/minute")
@require_auth
def secure_list(claims):
    data = Item.list()
    return resp_handler.ok(data=data)
