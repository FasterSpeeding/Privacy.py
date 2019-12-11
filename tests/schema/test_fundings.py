"""The tests for privacy.schema.funding"""
from privacy.schema import fundings


def test_funding_account():
    funding_account_obj = fundings.Account(
        **{"account_name": "American Dream Denial", "token": "3953-7543-7543-6542", "type": "CARD_DEBIT"}
    )
    assert funding_account_obj.account_name == "American Dream Denial"
    assert funding_account_obj.token == "3953-7543-7543-6542"
    assert funding_account_obj.type is fundings.Type.CARD_DEBIT
