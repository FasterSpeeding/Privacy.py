"""Tests for privacy.util.functional"""
from privacy.util.functional import b64_encode, get_dict_path, hmac_sign, optional


def test_b64_encode():
    assert b64_encode(b"ok, this worked!?!?!?!?") == "b2ssIHRoaXMgd29ya2VkIT8hPyE/IT8="


def test_get_dict_path():
    mock_dict = {"OK": "NO", "I": {"LLL": {"OWO": "nyaa"}, "PW": 22}, "LWLW": 2}
    assert get_dict_path(mock_dict, ("I", "LLL", "OWO")) == "nyaa"
    try:
        error = get_dict_path(mock_dict, "This key doesn't exist")
    except Exception as e:
        error = e

    assert isinstance(error, KeyError)


def test_hmac_sign():
    mock_signed = hmac_sign("c268d61ad6f545339e6c6d194c1e4104", "I am the computer man. I can do anything you can.")
    assert mock_signed == "fupsBqXVZUtsfwcukputmyWptu90rOTQUMEpgeHbH2Q="


def test_optional():
    mock_dict = {"some": "body", "once": "told", "me": "the"}
    assert optional(**mock_dict) == mock_dict

    mock_dict = {"this": "is", "empty and": None}
    assert optional(**mock_dict) == {"this": "is"}
