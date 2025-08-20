import json

from app import client

class Item:
    @staticmethod
    def list():
        result = client.query_json(
            "SELECT Item { id, name } ORDER BY .name LIMIT 10"
        )
        return json.loads(result)
