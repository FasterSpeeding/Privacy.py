"""Tests for privacy.util.functional"""
from privacy.util import functional


def test_b64_encode():
    assert functional.b64_encode(b"ok, this worked!?!?!?!?") == "b2ssIHRoaXMgd29ya2VkIT8hPyE/IT8="


def test_get_dict_path():
    class MockObject:
        class MockAttrObj:
            OwO = "nyaa"

    assert functional.get_attr_path(MockObject, ("MockAttrObj", "OwO")) == "nyaa"
    try:
        error = functional.get_attr_path(MockObject, "This key doesn't exist")
    except Exception as e:
        error = e

    assert isinstance(error, AttributeError)


def test_hmac_sign():
    mock_signed = functional.hmac_sign(
        "c268d61ad6f545339e6c6d194c1e4104",
        "I am the computer man. I can do anything you can.",
    )
    assert mock_signed == "fupsBqXVZUtsfwcukputmyWptu90rOTQUMEpgeHbH2Q="


def test_optional():
    mock_dict = {"some": "body", "once": "told", "me": "the"}
    assert functional.optional(**mock_dict) == mock_dict

    mock_dict = {"this": "is", "empty and": None}
    assert functional.optional(**mock_dict) == {"this": "is"}
