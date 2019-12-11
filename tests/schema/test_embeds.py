"""Tests for privacy.schema.embed"""
from privacy.schema import embeds


def test_embed_request():
    embed_request_obj = embeds.EmbedRequest(token="3523-6543-1236-8975", css="https://www.not_a.url")
    assert embed_request_obj.token == "3523-6543-1236-8975"
    assert embed_request_obj.css == "https://www.not_a.url"
    assert embed_request_obj.expiration is None
