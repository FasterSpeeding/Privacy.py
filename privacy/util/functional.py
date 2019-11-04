from datetime import datetime
from enum import Enum
from typing import Any, List
import base64
import hashlib
import hmac
import json


def b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def get_dict_path(data: dict, path: List[str]) -> Any:
    for key in path:
        data = data[key]

    return data


def hmac_sign(key: str, msg: str) -> str:
    hmac_buffer = hmac.new(
        key=bytes(key, "utf-8"),
        msg=bytes(msg, "utf-8"),
        digestmod=hashlib.sha256,
    )
    return b64_encode(hmac_buffer.digest())


class JsonEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif issubclass(obj.__class__, Enum):
            return obj.value
        else:
            return super(JsonEncoder, self).default(obj)


def optional(**kwargs: Any) -> dict:
    return {key: value for key, value in kwargs.items() if value is not None}
