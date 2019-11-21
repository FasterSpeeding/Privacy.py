"""General functions used by this module."""
from typing import Any, List
import base64
import hashlib
import hmac


def b64_encode(data: bytes) -> str:
    """
    Base64 encode bytes.

    Args:
        data (bytes): Data to be encoded

    Returns:
        str: A base64 utf-8 string.
    """
    return base64.b64encode(data).decode("utf-8")


def get_attr_path(data: dict, path: List[str]) -> Any:
    """
    Used to get a value in a dict based on a path.

    Args:
        data (dict): A dict of data to be searched.
        path (list): An ordered list of string attrs to be used for searching through the object.

    Returns:
        Any: The resultant value from the object(s).
    """
    for attr in path:
        data = getattr(data, attr)

    return data


def hmac_sign(key: str, msg: str) -> str:
    """
    Get a base64 encoded hmac has of a message.

    Args:
        key (str): The key used for generating the hash.
        msg (str): The message being hashed.

    Returns:
        str: base64 encoded utf-8 string.
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

    Returns:
        dict
    """
    return {key: value for key, value in kwargs.items() if value is not None}
