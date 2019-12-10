import json


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "json"):
            return obj.json()
        elif hasattr(obj, "value"):
            return obj.value

        return super().default(obj)

    @classmethod
    def dumps(cls, data: dict) -> str:
        return json.dumps(data, cls=cls)
