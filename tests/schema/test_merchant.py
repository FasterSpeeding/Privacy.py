"""Tests for privacy.schema.merchant"""
from privacy.schema import merchant


def test_merchant():
    merchant_obj = merchant.Merchant(**{
        "acceptor_id": "th",
        "city": "London",
        "country": "GB",
        "descriptor": "This is a card acceptor",
        "mcc": "0742",
        "state": "Texas",
    })
    assert merchant_obj.acceptor_id == "th"
    assert merchant_obj.city == "London"
    assert merchant_obj.country == "GB"
    assert merchant_obj.descriptor == "This is a card acceptor"
    assert merchant_obj.mcc == "0742"
    assert merchant_obj.state == "Texas"
