from typing import Iterable
import json

from privacy.api import RESTClient, Routes
from privacy.schema import (
    Card, Transaction, CardSpendLimitDurations, CardStates, CardTypes,
)
from privacy.util.functional import (
    b64_encode, JsonEncoder, hmac_sign, optional,
)
from privacy.util.logging import LoggingClass
from privacy.util.pagination import Direction


def auth_header(api_key=None):
    return optional(Authorization=api_key)


class Client(LoggingClass):
    def __init__(
            self, api_key: str = None,
            backoff: bool = True, debug: bool = False) -> None:
        self.api_key = api_key
        self.api = RESTClient(api_key=api_key, backoff=backoff, debug=debug)

    def update_api_key(self, api_key: str = None) -> None:
        self.api_key = api_key
        self.api.session.headers["Authorization"] = api_key

    def cards_list(
            self, token: str = None, page: int = None, page_size: int = None,
            begin: str = None, end: str = None, direction: Direction = None,
            api_key: str = None) -> Iterable[Card]:
        return Card.paginate(
            self,
            Routes.CARDS_LIST,
            headers=auth_header(api_key),
            direction=direction,
            params=optional(
                card_token=token,
                page=page,
                page_size=page_size,
                begin=begin,
                end=end,
            )
        )

    def transactions_list(
            self, approval_status: str = "all", token: str = None,
            page: int = None, page_size: int = None, begin: str = None,
            end: str = None, direction: Direction = None,
            api_key: str = None) -> Iterable[Transaction]:
        return Transaction.paginate(
            self,
            Routes.TRANSACTIONS_LIST,
            dict(approval_status=approval_status),
            headers=auth_header(api_key),
            direction=direction,
            params=optional(
                transaction_token=token,
                page=page,
                page_size=page_size,
                begin=begin,
                end=end,
            )
        )

    # Premium
    def cards_create(
            self, card_type: CardTypes, name: str = None,
            spend_limit: CardSpendLimitDurations = None,
            spend_limit_duration: int = None, api_key=None) -> Card:
        r = self.api(
            Routes.CARDS_CREATE,
            headers=auth_header(api_key),
            json=optional(
                type=card_type,
                name=name,
                spend_limit=spend_limit,
                spend_limit_duration=spend_limit_duration,
            )
        )
        return Card(client=self.api, **r.json())

    def cards_modify(
            self, card_token: str, state: CardStates = None,
            memo: str = None, spend_limit: int = None,
            spend_limit_duration: int = None, api_key: str = None) -> Card:
        r = self.api(
            Routes.CARDS_MODIFY,
            headers=auth_header(api_key),
            json=optional(
                card_token=card_token,
                state=state,
                memo=memo,
                spend_limit=spend_limit,
                spend_limit_duration=spend_limit_duration,
            )
        )
        return Card(client=self.api, **r.json())

    def hoisted_card_ui_get(
            self, embed_request: dict, api_key: str = None) -> str:
        embed_request_json = json.dumps(embed_request, cls=JsonEncoder)
        embed_request = b64_encode(bytes(embed_request_json, "utf-8"))
        embed_request_hmac = hmac_sign(api_key or self.api_key, embed_request)

        return self.api(
            Routes.HOSTED_CARD_UI_GET,
            headers=auth_header(api_key),
            json=dict(embed_request=embed_request, hmac=embed_request_hmac),
        ).content

    # Sandbox
    def auth_simulate(
            self, descriptor: str, pan: str,
            amount: int, api_key: str = None) -> dict:
        return self.api(
            Routes.SIMULATE_AUTH,
            headers=auth_header(api_key),
            json=dict(
                descriptor=descriptor,
                pan=pan,
                amount=amount,
            )
        ).json()

    def void_simulate(
            self, token: str, amount: int, api_key: str = None) -> dict:
        return self.api(
            Routes.SIMULATE_VOID,
            headers=auth_header(api_key),
            json=dict(token=token, amount=amount),
        ).json()

    def clearing_simulate(
            self, token: str, amount: int, api_key: str = None) -> dict:
        return self.api(
            Routes.SIMULATE_CLEARING,
            headers=auth_header(api_key),
            json=dict(token=token, amount=amount),
        ).json()

    def return_simulate(
            self, descriptor: str, pan: str,
            amount: int, api_key: str = None) -> dict:
        return self.api(
            Routes.SIMULATE_RETURN,
            headers=auth_header(api_key),
            json=dict(
                descriptor=descriptor,
                pan=pan,
                amount=amount,
            )
        ).json()
