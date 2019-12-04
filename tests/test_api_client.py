"""Tests for privacy.api_client"""
from unittest import mock


import pytest
import requests


from privacy import api_client
from privacy import http_client
from privacy.schema import card


def make_mock_response(json_return):
    json = mock.MagicMock(requests.models.Response.json, return_value=json_return)
    return mock.MagicMock(requests.models.Response, json=json, status_code=200)


@pytest.fixture()
def mock_api_client():  # mock_HTTPClient
    client = api_client.APIClient("a-token")
    session = mock.MagicMock(requests.session(), headers={"Authorization": "api-key A_key"})
    client.http = mock.MagicMock(spec_set=http_client.HTTPClient, session=session)
    return client


@pytest.fixture
def mock_card_payload():
    return {
        "created": "",
        "funding": {
            "account_name": "THIS_IS_AN_ACCOUNT",
            "token": "3234-1231-1231",
            "type": "CARD_DEBIT"
        },
        "hostname": "",
        "last_four": "4212",
        "memo": "Robbin Williams quote",
        "spend_limit": 55,
        "spend_limit_duration": "MONTHLY",
        "state": "OPEN",
        "token": "2031-4521-3212",
        "type": "SINGLE_USE",
    }


class TestAPIClient:
    def test_update_api_key(self, mock_api_client):
        mock_api_client.update_api_key("new_api_key")
        assert mock_api_client.http.session.headers["Authorization"] == "api-key new_api_key"

    def test_api_key(self, mock_api_client):
        assert mock_api_client.api_key == "A_key"

    @pytest.mark.skip(reason="Not Implemented")
    def test_cards_list(self, mock_api_client):
        mock_api_client.cards_list(
            token="a_token",
            page=4,
            page_size=2,
        )

    @pytest.mark.skip(reason="Not Implemented")
    def test_transactions_list(self, mock_api_client):
        ...

    @pytest.mark.skip(reason="Not Implemented")
    def test_cards_create(self, mock_api_client, mock_card_payload):
        # with mock.patch.object(mock_api_client.http.session, "request", return_value=make_mock_response(return_data)) as mock_api:
    #    mock_api_client.http.session.request = mock.MagicMock(return_value=make_mock_response(return_data))
    #     mock_api_client.http.session.request.return_value = make_mock_response(return_data)
        mock_api_client.http.return_value = make_mock_response(mock_card_payload)
        result = mock_api_client.cards_create(
            card_type=card.Type.SINGLE_USE,
            memo="Robbin Williams quote",
            spend_limit=55,
            spend_limit_duration=card.SpendLimitDuration.MONTHLY,
        )
        assert isinstance(result, card.Card)
        mock_api_client.http.assert_called_once_with(
            ("GET", "card"),
            json={
                "type": card.Type.SINGLE_USE,
                "memo": "Robbin Williams quote",
                "spend_limit": 55,
                "spend_limit_duration": card.SpendLimitDuration.MONTHLY,
        })

    @pytest.mark.skip(reason="Not Implemented")
    def test_cards_modify(self, mock_api_client, mock_card_payload):
        mock_api_client.http.return_value = make_mock_response(mock_card_payload)
        result = mock_api_client.cards_modify(
            token="2323-2323-2323",
            state=card.State.CLOSED,
            memo="rip",
            spend_limit=22,
            spend_limit_duration=card.SpendLimitDuration.FOREVER,
        )
        assert isinstance(result, card.Card)
        mock_api_client.http.assert_called_once_with(
            ("PUT", "card"),
            json={
                "card_token": "2323-2323-2323",
                "state": card.State.CLOSED,
                "memo": "rip",
                "spend_limit": 22,
                "spend_limit_duration": card.SpendLimitDuration.FOREVER,
        })
