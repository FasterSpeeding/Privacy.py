"""Classes and functions used by this module."""
from typing import Any, List
import base64
import hashlib
import hmac


def b64_encode(data: bytes) -> str:
    """
    Base64 encode bytes.

    Args:
        data:
            Bytes data to be encoded

    Returns:
        A base64 utf-8 string.
    """
    return base64.b64encode(data).decode("utf-8")


def get_dict_path(data: dict, path: List[str]) -> Any:
    """
    Used to get a value in a dict based on a path.

    Args:
        data:
            A dict of data to be searched.
        path:
            An ordered list of string keys to be used for iterating through the dict.

    Returns:
        The resultant dict value.
    """
    for key in path:
        data = data[key]

    return data


def hmac_sign(key: str, msg: str) -> str:
    """
    Get a base64 encoded hmac has of a message.

    Args:
        key:
            The str key used for generating the hash.
        msg:
            The str message being hashed.

    returns:
        base64 encoded utf-8 string.
    """
    hmac_buffer = hmac.new(
        key=bytes(key, "utf-8"),
        msg=bytes(msg, "utf-8"),
        digestmod=hashlib.sha256,
    )
    return b64_encode(hmac_buffer.digest())


def optional(**kwargs: Any) -> dict:
    """
    Take a set of keyword arguments and return a dict with only the not-None values.

    returns:
        dict
    """
    return {key: value for key, value in kwargs.items() if value is not None}
