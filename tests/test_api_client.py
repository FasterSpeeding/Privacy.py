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
    #client.api.session =
    session = mock.MagicMock(requests.session(), headers={"Authorization": "api-key A_key"})
    client.api = mock.MagicMock(http_client.HTTPClient, session=session,)
    return client


class TestAPIClient:
    def test_update_api_key(self, mock_api_client):
        mock_api_client.update_api_key("new_api_key")
        assert mock_api_client.api.session.headers["Authorization"] == "api-key new_api_key"

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

    def test_cards_create(self, mock_api_client):
        # with mock.patch.object(mock_api_client.api.session, "request", return_value=make_mock_response(return_data)) as mock_api:
    #    mock_api_client.api.session.request = mock.MagicMock(return_value=make_mock_response(return_data))
    #     mock_api_client.api.session.request.return_value = make_mock_response(return_data)
        mock_api_client.api.return_value = make_mock_response({
            "card_type": "SINGLE_USE",
            "memo": "Robbin Williams quote",
            "spend_limit": 55,
            "spend_limit_duration": "MONTHLY",
        })
        result = mock_api_client.cards_create(
            card_type=card.Type.SINGLE_USE,
            memo="Robbin Williams quote",
            spend_limit=55,
            spend_limit_duration=card.SpendLimitDuration.MONTHLY,
        )
        assert isinstance(result, card)
        mock_api_client.api.assert_called_once_with(
            http_client.Routes.CARDS_CREATE,
            json={
                "type": card.Type.SINGLE_USE,
                "memo": "Robbin Williams quote",
                "spend_limit": 55,
                "spend_limit_duration": card.SpendLimitDuration.MONTHLY,
        })
