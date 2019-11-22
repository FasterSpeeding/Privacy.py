"""Tests for privacy.schema.card"""
import pytest


from privacy.schema import card


@pytest.fixture
def mock_card_payload():
    return {
        "cvv": "032",
        "funding": {
            "account_name": "Major Park",
            "token": "4953-3234-1236",
            "type": "CARD_DEBIT"
        },
        "exp_month": "02",
        "exp_year": "2032",
        "hostname": "",
        "last_four": "0323",
        "pan": "2043234223422342",
        "spend_limit": "6400",
        "spend_limit_duration": "MONTHLY",
        "state": "CLOSED",
        "token": "2453-3423-6543-2342",
        "type": "SINGLE_USE",
    }


@pytest.mark.model
class TestCard:
    def test_model(self):
        pass

