"""Tests for privacy.schema.card"""
import pytest


from privacy.schema import cards, fundings


@pytest.fixture
def mock_card_payload():
    return {
        "cvv": "032",
        "funding": {"account_name": "Major Park", "token": "4953-3234-1236", "type": "CARD_DEBIT"},
        "exp_month": "02",
        "exp_year": "2032",
        "hostname": "",
        "last_four": "0323",
        "pan": "2043234223422342",
        "memo": "",
        "spend_limit": "6400",
        "spend_limit_duration": "MONTHLY",
        "state": "CLOSED",
        "token": "2453-3423-6543-2342",
        "type": "SINGLE_USE",
    }


class TestCard:
    def test_model(self, mock_card_payload):
        card_obj = cards.Card(**mock_card_payload)
        assert card_obj.cvv == "032"
        assert card_obj.funding.account_name == "Major Park"
        assert card_obj.funding.token == "4953-3234-1236"
        assert card_obj.funding.type is fundings.Type.CARD_DEBIT
        assert card_obj.exp_month == "02"
        assert card_obj.exp_year == "2032"
        assert card_obj.pan == "2043234223422342"
        assert card_obj.spend_limit_duration is cards.SpendLimitDuration.MONTHLY
        assert card_obj.state is cards.State.CLOSED
        assert card_obj.token == "2453-3423-6543-2342"
        assert card_obj.type is cards.Type.SINGLE_USE
        assert card_obj.memo == ""

    @pytest.mark.skip(reason="Not Implemented")
    def test_update(self):
        ...

    @pytest.mark.skip(reason="Not Implemented")
    def test_get_transactions(self):
        ...
