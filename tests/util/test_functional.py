"""Tests for privacy.util.functional"""
from privacy.util.functional import get_dict_path, optional


def test_get_dict_path():
    mock_dict = {"OK": "NO", "I": {"LLL": {"OWO": "nyaa"}, "PW": 22}, "LWLW": 2}
    assert get_dict_path(mock_dict, ("I", "LLL", "OWO")) == "nyaa"
    try:
        error = get_dict_path(mock_dict, "This key doesn't exist")
    except Exception as e:
        error = e

    assert isinstance(error, KeyError)


def test_optional():
    mock_dict = {"some": "body", "once": "told", "me": "the"}
    assert optional(**mock_dict) == mock_dict

    mock_dict = {"this": "is", "empty and": None}
    assert optional(**mock_dict) == {"this": "is"}
