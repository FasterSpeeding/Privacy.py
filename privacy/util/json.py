import json


class CustomJsonEncoder(json.JSONEncoder):
    """Used for handling json encoding with internal models and enums."""

    def default(self, obj):
        #  This will be found on pydantic based models where we want to use the built in encoder.
        if hasattr(obj, "json"):
            return obj.json()
        #  This will be found on enums where the value will be a json ready string or integer.
        elif hasattr(obj, "value"):
            return obj.value

        return super().default(obj)

    @classmethod
    def dumps(cls, data: dict) -> str:
        """A shortcut for json.dumps(data, cls=CustomJsonEncoder)."""
        return json.dumps(data, cls=cls)
